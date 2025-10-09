from fastapi import FastAPI, APIRouter, HTTPException, Depends, status
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
    engineio_logger=True
)

# Create the main app
app = FastAPI()
api_router = APIRouter(prefix="/api")

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

class VisitorCreate(BaseModel):
    name: str
    company: Optional[str] = None
    purpose: VisitorPurpose
    details: Optional[str] = None  # Pour précisions si "Autre" sélectionné

class VisitorResponse(BaseModel):
    model_config = ConfigDict(extra="ignore")
    id: str
    name: str
    company: Optional[str]
    purpose: VisitorPurpose
    details: Optional[str]
    arrival_time: str
    departure_time: Optional[str]
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
    
class PaymentConfirmation(BaseModel):
    action: str  # "confirm" or "reject"
    notes: Optional[str] = None
    
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

# Workflow Templates
WORKFLOWS = {
    "Canada": {
        "Work Permit": [
            {"title": "Initial Consultation & Eligibility Check", "description": "Assess eligibility for Canadian work permit", "documents": ["Valid passport", "Educational credentials", "Resume/CV", "Job offer letter"], "duration": "3-5 days"},
            {"title": "Document Collection", "description": "Gather all required documents", "documents": ["Job offer (LMIA or LMIA-exempt)", "Educational credentials (ECA if required)", "Language test results (IELTS/CELPIP/TEF)", "Proof of work experience", "Police clearance certificate"], "duration": "2-4 weeks"},
            {"title": "IRCC Account Creation", "description": "Create secure IRCC online account", "documents": ["Valid email address", "Security questions"], "duration": "1 day"},
            {"title": "Application Form Completion", "description": "Complete IMM forms accurately", "documents": ["IMM 1295 - Work Permit Application", "IMM 5707 - Family Information", "IMM 5645 - Family Information (if applicable)"], "duration": "3-7 days"},
            {"title": "Fee Payment", "description": "Pay IRCC processing fees online", "documents": ["Work permit fee: CAD $155", "Biometrics fee: CAD $85", "Payment receipt"], "duration": "1 day"},
            {"title": "Application Submission", "description": "Submit complete application via IRCC portal", "documents": ["All completed forms", "Supporting documents", "Payment confirmation"], "duration": "1 day"},
            {"title": "Biometrics Appointment", "description": "Provide fingerprints and photo at VAC", "documents": ["Biometrics instruction letter", "Valid passport", "Appointment confirmation"], "duration": "1-3 weeks"},
            {"title": "Application Processing", "description": "IRCC reviews application", "documents": ["Additional documents if requested", "Medical exam (if requested)"], "duration": "8-12 weeks"},
            {"title": "Decision Received", "description": "Receive approval or refusal notification", "documents": ["Port of Entry Letter of Introduction", "Visa (if from visa-required country)"], "duration": "1-2 days"},
            {"title": "Work Permit Issued", "description": "Receive work permit at port of entry", "documents": ["Work permit document", "Confirmation of work authorization"], "duration": "Upon arrival"}
        ],
        "Study Permit": [
            {"title": "Initial Consultation", "description": "Assess study goals and eligibility", "documents": ["Valid passport", "Academic transcripts", "English/French test scores"], "duration": "1-3 days"},
            {"title": "Letter of Acceptance from DLI", "description": "Obtain acceptance from Designated Learning Institution", "documents": ["Letter of Acceptance", "Proof of tuition payment"], "duration": "Varies by institution"},
            {"title": "PAL/TAL Attestation Letter", "description": "Obtain Provincial/Territorial Attestation Letter", "documents": ["PAL/TAL from province", "DLI confirmation"], "duration": "2-6 weeks"},
            {"title": "Financial Documentation", "description": "Prove sufficient funds for studies", "documents": ["Bank statements (CAD $10,000 + tuition)", "GIC certificate", "Sponsor's financial proof"], "duration": "1-2 weeks"},
            {"title": "IRCC Account & Application", "description": "Create account and complete study permit application", "documents": ["IMM 1294", "Letter of explanation", "Study plan"], "duration": "3-5 days"},
            {"title": "Biometrics & Medical Exam", "description": "Complete biometrics and medical if required", "documents": ["Biometrics receipt", "Medical exam results (IMM 1017)"], "duration": "2-4 weeks"},
            {"title": "Application Processing", "description": "IRCC processes study permit", "documents": ["Additional documents if requested"], "duration": "4-12 weeks"},
            {"title": "Study Permit Decision", "description": "Receive approval or refusal", "documents": ["Port of Entry Letter", "Visa (if required)"], "duration": "1-2 days"},
            {"title": "Travel to Canada", "description": "Enter Canada and receive study permit", "documents": ["Valid passport", "POE letter", "Letter of acceptance"], "duration": "Upon arrival"},
            {"title": "Study Permit Received", "description": "Study permit issued at port of entry", "documents": ["Study permit document"], "duration": "Immediate"}
        ],
        "Permanent Residence (Express Entry)": [
            {"title": "Eligibility Assessment", "description": "Determine Express Entry program eligibility", "documents": ["Language test results", "Educational credentials", "Work experience proof"], "duration": "1-2 weeks"},
            {"title": "Express Entry Profile Creation", "description": "Create Express Entry profile and enter pool", "documents": ["ECA report", "Language test results", "Proof of funds"], "duration": "3-5 days"},
            {"title": "Invitation to Apply (ITA)", "description": "Receive ITA if CRS score is high enough", "documents": ["ITA notification"], "duration": "Varies (pool draws every 2 weeks)"},
            {"title": "Document Preparation", "description": "Gather all supporting documents", "documents": ["Police certificates", "Medical exams", "Birth certificates", "Reference letters"], "duration": "3-6 weeks"},
            {"title": "PR Application Submission", "description": "Submit complete PR application within 60 days", "documents": ["All forms and supporting documents", "Payment of fees ($1,365 CAD)"], "duration": "Within 60 days of ITA"},
            {"title": "Biometrics", "description": "Provide biometrics at VAC", "documents": ["Biometrics instruction letter"], "duration": "1-2 weeks"},
            {"title": "Application Processing", "description": "IRCC processes PR application", "documents": ["Additional documents if requested"], "duration": "6 months (standard processing)"},
            {"title": "Confirmation of PR (COPR)", "description": "Receive COPR and PR visa", "documents": ["COPR document", "PR visa in passport"], "duration": "1-2 weeks after approval"},
            {"title": "Landing in Canada", "description": "Complete landing formalities at port of entry", "documents": ["COPR", "Valid passport"], "duration": "Upon arrival"},
            {"title": "PR Card Application", "description": "Receive PR card by mail", "documents": ["PR card", "Canadian address confirmation"], "duration": "4-6 weeks"}
        ]
    },
    "France": {
        "Work Permit (Talent Permit)": [
            {"title": "Initial Consultation", "description": "Assess eligibility for French Talent Permit", "documents": ["Valid passport", "CV/Resume", "Educational qualifications"], "duration": "2-3 days"},
            {"title": "Employment Contract", "description": "Secure job offer from French employer", "documents": ["Employment contract", "Job description", "Salary details (minimum €53,836/year)"], "duration": "Varies"},
            {"title": "Work Authorization (if required)", "description": "Employer obtains work authorization", "documents": ["DIRECCTE approval", "Proof of job posting (3 weeks)"], "duration": "2-4 weeks"},
            {"title": "Document Preparation", "description": "Gather documents for visa application", "documents": ["Passport (valid 3+ months)", "Photos (3.5 x 4.5 cm)", "Proof of accommodation in France", "Health insurance", "Proof of financial means"], "duration": "1-2 weeks"},
            {"title": "France-Visas Application", "description": "Complete online application on France-Visas", "documents": ["Online application form", "Supporting documents upload"], "duration": "1-2 days"},
            {"title": "Consulate Appointment", "description": "Attend visa interview and biometrics", "documents": ["Appointment confirmation", "Original documents", "Visa fee (€99)"], "duration": "1-3 weeks wait"},
            {"title": "VLS-TS Visa Issuance", "description": "Receive long-stay visa", "documents": ["Passport with visa", "OFII form"], "duration": "2-8 weeks"},
            {"title": "Entry to France", "description": "Enter France within visa validity", "documents": ["Valid passport with visa", "Supporting documents"], "duration": "Within 3 months of visa issue"},
            {"title": "OFII Validation", "description": "Validate visa online within 3 months", "documents": ["OFII validation (€200-250)", "Medical exam appointment", "Civic integration session"], "duration": "2-4 weeks"},
            {"title": "Carte de Séjour (Residence Permit)", "description": "Receive multi-year residence permit", "documents": ["Talent Permit card (valid up to 4 years)", "OFII stamp"], "duration": "After OFII validation"}
        ],
        "Student Visa": [
            {"title": "Initial Consultation", "description": "Assess study plans and program eligibility", "documents": ["Valid passport", "Academic transcripts"], "duration": "1-2 days"},
            {"title": "University Acceptance", "description": "Obtain acceptance from French institution", "documents": ["Letter of acceptance/enrollment", "Proof of registration fees payment"], "duration": "Varies by institution"},
            {"title": "Campus France Registration", "description": "Complete Campus France procedure (if required)", "documents": ["Campus France interview", "Academic documents", "Language proficiency proof"], "duration": "2-6 weeks"},
            {"title": "Financial Proof", "description": "Demonstrate sufficient funds", "documents": ["Bank statements (€615/month)", "Scholarship letter", "Sponsor's guarantee"], "duration": "1-2 weeks"},
            {"title": "Accommodation Proof", "description": "Secure housing in France", "documents": ["Lease agreement", "University housing confirmation", "Host attestation"], "duration": "1-3 weeks"},
            {"title": "VLS-TS Application", "description": "Apply for long-stay student visa", "documents": ["France-Visas form", "Acceptance letter", "Proof of funds", "Health insurance"], "duration": "1-2 days"},
            {"title": "Consulate Appointment", "description": "Attend visa interview", "documents": ["All original documents", "Visa fee (€50 for students)", "Biometrics"], "duration": "2-4 weeks wait"},
            {"title": "Student Visa Issuance", "description": "Receive student VLS-TS", "documents": ["Passport with visa"], "duration": "2-4 weeks"},
            {"title": "Arrival & OFII Validation", "description": "Enter France and validate visa online", "documents": ["OFII validation fee (€60)", "Medical exam (if required)"], "duration": "Within 3 months of arrival"},
            {"title": "Student Residence Permit", "description": "Receive student residence permit", "documents": ["Student carte de séjour"], "duration": "After OFII validation"}
        ],
        "Family Reunification": [
            {"title": "Eligibility Check", "description": "Verify sponsor's eligibility and residence status", "documents": ["Sponsor's residence permit", "Proof of residence duration (18+ months)", "Family relationship proof"], "duration": "1-2 days"},
            {"title": "Financial Requirements", "description": "Demonstrate sufficient income", "documents": ["Tax statements", "Pay slips (stable income)", "Proof of income above minimum threshold"], "duration": "1-2 weeks"},
            {"title": "Accommodation Proof", "description": "Prove adequate housing", "documents": ["Lease or property deed", "Utility bills", "Housing certificate from mayor"], "duration": "1-2 weeks"},
            {"title": "OFII Application Submission", "description": "Submit family reunification request to OFII", "documents": ["CERFA form 11436*05", "All supporting documents", "Application fee (€225)"], "duration": "1 day"},
            {"title": "OFII Review", "description": "OFII reviews application and conducts home visit", "documents": ["Home inspection report", "Additional documents if requested"], "duration": "6-12 months"},
            {"title": "Prefecture Decision", "description": "Prefecture issues decision on application", "documents": ["Approval or refusal notification"], "duration": "After OFII approval"},
            {"title": "Visa Application (if approved)", "description": "Family members apply for visa", "documents": ["Approval certificate", "Passport", "Civil documents"], "duration": "2-4 weeks"},
            {"title": "Entry to France", "description": "Family members enter France with visa", "documents": ["Valid visa", "Supporting documents"], "duration": "Within visa validity"},
            {"title": "Residence Permit Application", "description": "Apply for residence permit at prefecture", "documents": ["All visa documents", "Photos", "OFII validation"], "duration": "2-3 months"},
            {"title": "Family Residence Permit Issued", "description": "Receive 'Vie Privée et Familiale' permit", "documents": ["Residence permit (valid 1 year, renewable)"], "duration": "After prefecture approval"}
        ]
    }
}

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

@api_router.post("/auth/login", response_model=TokenResponse)
async def login(credentials: UserLogin):
    user = await db.users.find_one({"email": credentials.email})
    if not user or not verify_password(credentials.password, user["password"]):
        raise HTTPException(status_code=401, detail="Invalid email or password")
    
    if not user.get("is_active", True):
        raise HTTPException(status_code=403, detail="Account is inactive")
    
    access_token = create_access_token({"sub": user["id"], "role": user["role"]})
    
    user_response = UserResponse(
        id=user["id"],
        email=user["email"],
        full_name=user["full_name"],
        phone=user.get("phone"),
        role=user["role"],
        is_active=user["is_active"],
        created_at=user["created_at"]
    )
    
    return TokenResponse(access_token=access_token, token_type="bearer", user=user_response)

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
    # MANAGER and EMPLOYEE can create clients
    if current_user["role"] not in ["MANAGER", "EMPLOYEE"]:
        raise HTTPException(status_code=403, detail="Seuls les gestionnaires et employés peuvent créer des clients")
        
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
        raise HTTPException(status_code=403, detail="Only managers and employees can register visitors")
    
    visitor_id = str(uuid.uuid4())
    visitor_dict = {
        "id": visitor_id,
        "name": visitor_data.name,
        "company": visitor_data.company,
        "purpose": visitor_data.purpose.value,
        "details": visitor_data.details,
        "arrival_time": datetime.now(timezone.utc).isoformat(),
        "departure_time": None,
        "registered_by": current_user["id"],
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

# Include router
app.include_router(api_router)

app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=os.environ.get('CORS_ORIGINS', '*').split(','),
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount Socket.IO at /socket.io
app.mount("/socket.io", socket_app)

@app.on_event("shutdown")
async def shutdown_db_client():
    client.close()
