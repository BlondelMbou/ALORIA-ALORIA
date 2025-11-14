from fastapi import FastAPI, APIRouter, HTTPException, Depends, status
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from dotenv import load_dotenv
from starlette.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
import os
import logging
from pathlib import Path
from pydantic import BaseModel, Field, ConfigDict, EmailStr
from typing import List, Optional, Dict, Any
import uuid
from datetime import datetime, timezone, timedelta
from passlib.context import CryptContext
import jwt
import socketio
from fastapi.middleware import Middleware
import asyncio
from enum import Enum
import random
import string
import io
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.lib.units import inch
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
# Import du service d'e-mails
try:
    from email_service import (
        send_prospect_email, 
        send_user_welcome_email, 
        send_case_update_email,
        send_prospect_assignment_notification,
        send_consultant_appointment_notification
    )
    EMAIL_SERVICE_AVAILABLE = True
except ImportError as e:
    print(f"Service d'e-mails non disponible: {e}")
    EMAIL_SERVICE_AVAILABLE = False

ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

# MongoDB connection
mongo_url = os.environ['MONGO_URL']
client = AsyncIOMotorClient(mongo_url)
db = client[os.environ['DB_NAME']]

# Security
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
security = HTTPBearer()
SECRET_KEY = os.environ.get('SECRET_KEY', 'your-secret-key-change-in-production')
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24 * 7  # 7 days

# WebSocket/SocketIO Setup
sio = socketio.AsyncServer(
    cors_allowed_origins="*",
    logger=True,
    engineio_logger=True,
    async_mode='asgi',
    ping_timeout=60,
    ping_interval=25
)

# Create the main app
app = FastAPI()
api_router = APIRouter(prefix="/api")

# Initialize Scheduler for automated tasks
scheduler = AsyncIOScheduler()

# Mount Socket.IO
socket_app = socketio.ASGIApp(sio)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# WebSocket connection management
connected_users = {}  # {user_id: sid}

# WebSocket Events
@sio.event
async def connect(sid, environ):
    logger.info(f"Client {sid} connected")
    
@sio.event
async def disconnect(sid):
    logger.info(f"Client {sid} disconnected")
    # Remove from connected users
    for user_id, user_sid in list(connected_users.items()):
        if user_sid == sid:
            del connected_users[user_id]
            break

@sio.event
async def authenticate(sid, data):
    try:
        token = data.get('token')
        if not token:
            await sio.emit('error', {'message': 'Token required'}, room=sid)
            return
            
        # Verify token
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id = payload.get("sub")
        
        if user_id:
            connected_users[user_id] = sid
            await sio.emit('authenticated', {'user_id': user_id}, room=sid)
            logger.info(f"User {user_id} authenticated with session {sid}")
        else:
            await sio.emit('error', {'message': 'Invalid token'}, room=sid)
    except jwt.InvalidTokenError:
        await sio.emit('error', {'message': 'Invalid token'}, room=sid)

@sio.event 
async def send_message(sid, data):
    try:
        sender_id = None
        for user_id, user_sid in connected_users.items():
            if user_sid == sid:
                sender_id = user_id
                break
                
        if not sender_id:
            await sio.emit('error', {'message': 'Not authenticated'}, room=sid)
            return
            
        receiver_id = data.get('receiver_id')
        message_text = data.get('message')
        
        if not receiver_id or not message_text:
            await sio.emit('error', {'message': 'Missing receiver_id or message'}, room=sid)
            return
            
        # Save message to database
        message_id = str(uuid.uuid4())
        sender = await db.users.find_one({"id": sender_id})
        receiver = await db.users.find_one({"id": receiver_id})
        
        if not sender or not receiver:
            await sio.emit('error', {'message': 'Invalid sender or receiver'}, room=sid)
            return
            
        message_dict = {
            "id": message_id,
            "sender_id": sender_id,
            "sender_name": sender["full_name"],
            "sender_role": sender["role"],
            "receiver_id": receiver_id,
            "receiver_name": receiver["full_name"], 
            "receiver_role": receiver["role"],
            "message": message_text,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "read_status": False
        }
        
        await db.chat_messages.insert_one(message_dict)
        
        # Send to receiver if online
        receiver_sid = connected_users.get(receiver_id)
        if receiver_sid:
            await sio.emit('new_message', {
                'id': message_id,
                'sender_id': sender_id,
                'sender_name': sender["full_name"],
                'sender_role': sender["role"],
                'message': message_text,
                'timestamp': message_dict["timestamp"]
            }, room=receiver_sid)
            
        # Confirm to sender
        await sio.emit('message_sent', {
            'id': message_id,
            'receiver_name': receiver["full_name"],
            'message': message_text,
            'timestamp': message_dict["timestamp"]
        }, room=sid)
        
    except Exception as e:
        logger.error(f"Error sending message: {e}")
        await sio.emit('error', {'message': 'Failed to send message'}, room=sid)

# Helper functions
def hash_password(password: str) -> str:
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

def create_access_token(data: dict) -> str:
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

# Système de permissions hiérarchiques
ROLE_HIERARCHY = {
    "SUPERADMIN": 4,
    "MANAGER": 3,
    "CONSULTANT": 3,  # Même niveau que Manager
    "EMPLOYEE": 2,
    "CLIENT": 1
}

def can_create_role(creator_role: str, target_role: str) -> bool:
    """Vérifie si un utilisateur peut créer un autre utilisateur d'un certain rôle"""
    creator_level = ROLE_HIERARCHY.get(creator_role, 0)
    target_level = ROLE_HIERARCHY.get(target_role, 0)
    
    # SuperAdmin peut créer Manager et CONSULTANT
    if creator_role == "SUPERADMIN" and target_role in ["MANAGER", "CONSULTANT"]:
        return True
    # Manager peut créer Employee et Client  
    elif creator_role == "MANAGER" and target_role in ["EMPLOYEE", "CLIENT"]:
        return True
    # Employee peut créer Client
    elif creator_role == "EMPLOYEE" and target_role == "CLIENT":
        return True
    
    return False

def can_access_user(accessor_role: str, target_role: str, accessor_id: str = None, target_id: str = None) -> bool:
    """Vérifie si un utilisateur peut accéder aux données d'un autre"""
    accessor_level = ROLE_HIERARCHY.get(accessor_role, 0)
    target_level = ROLE_HIERARCHY.get(target_role, 0)
    
    # SuperAdmin peut tout voir
    if accessor_role == "SUPERADMIN":
        return True
    # Manager peut voir Employee et Client
    elif accessor_role == "MANAGER" and target_role in ["EMPLOYEE", "CLIENT"]:
        return True
    # Employee peut voir ses propres clients assignés
    elif accessor_role == "EMPLOYEE" and target_role == "CLIENT":
        return True  # Vérification spécifique dans l'API
    # Chacun peut voir ses propres données
    elif accessor_id == target_id:
        return True
        
    return False

# Fonction pour générer un mot de passe temporaire
import secrets
import string

def generate_temporary_password(length: int = 12) -> str:
    """Génère un mot de passe temporaire sécurisé"""
    alphabet = string.ascii_letters + string.digits + "!@#$%^&*"
    return ''.join(secrets.choice(alphabet) for _ in range(length))

async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    try:
        token = credentials.credentials
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id = payload.get("sub")
        if user_id is None:
            raise HTTPException(status_code=401, detail="Invalid authentication")
        
        user = await db.users.find_one({"id": user_id}, {"_id": 0})
        if user is None:
            raise HTTPException(status_code=401, detail="User not found")
        return user
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expired")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid token")

# Pydantic Models
class UserBase(BaseModel):
    email: EmailStr
    full_name: str
    phone: Optional[str] = None
    role: str  # MANAGER, EMPLOYEE, CLIENT

class UserCreate(UserBase):
    password: str

class UserResponse(UserBase):
    model_config = ConfigDict(extra="ignore")
    id: str
    is_active: bool
    created_at: str

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class TokenResponse(BaseModel):
    access_token: str
    token_type: str
    user: UserResponse

class UserRegister(BaseModel):
    email: EmailStr
    full_name: str
    phone: Optional[str] = None
    password: str

class LoginResponse(BaseModel):
    access_token: str
    token_type: str
    user: UserResponse

class ClientCreate(BaseModel):
    email: EmailStr
    full_name: str
    phone: str
    country: str
    visa_type: str
    message: Optional[str] = None

class ClientResponse(BaseModel):
    model_config = ConfigDict(extra="ignore")
    id: str
    user_id: str
    assigned_employee_id: Optional[str]
    assigned_employee_name: Optional[str]
    country: str
    visa_type: str
    current_status: str
    current_step: int
    progress_percentage: float
    created_at: str
    updated_at: str
    login_email: Optional[str] = None
    default_password: Optional[str] = None

class CaseResponse(BaseModel):
    model_config = ConfigDict(extra="ignore")
    id: str
    client_id: str
    client_name: str
    country: str
    visa_type: str
    workflow_steps: List[Dict[str, Any]]
    current_step_index: int
    status: str
    notes: Optional[str]
    created_at: str
    updated_at: str

class CaseUpdate(BaseModel):
    current_step_index: Optional[int] = None
    status: Optional[str] = None
    notes: Optional[str] = None

class MessageCreate(BaseModel):
    receiver_id: str
    client_id: str
    message: str

class MessageResponse(BaseModel):
    model_config = ConfigDict(extra="ignore")
    id: str
    sender_id: str
    sender_name: str
    receiver_id: str
    receiver_name: str
    client_id: str
    message: str
    read_status: bool
    created_at: str

class UserRole(str, Enum):
    SUPERADMIN = "SUPERADMIN"
    MANAGER = "MANAGER"
    EMPLOYEE = "EMPLOYEE" 
    CONSULTANT = "CONSULTANT"
    CLIENT = "CLIENT"

class VisitorPurpose(str, Enum):
    CONSULTATION = "Consultation initiale"
    DOCUMENT_SUBMISSION = "Remise de documents"
    STATUS_UPDATE = "Mise à jour du dossier"
    APPOINTMENT = "Rendez-vous planifié"
    URGENT_MATTER = "Affaire urgente"
    INFORMATION_REQUEST = "Demande d'informations"
    PAYMENT = "Paiement"
    OTHER = "Autre"

# V3 New Enums
class ExpenseCategory(str, Enum):
    SALAIRES = "SALAIRES"
    BUREAUX = "BUREAUX"
    JURIDIQUE = "JURIDIQUE"
    DOSSIERS = "DOSSIERS"
    MARKETING = "MARKETING"
    TECH = "TECH"
    TRANSPORT = "TRANSPORT"
    FORMATION = "FORMATION"

class ContactStatus(str, Enum):
    NEW = "nouveau"  # Formulaire soumis
    ASSIGNED_EMPLOYEE = "assigne_employe"  # Assigné à Employé/Manager par SuperAdmin
    PAYMENT_50K = "paiement_50k"  # Payé 50k CFA, affecté au consultant
    IN_CONSULTATION = "en_consultation"  # SuperAdmin en contact
    CONVERTED_CLIENT = "converti_client"  # Devenu client
    ARCHIVED = "archive"  # Archivé

class UrgencyLevel(str, Enum):
    URGENT = "Urgent"
    NORMAL = "Normal"
    INFORMATION = "Information"

class LeadSource(str, Enum):
    WEBSITE = "Site web"
    REFERRAL = "Référencement"
    WORD_OF_MOUTH = "Bouche à oreille"
    SOCIAL_MEDIA = "Réseaux sociaux"
    ADVERTISING = "Publicité"
    PARTNER = "Partenaire"
    OTHER = "Autre"

class VisitorCreate(BaseModel):
    full_name: str  # Nom complet du visiteur
    phone_number: str  # Numéro de téléphone
    purpose: VisitorPurpose  # Motif (dropdown)
    other_purpose: Optional[str] = None  # Précisions si "Autre" sélectionné
    cni_number: str  # Numéro de CNI (Carte Nationale d'Identité)

class VisitorResponse(BaseModel):
    model_config = ConfigDict(extra="ignore")
    id: str
    # Support ancien ET nouveau format pour rétrocompatibilité
    full_name: Optional[str] = None
    name: Optional[str] = None  # Ancien format
    phone_number: Optional[str] = None
    company: Optional[str] = None  # Ancien format
    purpose: str  # Accepter string au lieu de VisitorPurpose enum pour compatibilité
    other_purpose: Optional[str] = None
    details: Optional[str] = None  # Ancien format
    cni_number: Optional[str] = None
    registered_by: Optional[str] = None
    registered_by_id: Optional[str] = None
    arrival_time: str
    departure_time: Optional[str] = None
    created_at: str
    
class ChatMessage(BaseModel):
    id: str
    sender_id: str
    sender_name: str
    sender_role: str
    receiver_id: str
    receiver_name: str
    receiver_role: str
    message: str
    timestamp: str
    read_status: bool
    
class ChatMessageCreate(BaseModel):
    receiver_id: str
    message: str
    
class ChatConversation(BaseModel):
    participant_id: str
    participant_name: str
    participant_role: str
    last_message: Optional[str]
    last_message_time: Optional[str]
    unread_count: int

class WorkflowStepUpdate(BaseModel):
    step_index: int
    status: Optional[str] = None
    notes: Optional[str] = None
    
class CustomWorkflowStep(BaseModel):
    title: str
    description: str
    documents: List[str]
    duration: str

class PasswordChange(BaseModel):
    old_password: str
    new_password: str
    
class ClientCredentials(BaseModel):
    email: str
    password: str

# Nouveaux modèles pour les paiements
class PaymentDeclaration(BaseModel):
    amount: float
    currency: str = "EUR"
    description: Optional[str] = None
    payment_method: str  # "Cash", "Bank Transfer", "Check", etc.
    
class PaymentDeclarationResponse(BaseModel):
    model_config = ConfigDict(extra="ignore")
    id: str
    client_id: str
    client_name: str
    amount: float
    currency: str
    description: Optional[str]
    payment_method: str
    status: str  # "pending", "confirmed", "rejected"
    declared_at: str
    confirmed_at: Optional[str]
    confirmed_by: Optional[str]
    invoice_number: Optional[str]
    confirmation_code: Optional[str] = None
    pdf_invoice_url: Optional[str] = None
    rejection_reason: Optional[str] = None
    message: Optional[str] = None
    
# PaymentConfirmation model removed - replaced by PaymentConfirmRequest
    
# Modèles pour la création d'utilisateurs avec email
class UserCreateRequest(BaseModel):
    email: str
    full_name: str
    phone: str
    role: UserRole
    send_email: bool = True
    
class UserCreateResponse(BaseModel):
    model_config = ConfigDict(extra="ignore")
    id: str
    email: str
    full_name: str
    phone: str
    role: str
    temporary_password: Optional[str]  # Seulement si send_email=False
    email_sent: bool
    
# Modèles pour le monitoring SuperAdmin
class UserActivity(BaseModel):
    user_id: str
    user_name: str
    user_role: str
    action: str
    details: Optional[dict]
    ip_address: Optional[str]
    timestamp: str
    
class ImpersonationRequest(BaseModel):
    target_user_id: str

class NotificationCreate(BaseModel):
    user_id: str
    title: str
    message: str
    type: str  # 'message', 'case_update', 'visitor', etc.
    related_id: Optional[str] = None  # ID of related entity (case_id, message_id, etc.)

class NotificationResponse(BaseModel):
    model_config = ConfigDict(extra="ignore")
    id: str
    user_id: str
    title: str
    message: str
    type: str
    related_id: Optional[str]
    read: bool
    created_at: str

class DashboardStats(BaseModel):
    total_cases: int
    active_cases: int
    completed_cases: int
    pending_cases: int
    total_clients: int
    total_employees: int
    cases_by_country: Dict[str, int]
    cases_by_status: Dict[str, int]

# Modèles de Processus d'Immigration
WORKFLOWS = {
    "Canada": {
        "Permis de travail": [
            {"title": "Consultation initiale et vérification de l'admissibilité", "description": "Évaluer l'admissibilité au permis de travail canadien", "documents": ["Passeport valide", "Diplômes et attestations d'études", "CV détaillé", "Lettre d'offre d'emploi"], "duration": "3-5 jours"},
            {"title": "Collecte des documents", "description": "Rassembler tous les documents requis", "documents": ["Offre d'emploi (EIMT ou dispensée d'EIMT)", "Diplômes (ÉDE si requis)", "Résultats de tests linguistiques (IELTS/CELPIP/TEF)", "Preuve d'expérience professionnelle", "Certificat de police"], "duration": "2-4 semaines"},
            {"title": "Création du compte IRCC", "description": "Créer un compte en ligne sécurisé sur IRCC", "documents": ["Adresse courriel valide", "Questions de sécurité"], "duration": "1 jour"},
            {"title": "Remplissage des formulaires", "description": "Compléter avec précision les formulaires IMM", "documents": ["IMM 1295 - Demande de permis de travail", "IMM 5707 - Renseignements sur la famille", "IMM 5645 - Renseignements sur la famille (si applicable)"], "duration": "3-7 jours"},
            {"title": "Paiement des frais", "description": "Payer les frais de traitement IRCC en ligne", "documents": ["Frais de permis de travail : 155 $ CAD", "Frais de biométrie : 85 $ CAD", "Reçu de paiement"], "duration": "1 jour"},
            {"title": "Soumission de la demande", "description": "Soumettre la demande complète via le portail IRCC", "documents": ["Tous les formulaires remplis", "Documents justificatifs", "Confirmation de paiement"], "duration": "1 jour"},
            {"title": "Rendez-vous biométrique", "description": "Fournir les empreintes digitales et la photo au CAV", "documents": ["Lettre d'instructions pour la biométrie", "Passeport valide", "Confirmation de rendez-vous"], "duration": "1-3 semaines"},
            {"title": "Traitement de la demande", "description": "IRCC examine la demande", "documents": ["Documents additionnels si demandés", "Examen médical (si requis)"], "duration": "8-12 semaines"},
            {"title": "Décision reçue", "description": "Recevoir la notification d'approbation ou de refus", "documents": ["Lettre d'introduction au point d'entrée", "Visa (si pays nécessitant un visa)"], "duration": "1-2 jours"},
            {"title": "Délivrance du permis de travail", "description": "Recevoir le permis de travail au point d'entrée", "documents": ["Document de permis de travail", "Confirmation d'autorisation de travail"], "duration": "À l'arrivée"}
        ],
        "Permis d'études": [
            {"title": "Consultation initiale", "description": "Évaluer les objectifs d'études et l'admissibilité", "documents": ["Passeport valide", "Relevés de notes académiques", "Résultats de tests d'anglais/français"], "duration": "1-3 jours"},
            {"title": "Lettre d'acceptation d'un EED", "description": "Obtenir l'acceptation d'un établissement d'enseignement désigné", "documents": ["Lettre d'acceptation", "Preuve de paiement des frais de scolarité"], "duration": "Varie selon l'établissement"},
            {"title": "Lettre d'attestation PAL/TAL", "description": "Obtenir la lettre d'attestation provinciale/territoriale", "documents": ["PAL/TAL de la province", "Confirmation de l'EED"], "duration": "2-6 semaines"},
            {"title": "Documentation financière", "description": "Prouver les fonds suffisants pour les études", "documents": ["Relevés bancaires (10 000 $ CAD + frais de scolarité)", "Certificat CPG", "Preuve financière du répondant"], "duration": "1-2 semaines"},
            {"title": "Compte IRCC et demande", "description": "Créer un compte et compléter la demande de permis d'études", "documents": ["IMM 1294", "Lettre d'explication", "Plan d'études"], "duration": "3-5 jours"},
            {"title": "Biométrie et examen médical", "description": "Compléter la biométrie et l'examen médical si requis", "documents": ["Reçu de biométrie", "Résultats d'examen médical (IMM 1017)"], "duration": "2-4 semaines"},
            {"title": "Traitement de la demande", "description": "IRCC traite le permis d'études", "documents": ["Documents additionnels si demandés"], "duration": "4-12 semaines"},
            {"title": "Décision sur le permis d'études", "description": "Recevoir l'approbation ou le refus", "documents": ["Lettre de point d'entrée", "Visa (si requis)"], "duration": "1-2 jours"},
            {"title": "Voyage au Canada", "description": "Entrer au Canada et recevoir le permis d'études", "documents": ["Passeport valide", "Lettre POE", "Lettre d'acceptation"], "duration": "À l'arrivée"},
            {"title": "Réception du permis d'études", "description": "Permis d'études délivré au point d'entrée", "documents": ["Document de permis d'études"], "duration": "Immédiat"}
        ],
        "Résidence permanente (Entrée express)": [
            {"title": "Évaluation de l'admissibilité", "description": "Déterminer l'admissibilité au programme Entrée express", "documents": ["Résultats de tests linguistiques", "Diplômes et attestations", "Preuve d'expérience professionnelle"], "duration": "1-2 semaines"},
            {"title": "Création du profil Entrée express", "description": "Créer le profil Entrée express et entrer dans le bassin", "documents": ["Rapport d'ÉDE", "Résultats de tests linguistiques", "Preuve de fonds"], "duration": "3-5 jours"},
            {"title": "Invitation à présenter une demande (IPD)", "description": "Recevoir une IPD si le score CRS est suffisant", "documents": ["Notification d'IPD"], "duration": "Variable (tirages aux 2 semaines)"},
            {"title": "Préparation des documents", "description": "Rassembler tous les documents justificatifs", "documents": ["Certificats de police", "Examens médicaux", "Actes de naissance", "Lettres de référence"], "duration": "3-6 semaines"},
            {"title": "Soumission de la demande de RP", "description": "Soumettre la demande complète de RP dans les 60 jours", "documents": ["Tous les formulaires et documents justificatifs", "Paiement des frais (1 365 $ CAD)"], "duration": "Dans les 60 jours de l'IPD"},
            {"title": "Biométrie", "description": "Fournir les données biométriques au CAV", "documents": ["Lettre d'instructions pour la biométrie"], "duration": "1-2 semaines"},
            {"title": "Traitement de la demande", "description": "IRCC traite la demande de RP", "documents": ["Documents additionnels si demandés"], "duration": "6 mois (traitement standard)"},
            {"title": "Confirmation de résidence permanente (CRP)", "description": "Recevoir la CRP et le visa de RP", "documents": ["Document de CRP", "Visa de RP dans le passeport"], "duration": "1-2 semaines après approbation"},
            {"title": "Établissement au Canada", "description": "Compléter les formalités d'établissement au point d'entrée", "documents": ["CRP", "Passeport valide"], "duration": "À l'arrivée"},
            {"title": "Demande de carte de RP", "description": "Recevoir la carte de RP par courrier", "documents": ["Carte de RP", "Confirmation d'adresse canadienne"], "duration": "4-6 semaines"}
        ]
    },
    "France": {
        "Permis de travail (Passeport Talent)": [
            {"title": "Consultation initiale", "description": "Évaluer l'admissibilité au Passeport Talent français", "documents": ["Passeport valide", "CV détaillé", "Qualifications académiques"], "duration": "2-3 jours"},
            {"title": "Contrat de travail", "description": "Obtenir une offre d'emploi d'un employeur français", "documents": ["Contrat de travail", "Description du poste", "Détails du salaire (minimum 53 836 €/an)"], "duration": "Variable"},
            {"title": "Autorisation de travail (si requise)", "description": "L'employeur obtient l'autorisation de travail", "documents": ["Approbation DIRECCTE", "Preuve de publication d'offre (3 semaines)"], "duration": "2-4 semaines"},
            {"title": "Préparation des documents", "description": "Rassembler les documents pour la demande de visa", "documents": ["Passeport (valide 3+ mois)", "Photos (3,5 x 4,5 cm)", "Justificatif d'hébergement en France", "Assurance santé", "Justificatif de ressources financières"], "duration": "1-2 semaines"},
            {"title": "Demande France-Visas", "description": "Compléter la demande en ligne sur France-Visas", "documents": ["Formulaire de demande en ligne", "Téléversement des documents justificatifs"], "duration": "1-2 jours"},
            {"title": "Rendez-vous consulaire", "description": "Assister à l'entretien visa et à la biométrie", "documents": ["Confirmation de rendez-vous", "Documents originaux", "Frais de visa (99 €)"], "duration": "1-3 semaines d'attente"},
            {"title": "Délivrance du visa VLS-TS", "description": "Recevoir le visa de long séjour", "documents": ["Passeport avec visa", "Formulaire OFII"], "duration": "2-8 semaines"},
            {"title": "Entrée en France", "description": "Entrer en France dans la validité du visa", "documents": ["Passeport valide avec visa", "Documents justificatifs"], "duration": "Dans les 3 mois de délivrance du visa"},
            {"title": "Validation OFII", "description": "Valider le visa en ligne dans les 3 mois", "documents": ["Validation OFII (200-250 €)", "Rendez-vous examen médical", "Session d'intégration civique"], "duration": "2-4 semaines"},
            {"title": "Carte de séjour (Titre de séjour)", "description": "Recevoir le titre de séjour pluriannuel", "documents": ["Carte Passeport Talent (valide jusqu'à 4 ans)", "Tampon OFII"], "duration": "Après validation OFII"}
        ],
        "Visa étudiant": [
            {"title": "Consultation initiale", "description": "Évaluer les plans d'études et l'admissibilité au programme", "documents": ["Passeport valide", "Relevés de notes académiques"], "duration": "1-2 jours"},
            {"title": "Acceptation universitaire", "description": "Obtenir l'acceptation d'un établissement français", "documents": ["Lettre d'acceptation/inscription", "Preuve de paiement des frais d'inscription"], "duration": "Variable selon l'établissement"},
            {"title": "Inscription Campus France", "description": "Compléter la procédure Campus France (si requise)", "documents": ["Entretien Campus France", "Documents académiques", "Preuve de compétence linguistique"], "duration": "2-6 semaines"},
            {"title": "Justificatif financier", "description": "Démontrer les ressources financières suffisantes", "documents": ["Relevés bancaires (615 €/mois)", "Lettre de bourse", "Attestation de prise en charge"], "duration": "1-2 semaines"},
            {"title": "Justificatif de logement", "description": "Sécuriser un hébergement en France", "documents": ["Contrat de bail", "Confirmation de logement universitaire", "Attestation d'hébergement"], "duration": "1-3 semaines"},
            {"title": "Demande VLS-TS", "description": "Demander le visa de long séjour étudiant", "documents": ["Formulaire France-Visas", "Lettre d'acceptation", "Justificatif de ressources", "Assurance santé"], "duration": "1-2 jours"},
            {"title": "Rendez-vous consulaire", "description": "Assister à l'entretien visa", "documents": ["Tous les documents originaux", "Frais de visa (50 € pour étudiants)", "Biométrie"], "duration": "2-4 semaines d'attente"},
            {"title": "Délivrance du visa étudiant", "description": "Recevoir le VLS-TS étudiant", "documents": ["Passeport avec visa"], "duration": "2-4 semaines"},
            {"title": "Arrivée et validation OFII", "description": "Entrer en France et valider le visa en ligne", "documents": ["Frais de validation OFII (60 €)", "Examen médical (si requis)"], "duration": "Dans les 3 mois de l'arrivée"},
            {"title": "Titre de séjour étudiant", "description": "Recevoir le titre de séjour étudiant", "documents": ["Carte de séjour étudiant"], "duration": "Après validation OFII"}
        ],
        "Regroupement familial": [
            {"title": "Vérification de l'admissibilité", "description": "Vérifier l'admissibilité du répondant et son statut de résident", "documents": ["Titre de séjour du répondant", "Preuve de durée de résidence (18+ mois)", "Preuve de lien familial"], "duration": "1-2 jours"},
            {"title": "Conditions de ressources", "description": "Démontrer des revenus suffisants", "documents": ["Avis d'imposition", "Bulletins de salaire (revenus stables)", "Justificatif de revenus au-dessus du seuil minimum"], "duration": "1-2 semaines"},
            {"title": "Justificatif de logement", "description": "Prouver un logement adéquat", "documents": ["Bail ou titre de propriété", "Factures de services publics", "Attestation de logement du maire"], "duration": "1-2 semaines"},
            {"title": "Dépôt de la demande OFII", "description": "Soumettre la demande de regroupement familial à l'OFII", "documents": ["Formulaire CERFA 11436*05", "Tous les documents justificatifs", "Frais de demande (225 €)"], "duration": "1 jour"},
            {"title": "Examen OFII", "description": "L'OFII examine la demande et effectue une visite à domicile", "documents": ["Rapport de visite à domicile", "Documents additionnels si demandés"], "duration": "6-12 mois"},
            {"title": "Décision de la préfecture", "description": "La préfecture émet une décision sur la demande", "documents": ["Notification d'approbation ou de refus"], "duration": "Après approbation OFII"},
            {"title": "Demande de visa (si approuvée)", "description": "Les membres de la famille demandent le visa", "documents": ["Certificat d'approbation", "Passeport", "Documents d'état civil"], "duration": "2-4 semaines"},
            {"title": "Entrée en France", "description": "Les membres de la famille entrent en France avec le visa", "documents": ["Visa valide", "Documents justificatifs"], "duration": "Dans la validité du visa"},
            {"title": "Demande de titre de séjour", "description": "Demander le titre de séjour à la préfecture", "documents": ["Tous les documents de visa", "Photos", "Validation OFII"], "duration": "2-3 mois"},
            {"title": "Délivrance du titre de séjour familial", "description": "Recevoir le titre 'Vie Privée et Familiale'", "documents": ["Titre de séjour (valide 1 an, renouvelable)"], "duration": "Après approbation de la préfecture"}
        ]
    }
}

# V3 New Models
class WithdrawalCreate(BaseModel):
    amount: float = Field(gt=0, description="Montant du retrait")
    category: ExpenseCategory
    subcategory: str
    description: str
    receipt_url: Optional[str] = None

class WithdrawalResponse(BaseModel):
    model_config = ConfigDict(extra="ignore")
    id: str
    manager_id: str
    manager_name: str
    amount: float
    category: ExpenseCategory
    subcategory: str
    description: str
    receipt_url: Optional[str]
    withdrawal_date: str
    created_at: str

class ContactMessageCreate(BaseModel):
    name: str = Field(min_length=2, max_length=100)
    email: EmailStr
    phone: Optional[str] = Field(None, max_length=20)
    country: str
    visa_type: Optional[str] = None
    budget_range: Optional[str] = None
    urgency_level: UrgencyLevel = UrgencyLevel.NORMAL
    message: str = Field(min_length=10, max_length=1000)
    lead_source: LeadSource = LeadSource.WEBSITE
    how_did_you_know: str = Field(min_length=1, max_length=100)
    referred_by_employee: Optional[str] = Field(None, max_length=100)

class ContactMessageResponse(BaseModel):
    model_config = ConfigDict(extra="ignore")
    id: str
    name: str
    email: str
    phone: Optional[str]
    country: str
    visa_type: Optional[str]
    budget_range: Optional[str]
    urgency_level: str
    message: str
    status: str
    assigned_to: Optional[str] = None
    assigned_to_name: Optional[str] = None
    lead_source: str
    conversion_probability: int
    notes: str
    how_did_you_know: Optional[str] = None  # Optionnel pour rétrocompatibilité
    referred_by_employee: Optional[str] = None
    payment_50k_amount: Optional[float] = None
    payment_50k_date: Optional[str] = None
    consultant_notes: Optional[List[Dict[str, Any]]] = []
    created_at: str
    updated_at: str

class ActivityLogResponse(BaseModel):
    model_config = ConfigDict(extra="ignore")
    id: str
    user_id: str
    user_name: str
    action: str
    resource_type: str
    resource_id: Optional[str]
    details: Optional[Dict[str, Any]]
    timestamp: str

class BalanceResponse(BaseModel):
    current_balance: float
    total_payments: float
    total_withdrawals: float
    last_updated: str
    
class ExpenseCategoryInfo(BaseModel):
    name: str
    subcategories: List[str]
    icon: str
    color: str

class ServiceInfo(BaseModel):
    name: str
    description: str
    duration: str
    success_rate: int
    price_from: int

class TeamMember(BaseModel):
    name: str
    role: str
    specialization: str
    experience: str
    languages: List[str]

class CompanyInfo(BaseModel):
    name: str
    tagline: str
    description: str
    contact: Dict[str, Any]
    business_hours: Dict[str, str]
    services: List[ServiceInfo]
    social_media: Dict[str, str]
    certifications: List[str]
    statistics: Dict[str, Any]
    team: List[TeamMember]

class PaymentConfirmRequest(BaseModel):
    action: str  # "CONFIRMED" or "REJECTED"
    rejection_reason: Optional[str] = None
    confirmation_code: Optional[str] = None

# V3 Configuration Data
EXPENSE_CATEGORIES_CONFIG = {
    "SALAIRES": {
        "name": "Salaires & Charges",
        "subcategories": ["Salaires", "Charges sociales", "Primes", "Formation", "Mutuelle"],
        "icon": "💼",
        "color": "#3B82F6"
    },
    "BUREAUX": {
        "name": "Locaux & Bureaux", 
        "subcategories": ["Loyer", "Charges locatives", "Électricité", "Internet", "Téléphone", "Assurance"],
        "icon": "🏢",
        "color": "#8B5CF6"
    },
    "JURIDIQUE": {
        "name": "Juridique & Administration",
        "subcategories": ["Frais avocat", "Traductions", "Légalisations", "Frais consulaires", "Notaire"],
        "icon": "⚖️", 
        "color": "#EF4444"
    },
    "DOSSIERS": {
        "name": "Traitement Dossiers",
        "subcategories": ["Frais préfecture", "Timbres fiscaux", "Courriers recommandés", "Déplacements clients"],
        "icon": "📋",
        "color": "#F59E0B"
    },
    "MARKETING": {
        "name": "Marketing & Communication",
        "subcategories": ["Publicité en ligne", "Site web", "Réseaux sociaux", "Événements", "Print"],
        "icon": "📈",
        "color": "#10B981"
    },
    "TECH": {
        "name": "Outils & Logiciels",
        "subcategories": ["Logiciels", "Matériel informatique", "Maintenance", "Sauvegardes", "Licences"],
        "icon": "💻", 
        "color": "#F97316"
    },
    "TRANSPORT": {
        "name": "Transport & Déplacements",
        "subcategories": ["Carburant", "Transports clients", "Missions", "Parking", "Location véhicule"],
        "icon": "🚗",
        "color": "#06B6D4"
    },
    "FORMATION": {
        "name": "Formation & Veille Juridique", 
        "subcategories": ["Formations équipe", "Abonnements juridiques", "Conférences", "Certifications"],
        "icon": "📚",
        "color": "#84CC16"
    }
}

# Données entreprise réalistes
COMPANY_DATA = {
    "name": "ALORIA AGENCY",
    "tagline": "Votre Partenaire Immigration de Confiance",
    "description": "Spécialistes en immigration France-Canada depuis 2020. Nous accompagnons particuliers et entreprises dans toutes leurs démarches d'immigration avec un taux de réussite de 95%.",
    "contact": {
        "phone": "+33 1 75 43 89 12",
        "email": "contact@aloria-agency.com", 
        "whatsapp": "+33 6 78 92 45 31",
        "address": "45 Avenue Victor Hugo",
        "postal_code": "75016",
        "city": "Paris",
        "country": "France",
        "metro": "Métro Victor Hugo (Ligne 2)",
        "parking": "Parking disponible à proximité"
    },
    "business_hours": {
        "monday": "09:00-18:00",
        "tuesday": "09:00-18:00", 
        "wednesday": "09:00-18:00",
        "thursday": "09:00-18:00",
        "friday": "09:00-17:00",
        "saturday": "10:00-14:00",
        "sunday": "Fermé"
    },
    "services": [
        {
            "name": "Visa Étudiant France",
            "description": "Accompagnement complet pour obtenir votre visa étudiant français",
            "duration": "2-4 semaines",
            "success_rate": 98,
            "price_from": 890
        },
        {
            "name": "Permis de Travail Canada", 
            "description": "Expertise LMIA et permis de travail fermé/ouvert",
            "duration": "3-6 mois",
            "success_rate": 94,
            "price_from": 1590
        },
        {
            "name": "Regroupement Familial",
            "description": "Réunissez votre famille en France ou au Canada",
            "duration": "4-8 mois",
            "success_rate": 96,
            "price_from": 1290
        },
        {
            "name": "Naturalisation française",
            "description": "Obtenez la nationalité française par naturalisation",
            "duration": "12-18 mois",
            "success_rate": 92,
            "price_from": 2190
        },
        {
            "name": "Visa Investisseur",
            "description": "Visa entrepreneur et investisseur France/Canada",
            "duration": "6-12 mois", 
            "success_rate": 89,
            "price_from": 2890
        }
    ],
    "social_media": {
        "linkedin": "https://linkedin.com/company/aloria-agency",
        "facebook": "https://facebook.com/aloria.agency.officiel",
        "instagram": "https://instagram.com/aloria_agency",
        "youtube": "https://youtube.com/@aloria-agency"
    },
    "certifications": [
        "Membre du Conseil National des Barreaux (France)",
        "ICCRC Certified Immigration Consultant (Canada)",
        "Certification ISO 9001:2015 Qualité",
        "Agrément Préfecture de Paris"
    ],
    "statistics": {
        "years_experience": 5,
        "successful_cases": 1247,
        "countries_served": 28,
        "success_rate": 95,
        "average_processing_time": "45 jours",
        "client_satisfaction": 4.9
    },
    "team": [
        {
            "name": "Sophie Dubois",
            "role": "Directrice & Avocate",
            "specialization": "Droit des étrangers France",
            "experience": "12 ans",
            "languages": ["Français", "Anglais", "Espagnol"]
        },
        {
            "name": "Jean-Marc Tremblay", 
            "role": "Consultant Immigration Canada",
            "specialization": "Immigration Canada & Québec",
            "experience": "8 ans",
            "languages": ["Français", "Anglais"]
        }
    ]
}

# Helper Functions V3
def generate_confirmation_code() -> str:
    """Génère un code de confirmation aléatoire de 4 caractères"""
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=4))

def calculate_lead_score(message_data: dict) -> int:
    """Calcule le score de lead basé sur différents critères"""
    score = 50  # Score de base
    
    # Budget élevé = +30 points
    if message_data.get('budget_range') == "5000+€":
        score += 30
    elif message_data.get('budget_range') == "3000-5000€":
        score += 20
    elif message_data.get('budget_range') == "1000-3000€":
        score += 10
    
    # Urgence = +20 points  
    if message_data.get('urgency_level') == "Urgent":
        score += 20
    elif message_data.get('urgency_level') == "Normal":
        score += 10
    
    # Pays facilité = +15 points
    easy_countries = ["France", "Canada", "Belgique", "Suisse"]
    if message_data.get('country') in easy_countries:
        score += 15
    
    # Message détaillé = +10 points
    if len(message_data.get('message', '')) > 200:
        score += 10
    
    # Informations complètes = +5 points
    if message_data.get('phone') and message_data.get('visa_type'):
        score += 5
        
    return min(score, 100)  # Max 100

async def generate_invoice_pdf(payment_data: dict) -> bytes:
    """Génère une facture PDF basique"""
    buffer = io.BytesIO()
    
    # Créer le PDF avec reportlab
    c = canvas.Canvas(buffer, pagesize=letter)
    width, height = letter
    
    # En-tête
    c.setFont("Helvetica-Bold", 20)
    c.drawString(50, height - 50, "ALORIA AGENCY")
    c.setFont("Helvetica", 10)
    c.drawString(50, height - 70, "45 Avenue Victor Hugo, 75016 Paris")
    c.drawString(50, height - 85, "Tél: +33 1 75 43 89 12 | Email: contact@aloria-agency.com")
    
    # Titre facture
    c.setFont("Helvetica-Bold", 16)
    c.drawString(50, height - 130, f"FACTURE N° {payment_data['invoice_number']}")
    
    # Informations client
    c.setFont("Helvetica", 12)
    c.drawString(50, height - 170, f"Client: {payment_data['client_name']}")
    c.drawString(50, height - 190, f"Date: {payment_data['created_at'][:10]}")
    
    # Détails paiement
    c.drawString(50, height - 230, "DESCRIPTION DES SERVICES:")
    c.drawString(50, height - 250, payment_data.get('description', 'Services d\'immigration'))
    
    # Montant
    c.setFont("Helvetica-Bold", 14)
    c.drawString(50, height - 300, f"MONTANT: {payment_data['amount']} {payment_data['currency']}")
    
    # Méthode de paiement
    c.setFont("Helvetica", 12)
    c.drawString(50, height - 330, f"Méthode de paiement: {payment_data['payment_method']}")
    
    # Pied de page
    c.drawString(50, 50, "Merci de votre confiance - ALORIA AGENCY")
    
    c.save()
    buffer.seek(0)
    return buffer.getvalue()

# Authentication Endpoints
@api_router.post("/auth/register", response_model=TokenResponse)
async def register(user_data: UserCreate):
    # Check if user exists
    existing_user = await db.users.find_one({"email": user_data.email})
    if existing_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    # Create user
    user_id = str(uuid.uuid4())
    user_dict = {
        "id": user_id,
        "email": user_data.email,
        "password": hash_password(user_data.password),
        "full_name": user_data.full_name,
        "phone": user_data.phone,
        "role": user_data.role,
        "is_active": True,
        "created_at": datetime.now(timezone.utc).isoformat()
    }
    
    await db.users.insert_one(user_dict)
    
    # Create token
    access_token = create_access_token({"sub": user_id, "role": user_data.role})
    
    user_response = UserResponse(
        id=user_id,
        email=user_data.email,
        full_name=user_data.full_name,
        phone=user_data.phone,
        role=user_data.role,
        is_active=True,
        created_at=user_dict["created_at"]
    )
    
    return TokenResponse(access_token=access_token, token_type="bearer", user=user_response)

@api_router.post("/auth/login", response_model=LoginResponse)
async def login(user_credentials: UserLogin):
    user = await db.users.find_one({"email": user_credentials.email})
    
    if not user or not verify_password(user_credentials.password, user["password"]):
        raise HTTPException(status_code=401, detail="Email ou mot de passe incorrect")
    
    if not user.get("is_active", True):
        raise HTTPException(status_code=401, detail="Compte désactivé")
    
    access_token = create_access_token(data={"sub": user["id"], "role": user["role"]})
    
    # Log de connexion
    await log_user_activity(
        user_id=user["id"],
        action="login",
        details={"login_time": datetime.now(timezone.utc).isoformat()}
    )
    
    return LoginResponse(
        access_token=access_token,
        token_type="bearer",
        user=UserResponse(**user)
    )

# API spéciale pour créer le premier SuperAdmin
@api_router.post("/auth/create-superadmin")
async def create_first_superadmin(
    superadmin_data: UserRegister,
    secret_key: str  # Clé secrète pour sécuriser cette API
):
    """Crée le premier SuperAdmin - API sécurisée"""
    
    # Vérifier la clé secrète (devrait être dans les variables d'environnement)
    expected_secret = os.environ.get("SUPERADMIN_CREATION_SECRET", "ALORIA_SUPER_SECRET_2024")
    if secret_key != expected_secret:
        raise HTTPException(status_code=403, detail="Clé secrète incorrecte")
    
    # Vérifier qu'il n'y a pas déjà de SuperAdmin
    existing_superadmin = await db.users.find_one({"role": "SUPERADMIN"})
    if existing_superadmin:
        raise HTTPException(status_code=400, detail="Un SuperAdmin existe déjà")
    
    # Vérifier que l'email n'existe pas
    existing_user = await db.users.find_one({"email": superadmin_data.email})
    if existing_user:
        raise HTTPException(status_code=400, detail="Un utilisateur avec cet email existe déjà")
    
    # Créer le SuperAdmin
    user_id = str(uuid.uuid4())
    hashed_password = hash_password(superadmin_data.password)
    
    superadmin_dict = {
        "id": user_id,
        "email": superadmin_data.email,
        "password": hashed_password,
        "full_name": superadmin_data.full_name,
        "phone": superadmin_data.phone,
        "role": "SUPERADMIN",
        "is_active": True,
        "created_at": datetime.now(timezone.utc).isoformat(),
        "created_by": "system",
        "password_changed": True  # SuperAdmin n'a pas besoin de changer son mot de passe
    }
    
    await db.users.insert_one(superadmin_dict)
    
    # Log la création
    await log_user_activity(
        user_id=user_id,
        action="superadmin_created",
        details={"created_by": "system", "initial_setup": True}
    )
    
    return {
        "message": "SuperAdmin créé avec succès",
        "user": {
            "id": user_id,
            "email": superadmin_data.email,
            "full_name": superadmin_data.full_name,
            "role": "SUPERADMIN"
        }
    }

@api_router.get("/auth/me", response_model=UserResponse)
async def get_me(current_user: dict = Depends(get_current_user)):
    return UserResponse(**current_user)

@api_router.patch("/auth/change-password")
async def change_password(password_data: PasswordChange, current_user: dict = Depends(get_current_user)):
    # Verify old password
    user = await db.users.find_one({"id": current_user["id"]})
    if not user or not verify_password(password_data.old_password, user["password"]):
        raise HTTPException(status_code=400, detail="Mot de passe actuel incorrect")
    
    # Update password
    new_hashed_password = hash_password(password_data.new_password)
    await db.users.update_one(
        {"id": current_user["id"]},
        {"$set": {"password": new_hashed_password}}
    )
    
    return {"message": "Mot de passe mis à jour avec succès"}

@api_router.get("/clients/{client_id}/credentials")
async def get_client_credentials(client_id: str, current_user: dict = Depends(get_current_user)):
    if current_user["role"] not in ["MANAGER", "EMPLOYEE"]:
        raise HTTPException(status_code=403, detail="Accès refusé")
    
    # Get client
    client = await db.clients.find_one({"id": client_id})
    if not client:
        raise HTTPException(status_code=404, detail="Client non trouvé")
    
    # Check permissions for employee
    if current_user["role"] == "EMPLOYEE" and client["assigned_employee_id"] != current_user["id"]:
        raise HTTPException(status_code=403, detail="Accès refusé - client non assigné")
    
    # Get user credentials
    user = await db.users.find_one({"id": client["user_id"]})
    if not user:
        raise HTTPException(status_code=404, detail="Utilisateur client non trouvé")
    
    return ClientCredentials(
        email=user["email"],
        password="Aloria2024!"  # Default password
    )

# Client Management
@api_router.post("/clients", response_model=ClientResponse) 
async def create_client(client_data: ClientCreate, current_user: dict = Depends(get_current_user)):
    # Vérifier les permissions avec la nouvelle hiérarchie
    if not can_create_role(current_user["role"], "CLIENT"):
        raise HTTPException(
            status_code=403, 
            detail="Vous n'avez pas l'autorisation de créer un client"
        )
        
    # Check if user exists with this email
    existing_user = await db.users.find_one({"email": client_data.email})
    
    if existing_user:
        # User exists, just create client record
        user_id = existing_user["id"]
    else:
        # Create new user account for client
        user_id = str(uuid.uuid4())
        user_dict = {
            "id": user_id,
            "email": client_data.email,
            "password": hash_password("Aloria2024!"),  # Temporary password - must be changed
            "full_name": client_data.full_name,
            "phone": client_data.phone,
            "role": "CLIENT",
            "is_active": True,
            "created_at": datetime.now(timezone.utc).isoformat()
        }
        await db.users.insert_one(user_dict)
    
    # Find employee with least clients for load balancing
    assigned_employee_id = None
    employees = await db.users.find({"role": "EMPLOYEE", "is_active": True}).to_list(100)
    if employees:
        # Count clients per employee
        employee_loads = []
        for emp in employees:
            count = await db.clients.count_documents({"assigned_employee_id": emp["id"]})
            employee_loads.append((emp["id"], count))
        assigned_employee_id = min(employee_loads, key=lambda x: x[1])[0]
    
    # Create client record
    client_id = str(uuid.uuid4())
    client_dict = {
        "id": client_id,
        "user_id": user_id,
        "assigned_employee_id": assigned_employee_id,
        "country": client_data.country,
        "visa_type": client_data.visa_type,
        "current_status": "Nouveau",
        "current_step": 0,
        "progress_percentage": 0.0,
        "created_at": datetime.now(timezone.utc).isoformat(),
        "updated_at": datetime.now(timezone.utc).isoformat()
    }
    await db.clients.insert_one(client_dict)
    
    # Create case with workflow
    workflow_steps = WORKFLOWS.get(client_data.country, {}).get(client_data.visa_type, [])
    case_id = str(uuid.uuid4())
    case_dict = {
        "id": case_id,
        "client_id": client_id,
        "country": client_data.country,
        "visa_type": client_data.visa_type,
        "workflow_steps": workflow_steps,
        "current_step_index": 0,
        "status": "Nouveau",
        "notes": client_data.message or "",
        "created_at": datetime.now(timezone.utc).isoformat(),
        "updated_at": datetime.now(timezone.utc).isoformat()
    }
    await db.cases.insert_one(case_dict)
    
    # Get assigned employee name
    assigned_employee_name = None
    if assigned_employee_id:
        employee = await db.users.find_one({"id": assigned_employee_id})
        if employee:
            assigned_employee_name = employee["full_name"]
    
    # Log activity to user_activities collection (for SuperAdmin monitoring)
    try:
        activity = {
            "id": str(uuid.uuid4()),
            "user_id": current_user["id"],
            "user_name": current_user["full_name"],
            "user_role": current_user["role"],
            "action": "client_created",
            "details": {
                "client_id": client_id,
                "client_name": client_data.full_name,
                "client_email": client_data.email,
                "country": client_data.country,
                "visa_type": client_data.visa_type
            },
            "ip_address": None,
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
        await db.user_activities.insert_one(activity)
    except Exception as e:
        logger.error(f"Erreur lors de l'enregistrement de l'activité client_created: {e}")

    return ClientResponse(
        id=client_id,
        user_id=user_id,
        assigned_employee_id=assigned_employee_id,
        assigned_employee_name=assigned_employee_name,
        country=client_data.country,
        visa_type=client_data.visa_type,
        current_status="Nouveau",
        current_step=0,
        progress_percentage=0.0,
        created_at=client_dict["created_at"],
        updated_at=client_dict["updated_at"],
        login_email=client_data.email,
        default_password="Aloria2024!" if not existing_user else None
    )

@api_router.get("/clients", response_model=List[ClientResponse])
async def get_clients(current_user: dict = Depends(get_current_user)):
    # Manager sees all clients, Employee sees only their clients
    query = {}
    if current_user["role"] == "EMPLOYEE":
        query["assigned_employee_id"] = current_user["id"]
    elif current_user["role"] == "CLIENT":
        query["user_id"] = current_user["id"]
    
    clients = await db.clients.find(query, {"_id": 0}).to_list(1000)
    
    # Enrich with employee names
    for client in clients:
        if client.get("assigned_employee_id"):
            employee = await db.users.find_one({"id": client["assigned_employee_id"]})
            client["assigned_employee_name"] = employee["full_name"] if employee else None
        else:
            client["assigned_employee_name"] = None
    
    return [ClientResponse(**client) for client in clients]

@api_router.get("/clients/{client_id}", response_model=ClientResponse)
async def get_client(client_id: str, current_user: dict = Depends(get_current_user)):
    client = await db.clients.find_one({"id": client_id}, {"_id": 0})
    if not client:
        raise HTTPException(status_code=404, detail="Client not found")
    
    # Check permissions
    if current_user["role"] == "EMPLOYEE" and client["assigned_employee_id"] != current_user["id"]:
        raise HTTPException(status_code=403, detail="Access denied")
    if current_user["role"] == "CLIENT" and client["user_id"] != current_user["id"]:
        raise HTTPException(status_code=403, detail="Access denied")
    
    # Get assigned employee name
    if client.get("assigned_employee_id"):
        employee = await db.users.find_one({"id": client["assigned_employee_id"]})
        client["assigned_employee_name"] = employee["full_name"] if employee else None
    else:
        client["assigned_employee_name"] = None
    
    return ClientResponse(**client)

# Case Management
@api_router.get("/cases", response_model=List[CaseResponse])
async def get_cases(current_user: dict = Depends(get_current_user)):
    # Get clients based on role
    if current_user["role"] == "MANAGER":
        clients = await db.clients.find({}, {"_id": 0}).to_list(1000)
    elif current_user["role"] == "EMPLOYEE":
        clients = await db.clients.find({"assigned_employee_id": current_user["id"]}, {"_id": 0}).to_list(1000)
    else:  # CLIENT
        clients = await db.clients.find({"user_id": current_user["id"]}, {"_id": 0}).to_list(1000)
    
    client_ids = [c["id"] for c in clients]
    cases = await db.cases.find({"client_id": {"$in": client_ids}}, {"_id": 0}).to_list(1000)
    
    # Enrich with client names
    client_map = {}
    for client in clients:
        user = await db.users.find_one({"id": client["user_id"]})
        if user:
            client_map[client["id"]] = user["full_name"]
    
    for case in cases:
        case["client_name"] = client_map.get(case["client_id"], "Unknown")
    
    return [CaseResponse(**case) for case in cases]

@api_router.get("/cases/{case_id}", response_model=CaseResponse)
async def get_case(case_id: str, current_user: dict = Depends(get_current_user)):
    case = await db.cases.find_one({"id": case_id}, {"_id": 0})
    if not case:
        raise HTTPException(status_code=404, detail="Case not found")
    
    # Check permissions
    client = await db.clients.find_one({"id": case["client_id"]})
    if not client:
        raise HTTPException(status_code=404, detail="Client not found")
    
    if current_user["role"] == "EMPLOYEE" and client["assigned_employee_id"] != current_user["id"]:
        raise HTTPException(status_code=403, detail="Access denied")
    if current_user["role"] == "CLIENT" and client["user_id"] != current_user["id"]:
        raise HTTPException(status_code=403, detail="Access denied")
    
    # Get client name
    user = await db.users.find_one({"id": client["user_id"]})
    case["client_name"] = user["full_name"] if user else "Unknown"
    
    return CaseResponse(**case)

@api_router.patch("/cases/{case_id}", response_model=CaseResponse)
async def update_case(case_id: str, update_data: CaseUpdate, current_user: dict = Depends(get_current_user)):
    # Only MANAGER can update cases - employees have read-only access
    if current_user["role"] != "MANAGER":
        raise HTTPException(status_code=403, detail="Seuls les gestionnaires peuvent modifier les dossiers")
        
    case = await db.cases.find_one({"id": case_id})
    if not case:
        raise HTTPException(status_code=404, detail="Dossier non trouvé")
    
    # Check if case exists
    client = await db.clients.find_one({"id": case["client_id"]})
    if not client:
        raise HTTPException(status_code=404, detail="Client non trouvé")
    
    # Get client user info for notifications
    user = await db.users.find_one({"id": client["user_id"]})
    client_name = user["full_name"] if user else "Unknown"
    
    # Manager can update everything
    update_dict = {k: v for k, v in update_data.model_dump().items() if v is not None}
    update_dict["updated_at"] = datetime.now(timezone.utc).isoformat()
    
    await db.cases.update_one({"id": case_id}, {"$set": update_dict})
    
    # Update client progress if step is updated
    if update_data.current_step_index is not None:
        total_steps = len(case["workflow_steps"])
        progress = (update_data.current_step_index / total_steps) * 100 if total_steps > 0 else 0
        await db.clients.update_one(
            {"id": case["client_id"]},
            {"$set": {
                "current_step": update_data.current_step_index,
                "progress_percentage": progress,
                "current_status": update_data.status if update_data.status else case["status"],
                "updated_at": datetime.now(timezone.utc).isoformat()
            }}
        )
        
        # Create notifications for case update
        
        # Notify client
        await create_notification(
            user_id=client["user_id"],
            title="Mise à jour de votre dossier",
            message=f"Votre dossier a été mis à jour par {current_user['full_name']}. Statut: {update_data.status or case['status']}",
            type="case_update",
            related_id=case_id
        )
        
        # Notify assigned employee if different from current user
        if client.get("assigned_employee_id") and client["assigned_employee_id"] != current_user["id"]:
            await create_notification(
                user_id=client["assigned_employee_id"],
                title="Dossier client mis à jour",
                message=f"Le dossier de {client_name} a été mis à jour par {current_user['full_name']}",
                type="case_update",
                related_id=case_id
            )
        
        # Send WebSocket updates
        client_sid = connected_users.get(client["user_id"])
        if client_sid:
            await sio.emit('case_updated', {
                'case_id': case_id,
                'client_name': client_name,
                'current_step': update_data.current_step_index,
                'progress': progress,
                'status': update_data.status or case["status"],
                'updated_by': current_user["full_name"]
            }, room=client_sid)
        
        # Notify assigned employee via WebSocket
        if client.get("assigned_employee_id"):
            employee_sid = connected_users.get(client["assigned_employee_id"])
            if employee_sid:
                await sio.emit('case_updated', {
                    'case_id': case_id,
                    'client_name': client_name,
                    'current_step': update_data.current_step_index,
                    'progress': progress,
                    'status': update_data.status or case["status"],
                    'updated_by': current_user["full_name"]
                }, room=employee_sid)
    
    # Get updated case
    updated_case = await db.cases.find_one({"id": case_id}, {"_id": 0})
    updated_case["client_name"] = client_name
    
    # Envoi automatique d'e-mail de mise à jour au client
    if EMAIL_SERVICE_AVAILABLE and updated_case:
        try:
            # Récupérer les données complètes du client
            client = await db.users.find_one({"id": updated_case["client_id"]})
            
            if client:
                client_data = {
                    "full_name": client.get("full_name", "Client"),
                    "email": client.get("email")
                }
                
                case_data = {
                    "id": case_id,
                    "current_step_name": updated_case.get("current_step_name", "En cours"),
                    "status": updated_case.get("status", "En cours"),
                    "country": updated_case.get("country", ""),
                    "visa_type": updated_case.get("visa_type", ""),
                    "progress_percentage": updated_case.get("progress_percentage", 0),
                    "manager_name": current_user["full_name"],
                    "notes": update_data.notes or ""
                }
                
                email_sent = await send_case_update_email(client_data, case_data)
                
                if email_sent:
                    logger.info(f"E-mail de mise à jour envoyé au client {client['email']}")
                    # Enregistrer l'envoi d'e-mail dans la base
                    await db.cases.update_one(
                        {"id": case_id},
                        {"$set": {"last_update_email_sent": True, "last_update_email_sent_at": datetime.now(timezone.utc).isoformat()}}
                    )
                else:
                    logger.warning(f"Échec envoi e-mail de mise à jour au client {client['email']}")
            
        except Exception as e:
            logger.error(f"Erreur envoi e-mail mise à jour dossier {case_id}: {e}")
    
    return CaseResponse(**updated_case)

# Messaging
@api_router.post("/messages", response_model=MessageResponse)
async def send_message(message_data: MessageCreate, current_user: dict = Depends(get_current_user)):
    message_id = str(uuid.uuid4())
    message_dict = {
        "id": message_id,
        "sender_id": current_user["id"],
        "receiver_id": message_data.receiver_id,
        "client_id": message_data.client_id,
        "message": message_data.message,
        "read_status": False,
        "created_at": datetime.now(timezone.utc).isoformat()
    }
    
    await db.messages.insert_one(message_dict)
    
    # Get sender and receiver names
    sender = await db.users.find_one({"id": current_user["id"]})
    receiver = await db.users.find_one({"id": message_data.receiver_id})
    
    return MessageResponse(
        id=message_id,
        sender_id=current_user["id"],
        sender_name=sender["full_name"] if sender else "Unknown",
        receiver_id=message_data.receiver_id,
        receiver_name=receiver["full_name"] if receiver else "Unknown",
        client_id=message_data.client_id,
        message=message_data.message,
        read_status=False,
        created_at=message_dict["created_at"]
    )

@api_router.get("/messages/client/{client_id}", response_model=List[MessageResponse])
async def get_messages(client_id: str, current_user: dict = Depends(get_current_user)):
    # Get messages for this client
    messages = await db.messages.find(
        {"client_id": client_id},
        {"_id": 0}
    ).sort("created_at", 1).to_list(1000)
    
    # Enrich with names
    user_cache = {}
    for msg in messages:
        for user_id_key in ["sender_id", "receiver_id"]:
            user_id = msg[user_id_key]
            if user_id not in user_cache:
                user = await db.users.find_one({"id": user_id})
                user_cache[user_id] = user["full_name"] if user else "Unknown"
        
        msg["sender_name"] = user_cache[msg["sender_id"]]
        msg["receiver_name"] = user_cache[msg["receiver_id"]]
    
    # Mark messages as read if current user is receiver
    await db.messages.update_many(
        {"client_id": client_id, "receiver_id": current_user["id"]},
        {"$set": {"read_status": True}}
    )
    
    return [MessageResponse(**msg) for msg in messages]

@api_router.get("/messages/unread", response_model=int)
async def get_unread_count(current_user: dict = Depends(get_current_user)):
    count = await db.messages.count_documents({
        "receiver_id": current_user["id"],
        "read_status": False
    })
    return count

# Chat API
@api_router.get("/chat/conversations", response_model=List[ChatConversation])
async def get_chat_conversations(current_user: dict = Depends(get_current_user)):
    # Get all conversations for current user
    messages = await db.chat_messages.find({
        "$or": [
            {"sender_id": current_user["id"]}, 
            {"receiver_id": current_user["id"]}
        ]
    }, {"_id": 0}).sort("timestamp", -1).to_list(1000)
    
    # Group by participant
    conversations = {}
    for msg in messages:
        other_user_id = msg["receiver_id"] if msg["sender_id"] == current_user["id"] else msg["sender_id"]
        other_user_name = msg["receiver_name"] if msg["sender_id"] == current_user["id"] else msg["sender_name"]  
        other_user_role = msg["receiver_role"] if msg["sender_id"] == current_user["id"] else msg["sender_role"]
        
        if other_user_id not in conversations:
            conversations[other_user_id] = {
                "participant_id": other_user_id,
                "participant_name": other_user_name,
                "participant_role": other_user_role,
                "last_message": msg["message"],
                "last_message_time": msg["timestamp"],
                "unread_count": 0
            }
            
        # Count unread messages from this participant
        if msg["receiver_id"] == current_user["id"] and not msg["read_status"]:
            conversations[other_user_id]["unread_count"] += 1
    
    return [ChatConversation(**conv) for conv in conversations.values()]

@api_router.get("/chat/messages/{participant_id}", response_model=List[ChatMessage])
async def get_chat_messages(participant_id: str, current_user: dict = Depends(get_current_user)):
    # Get messages between current user and participant
    messages = await db.chat_messages.find({
        "$or": [
            {"sender_id": current_user["id"], "receiver_id": participant_id},
            {"sender_id": participant_id, "receiver_id": current_user["id"]}
        ]
    }, {"_id": 0}).sort("timestamp", 1).to_list(1000)
    
    # Mark messages as read
    await db.chat_messages.update_many(
        {"sender_id": participant_id, "receiver_id": current_user["id"]},
        {"$set": {"read_status": True}}
    )
    
    return [ChatMessage(**msg) for msg in messages]

@api_router.post("/chat/send", response_model=ChatMessage)
async def send_chat_message(message_data: ChatMessageCreate, current_user: dict = Depends(get_current_user)):
    # Get receiver info
    receiver = await db.users.find_one({"id": message_data.receiver_id})
    if not receiver:
        raise HTTPException(status_code=404, detail="Receiver not found")
    
    # Vérifier les permissions de communication
    can_communicate = False
    
    if current_user["role"] == "MANAGER":
        # Manager peut communiquer avec tous les EMPLOYEES et CLIENTS
        can_communicate = receiver["role"] in ["EMPLOYEE", "CLIENT"]
        
    elif current_user["role"] == "EMPLOYEE":
        # Employee peut communiquer avec MANAGER et ses CLIENTS assignés
        if receiver["role"] == "MANAGER":
            can_communicate = True
        elif receiver["role"] == "CLIENT":
            # Vérifier si le client est assigné à cet employé
            client_record = await db.clients.find_one({"user_id": receiver["id"]})
            if client_record and client_record.get("assigned_employee_id") == current_user["id"]:
                can_communicate = True
                
    elif current_user["role"] == "CLIENT":
        # Client peut communiquer avec son EMPLOYEE assigné et les MANAGERS
        if receiver["role"] == "MANAGER":
            can_communicate = True
        elif receiver["role"] == "EMPLOYEE":
            # Vérifier si cet employé est assigné au client
            client_record = await db.clients.find_one({"user_id": current_user["id"]})
            if client_record and client_record.get("assigned_employee_id") == receiver["id"]:
                can_communicate = True
    
    if not can_communicate:
        raise HTTPException(status_code=403, detail="Vous n'êtes pas autorisé à communiquer avec cet utilisateur")
    
    # Create message
    message_id = str(uuid.uuid4())
    message_dict = {
        "id": message_id,
        "sender_id": current_user["id"],
        "sender_name": current_user["full_name"],
        "sender_role": current_user["role"],
        "receiver_id": message_data.receiver_id,
        "receiver_name": receiver["full_name"],
        "receiver_role": receiver["role"],
        "message": message_data.message,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "read_status": False
    }
    
    await db.chat_messages.insert_one(message_dict)
    
    # Create notification for message
    await create_notification(
        user_id=message_data.receiver_id,
        title=f"Nouveau message de {current_user['full_name']}",
        message=message_data.message[:100] + ("..." if len(message_data.message) > 100 else ""),
        type="message",
        related_id=message_id
    )
    
    # Send via WebSocket if receiver is online
    receiver_sid = connected_users.get(message_data.receiver_id)
    if receiver_sid:
        await sio.emit('new_message', {
            'id': message_id,
            'sender_id': current_user["id"],
            'sender_name': current_user["full_name"],
            'sender_role': current_user["role"],
            'message': message_data.message,
            'timestamp': message_dict["timestamp"]
        }, room=receiver_sid)
    
    return ChatMessage(**message_dict)

@api_router.get("/chat/unread-count")
async def get_unread_chat_count(current_user: dict = Depends(get_current_user)):
    count = await db.chat_messages.count_documents({
        "receiver_id": current_user["id"],
        "read_status": False
    })
    return {"unread_count": count}

# Visitors
@api_router.post("/visitors", response_model=VisitorResponse)
async def create_visitor(visitor_data: VisitorCreate, current_user: dict = Depends(get_current_user)):
    if current_user["role"] not in ["MANAGER", "EMPLOYEE"]:
        raise HTTPException(status_code=403, detail="Seuls les managers et employés peuvent enregistrer des visiteurs")
    
    visitor_id = str(uuid.uuid4())
    visitor_dict = {
        "id": visitor_id,
        "full_name": visitor_data.full_name,
        "phone_number": visitor_data.phone_number,
        "purpose": visitor_data.purpose.value,
        "other_purpose": visitor_data.other_purpose if visitor_data.purpose == VisitorPurpose.OTHER else None,
        "cni_number": visitor_data.cni_number,
        "arrival_time": datetime.now(timezone.utc).isoformat(),
        "departure_time": None,
        "registered_by": current_user["full_name"],  # Nom de l'employé/manager
        "registered_by_id": current_user["id"],
        "created_at": datetime.now(timezone.utc).isoformat()
    }
    
    await db.visitors.insert_one(visitor_dict)
    return VisitorResponse(**visitor_dict)

@api_router.get("/visitors", response_model=List[VisitorResponse])
async def get_visitors(current_user: dict = Depends(get_current_user)):
    if current_user["role"] not in ["MANAGER", "EMPLOYEE"]:
        raise HTTPException(status_code=403, detail="Access denied")
    
    visitors = await db.visitors.find({}, {"_id": 0}).sort("created_at", -1).to_list(1000)
    return [VisitorResponse(**v) for v in visitors]

@api_router.patch("/visitors/{visitor_id}/checkout")
async def checkout_visitor(visitor_id: str, current_user: dict = Depends(get_current_user)):
    if current_user["role"] not in ["MANAGER", "EMPLOYEE"]:
        raise HTTPException(status_code=403, detail="Access denied")
    
    await db.visitors.update_one(
        {"id": visitor_id},
        {"$set": {"departure_time": datetime.now(timezone.utc).isoformat()}}
    )
    return {"message": "Visitor checked out"}

# Dashboard Stats
@api_router.get("/dashboard/stats", response_model=DashboardStats)
async def get_dashboard_stats(current_user: dict = Depends(get_current_user)):
    if current_user["role"] != "MANAGER":
        raise HTTPException(status_code=403, detail="Only managers can view dashboard stats")
    
    # Get all cases
    cases = await db.cases.find({}, {"_id": 0}).to_list(10000)
    
    # Calculate stats
    total_cases = len(cases)
    cases_by_status = {}
    cases_by_country = {}
    
    active_cases = 0
    completed_cases = 0
    pending_cases = 0
    
    for case in cases:
        status = case["status"]
        country = case["country"]
        
        cases_by_status[status] = cases_by_status.get(status, 0) + 1
        cases_by_country[country] = cases_by_country.get(country, 0) + 1
        
        if status in ["In Progress", "Under Review"]:
            active_cases += 1
        elif status in ["Approved", "Completed"]:
            completed_cases += 1
        elif status in ["New", "Documents Pending"]:
            pending_cases += 1
    
    total_clients = await db.clients.count_documents({})
    total_employees = await db.users.count_documents({"role": "EMPLOYEE"})
    
    return DashboardStats(
        total_cases=total_cases,
        active_cases=active_cases,
        completed_cases=completed_cases,
        pending_cases=pending_cases,
        total_clients=total_clients,
        total_employees=total_employees,
        cases_by_country=cases_by_country,
        cases_by_status=cases_by_status
    )

# Employee Management
@api_router.get("/employees", response_model=List[UserResponse])
async def get_employees(current_user: dict = Depends(get_current_user)):
    if current_user["role"] != "MANAGER":
        raise HTTPException(status_code=403, detail="Only managers can view employees")
    
    employees = await db.users.find({"role": "EMPLOYEE"}, {"_id": 0}).to_list(1000)
    return [UserResponse(**emp) for emp in employees]

@api_router.patch("/employees/{employee_id}/toggle-status")
async def toggle_employee_status(employee_id: str, current_user: dict = Depends(get_current_user)):
    if current_user["role"] != "MANAGER":
        raise HTTPException(status_code=403, detail="Only managers can modify employees")
    
    employee = await db.users.find_one({"id": employee_id, "role": "EMPLOYEE"})
    if not employee:
        raise HTTPException(status_code=404, detail="Employee not found")
    
    new_status = not employee.get("is_active", True)
    await db.users.update_one({"id": employee_id}, {"$set": {"is_active": new_status}})
    
    return {"message": f"Employee {'activated' if new_status else 'deactivated'}"}

@api_router.patch("/clients/{client_id}/reassign")
async def reassign_client(client_id: str, new_employee_id: str, current_user: dict = Depends(get_current_user)):
    if current_user["role"] != "MANAGER":
        raise HTTPException(status_code=403, detail="Only managers can reassign clients")
    
    # Verify employee exists
    employee = await db.users.find_one({"id": new_employee_id, "role": "EMPLOYEE"})
    if not employee:
        raise HTTPException(status_code=404, detail="Employee not found")
    
    # Update client
    result = await db.clients.update_one(
        {"id": client_id},
        {"$set": {"assigned_employee_id": new_employee_id, "updated_at": datetime.now(timezone.utc).isoformat()}}
    )
    
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Client not found")
    
    return {"message": "Client reassigned successfully"}

# Workflows
@api_router.get("/workflows")
async def get_workflows():
    return WORKFLOWS

@api_router.post("/workflows/{country}/{visa_type}/steps")
async def add_custom_workflow_step(
    country: str, 
    visa_type: str, 
    step_data: CustomWorkflowStep, 
    current_user: dict = Depends(get_current_user)
):
    if current_user["role"] != "MANAGER":
        raise HTTPException(status_code=403, detail="Only managers can modify workflows")
    
    # Get or create custom workflow
    custom_workflow = await db.custom_workflows.find_one({
        "country": country,
        "visa_type": visa_type
    })
    
    if not custom_workflow:
        # Create from base workflow
        base_steps = WORKFLOWS.get(country, {}).get(visa_type, [])
        custom_workflow = {
            "id": str(uuid.uuid4()),
            "country": country,
            "visa_type": visa_type,
            "steps": base_steps.copy(),
            "created_by": current_user["id"],
            "created_at": datetime.now(timezone.utc).isoformat(),
            "updated_at": datetime.now(timezone.utc).isoformat()
        }
    
    # Add new step
    new_step = {
        "title": step_data.title,
        "description": step_data.description,
        "documents": step_data.documents,
        "duration": step_data.duration,
        "custom": True,
        "added_by": current_user["full_name"],
        "added_at": datetime.now(timezone.utc).isoformat()
    }
    
    custom_workflow["steps"].append(new_step)
    custom_workflow["updated_at"] = datetime.now(timezone.utc).isoformat()
    
    # Save or update
    await db.custom_workflows.replace_one(
        {"country": country, "visa_type": visa_type},
        custom_workflow,
        upsert=True
    )
    
    return {"message": "Étape ajoutée avec succès", "step": new_step}

@api_router.get("/workflows/{country}/{visa_type}/custom")
async def get_custom_workflow(country: str, visa_type: str, current_user: dict = Depends(get_current_user)):
    # Check for custom workflow
    custom_workflow = await db.custom_workflows.find_one({
        "country": country,
        "visa_type": visa_type
    }, {"_id": 0})
    
    if custom_workflow:
        return custom_workflow["steps"]
    else:
        # Return base workflow
        return WORKFLOWS.get(country, {}).get(visa_type, [])

@api_router.get("/users/available-contacts")
async def get_available_contacts(current_user: dict = Depends(get_current_user)):
    """Get list of users the current user can chat with"""
    contacts = []
    
    if current_user["role"] == "MANAGER":
        # Manager can chat with all employees and clients
        employees = await db.users.find({"role": "EMPLOYEE", "is_active": True}, {"_id": 0}).to_list(100)
        clients = await db.users.find({"role": "CLIENT", "is_active": True}, {"_id": 0}).to_list(1000)
        contacts.extend(employees)
        contacts.extend(clients)
        
    elif current_user["role"] == "EMPLOYEE":
        # Employee can chat with manager and assigned clients
        managers = await db.users.find({"role": "MANAGER", "is_active": True}, {"_id": 0}).to_list(10)
        contacts.extend(managers)
        
        # Get assigned clients
        assigned_clients = await db.clients.find({"assigned_employee_id": current_user["id"]}, {"_id": 0}).to_list(1000)
        for client in assigned_clients:
            user = await db.users.find_one({"id": client["user_id"], "is_active": True}, {"_id": 0})
            if user:
                contacts.append(user)
                
    elif current_user["role"] == "CLIENT":
        # Client can chat with assigned employee and managers
        client_record = await db.clients.find_one({"user_id": current_user["id"]})
        if client_record and client_record.get("assigned_employee_id"):
            employee = await db.users.find_one({"id": client_record["assigned_employee_id"], "is_active": True}, {"_id": 0})
            if employee:
                contacts.append(employee)
        
        managers = await db.users.find({"role": "MANAGER", "is_active": True}, {"_id": 0}).to_list(10)
        contacts.extend(managers)
    
    # Remove duplicates and current user
    unique_contacts = []
    seen_ids = set()
    for contact in contacts:
        if contact["id"] not in seen_ids and contact["id"] != current_user["id"]:
            unique_contacts.append({
                "id": contact["id"],
                "full_name": contact["full_name"],
                "role": contact["role"],
                "email": contact["email"]
            })
            seen_ids.add(contact["id"])
    
    return unique_contacts

# Gestion avancée des utilisateurs avec hiérarchie
@api_router.post("/users/create", response_model=UserCreateResponse)
async def create_user_advanced(user_data: UserCreateRequest, current_user: dict = Depends(get_current_user)):
    """Créer un utilisateur selon la hiérarchie des rôles"""
    
    # Vérifier les permissions
    if not can_create_role(current_user["role"], user_data.role.value):
        raise HTTPException(
            status_code=403, 
            detail=f"Vous n'avez pas l'autorisation de créer un utilisateur {user_data.role.value}"
        )
    
    # Vérifier si l'utilisateur existe déjà
    existing_user = await db.users.find_one({"email": user_data.email})
    if existing_user:
        raise HTTPException(status_code=400, detail="Un utilisateur avec cet email existe déjà")
    
    # Générer un mot de passe temporaire
    temp_password = generate_temporary_password()
    hashed_password = hash_password(temp_password)
    
    # Créer l'utilisateur
    user_id = str(uuid.uuid4())
    new_user = {
        "id": user_id,
        "email": user_data.email,
        "password": hashed_password,
        "full_name": user_data.full_name,
        "phone": user_data.phone,
        "role": user_data.role.value,
        "is_active": True,
        "created_at": datetime.now(timezone.utc).isoformat(),
        "created_by": current_user["id"],
        "password_changed": False  # Pour forcer le changement au premier login
    }
    
    await db.users.insert_one(new_user)
    
    # Enregistrer l'activité
    await log_user_activity(
        user_id=current_user["id"],
        action="create_user",
        details={
            "created_user_id": user_id,
            "created_user_role": user_data.role.value,
            "created_user_email": user_data.email
        }
    )
    
    # Envoi automatique d'e-mail de bienvenue
    email_sent = False
    if user_data.send_email and EMAIL_SERVICE_AVAILABLE:
        try:
            user_email_data = {
                "full_name": user_data.full_name,
                "email": user_data.email,
                "role": user_data.role.value,
                "login_email": user_data.email,
                "default_password": temp_password
            }
            
            email_sent = await send_user_welcome_email(user_email_data)
            
            if email_sent:
                logger.info(f"E-mail de bienvenue envoyé à {user_data.email} ({user_data.role.value})")
                # Enregistrer dans la base que l'e-mail a été envoyé
                await db.users.update_one(
                    {"id": user_id},
                    {"$set": {"welcome_email_sent": True, "welcome_email_sent_at": datetime.now(timezone.utc).isoformat()}}
                )
            else:
                logger.warning(f"Échec envoi e-mail de bienvenue à {user_data.email}")
                
        except Exception as e:
            logger.error(f"Erreur envoi e-mail utilisateur {user_data.email}: {e}")
            email_sent = False
    
    return UserCreateResponse(
        id=user_id,
        email=user_data.email,
        full_name=user_data.full_name,
        phone=user_data.phone,
        role=user_data.role.value,
        temporary_password=temp_password if not user_data.send_email else None,
        email_sent=email_sent
    )

# Fonction pour enregistrer l'activité utilisateur (monitoring SuperAdmin)
async def log_user_activity(user_id: str, action: str, details: dict = None, ip_address: str = None):
    """Enregistre l'activité utilisateur pour le monitoring"""
    try:
        # Handle special user IDs
        if user_id == "system":
            user_name = "System"
            user_role = "SYSTEM"
        elif user_id == "public":
            user_name = "Visiteur Public"
            user_role = "PUBLIC"
        else:
            user = await db.users.find_one({"id": user_id})
            if user:
                user_name = user["full_name"]
                user_role = user["role"]
            else:
                user_name = "Unknown User"
                user_role = "UNKNOWN"
        
        activity = {
            "id": str(uuid.uuid4()),
            "user_id": user_id,
            "user_name": user_name,
            "user_role": user_role,
            "action": action,
            "details": details or {},
            "ip_address": ip_address,
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
        await db.user_activities.insert_one(activity)
    except Exception as e:
        logger.error(f"Erreur lors de l'enregistrement de l'activité: {e}")

# Fonction d'envoi d'email (placeholder pour l'instant)
async def send_welcome_email(email: str, name: str, role: str, password: str, created_by: str):
    """Envoie un email de bienvenue avec les informations de connexion"""
    # TODO: Intégrer avec un service d'email réel (SendGrid, Mailgun, etc.)
    subject = "Bienvenue chez ALORIA AGENCY - Vos informations de connexion"
    
    body = f"""
    Bonjour {name},
    
    Vous avez été ajouté(e) à la plateforme ALORIA AGENCY par {created_by}.
    
    Voici vos informations de connexion :
    - Email : {email}
    - Mot de passe temporaire : {password}
    - Rôle : {role}
    
    Veuillez vous connecter et changer votre mot de passe dès votre première connexion.
    
    Lien de connexion : https://aloria-agency.com/login
    
    Cordialement,
    L'équipe ALORIA AGENCY
    """
    
    # Simulation d'envoi d'email (pour l'instant on log juste)
    logger.info(f"EMAIL ENVOYÉ À {email}: {subject}")
    logger.info(f"Contenu: {body}")
    
    # Dans une vraie implémentation, on utiliserait un service comme SendGrid:
    # await sendgrid_client.send_email(to=email, subject=subject, body=body)
    
    return True

# Système de gestion des paiements déclaratifs
@api_router.post("/payments/declare", response_model=PaymentDeclarationResponse)
async def declare_payment(payment_data: PaymentDeclaration, current_user: dict = Depends(get_current_user)):
    """Client déclare un paiement effectué"""
    if current_user["role"] != "CLIENT":
        raise HTTPException(status_code=403, detail="Seuls les clients peuvent déclarer des paiements")
    
    # Trouver le client
    client = await db.clients.find_one({"user_id": current_user["id"]})
    if not client:
        raise HTTPException(status_code=404, detail="Profil client non trouvé")
    
    # Créer la déclaration de paiement
    payment_id = str(uuid.uuid4())
    payment_dict = {
        "id": payment_id,
        "client_id": client["id"],
        "client_name": current_user["full_name"],
        "amount": payment_data.amount,
        "currency": payment_data.currency,
        "description": payment_data.description,
        "payment_method": payment_data.payment_method,
        "status": "pending",
        "declared_at": datetime.now(timezone.utc).isoformat(),
        "confirmed_at": None,
        "confirmed_by": None,
        "invoice_number": None
    }
    
    await db.payment_declarations.insert_one(payment_dict)
    
    # Notifier le manager
    managers = await db.users.find({"role": "MANAGER", "is_active": True}).to_list(100)
    for manager in managers:
        await create_notification(
            user_id=manager["id"],
            title=f"Nouveau paiement déclaré - {current_user['full_name']}",
            message=f"Montant: {payment_data.amount} {payment_data.currency} - Méthode: {payment_data.payment_method}",
            type="payment_declaration",
            related_id=payment_id
        )
        
        # WebSocket en temps réel
        manager_sid = connected_users.get(manager["id"])
        if manager_sid:
            await sio.emit('payment_declared', {
                'payment_id': payment_id,
                'client_name': current_user["full_name"],
                'amount': payment_data.amount,
                'currency': payment_data.currency,
                'payment_method': payment_data.payment_method
            }, room=manager_sid)
    
    # Notifier aussi tous les SuperAdmin des nouvelles déclarations
    superadmins = await db.users.find({"role": "SUPERADMIN", "is_active": True}).to_list(10)
    for superadmin in superadmins:
        await create_notification(
            user_id=superadmin["id"],
            title="💳 Nouvelle déclaration de paiement",
            message=f"Client: {current_user['full_name']} - Montant: {payment_data.amount} {payment_data.currency} (En attente de validation)",
            type="admin_payment_declared",
            related_id=payment_id
        )
    
    # Log activité
    await log_user_activity(
        user_id=current_user["id"],
        action="declare_payment",
        details={"payment_id": payment_id, "amount": payment_data.amount}
    )
    
    return PaymentDeclarationResponse(**payment_dict)

@api_router.get("/payments/pending", response_model=List[PaymentDeclarationResponse])
async def get_pending_payments(current_user: dict = Depends(get_current_user)):
    """Manager récupère les paiements en attente de confirmation"""
    if current_user["role"] not in ["MANAGER", "SUPERADMIN"]:
        raise HTTPException(status_code=403, detail="Accès refusé")
    
    payments = await db.payment_declarations.find(
        {"status": "pending"}, {"_id": 0}
    ).sort("declared_at", -1).to_list(100)
    
    return [PaymentDeclarationResponse(**payment) for payment in payments]

# OLD PAYMENT CONFIRMATION ENDPOINT REMOVED - DUPLICATE OF ENHANCED VERSION BELOW

# Fonction pour générer une facture PDF simple
async def generate_invoice_pdf(payment_id: str, invoice_number: str):
    """Génère une facture PDF complète pour le paiement confirmé"""
    try:
        payment = await db.payment_declarations.find_one({"id": payment_id})
        if not payment:
            return
            
        # Données de la facture
        invoice_data = {
            "invoice_number": invoice_number,
            "date": datetime.now().strftime("%d/%m/%Y"),
            "client_name": payment["client_name"],
            "amount": payment["amount"],
            "currency": payment["currency"],
            "description": payment["description"] or "Services d'immigration",
            "payment_method": payment["payment_method"],
            "created_at": payment.get("declared_at", datetime.now(timezone.utc).isoformat())
        }
        
        # Stocker les données de facture en base
        invoice_record = {
            "id": str(uuid.uuid4()),
            "payment_id": payment_id,
            "invoice_number": invoice_number,
            "data": invoice_data,
            "created_at": datetime.now(timezone.utc).isoformat()
        }
        
        await db.invoices.insert_one(invoice_record)
        
        # Générer le fichier PDF physique
        pdf_path = f"/app/backend/invoices/{invoice_number}.pdf"
        
        # Créer le PDF avec reportlab
        c = canvas.Canvas(pdf_path, pagesize=letter)
        width, height = letter
        
        # En-tête avec logo et informations entreprise
        c.setFont("Helvetica-Bold", 24)
        c.setFillColorRGB(0.96, 0.49, 0.13)  # Orange ALORIA
        c.drawString(50, height - 50, "ALORIA AGENCY")
        
        c.setFillColorRGB(0, 0, 0)  # Noir
        c.setFont("Helvetica", 10)
        c.drawString(50, height - 70, "Bureau de Douala, Cameroun")
        c.drawString(50, height - 85, "Tél: +237 6XX XX XX XX | Email: contact@aloria-agency.com")
        
        # Ligne de séparation
        c.setStrokeColorRGB(0.96, 0.49, 0.13)
        c.setLineWidth(2)
        c.line(50, height - 100, width - 50, height - 100)
        
        # Titre facture
        c.setFillColorRGB(0, 0, 0)
        c.setFont("Helvetica-Bold", 18)
        c.drawString(50, height - 140, f"FACTURE N° {invoice_number}")
        
        c.setFont("Helvetica", 11)
        c.drawString(50, height - 165, f"Date d'émission: {invoice_data['date']}")
        
        # Informations client (encadré)
        c.setStrokeColorRGB(0.8, 0.8, 0.8)
        c.setLineWidth(1)
        c.rect(50, height - 250, width - 100, 60)
        
        c.setFont("Helvetica-Bold", 12)
        c.drawString(60, height - 210, "CLIENT:")
        c.setFont("Helvetica", 11)
        c.drawString(60, height - 230, invoice_data['client_name'])
        
        # Détails des services (encadré)
        c.rect(50, height - 380, width - 100, 100)
        c.setFont("Helvetica-Bold", 12)
        c.drawString(60, height - 310, "DESCRIPTION DES SERVICES:")
        c.setFont("Helvetica", 11)
        c.drawString(60, height - 335, invoice_data['description'])
        c.drawString(60, height - 355, f"Méthode de paiement: {invoice_data['payment_method']}")
        
        # Montant (encadré avec fond orange clair)
        c.setFillColorRGB(0.96, 0.49, 0.13, alpha=0.1)
        c.rect(50, height - 460, width - 100, 50, fill=1)
        
        c.setFillColorRGB(0, 0, 0)
        c.setFont("Helvetica-Bold", 16)
        c.drawString(60, height - 435, f"MONTANT TOTAL: {invoice_data['amount']} {invoice_data['currency']}")
        
        # Pied de page
        c.setFont("Helvetica-Oblique", 10)
        c.setFillColorRGB(0.5, 0.5, 0.5)
        c.drawString(50, 80, "Cette facture atteste du paiement des services d'immigration.")
        c.drawString(50, 65, "Pour toute question, veuillez nous contacter à contact@aloria-agency.com")
        
        c.setFont("Helvetica-Bold", 11)
        c.setFillColorRGB(0.96, 0.49, 0.13)
        c.drawString(width/2 - 100, 40, "Merci de votre confiance - ALORIA AGENCY")
        
        c.save()
        logger.info(f"✅ Facture PDF {invoice_number} générée avec succès à {pdf_path}")
        
    except Exception as e:
        logger.error(f"❌ Erreur génération facture PDF: {e}", exc_info=True)

@api_router.get("/payments/client-history", response_model=List[PaymentDeclarationResponse])
async def get_client_payment_history(current_user: dict = Depends(get_current_user)):
    """Client récupère son historique de paiements"""
    if current_user["role"] != "CLIENT":
        raise HTTPException(status_code=403, detail="Accès refusé")
    
    client = await db.clients.find_one({"user_id": current_user["id"]})
    if not client:
        raise HTTPException(status_code=404, detail="Profil client non trouvé")
    
    payments = await db.payment_declarations.find(
        {"client_id": client["id"]}, {"_id": 0}
    ).sort("declared_at", -1).to_list(100)
    
    return [PaymentDeclarationResponse(**payment) for payment in payments]

@api_router.get("/invoices/{invoice_number}")
async def download_invoice(invoice_number: str, current_user: dict = Depends(get_current_user)):
    """Télécharger une facture PDF"""
    # Vérifier que l'utilisateur a le droit de télécharger cette facture
    invoice = await db.invoices.find_one({"invoice_number": invoice_number})
    if not invoice:
        raise HTTPException(status_code=404, detail="Facture non trouvée")
    
    payment = await db.payment_declarations.find_one({"id": invoice["payment_id"]})
    if not payment:
        raise HTTPException(status_code=404, detail="Paiement associé non trouvé")
    
    # Vérifier les permissions
    if current_user["role"] == "CLIENT":
        client = await db.clients.find_one({"user_id": current_user["id"]})
        if not client or payment["client_id"] != client["id"]:
            raise HTTPException(status_code=403, detail="Accès refusé à cette facture")
    elif current_user["role"] not in ["MANAGER", "SUPERADMIN"]:
        raise HTTPException(status_code=403, detail="Accès refusé")
    
    pdf_path = f"/app/backend/invoices/{invoice_number}.pdf"
    
    # Vérifier que le fichier existe
    import os
    if not os.path.exists(pdf_path):
        raise HTTPException(status_code=404, detail="Fichier PDF non trouvé")
    
    return FileResponse(
        path=pdf_path,
        media_type="application/pdf",
        filename=f"{invoice_number}.pdf"
    )

@api_router.get("/payments/manager-history", response_model=List[PaymentDeclarationResponse])
async def get_manager_payment_history(current_user: dict = Depends(get_current_user)):
    """Manager récupère l'historique complet des paiements"""
    if current_user["role"] not in ["MANAGER", "SUPERADMIN"]:
        raise HTTPException(status_code=403, detail="Accès refusé")
    
    payments = await db.payment_declarations.find(
        {}, {"_id": 0}
    ).sort("declared_at", -1).to_list(1000)
    
    return [PaymentDeclarationResponse(**payment) for payment in payments]

# APIs SuperAdmin pour monitoring et gestion complète
@api_router.get("/admin/users", response_model=List[UserResponse])
async def get_all_users(current_user: dict = Depends(get_current_user)):
    """SuperAdmin récupère tous les utilisateurs"""
    if current_user["role"] != "SUPERADMIN":
        raise HTTPException(status_code=403, detail="Accès SuperAdmin requis")
    
    users = await db.users.find({}, {"_id": 0, "password": 0}).sort("created_at", -1).to_list(1000)
    return [UserResponse(**user) for user in users]

@api_router.get("/admin/activities", response_model=List[UserActivity])
async def get_user_activities(
    limit: int = 100, 
    user_id: str = None, 
    action: str = None,
    current_user: dict = Depends(get_current_user)
):
    """SuperAdmin récupère les activités utilisateur"""
    if current_user["role"] != "SUPERADMIN":
        raise HTTPException(status_code=403, detail="Accès SuperAdmin requis")
    
    filter_dict = {}
    if user_id:
        filter_dict["user_id"] = user_id
    if action:
        filter_dict["action"] = {"$regex": action, "$options": "i"}
    
    activities = await db.user_activities.find(
        filter_dict, {"_id": 0}
    ).sort("timestamp", -1).limit(limit).to_list(limit)
    
    return [UserActivity(**activity) for activity in activities]

@api_router.post("/admin/impersonate")
async def impersonate_user(request: ImpersonationRequest, current_user: dict = Depends(get_current_user)):
    """SuperAdmin peut se connecter en tant qu'autre utilisateur"""
    if current_user["role"] != "SUPERADMIN":
        raise HTTPException(status_code=403, detail="Accès SuperAdmin requis")
    
    # Vérifier que l'utilisateur cible existe
    target_user = await db.users.find_one({"id": request.target_user_id})
    if not target_user:
        raise HTTPException(status_code=404, detail="Utilisateur cible non trouvé")
    
    # Ne pas permettre l'impersonation d'un autre SuperAdmin
    if target_user["role"] == "SUPERADMIN" and target_user["id"] != current_user["id"]:
        raise HTTPException(status_code=403, detail="Impossible d'impersonner un autre SuperAdmin")
    
    # Générer un token d'impersonation
    impersonation_data = {
        "sub": target_user["id"],
        "role": target_user["role"],
        "impersonated_by": current_user["id"],
        "impersonation": True,
        "exp": datetime.now(timezone.utc) + timedelta(hours=1)  # Token valide 1h
    }
    
    impersonation_token = jwt.encode(impersonation_data, SECRET_KEY, algorithm=ALGORITHM)
    
    # Log l'impersonation
    await log_user_activity(
        user_id=current_user["id"],
        action="impersonate_user",
        details={
            "target_user_id": request.target_user_id,
            "target_user_name": target_user["full_name"],
            "target_user_role": target_user["role"]
        }
    )
    
    return {
        "impersonation_token": impersonation_token,
        "target_user": {
            "id": target_user["id"],
            "name": target_user["full_name"],
            "email": target_user["email"],
            "role": target_user["role"]
        },
        "expires_in": 3600  # 1 heure
    }

@api_router.get("/admin/dashboard-stats")
async def get_admin_dashboard_stats(current_user: dict = Depends(get_current_user)):
    """SuperAdmin récupère les statistiques globales"""
    if current_user["role"] != "SUPERADMIN":
        raise HTTPException(status_code=403, detail="Accès SuperAdmin requis")
    
    # Compter les utilisateurs par rôle
    total_users = await db.users.count_documents({"is_active": True})
    managers = await db.users.count_documents({"role": "MANAGER", "is_active": True})
    employees = await db.users.count_documents({"role": "EMPLOYEE", "is_active": True})
    clients = await db.users.count_documents({"role": "CLIENT", "is_active": True})
    
    # Compter les éléments métier
    total_cases = await db.cases.count_documents({})
    active_cases = await db.cases.count_documents({"status": {"$nin": ["Terminated", "Rejected"]}})
    total_payments = await db.payment_declarations.count_documents({})
    pending_payments = await db.payment_declarations.count_documents({"status": "pending"})
    
    # Paiements consultation (50k CFA)
    consultation_payments_list = await db.payments.find({"type": "consultation"}).to_list(1000)
    consultation_count = len(consultation_payments_list)
    consultation_total = sum(p.get("amount", 0) for p in consultation_payments_list)
    
    # Activités récentes
    recent_activities = await db.user_activities.find(
        {}, {"_id": 0}
    ).sort("timestamp", -1).limit(10).to_list(10)
    
    # Connexions aujourd'hui
    today = datetime.now(timezone.utc).date().isoformat()
    daily_logins = await db.user_activities.count_documents({
        "action": "login",
        "timestamp": {"$regex": f"^{today}"}
    })
    
    return {
        "users": {
            "total": total_users,
            "managers": managers,
            "employees": employees,
            "clients": clients
        },
        "business": {
            "total_cases": total_cases,
            "active_cases": active_cases,
            "total_payments": total_payments,
            "pending_payments": pending_payments
        },
        "consultations": {
            "total_count": consultation_count,
            "total_amount": consultation_total,
            "currency": "CFA"
        },
        "activity": {
            "daily_logins": daily_logins,
            "recent_activities": recent_activities
        }
    }

@api_router.patch("/admin/users/{user_id}")
async def admin_update_user(
    user_id: str, 
    updates: dict,
    current_user: dict = Depends(get_current_user)
):
    """SuperAdmin peut modifier n'importe quel utilisateur"""
    if current_user["role"] != "SUPERADMIN":
        raise HTTPException(status_code=403, detail="Accès SuperAdmin requis")
    
    # Vérifier que l'utilisateur existe
    target_user = await db.users.find_one({"id": user_id})
    if not target_user:
        raise HTTPException(status_code=404, detail="Utilisateur non trouvé")
    
    # Empêcher la modification d'autres SuperAdmins (sauf soi-même)
    if target_user["role"] == "SUPERADMIN" and target_user["id"] != current_user["id"]:
        raise HTTPException(status_code=403, detail="Impossible de modifier un autre SuperAdmin")
    
    # Valider et appliquer les modifications
    allowed_fields = ["full_name", "phone", "is_active", "role"]
    update_dict = {k: v for k, v in updates.items() if k in allowed_fields}
    
    if update_dict:
        update_dict["updated_at"] = datetime.now(timezone.utc).isoformat()
        await db.users.update_one({"id": user_id}, {"$set": update_dict})
        
        # Log l'action
        await log_user_activity(
            user_id=current_user["id"],
            action="admin_update_user",
            details={
                "target_user_id": user_id,
                "modifications": update_dict
            }
        )
    
    return {"message": "Utilisateur mis à jour avec succès", "modified_fields": list(update_dict.keys())}

@api_router.delete("/admin/users/{user_id}")
async def admin_delete_user(user_id: str, current_user: dict = Depends(get_current_user)):
    """SuperAdmin peut supprimer un utilisateur (soft delete)"""
    if current_user["role"] != "SUPERADMIN":
        raise HTTPException(status_code=403, detail="Accès SuperAdmin requis")
    
    # Vérifier que l'utilisateur existe
    target_user = await db.users.find_one({"id": user_id})
    if not target_user:
        raise HTTPException(status_code=404, detail="Utilisateur non trouvé")
    
    # Empêcher la suppression d'autres SuperAdmins
    if target_user["role"] == "SUPERADMIN":
        raise HTTPException(status_code=403, detail="Impossible de supprimer un SuperAdmin")
    
    # Soft delete
    await db.users.update_one(
        {"id": user_id}, 
        {"$set": {
            "is_active": False, 
            "deleted_at": datetime.now(timezone.utc).isoformat(),
            "deleted_by": current_user["id"]
        }}
    )
    
    # Log l'action
    await log_user_activity(
        user_id=current_user["id"],
        action="admin_delete_user",
        details={
            "target_user_id": user_id,
            "target_user_name": target_user["full_name"],
            "target_user_role": target_user["role"]
        }
    )
    
    return {"message": "Utilisateur supprimé avec succès"}

# APIs de recherche intelligente
@api_router.get("/search/global")
async def global_search(
    query: str,
    category: Optional[str] = None,  # "users", "clients", "cases", "visitors"
    limit: int = 20,
    current_user: dict = Depends(get_current_user)
):
    """Recherche intelligente globale dans toute l'application"""
    
    if len(query.strip()) < 2:
        return {"results": [], "total": 0}
    
    results = []
    
    # Construire le pattern de recherche (insensible à la casse)
    search_pattern = {"$regex": query, "$options": "i"}
    
    # Recherche dans les utilisateurs (si autorisé)
    if (category is None or category == "users") and current_user["role"] in ["MANAGER", "SUPERADMIN"]:
        users = await db.users.find({
            "$or": [
                {"full_name": search_pattern},
                {"email": search_pattern},
                {"phone": search_pattern}
            ],
            "is_active": True
        }, {"_id": 0, "password": 0}).limit(limit).to_list(limit)
        
        for user in users:
            results.append({
                "type": "user",
                "id": user["id"],
                "title": user["full_name"],
                "subtitle": f"{user['email']} - {user['role']}",
                "data": user
            })
    
    # Recherche dans les clients
    if (category is None or category == "clients") and current_user["role"] in ["MANAGER", "EMPLOYEE", "SUPERADMIN"]:
        # Pour les employés, limiter aux clients assignés
        client_filter = {}
        if current_user["role"] == "EMPLOYEE":
            client_filter["assigned_employee_id"] = current_user["id"]
        
        clients = await db.clients.find(client_filter, {"_id": 0}).to_list(1000)
        client_ids = [c["id"] for c in clients]
        
        # Rechercher dans les utilisateurs clients correspondants
        client_users = await db.users.find({
            "id": {"$in": [c["user_id"] for c in clients]},
            "$or": [
                {"full_name": search_pattern},
                {"email": search_pattern},
                {"phone": search_pattern}
            ]
        }, {"_id": 0, "password": 0}).limit(limit).to_list(limit)
        
        for client_user in client_users:
            client_data = next((c for c in clients if c["user_id"] == client_user["id"]), None)
            if client_data:
                results.append({
                    "type": "client",
                    "id": client_data["id"],
                    "title": client_user["full_name"],
                    "subtitle": f"{client_data['country']} - {client_data['visa_type']} - {client_data['current_status']}",
                    "data": {**client_user, **client_data}
                })
    
    # Recherche dans les dossiers/cas
    if (category is None or category == "cases") and current_user["role"] in ["MANAGER", "EMPLOYEE", "SUPERADMIN"]:
        case_filter = {}
        if current_user["role"] == "EMPLOYEE":
            # Limiter aux cas des clients assignés à cet employé
            employee_clients = await db.clients.find(
                {"assigned_employee_id": current_user["id"]}, {"_id": 0}
            ).to_list(1000)
            case_filter["client_id"] = {"$in": [c["id"] for c in employee_clients]}
        
        # Recherche par status, country, visa_type, notes
        case_filter["$or"] = [
            {"status": search_pattern},
            {"country": search_pattern},
            {"visa_type": search_pattern},
            {"notes": search_pattern}
        ]
        
        cases = await db.cases.find(case_filter, {"_id": 0}).sort("updated_at", -1).limit(limit).to_list(limit)
        
        for case in cases:
            # Récupérer le nom du client
            client = await db.clients.find_one({"id": case["client_id"]})
            client_name = "Client inconnu"
            if client:
                client_user = await db.users.find_one({"id": client["user_id"]})
                if client_user:
                    client_name = client_user["full_name"]
            
            results.append({
                "type": "case",
                "id": case["id"],
                "title": f"Dossier {client_name}",
                "subtitle": f"{case['country']} - {case['visa_type']} - {case['status']}",
                "data": {**case, "client_name": client_name}
            })
    
    # Recherche dans les visiteurs
    if (category is None or category == "visitors") and current_user["role"] in ["MANAGER", "EMPLOYEE", "SUPERADMIN"]:
        visitors = await db.visitors.find({
            "$or": [
                {"name": search_pattern},
                {"company": search_pattern},
                {"purpose": search_pattern}
            ]
        }, {"_id": 0}).sort("created_at", -1).limit(limit).to_list(limit)
        
        for visitor in visitors:
            results.append({
                "type": "visitor",
                "id": visitor["id"],
                "title": visitor["name"],
                "subtitle": f"{visitor.get('company', 'N/A')} - {visitor['purpose']} - {visitor['arrival_time'][:10]}",
                "data": visitor
            })
    
    # Trier les résultats par pertinence (nom exact en premier)
    def sort_key(item):
        title_lower = item["title"].lower()
        query_lower = query.lower()
        if title_lower == query_lower:
            return 0  # Correspondance exacte
        elif title_lower.startswith(query_lower):
            return 1  # Commence par la query
        else:
            return 2  # Contient la query
    
    results.sort(key=sort_key)
    
    return {
        "results": results[:limit],
        "total": len(results),
        "query": query
    }

# API étendue pour la gestion des visiteurs
@api_router.get("/visitors/list", response_model=List[VisitorResponse])
async def get_visitors_list(
    limit: int = 100,
    date_from: Optional[str] = None,
    date_to: Optional[str] = None,
    purpose: Optional[str] = None,
    current_user: dict = Depends(get_current_user)
):
    """Récupère la liste des visiteurs avec filtres"""
    if current_user["role"] not in ["MANAGER", "EMPLOYEE", "SUPERADMIN"]:
        raise HTTPException(status_code=403, detail="Accès refusé")
    
    # Construire le filtre
    filter_dict = {}
    
    if date_from:
        filter_dict["created_at"] = {"$gte": date_from}
    if date_to:
        if "created_at" in filter_dict:
            filter_dict["created_at"]["$lte"] = date_to
        else:
            filter_dict["created_at"] = {"$lte": date_to}
    
    if purpose:
        filter_dict["purpose"] = purpose
    
    # Récupérer les visiteurs
    visitors = await db.visitors.find(
        filter_dict, {"_id": 0}
    ).sort("created_at", -1).limit(limit).to_list(limit)
    
    return [VisitorResponse(**visitor) for visitor in visitors]

@api_router.get("/visitors/stats")
async def get_visitor_stats(current_user: dict = Depends(get_current_user)):
    """Statistiques des visiteurs"""
    if current_user["role"] not in ["MANAGER", "EMPLOYEE", "SUPERADMIN"]:
        raise HTTPException(status_code=403, detail="Accès refusé")
    
    # Visiteurs aujourd'hui
    today = datetime.now(timezone.utc).date().isoformat()
    today_visitors = await db.visitors.count_documents({
        "created_at": {"$regex": f"^{today}"}
    })
    
    # Visiteurs cette semaine
    week_ago = (datetime.now(timezone.utc) - timedelta(days=7)).isoformat()
    week_visitors = await db.visitors.count_documents({
        "created_at": {"$gte": week_ago}
    })
    
    # Visiteurs par motif
    purpose_stats = []
    purposes = ["Consultation initiale", "Remise de documents", "Mise à jour du dossier", 
               "Rendez-vous planifié", "Affaire urgente", "Demande d'informations", 
               "Paiement", "Autre"]
    
    for purpose in purposes:
        count = await db.visitors.count_documents({"purpose": purpose})
        if count > 0:
            purpose_stats.append({"purpose": purpose, "count": count})
    
    # Visiteurs actuellement présents (arrivés mais pas encore partis)
    present_visitors = await db.visitors.count_documents({
        "departure_time": None
    })
    
    return {
        "today": today_visitors,
        "week": week_visitors,
        "present": present_visitors,
        "by_purpose": purpose_stats
    }

# Notifications API
async def create_notification(user_id: str, title: str, message: str, type: str, related_id: str = None):
    """Helper function to create notifications"""
    notification_id = str(uuid.uuid4())
    notification_dict = {
        "id": notification_id,
        "user_id": user_id,
        "title": title,
        "message": message,
        "type": type,
        "related_id": related_id,
        "read": False,
        "created_at": datetime.now(timezone.utc).isoformat()
    }
    await db.notifications.insert_one(notification_dict)
    
    # Send real-time notification via WebSocket
    user_sid = connected_users.get(user_id)
    if user_sid:
        await sio.emit('new_notification', {
            'id': notification_id,
            'title': title,
            'message': message,
            'type': type,
            'created_at': notification_dict["created_at"]
        }, room=user_sid)
    
    return notification_id

@api_router.get("/notifications", response_model=List[NotificationResponse])
async def get_notifications(current_user: dict = Depends(get_current_user)):
    notifications = await db.notifications.find(
        {"user_id": current_user["id"]}, {"_id": 0}
    ).sort("created_at", -1).limit(50).to_list(50)
    
    return [NotificationResponse(**notif) for notif in notifications]

@api_router.patch("/notifications/{notification_id}/read")
async def mark_notification_read(notification_id: str, current_user: dict = Depends(get_current_user)):
    result = await db.notifications.update_one(
        {"id": notification_id, "user_id": current_user["id"]},
        {"$set": {"read": True}}
    )
    
    if result.modified_count == 0:
        raise HTTPException(status_code=404, detail="Notification non trouvée")
    
    return {"message": "Notification marquée comme lue"}

@api_router.get("/notifications/unread-count")
async def get_unread_notifications_count(current_user: dict = Depends(get_current_user)):
    count = await db.notifications.count_documents({
        "user_id": current_user["id"],
        "read": False
    })
    return {"unread_count": count}

# ==================== V3 NEW ENDPOINTS ====================

# Balance & Withdrawals Management
@api_router.get("/balance/current", response_model=BalanceResponse)
async def get_current_balance(current_user: dict = Depends(get_current_user)):
    """Obtenir le solde actuel de l'entreprise (SuperAdmin/Manager seulement)"""
    if current_user["role"] not in ["SUPERADMIN", "MANAGER"]:
        raise HTTPException(status_code=403, detail="Accès refusé")
    
    # Calculer le solde en temps réel
    # Total des paiements confirmés
    payments_pipeline = [
        {"$match": {"status": "CONFIRMED"}},
        {"$group": {"_id": None, "total": {"$sum": "$amount"}}}
    ]
    payments_result = await db.payment_declarations.aggregate(payments_pipeline).to_list(1)
    total_payments = payments_result[0]["total"] if payments_result else 0.0
    
    # Total des retraits
    withdrawals_pipeline = [
        {"$group": {"_id": None, "total": {"$sum": "$amount"}}}
    ]
    withdrawals_result = await db.withdrawals.aggregate(withdrawals_pipeline).to_list(1)
    total_withdrawals = withdrawals_result[0]["total"] if withdrawals_result else 0.0
    
    current_balance = total_payments - total_withdrawals
    
    # Mettre à jour le solde dans la base
    await db.company_balance.update_one(
        {},
        {
            "$set": {
                "current_balance": current_balance,
                "total_payments": total_payments,
                "total_withdrawals": total_withdrawals,
                "last_updated": datetime.now(timezone.utc).isoformat(),
                "last_calculation": {
                    "total_payments": total_payments,
                    "total_withdrawals": total_withdrawals,
                    "balance": current_balance
                }
            }
        },
        upsert=True
    )
    
    return BalanceResponse(
        current_balance=current_balance,
        total_payments=total_payments,
        total_withdrawals=total_withdrawals,
        last_updated=datetime.now(timezone.utc).isoformat()
    )

@api_router.post("/withdrawals", response_model=WithdrawalResponse)
async def create_withdrawal(withdrawal_data: WithdrawalCreate, current_user: dict = Depends(get_current_user)):
    """Créer un nouveau retrait (Manager seulement)"""
    if current_user["role"] != "MANAGER":
        raise HTTPException(status_code=403, detail="Seuls les managers peuvent déclarer des retraits")
    
    withdrawal_id = str(uuid.uuid4())
    withdrawal_dict = {
        "id": withdrawal_id,
        "manager_id": current_user["id"],
        "manager_name": current_user["full_name"],
        "amount": withdrawal_data.amount,
        "category": withdrawal_data.category,
        "subcategory": withdrawal_data.subcategory,
        "description": withdrawal_data.description,
        "receipt_url": withdrawal_data.receipt_url,
        "withdrawal_date": datetime.now(timezone.utc).isoformat(),
        "created_at": datetime.now(timezone.utc).isoformat()
    }
    
    await db.withdrawals.insert_one(withdrawal_dict)
    
    # Log de l'activité
    await log_user_activity(
        user_id=current_user["id"],
        action="withdrawal_created",
        details={
            "withdrawal_id": withdrawal_id,
            "amount": withdrawal_data.amount,
            "category": withdrawal_data.category,
            "subcategory": withdrawal_data.subcategory
        }
    )
    
    # Notification au SuperAdmin
    superadmin = await db.users.find_one({"role": "SUPERADMIN"})
    if superadmin:
        await create_notification(
            user_id=superadmin["id"],
            title="Nouveau retrait déclaré",
            message=f"{current_user['full_name']} a déclaré un retrait de {withdrawal_data.amount}€ ({withdrawal_data.category})",
            type="withdrawal",
            related_id=withdrawal_id
        )
    
    return WithdrawalResponse(**withdrawal_dict)

@api_router.get("/withdrawals", response_model=List[WithdrawalResponse])
async def get_withdrawals(current_user: dict = Depends(get_current_user)):
    """Obtenir la liste des retraits"""
    query = {}
    
    # Manager voit ses propres retraits, SuperAdmin voit tout
    if current_user["role"] == "MANAGER":
        query["manager_id"] = current_user["id"]
    elif current_user["role"] not in ["SUPERADMIN"]:
        raise HTTPException(status_code=403, detail="Accès refusé")
    
    withdrawals = await db.withdrawals.find(query, {"_id": 0}).sort("withdrawal_date", -1).to_list(100)
    return [WithdrawalResponse(**w) for w in withdrawals]

@api_router.get("/expense-categories", response_model=Dict[str, ExpenseCategoryInfo])
async def get_expense_categories():
    """Obtenir les catégories de dépenses disponibles"""
    return {
        cat_key: ExpenseCategoryInfo(**cat_data) 
        for cat_key, cat_data in EXPENSE_CATEGORIES_CONFIG.items()
    }

# Enhanced Payments with Confirmation Code
@api_router.patch("/payments/{payment_id}/confirm", response_model=PaymentDeclarationResponse)
async def confirm_payment_with_code(
    payment_id: str, 
    confirmation_data: PaymentConfirmRequest, 
    current_user: dict = Depends(get_current_user)
):
    """Confirmer ou rejeter un paiement (Manager seulement)"""
    if current_user["role"] != "MANAGER":
        raise HTTPException(status_code=403, detail="Seuls les managers peuvent confirmer les paiements")
    
    payment = await db.payment_declarations.find_one({"id": payment_id})
    if not payment:
        raise HTTPException(status_code=404, detail="Paiement non trouvé")
    
    if payment["status"] != "pending":
        raise HTTPException(status_code=400, detail="Ce paiement a déjà été traité")
    
    if confirmation_data.action == "REJECTED":
        if not confirmation_data.rejection_reason:
            raise HTTPException(status_code=400, detail="Un motif de rejet est obligatoire")
        
        # Rejeter le paiement
        update_dict = {
            "status": "REJECTED",
            "rejection_reason": confirmation_data.rejection_reason,
            "confirmed_by": current_user["id"],
            "confirmed_at": datetime.now(timezone.utc).isoformat()
        }
        
        await db.payment_declarations.update_one({"id": payment_id}, {"$set": update_dict})
        
        # Notifier le client du rejet
        await create_notification(
            user_id=payment["client_id"],
            title="Paiement rejeté",
            message=f"Votre paiement de {payment['amount']} {payment['currency']} a été rejeté. Motif: {confirmation_data.rejection_reason}",
            type="payment_rejected",
            related_id=payment_id
        )
        
    elif confirmation_data.action == "CONFIRMED":
        logger.info(f"=== PAYMENT CONFIRMATION DEBUG ===")
        logger.info(f"Payment ID: {payment_id}")
        logger.info(f"Action: {confirmation_data.action}")
        logger.info(f"Payment has code: {bool(payment.get('confirmation_code'))}")
        logger.info(f"Received code: {confirmation_data.confirmation_code}")
        
        # Étape 1: Générer un code de confirmation si pas encore fait
        if not payment.get("confirmation_code"):
            confirmation_code = generate_confirmation_code()
            logger.info(f"Generated new code: {confirmation_code}")
            await db.payment_declarations.update_one(
                {"id": payment_id}, 
                {"$set": {"confirmation_code": confirmation_code, "confirmation_required": True}}
            )
            # Obtenir le paiement mis à jour avec le code
            updated_payment_with_code = await db.payment_declarations.find_one({"id": payment_id}, {"_id": 0})
            updated_payment_with_code["message"] = "Code de confirmation généré. Veuillez le saisir pour valider."
            return PaymentDeclarationResponse(**updated_payment_with_code)
        
        # Étape 2: Vérifier le code saisi
        if not confirmation_data.confirmation_code:
            logger.error("No confirmation code provided")
            raise HTTPException(status_code=400, detail="Code de confirmation requis")
        
        stored_code = payment["confirmation_code"]
        provided_code = confirmation_data.confirmation_code
        logger.info(f"Stored code: {stored_code}")
        logger.info(f"Provided code: {provided_code}")
        logger.info(f"Codes match: {provided_code == stored_code}")
        
        if provided_code != stored_code:
            logger.error(f"Code mismatch: expected {stored_code}, got {provided_code}")
            
            # Incrémenter le compteur de tentatives
            attempts = payment.get("confirmation_attempts", 0) + 1
            await db.payment_declarations.update_one(
                {"id": payment_id}, 
                {"$set": {"confirmation_attempts": attempts}}
            )
            
            # Si 3 tentatives échouées, rejeter automatiquement
            if attempts >= 3:
                await db.payment_declarations.update_one(
                    {"id": payment_id}, 
                    {"$set": {
                        "status": "REJECTED",
                        "rejection_reason": "Code de vérification du paiement invalide (3 tentatives échouées)",
                        "confirmed_by": current_user["id"],
                        "confirmed_at": datetime.now(timezone.utc).isoformat()
                    }}
                )
                
                # Notifier le client du rejet automatique
                await create_notification(
                    user_id=payment["client_id"],
                    title="Paiement rejeté",
                    message=f"Votre paiement de {payment['amount']} {payment['currency']} a été rejeté automatiquement après 3 tentatives de code invalides.",
                    type="payment_rejected",
                    related_id=payment_id
                )
                
                raise HTTPException(
                    status_code=400, 
                    detail="Paiement rejeté automatiquement après 3 tentatives de code invalides"
                )
            
            # Sinon, indiquer le nombre de tentatives restantes
            remaining = 3 - attempts
            raise HTTPException(
                status_code=400, 
                detail=f"Code de confirmation incorrect. Tentatives restantes: {remaining}/3"
            )
        
        # Confirmer le paiement
        invoice_number = f"ALO-{datetime.now().strftime('%Y%m%d')}-{payment_id[:8].upper()}"
        
        update_dict = {
            "status": "CONFIRMED",
            "confirmed_by": current_user["id"],
            "confirmed_at": datetime.now(timezone.utc).isoformat(),
            "invoice_number": invoice_number
        }
        
        await db.payment_declarations.update_one({"id": payment_id}, {"$set": update_dict})
        
        # Générer le PDF de la facture
        payment_data_for_pdf = {
            **payment,
            **update_dict,
            "client_name": payment.get("client_name", "Client"),
            "manager_name": current_user["full_name"]
        }
        
        try:
            # Use the existing PDF generation function
            await generate_invoice_pdf(payment_id, invoice_number)
            # Store PDF URL
            pdf_url = f"/invoices/{invoice_number}.pdf"
            await db.payment_declarations.update_one(
                {"id": payment_id}, 
                {"$set": {"pdf_invoice_url": pdf_url}}
            )
        except Exception as e:
            logger.error(f"Erreur génération PDF: {e}")
        
        # Notifier le client de la confirmation
        await create_notification(
            user_id=payment["client_id"],
            title="Paiement confirmé",
            message=f"Votre paiement de {payment['amount']} {payment['currency']} a été confirmé. Facture N° {invoice_number}",
            type="payment_confirmed",
            related_id=payment_id
        )
        
        # Notifier tous les SuperAdmin des paiements confirmés
        superadmins = await db.users.find({"role": "SUPERADMIN", "is_active": True}).to_list(10)
        for superadmin in superadmins:
            await create_notification(
                user_id=superadmin["id"],
                title="💰 Paiement confirmé",
                message=f"Paiement de {payment['amount']} {payment['currency']} confirmé par {current_user['full_name']} - Client: {payment.get('client_name', payment['client_id'])}",
                type="admin_payment_confirmed",
                related_id=payment_id
            )
    
    # Log de l'activité
    await log_user_activity(
        user_id=current_user["id"],
        action=f"payment_{confirmation_data.action.lower()}",
        details={
            "payment_id": payment_id,
            "amount": payment["amount"],
            "client_id": payment["client_id"],
            "action": confirmation_data.action
        }
    )
    
    # Retourner le paiement mis à jour
    updated_payment = await db.payment_declarations.find_one({"id": payment_id}, {"_id": 0})
    return PaymentDeclarationResponse(**updated_payment)

@api_router.get("/payments/pending", response_model=List[PaymentDeclarationResponse])
async def get_pending_payments(current_user: dict = Depends(get_current_user)):
    """Obtenir les paiements en attente (Manager seulement)"""
    if current_user["role"] != "MANAGER":
        raise HTTPException(status_code=403, detail="Accès refusé")
    
    payments = await db.payment_declarations.find(
        {"status": "pending"}, {"_id": 0}
    ).sort("declared_at", 1).to_list(100)
    
    return [PaymentDeclarationResponse(**p) for p in payments]

@api_router.get("/payments/history", response_model=List[PaymentDeclarationResponse])
async def get_payment_history(current_user: dict = Depends(get_current_user)):
    """Obtenir l'historique des paiements (Manager/SuperAdmin seulement)"""
    if current_user["role"] not in ["MANAGER", "SUPERADMIN"]:
        raise HTTPException(status_code=403, detail="Accès refusé")
    
    payments = await db.payment_declarations.find(
        {}, {"_id": 0}
    ).sort("declared_at", -1).to_list(100)
    
    return [PaymentDeclarationResponse(**p) for p in payments]

@api_router.get("/payments/client-history", response_model=List[PaymentDeclarationResponse])
async def get_client_payment_history(current_user: dict = Depends(get_current_user)):
    """Obtenir l'historique des paiements pour un client spécifique"""
    if current_user["role"] != "CLIENT":
        raise HTTPException(status_code=403, detail="Accès réservé aux clients")
    
    # Find the client record for this user
    client = await db.clients.find_one({"user_id": current_user["id"]})
    if not client:
        raise HTTPException(status_code=404, detail="Profil client non trouvé")
    
    payments = await db.payment_declarations.find(
        {"client_id": client["id"]}, {"_id": 0}
    ).sort("declared_at", -1).to_list(100)
    
    return [PaymentDeclarationResponse(**p) for p in payments]

@api_router.get("/payments/consultations")
async def get_consultation_payments(current_user: dict = Depends(get_current_user)):
    """Obtenir tous les paiements de consultation (50k CFA) - SuperAdmin uniquement"""
    if current_user["role"] != "SUPERADMIN":
        raise HTTPException(status_code=403, detail="Accès réservé aux SuperAdmin")
    
    # Récupérer tous les paiements de type consultation
    consultation_payments = await db.payments.find(
        {"type": "consultation"}, {"_id": 0}
    ).sort("created_at", -1).to_list(1000)
    
    # Calculer le total
    total_amount = sum(p.get("amount", 0) for p in consultation_payments)
    
    return {
        "payments": consultation_payments,
        "total_count": len(consultation_payments),
        "total_amount": total_amount,
        "currency": "CFA"
    }

@api_router.get("/payments/{payment_id}/invoice")
async def download_invoice(payment_id: str, current_user: dict = Depends(get_current_user)):
    """Télécharger la facture PDF pour un paiement"""
    from fastapi.responses import StreamingResponse
    from invoice_generator import generate_invoice_pdf
    
    # Récupérer le paiement
    payment = await db.payments.find_one({"id": payment_id}, {"_id": 0})
    if not payment:
        raise HTTPException(status_code=404, detail="Paiement non trouvé")
    
    # Vérifier les permissions
    client_id = payment.get("client_id") or payment.get("user_id")
    
    if current_user["role"] == "CLIENT":
        # Le client peut télécharger ses propres factures
        if client_id != current_user["id"]:
            raise HTTPException(status_code=403, detail="Accès non autorisé")
    elif current_user["role"] == "EMPLOYEE":
        # L'employé peut télécharger les factures de ses clients
        client_record = await db.clients.find_one({"user_id": client_id})
        if not client_record or client_record.get("assigned_employee_id") != current_user["id"]:
            raise HTTPException(status_code=403, detail="Accès non autorisé")
    elif current_user["role"] not in ["MANAGER", "SUPERADMIN"]:
        raise HTTPException(status_code=403, detail="Accès non autorisé")
    
    # Récupérer les informations du client
    client_user = await db.users.find_one({"id": client_id}, {"_id": 0})
    if not client_user:
        client_data = {
            "full_name": "Client",
            "email": payment.get("user_email", "N/A"),
            "phone": "N/A"
        }
    else:
        client_data = {
            "full_name": client_user.get("full_name", "N/A"),
            "email": client_user.get("email", "N/A"),
            "phone": client_user.get("phone", "N/A")
        }
    
    # Générer le PDF
    pdf_buffer = generate_invoice_pdf(payment, client_data)
    
    # Retourner le PDF
    return StreamingResponse(
        pdf_buffer,
        media_type="application/pdf",
        headers={
            "Content-Disposition": f"attachment; filename=Facture_{payment.get('invoice_number', payment_id)}.pdf"
        }
    )

# Contact Messages & CRM
@api_router.post("/contact-messages", response_model=ContactMessageResponse)
async def create_contact_message(message_data: ContactMessageCreate):
    """Créer un nouveau message de contact (API publique)"""
    message_id = str(uuid.uuid4())
    
    # Calculer le score de lead
    lead_score = calculate_lead_score(message_data.model_dump())
    
    # Tentative d'attribution automatique si un employé est mentionné
    assigned_employee_id = None
    assigned_employee_name = None
    
    if message_data.how_did_you_know == "Par une personne" and message_data.referred_by_employee:
        # Recherche de l'employé par nom (recherche flexible)
        employee_name_parts = message_data.referred_by_employee.strip().lower().split()
        if employee_name_parts:
            # Construire une requête de recherche flexible
            name_query = {
                "$and": [
                    {"role": "EMPLOYEE"},
                    {"is_active": True},
                    {
                        "$or": [
                            {"full_name": {"$regex": message_data.referred_by_employee, "$options": "i"}},
                            {
                                "$and": [
                                    {"full_name": {"$regex": employee_name_parts[0], "$options": "i"}},
                                    {"full_name": {"$regex": employee_name_parts[-1], "$options": "i"}} if len(employee_name_parts) > 1 else {}
                                ]
                            }
                        ]
                    }
                ]
            }
            
            employee = await db.users.find_one(name_query)
            if employee:
                assigned_employee_id = employee["id"]
                assigned_employee_name = employee["full_name"]
                logger.info(f"Attribution automatique du prospect {message_data.name} à l'employé {assigned_employee_name}")
    
    message_dict = {
        "id": message_id,
        "name": message_data.name,
        "email": message_data.email,
        "phone": message_data.phone,
        "country": message_data.country,
        "visa_type": message_data.visa_type,
        "budget_range": message_data.budget_range,
        "urgency_level": message_data.urgency_level,
        "message": message_data.message,
        "status": ContactStatus.NEW,  # Toujours "nouveau" au départ
        "assigned_to": None,  # SuperAdmin assignera plus tard
        "assigned_to_name": None,
        "lead_source": message_data.lead_source,
        "conversion_probability": lead_score,
        "notes": "",
        "how_did_you_know": message_data.how_did_you_know,
        "referred_by_employee": message_data.referred_by_employee,
        "payment_50k_amount": None,
        "payment_50k_date": None,
        "consultant_notes": [],
        "follow_up_date": None,
        "created_at": datetime.now(timezone.utc).isoformat(),
        "updated_at": datetime.now(timezone.utc).isoformat()
    }
    
    await db.contact_messages.insert_one(message_dict)
    
    # Envoi automatique d'e-mail de bienvenue au prospect
    if EMAIL_SERVICE_AVAILABLE:
        try:
            email_sent = await send_prospect_email(message_data.model_dump())
            if email_sent:
                logger.info(f"E-mail de bienvenue envoyé à {message_data.email}")
                # Mettre à jour le message pour indiquer l'envoi d'e-mail
                await db.contact_messages.update_one(
                    {"id": message_id},
                    {"$set": {"welcome_email_sent": True, "welcome_email_sent_at": datetime.now(timezone.utc).isoformat()}}
                )
            else:
                logger.warning(f"Échec envoi e-mail de bienvenue à {message_data.email}")
        except Exception as e:
            logger.error(f"Erreur envoi e-mail prospect {message_data.email}: {e}")
    
    # Notifier les managers du nouveau lead
    managers = await db.users.find({"role": "MANAGER", "is_active": True}).to_list(10)
    for manager in managers:
        notification_message = f"{message_data.name} ({message_data.country}) - Score: {lead_score}%"
        if assigned_employee_name:
            notification_message += f" - Assigné à: {assigned_employee_name}"
        
        await create_notification(
            user_id=manager["id"],
            title="Nouveau contact prospect",
            message=notification_message,
            type="new_lead",
            related_id=message_id
        )
    
    # Si un employé est assigné automatiquement, le notifier aussi
    if assigned_employee_id:
        await create_notification(
            user_id=assigned_employee_id,
            title="🎯 Nouveau prospect vous est assigné",
            message=f"{message_data.name} vous a été recommandé par {message_data.referred_by_employee}. Score: {lead_score}% - Priorité de contact!",
            type="assigned_lead",
            related_id=message_id
        )
    
    # Log de l'activité
    await log_user_activity(
        user_id="public",
        action="contact_message_created",
        details={
            "message_id": message_id,
            "name": message_data.name,
            "country": message_data.country,
            "lead_score": lead_score
        }
    )
    
    return ContactMessageResponse(**message_dict)

@api_router.get("/contact-messages", response_model=List[ContactMessageResponse])
async def get_contact_messages(
    status: Optional[str] = None,
    current_user: dict = Depends(get_current_user)
):
    """Obtenir les messages de contact (SuperAdmin/Manager/Employee/Consultant)"""
    if current_user["role"] not in ["SUPERADMIN", "MANAGER", "EMPLOYEE", "CONSULTANT"]:
        raise HTTPException(status_code=403, detail="Accès refusé")
    
    query = {}
    if status:
        query["status"] = status
    
    # SUPERADMIN voit TOUS les prospects
    if current_user["role"] == "SUPERADMIN":
        pass  # Pas de filtre
    # CONSULTANT voit seulement les prospects avec statut paiement_50k
    elif current_user["role"] == "CONSULTANT":
        query["status"] = "paiement_50k"
    # MANAGER et EMPLOYEE voient seulement les messages qui leur sont assignés
    elif current_user["role"] in ["MANAGER", "EMPLOYEE"]:
        query["assigned_to"] = current_user["id"]
    
    messages = await db.contact_messages.find(query, {"_id": 0}).sort("created_at", -1).to_list(200)
    return [ContactMessageResponse(**msg) for msg in messages]

@api_router.patch("/contact-messages/{message_id}/assign")
async def assign_contact_message(
    message_id: str,
    assignment_data: dict,
    current_user: dict = Depends(get_current_user)
):
    """Assigner un prospect à un employé/manager (SuperAdmin seulement)"""
    if current_user["role"] != "SUPERADMIN":
        raise HTTPException(status_code=403, detail="Seul le SuperAdmin peut assigner les prospects")
    
    assignee_id = assignment_data.get("assigned_to")
    if not assignee_id:
        raise HTTPException(status_code=400, detail="Identifiant de l'assigné requis")
    
    assignee = await db.users.find_one({"id": assignee_id, "role": {"$in": ["MANAGER", "EMPLOYEE"]}, "is_active": True})
    if not assignee:
        raise HTTPException(status_code=404, detail="Employé/Manager non trouvé")
    
    result = await db.contact_messages.update_one(
        {"id": message_id},
        {
            "$set": {
                "assigned_to": assignee_id,
                "assigned_to_name": assignee["full_name"],
                "status": ContactStatus.ASSIGNED_EMPLOYEE,
                "updated_at": datetime.now(timezone.utc).isoformat()
            }
        }
    )
    
    if result.modified_count == 0:
        raise HTTPException(status_code=404, detail="Prospect non trouvé")
    
    # Récupérer le prospect
    prospect = await db.contact_messages.find_one({"id": message_id})
    
    # Notifier l'assigné
    await create_notification(
        user_id=assignee_id,
        title="🎯 Nouveau prospect assigné",
        message=f"Le prospect {prospect['name']} ({prospect['country']}) vous a été assigné par le consultant.",
        type="prospect_assigned",
        related_id=message_id
    )
    
    # Log activity
    await log_user_activity(
        user_id=current_user["id"],
        action="prospect_assigned",
        details={
            "prospect_id": message_id,
            "prospect_name": prospect["name"],
            "assigned_to": assignee["full_name"]
        }
    )
    
    # Envoyer email de notification à l'assigné
    if EMAIL_SERVICE_AVAILABLE:
        try:
            email_sent = await send_prospect_assignment_notification(
                prospect_data=prospect,
                assignee_data=assignee
            )
            if email_sent:
                logger.info(f"Email d'assignment envoyé à {assignee['email']}")
        except Exception as e:
            logger.error(f"Erreur envoi email assignment: {e}")
    
    return {"message": "Prospect assigné avec succès", "assigned_to_name": assignee["full_name"]}

@api_router.patch("/contact-messages/{message_id}/status")
async def update_contact_message_status(
    message_id: str,
    status_data: dict,
    current_user: dict = Depends(get_current_user)
):
    """Mettre à jour le statut d'un message de contact"""
    if current_user["role"] not in ["MANAGER", "EMPLOYEE", "SUPERADMIN"]:
        raise HTTPException(status_code=403, detail="Accès refusé")
    
    # Vérifier que le message existe et que l'utilisateur y a accès
    query = {"id": message_id}
    if current_user["role"] == "EMPLOYEE":
        query["assigned_to"] = current_user["id"]
    
    message = await db.contact_messages.find_one(query)
    if not message:
        raise HTTPException(status_code=404, detail="Message non trouvé")
    
    new_status = status_data.get("status")
    valid_statuses = ["new", "read", "responded", "converted", "closed"]
    
    if new_status not in valid_statuses:
        raise HTTPException(status_code=400, detail=f"Statut invalide. Statuts autorisés: {valid_statuses}")
    
    # Mettre à jour le message
    result = await db.contact_messages.update_one(
        {"id": message_id},
        {
            "$set": {
                "status": new_status,
                "updated_at": datetime.now(timezone.utc).isoformat()
            }
        }
    )
    
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Erreur lors de la mise à jour")
    
    return {"message": "Statut mis à jour avec succès", "new_status": new_status}

@api_router.post("/contact-messages/{message_id}/respond")
async def respond_to_contact_message(
    message_id: str,
    response_data: dict,
    current_user: dict = Depends(get_current_user)
):
    """Répondre à un message de contact"""
    if current_user["role"] not in ["MANAGER", "EMPLOYEE", "SUPERADMIN"]:
        raise HTTPException(status_code=403, detail="Accès refusé")
    
    # Vérifier que le message existe et que l'utilisateur y a accès
    query = {"id": message_id}
    if current_user["role"] == "EMPLOYEE":
        query["assigned_to"] = current_user["id"]
    
    message = await db.contact_messages.find_one(query)
    if not message:
        raise HTTPException(status_code=404, detail="Message non trouvé")
    
    # Données de la réponse
    subject = response_data.get("subject", "")
    response_message = response_data.get("message", "")
    
    if not response_message.strip():
        raise HTTPException(status_code=400, detail="Le message de réponse est requis")
    
    # Créer l'entrée de réponse
    response_id = str(uuid.uuid4())
    response_entry = {
        "id": response_id,
        "message_id": message_id,
        "responder_id": current_user["id"],
        "responder_name": current_user["full_name"],
        "subject": subject,
        "message": response_message,
        "sent_at": datetime.now(timezone.utc).isoformat()
    }
    
    # Sauvegarder la réponse dans une collection séparée
    await db.contact_responses.insert_one(response_entry)
    
    # Mettre à jour le statut du message original
    await db.contact_messages.update_one(
        {"id": message_id},
        {
            "$set": {
                "status": ContactStatus.RESPONDED,
                "last_response_at": datetime.now(timezone.utc).isoformat(),
                "updated_at": datetime.now(timezone.utc).isoformat()
            },
            "$inc": {"response_count": 1}
        }
    )
    
    # Log d'activité
    await log_user_activity(
        user_id=current_user["id"],
        action="RESPOND_TO_CONTACT",
        resource_type="contact_message",
        resource_id=message_id,
        details={
            "contact_email": message["email"],
            "subject": subject,
            "response_length": len(response_message)
        }
    )
    
    return {
        "message": "Réponse envoyée avec succès",
        "response_id": response_id,
        "sent_to": message["email"]
    }


class ConsultantPaymentRequest(BaseModel):
    payment_method: str = "Cash"  # Cash, Mobile Money, Virement
    transaction_reference: Optional[str] = None

@api_router.patch("/contact-messages/{message_id}/assign-consultant")
async def assign_prospect_to_consultant(
    message_id: str,
    payment_data: ConsultantPaymentRequest,
    current_user: dict = Depends(get_current_user)
):
    """Affecter un prospect au consultant (SuperAdmin) après paiement 50k CFA (Manager/Employee)"""
    if current_user["role"] not in ["MANAGER", "EMPLOYEE"]:
        raise HTTPException(status_code=403, detail="Seuls les employés/managers peuvent affecter au consultant")
    
    # Vérifier que le prospect existe et est assigné à l'utilisateur courant
    prospect = await db.contact_messages.find_one({"id": message_id, "assigned_to": current_user["id"]})
    if not prospect:
        raise HTTPException(status_code=404, detail="Prospect non trouvé ou non assigné à vous")
    
    if prospect["status"] == ContactStatus.PAYMENT_50K:
        raise HTTPException(status_code=400, detail="Ce prospect est déjà affecté au consultant")
    
    # Créer un enregistrement de paiement consultation dans la collection payments
    payment_id = str(uuid.uuid4())
    payment_date = datetime.now(timezone.utc)
    payment_doc = {
        "id": payment_id,
        "invoice_number": f"CONS-{datetime.now().strftime('%Y%m%d')}-{payment_id[:8].upper()}",
        "type": "consultation",  # Type spécial pour paiement consultation
        "amount": 50000,
        "currency": "CFA",
        "payment_method": payment_data.payment_method,
        "transaction_reference": payment_data.transaction_reference,
        "status": "CONFIRMED",  # Automatiquement confirmé par Manager/Employee
        "prospect_id": message_id,
        "prospect_name": prospect["name"],
        "prospect_email": prospect["email"],
        "confirmed_by": current_user["id"],
        "confirmed_by_name": current_user["full_name"],
        "confirmed_at": payment_date.isoformat(),
        "created_at": payment_date.isoformat(),
        "updated_at": payment_date.isoformat()
    }
    
    await db.payments.insert_one(payment_doc)
    
    # Mettre à jour le prospect
    result = await db.contact_messages.update_one(
        {"id": message_id},
        {
            "$set": {
                "status": ContactStatus.PAYMENT_50K,
                "payment_50k_amount": 50000,
                "payment_50k_date": payment_date.isoformat(),
                "payment_50k_id": payment_id,  # Lien vers le paiement
                "payment_50k_method": payment_data.payment_method,
                "updated_at": payment_date.isoformat()
            }
        }
    )
    
    if result.modified_count == 0:
        raise HTTPException(status_code=500, detail="Erreur lors de l'affectation")
    
    # Notifier le SuperAdmin
    superadmins = await db.users.find({"role": "SUPERADMIN", "is_active": True}).to_list(10)
    for admin in superadmins:
        await create_notification(
            user_id=admin["id"],
            title="💰 Paiement Consultation 50,000 CFA",
            message=f"{prospect['name']} a payé 50,000 CFA pour consultation. Méthode: {payment_data.payment_method}. Confirmé par {current_user['full_name']}.",
            type="payment_consultation",
            related_id=message_id
        )
    
    # Log activity
    await log_user_activity(
        user_id=current_user["id"],
        action="consultation_payment_confirmed",
        details={
            "prospect_id": message_id,
            "prospect_name": prospect["name"],
            "payment_amount": 50000,
            "payment_method": payment_data.payment_method,
            "payment_id": payment_id,
            "currency": "CFA"
        }
    )
    
    # Envoyer email au prospect pour confirmer RDV consultant
    if EMAIL_SERVICE_AVAILABLE:
        try:
            prospect_with_assignee = {
                **prospect,
                "assigned_by_name": current_user["full_name"]
            }
            email_sent = await send_consultant_appointment_notification(prospect_with_assignee)
            if email_sent:
                logger.info(f"Email RDV consultant envoyé à {prospect['email']}")
        except Exception as e:
            logger.error(f"Erreur envoi email RDV consultant: {e}")
    
    return {
        "message": "Prospect affecté au consultant avec succès",
        "payment_50k_amount": 50000,
        "payment_id": payment_id,
        "invoice_number": payment_doc["invoice_number"]
    }

class ConsultantNotesRequest(BaseModel):
    note: str
    is_potential_client: bool = False
    potential_level: str = "NON"  # OUI, NON, PEUT-ÊTRE

@api_router.patch("/contact-messages/{message_id}/consultant-notes")
async def add_consultant_notes(
    message_id: str,
    notes_data: ConsultantNotesRequest,
    current_user: dict = Depends(get_current_user)
):
    """Ajouter des notes consultant sur un prospect avec évaluation potentiel client"""
    if current_user["role"] not in ["SUPERADMIN", "CONSULTANT"]:
        raise HTTPException(status_code=403, detail="Seul le consultant peut ajouter des notes")
    
    prospect = await db.contact_messages.find_one({"id": message_id})
    if not prospect:
        raise HTTPException(status_code=404, detail="Prospect non trouvé")
    
    if not notes_data.note.strip():
        raise HTTPException(status_code=400, detail="La note ne peut pas être vide")
    
    # Créer l'objet note
    note_entry = {
        "id": str(uuid.uuid4()),
        "content": notes_data.note,
        "created_by": current_user["full_name"],
        "created_at": datetime.now(timezone.utc).isoformat()
    }
    
    # Ajouter la note à l'historique
    update_data = {
        "$push": {"consultant_notes": note_entry},
        "$set": {
            "status": ContactStatus.IN_CONSULTATION,
            "is_potential_client": notes_data.is_potential_client,
            "potential_level": notes_data.potential_level,
            "consultation_completed_at": datetime.now(timezone.utc).isoformat(),
            "updated_at": datetime.now(timezone.utc).isoformat()
        }
    }
    
    result = await db.contact_messages.update_one(
        {"id": message_id},
        update_data
    )
    
    if result.modified_count == 0:
        raise HTTPException(status_code=500, detail="Erreur lors de l'ajout de la note")
    
    # Notifier Manager/Employee qui a assigné le prospect
    if prospect.get("assigned_to"):
        assignee = await db.users.find_one({"id": prospect["assigned_to"]})
        if assignee:
            notification_title = "✅ Consultation Terminée"
            
            if notes_data.is_potential_client and notes_data.potential_level == "OUI":
                notification_msg = f"🎯 POTENTIEL CLIENT - {prospect['name']} : Consultation terminée. Prospect très intéressé ! Contactez sous 48h."
                notification_type = "consultation_potential_client"
            elif notes_data.potential_level == "PEUT-ÊTRE":
                notification_msg = f"⚠️ {prospect['name']} : Consultation terminée. Prospect hésitant, suivi recommandé."
                notification_type = "consultation_maybe"
            else:
                notification_msg = f"ℹ️ {prospect['name']} : Consultation terminée. Prospect non qualifié pour le moment."
                notification_type = "consultation_not_qualified"
            
            await create_notification(
                user_id=assignee["id"],
                title=notification_title,
                message=notification_msg,
                type=notification_type,
                related_id=message_id
            )
            
            # Envoyer email si potentiel client
            if notes_data.is_potential_client and notes_data.potential_level == "OUI":
                # TODO: Implémenter email notification
                logger.info(f"Email notification needed for {assignee['email']} about potential client {prospect['name']}")
    
    # Log activity
    await log_user_activity(
        user_id=current_user["id"],
        action="consultant_note_added",
        details={
            "prospect_id": message_id,
            "prospect_name": prospect["name"],
            "is_potential_client": notes_data.is_potential_client,
            "potential_level": notes_data.potential_level,
            "note_preview": notes_data.note[:100]
        }
    )
    
    return {
        "message": "Note ajoutée avec succès",
        "note_id": note_entry["id"],
        "is_potential_client": notes_data.is_potential_client,
        "potential_level": notes_data.potential_level
    }

@api_router.get("/contact-messages/check-48h-alerts")
async def check_48h_consultation_alerts(current_user: dict = Depends(get_current_user)):
    """Vérifier prospects potentiels non convertis depuis >48h et envoyer notifications"""
    if current_user["role"] not in ["SUPERADMIN", "MANAGER", "EMPLOYEE"]:
        raise HTTPException(status_code=403, detail="Accès non autorisé")
    
    # Calculer timestamp 48h avant maintenant
    now = datetime.now(timezone.utc)
    hours_48_ago = now - timedelta(hours=48)
    
    # Chercher prospects potentiels (consultation terminée il y a >48h, non convertis)
    query = {
        "status": ContactStatus.IN_CONSULTATION,
        "is_potential_client": True,
        "potential_level": "OUI",
        "consultation_completed_at": {"$lt": hours_48_ago.isoformat()}
    }
    
    # Filtrer par assignation si pas SuperAdmin
    if current_user["role"] != "SUPERADMIN":
        query["assigned_to"] = current_user["id"]
    
    prospects_needing_followup = await db.contact_messages.find(query).to_list(100)
    
    alerts_sent = 0
    for prospect in prospects_needing_followup:
        # Créer notification rappel
        await create_notification(
            user_id=prospect["assigned_to"],
            title="⏰ RAPPEL URGENT - 48H Dépassées",
            message=f"🚨 {prospect['name']} : Prospect potentiel client non converti depuis 48h. Action requise !",
            type="urgent_followup_48h",
            related_id=prospect["id"]
        )
        alerts_sent += 1
        
        # Marquer qu'alerte 48h a été envoyée
        await db.contact_messages.update_one(
            {"id": prospect["id"]},
            {"$set": {"alert_48h_sent": True, "alert_48h_sent_at": now.isoformat()}}
        )
    
    return {
        "message": f"{alerts_sent} alertes envoyées",
        "prospects_needing_action": len(prospects_needing_followup)
    }

@api_router.post("/contact-messages/{message_id}/convert-to-client")
async def convert_prospect_to_client(
    message_id: str,
    client_data: dict,
    current_user: dict = Depends(get_current_user)
):
    """Convertir un prospect en client (Manager/Employee)"""
    if current_user["role"] not in ["MANAGER", "EMPLOYEE"]:
        raise HTTPException(status_code=403, detail="Seuls les employés/managers peuvent convertir les prospects")
    
    # Vérifier que le prospect existe et est assigné à l'utilisateur
    prospect = await db.contact_messages.find_one({"id": message_id, "assigned_to": current_user["id"]})
    if not prospect:
        raise HTTPException(status_code=404, detail="Prospect non trouvé ou non assigné à vous")
    
    # Récupérer les données du client
    first_payment = client_data.get("first_payment_amount", 0)
    country = client_data.get("country", prospect.get("country", ""))
    visa_type = client_data.get("visa_type", prospect.get("visa_type", ""))
    
    if not country or not visa_type:
        raise HTTPException(status_code=400, detail="Pays et type de visa requis")
    
    # Créer l'utilisateur client
    client_id = str(uuid.uuid4())
    temp_password = generate_temporary_password()
    hashed_password = pwd_context.hash(temp_password)
    
    user_dict = {
        "id": client_id,
        "email": prospect["email"],
        "full_name": prospect["name"],
        "phone": prospect.get("phone", ""),
        "password": hashed_password,
        "role": "CLIENT",
        "is_active": True,
        "created_at": datetime.now(timezone.utc).isoformat()
    }
    
    await db.users.insert_one(user_dict)
    
    # Créer le profil client dans la collection clients
    client_profile_dict = {
        "id": str(uuid.uuid4()),
        "user_id": client_id,
        "full_name": prospect["name"],
        "email": prospect["email"],
        "phone": prospect.get("phone", ""),
        "country": country,
        "visa_type": visa_type,
        "assigned_employee_id": current_user["id"],
        "assigned_employee_name": current_user["full_name"],
        "status": "active",
        "created_at": datetime.now(timezone.utc).isoformat(),
        "updated_at": datetime.now(timezone.utc).isoformat()
    }
    
    await db.clients.insert_one(client_profile_dict)
    
    # Créer le dossier client
    case_id = str(uuid.uuid4())
    
    # Récupérer le workflow
    workflows_data = await db.workflows.find_one({"country": country})
    if not workflows_data:
        # Workflow par défaut si non trouvé
        workflow_steps = WORKFLOWS.get(country, {}).get(visa_type, [])
    else:
        workflow_steps = workflows_data.get("workflows", {}).get(visa_type, [])
    
    case_dict = {
        "id": case_id,
        "client_id": client_id,
        "client_name": prospect["name"],
        "client_email": prospect["email"],
        "assigned_employee_id": current_user["id"],
        "assigned_employee_name": current_user["full_name"],
        "country": country,
        "visa_type": visa_type,
        "status": "En cours",
        "current_step_index": 0,
        "workflow_steps": workflow_steps,
        "progress_percentage": 0,
        "created_at": datetime.now(timezone.utc).isoformat(),
        "updated_at": datetime.now(timezone.utc).isoformat()
    }
    
    await db.cases.insert_one(case_dict)
    
    # Si un premier paiement est déclaré, l'enregistrer
    if first_payment and first_payment > 0:
        payment_id = str(uuid.uuid4())
        payment_dict = {
            "id": payment_id,
            "user_id": client_id,
            "client_id": client_id,
            "amount": first_payment,
            "currency": "CFA",
            "payment_method": "Virement bancaire",
            "description": "Premier versement pour devenir client",
            "status": "confirmed",
            "invoice_number": f"ALO-{datetime.now(timezone.utc).strftime('%Y%m%d')}-{uuid.uuid4().hex[:8].upper()}",
            "created_at": datetime.now(timezone.utc).isoformat(),
            "confirmed_at": datetime.now(timezone.utc).isoformat(),
            "confirmed_by": current_user["id"]
        }
        await db.payments.insert_one(payment_dict)
    
    # Mettre à jour le statut du prospect
    await db.contact_messages.update_one(
        {"id": message_id},
        {
            "$set": {
                "status": ContactStatus.CONVERTED_CLIENT,
                "client_id": client_id,
                "updated_at": datetime.now(timezone.utc).isoformat()
            }
        }
    )
    
    # Envoyer email au nouveau client avec ses identifiants
    if EMAIL_SERVICE_AVAILABLE:
        try:
            email_sent = await send_user_welcome_email({
                "email": prospect["email"],
                "full_name": prospect["name"],
                "role": "CLIENT",
                "login_email": prospect["email"],
                "default_password": temp_password
            })
            if email_sent:
                logger.info(f"Email de bienvenue envoyé au nouveau client {prospect['email']}")
        except Exception as e:
            logger.error(f"Erreur envoi email au client {prospect['email']}: {e}")
    
    # Notifier le client (dans l'app)
    await create_notification(
        user_id=client_id,
        title="🎉 Bienvenue chez ALORIA AGENCY!",
        message=f"Votre dossier d'immigration pour {country} - {visa_type} a été créé. Consultez votre espace client.",
        type="client_created"
    )
    
    # Log activity
    await log_user_activity(
        user_id=current_user["id"],
        action="prospect_converted_to_client",
        details={
            "prospect_id": message_id,
            "client_id": client_id,
            "client_name": prospect["name"],
            "first_payment": first_payment
        }
    )
    
    return {
        "message": "Prospect converti en client avec succès",
        "client_id": client_id,
        "case_id": case_id,
        "login_email": prospect["email"],
        "temporary_password": temp_password
    }

# Activity Logs
@api_router.get("/activities", response_model=List[ActivityLogResponse])
async def get_activity_logs(
    limit: int = 50,
    user_id: Optional[str] = None,
    action: Optional[str] = None,
    current_user: dict = Depends(get_current_user)
):
    """Obtenir l'historique des activités (SuperAdmin/Manager)"""
    if current_user["role"] not in ["SUPERADMIN", "MANAGER"]:
        raise HTTPException(status_code=403, detail="Accès refusé")
    
    query = {}
    if user_id:
        query["user_id"] = user_id
    if action:
        query["action"] = {"$regex": action, "$options": "i"}
    
    activities = await db.activity_logs.find(query, {"_id": 0}).sort("timestamp", -1).limit(limit).to_list(limit)
    return [ActivityLogResponse(**activity) for activity in activities]

# Company Information
@api_router.get("/company-info", response_model=CompanyInfo)
async def get_company_info():
    """Obtenir les informations de l'entreprise (API publique)"""
    return CompanyInfo(**COMPANY_DATA)

# Search Enhancement
@api_router.get("/search/global")
async def global_search(
    q: str,
    category: str = "all",
    limit: int = 10,
    current_user: dict = Depends(get_current_user)
):
    """Recherche globale intelligente"""
    if len(q.strip()) < 2:
        return []
    
    results = []
    query_regex = {"$regex": q, "$options": "i"}
    
    # Recherche dans les clients
    if category in ["all", "clients"]:
        clients_query = {}
        if current_user["role"] == "EMPLOYEE":
            clients_query["assigned_employee_id"] = current_user["id"]
        
        clients_query["$or"] = [
            {"country": query_regex},
            {"visa_type": query_regex},
            {"current_status": query_regex}
        ]
        
        clients = await db.clients.find(clients_query, {"_id": 0}).limit(limit//3).to_list(limit//3)
        
        for client in clients:
            user = await db.users.find_one({"id": client["user_id"]})
            if user and q.lower() in user["full_name"].lower():
                results.append({
                    "id": client["id"],
                    "title": user["full_name"],
                    "description": f"{client['country']} - {client['visa_type']} - {client['current_status']}",
                    "category": "clients",
                    "url": f"/clients/{client['id']}"
                })
    
    # Recherche dans les dossiers
    if category in ["all", "cases"]:
        cases = await db.cases.find({
            "$or": [
                {"country": query_regex},
                {"visa_type": query_regex},
                {"status": query_regex}
            ]
        }, {"_id": 0}).limit(limit//3).to_list(limit//3)
        
        for case in cases:
            client = await db.clients.find_one({"id": case["client_id"]})
            if client:
                user = await db.users.find_one({"id": client["user_id"]})
                client_name = user["full_name"] if user else "Client inconnu"
                results.append({
                    "id": case["id"],
                    "title": f"Dossier {client_name}",
                    "description": f"{case['country']} - {case['visa_type']} - Étape {case['current_step_index']}",
                    "category": "cases",
                    "url": f"/cases/{case['id']}"
                })
    
    # Recherche dans les utilisateurs (Manager/SuperAdmin seulement)
    if category in ["all", "users"] and current_user["role"] in ["MANAGER", "SUPERADMIN"]:
        users = await db.users.find({
            "$or": [
                {"full_name": query_regex},
                {"email": query_regex},
                {"role": query_regex}
            ],
            "role": {"$ne": "CLIENT"}  # Exclure les clients de la recherche utilisateurs
        }, {"_id": 0}).limit(limit//3).to_list(limit//3)
        
        for user in users:
            results.append({
                "id": user["id"],
                "title": user["full_name"],
                "description": f"{user['role']} - {user['email']}",
                "category": "users",
                "url": f"/users/{user['id']}"
            })
    
    # Recherche dans les visiteurs (Employee/Manager)
    if category in ["all", "visitors"] and current_user["role"] in ["EMPLOYEE", "MANAGER"]:
        visitors = await db.visitors.find({
            "$or": [
                {"name": query_regex},
                {"company": query_regex},
                {"purpose": query_regex}
            ]
        }, {"_id": 0}).limit(limit//3).to_list(limit//3)
        
        for visitor in visitors:
            results.append({
                "id": visitor["id"],
                "title": visitor["name"],
                "description": f"{visitor.get('company', 'Particulier')} - {visitor['purpose']}",
                "category": "visitors",
                "url": f"/visitors/{visitor['id']}"
            })
    
    # Trier par pertinence (simple)
    results.sort(key=lambda x: q.lower() in x["title"].lower(), reverse=True)
    
    return results[:limit]

# Sequential Case Progression Validation
@api_router.patch("/cases/{case_id}/progress", response_model=CaseResponse)
async def update_case_progress_sequential(
    case_id: str,
    progress_data: WorkflowStepUpdate,
    current_user: dict = Depends(get_current_user)
):
    """Mettre à jour la progression d'un dossier avec validation séquentielle (Manager seulement)"""
    if current_user["role"] != "MANAGER":
        raise HTTPException(status_code=403, detail="Seuls les gestionnaires peuvent modifier la progression")
    
    case = await db.cases.find_one({"id": case_id})
    if not case:
        raise HTTPException(status_code=404, detail="Dossier non trouvé")
    
    current_step = case.get("current_step_index", 0)
    new_step = progress_data.step_index
    
    # Validation séquentielle : ne peut avancer que d'une étape à la fois
    if new_step > current_step + 1:
        raise HTTPException(
            status_code=400, 
            detail=f"Progression séquentielle obligatoire. Vous devez d'abord valider l'étape {current_step + 1}"
        )
    
    # Ne peut pas reculer de plus d'une étape
    if new_step < current_step - 1:
        raise HTTPException(
            status_code=400,
            detail=f"Vous ne pouvez pas revenir plus d'une étape en arrière"
        )
    
    # Mise à jour autorisée
    total_steps = len(case.get("workflow_steps", []))
    progress_percentage = (new_step / total_steps * 100) if total_steps > 0 else 0
    
    update_dict = {
        "current_step_index": new_step,
        "updated_at": datetime.now(timezone.utc).isoformat()
    }
    
    if progress_data.status:
        update_dict["status"] = progress_data.status
    if progress_data.notes:
        update_dict["notes"] = progress_data.notes
    
    await db.cases.update_one({"id": case_id}, {"$set": update_dict})
    
    # Mettre à jour le client
    await db.clients.update_one(
        {"id": case["client_id"]},
        {"$set": {
            "current_step": new_step,
            "progress_percentage": progress_percentage,
            "updated_at": datetime.now(timezone.utc).isoformat()
        }}
    )
    
    # Log de l'activité
    await log_user_activity(
        user_id=current_user["id"],
        action="case_progress_updated",
        details={
            "case_id": case_id,
            "previous_step": current_step,
            "new_step": new_step,
            "progress_percentage": progress_percentage
        }
    )
    
    # Obtenir le dossier mis à jour
    updated_case = await db.cases.find_one({"id": case_id}, {"_id": 0})
    client = await db.clients.find_one({"id": case["client_id"]})
    if client:
        user = await db.users.find_one({"id": client["user_id"]})
        updated_case["client_name"] = user["full_name"] if user else "Client inconnu"
    
    return CaseResponse(**updated_case)

# Include router
app.include_router(api_router)

app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=os.environ.get('CORS_ORIGINS', '*').split(','),
    allow_methods=["*"],
    allow_headers=["*"],
)

# Automated Task: Check 48h consultation alerts
async def auto_check_48h_alerts():
    """Tâche automatique qui vérifie les prospects potentiels non convertis depuis >48h"""
    try:
        logger.info("🕐 Running automated 48h consultation alerts check...")
        
        now = datetime.now(timezone.utc)
        hours_48_ago = now - timedelta(hours=48)
        
        # Chercher prospects potentiels non convertis depuis >48h
        query = {
            "status": ContactStatus.IN_CONSULTATION,
            "is_potential_client": True,
            "potential_level": "OUI",
            "consultation_completed_at": {"$lt": hours_48_ago.isoformat()},
            "alert_48h_sent": {"$ne": True}  # Pas encore alerté
        }
        
        prospects = await db.contact_messages.find(query).to_list(100)
        alerts_sent = 0
        
        for prospect in prospects:
            if prospect.get("assigned_to"):
                # Créer notification rappel
                await create_notification(
                    user_id=prospect["assigned_to"],
                    title="⏰ RAPPEL URGENT - 48H Dépassées",
                    message=f"🚨 {prospect['name']} : Prospect potentiel client non converti depuis 48h. Action requise immédiatement !",
                    type="urgent_followup_48h",
                    related_id=prospect["id"]
                )
                alerts_sent += 1
                
                # Marquer alerte envoyée
                await db.contact_messages.update_one(
                    {"id": prospect["id"]},
                    {"$set": {"alert_48h_sent": True, "alert_48h_sent_at": now.isoformat()}}
                )
        
        logger.info(f"✅ 48h check complete: {alerts_sent} alerts sent for {len(prospects)} prospects")
        
    except Exception as e:
        logger.error(f"❌ Error in auto_check_48h_alerts: {e}")

# Setup startup event
@app.on_event("startup")
async def startup_scheduler():
    """Démarrer le scheduler pour les tâches automatiques"""
    # Ajouter tâche: Vérifier 48h toutes les heures
    scheduler.add_job(
        auto_check_48h_alerts,
        CronTrigger(hour='*'),  # Toutes les heures
        id='check_48h_alerts',
        name='Check 48h consultation alerts',
        replace_existing=True
    )
    scheduler.start()
    logger.info("✅ Scheduler started - 48h alerts will be checked every hour")

# Setup shutdown event
@app.on_event("shutdown")
async def shutdown_db_client():
    scheduler.shutdown()
    client.close()

# Mount Socket.IO sur un path spécifique pour ne pas écraser les routes API
# Créer l'app Socket.IO comme app séparée
socket_app = socketio.ASGIApp(sio)

# Monter socket.io sur /socket.io
from starlette.routing import Mount
app.mount("/socket.io", socket_app)

# L'app FastAPI reste l'app principale exportée pour uvicorn
