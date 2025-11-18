"""
Service de gestion des clients - ALORIA AGENCY

Ce service centralise TOUTE la logique de création et gestion des profils clients.
Garantit que chaque client créé aura:
- Un profil dans la collection 'clients'
- Un dossier (case) avec workflow approprié
- Un dashboard accessible immédiatement
"""

import uuid
import logging
from datetime import datetime, timezone
from typing import Dict, Optional, List

logger = logging.getLogger(__name__)

# Workflows par pays et type de visa (importé depuis server.py)
WORKFLOWS = {}

# Mapping des noms de visa anglais → français
VISA_TYPE_MAPPING = {
    # Canada
    "Work Permit": "Permis de travail",
    "Study Permit": "Permis d'études",
    "Permanent Residence (Express Entry)": "Résidence permanente (Entrée express)",
    # France
    "Work Permit (Talent Passport)": "Permis de travail (Passeport Talent)",
    "Student Visa": "Visa étudiant",
    "Family Reunification": "Regroupement familial"
}


def set_workflows(workflows: Dict):
    """Initialise les workflows depuis server.py"""
    global WORKFLOWS
    WORKFLOWS = workflows


def normalize_visa_type(visa_type: str) -> str:
    """
    Normalise le type de visa en convertissant les noms anglais en français.
    
    Args:
        visa_type: Type de visa (peut être en anglais ou français)
    
    Returns:
        str: Type de visa en français (clé pour WORKFLOWS)
    """
    # Si déjà en français, retourner tel quel
    if visa_type in ["Permis de travail", "Permis d'études", "Résidence permanente (Entrée express)",
                     "Permis de travail (Passeport Talent)", "Visa étudiant", "Regroupement familial"]:
        return visa_type
    
    # Sinon, chercher la traduction
    return VISA_TYPE_MAPPING.get(visa_type, visa_type)


async def create_client_profile(
    db,
    user_id: str,
    email: str,
    full_name: str,
    phone: str,
    country: str,
    visa_type: str,
    assigned_employee_id: str,
    created_by_id: str,
    first_payment: float = 0,
    payment_method: str = None,
    additional_data: Dict = None
) -> Dict:
    """
    Fonction UNIVERSELLE pour créer un profil client complet.
    
    Crée AUTOMATIQUEMENT et GARANTIT:
    1. Profil client dans collection 'clients'
    2. Dossier (case) avec workflow approprié (Canada/France)
    3. Premier paiement enregistré si fourni
    4. Dashboard client accessible immédiatement
    
    Args:
        db: Instance de la base de données
        user_id: ID de l'utilisateur client
        email: Email du client
        full_name: Nom complet du client
        phone: Téléphone du client
        country: Pays de destination (Canada, France)
        visa_type: Type de visa
        assigned_employee_id: ID de l'employé assigné
        created_by_id: ID de l'utilisateur créateur
        first_payment: Montant du premier paiement (optionnel)
        payment_method: Méthode de paiement (optionnel)
        additional_data: Données supplémentaires
    
    Returns:
        Dict contenant:
        - client_id: ID du profil client
        - case_id: ID du dossier créé
        - workflow_steps: Liste des étapes du workflow
        - dashboard_ready: bool confirmant que le dashboard est accessible
        - payment_id: ID du paiement si créé
    """
    from .user_service import get_user_by_id
    
    # 1. Créer le profil client dans la collection 'clients'
    client_id = str(uuid.uuid4())
    
    # Récupérer le nom de l'employé assigné
    assigned_employee_name = None
    if assigned_employee_id:
        employee = await get_user_by_id(db, assigned_employee_id)
        if employee:
            assigned_employee_name = employee["full_name"]
    
    client_dict = {
        "id": client_id,
        "user_id": user_id,
        "full_name": full_name,
        "email": email,
        "phone": phone,
        "assigned_employee_id": assigned_employee_id,
        "assigned_employee_name": assigned_employee_name,
        "country": country,
        "visa_type": visa_type,
        "current_status": "Nouveau",
        "current_step": 0,
        "progress_percentage": 0.0,
        "status": "active",
        "created_at": datetime.now(timezone.utc).isoformat(),
        "updated_at": datetime.now(timezone.utc).isoformat(),
        "created_by": created_by_id
    }
    
    if additional_data:
        client_dict.update(additional_data)
    
    await db.clients.insert_one(client_dict)
    logger.info(f"Profil client créé: {client_id} ({full_name})")
    
    # 2. Normaliser le type de visa (anglais → français) et récupérer le workflow
    normalized_visa_type = normalize_visa_type(visa_type)
    workflow_steps = await get_workflow_for_client(db, country, normalized_visa_type)
    logger.info(f"Workflow récupéré pour {country} - {normalized_visa_type}: {len(workflow_steps)} étapes")
    
    # 3. Créer le dossier (case) avec workflow
    case_id = str(uuid.uuid4())
    case_dict = {
        "id": case_id,
        "client_id": user_id,  # ID de l'utilisateur pour correspondance
        "client_name": full_name,
        "client_email": email,
        "assigned_employee_id": assigned_employee_id,
        "assigned_employee_name": assigned_employee_name,
        "country": country,
        "visa_type": visa_type,
        "workflow_steps": workflow_steps,
        "current_step_index": 0,
        "status": "Nouveau",
        "progress_percentage": 0,
        "notes": additional_data.get("message", "") if additional_data else "",
        "created_at": datetime.now(timezone.utc).isoformat(),
        "updated_at": datetime.now(timezone.utc).isoformat(),
        "created_by": created_by_id
    }
    
    await db.cases.insert_one(case_dict)
    logger.info(f"Dossier (case) créé: {case_id} pour client {full_name}")
    
    # 4. Enregistrer le premier paiement si fourni
    payment_id = None
    if first_payment and first_payment > 0:
        payment_id = await record_first_payment(
            db=db,
            user_id=user_id,
            client_id=user_id,
            client_name=full_name,
            amount=first_payment,
            payment_method=payment_method or "Premier versement",
            confirmed_by=created_by_id
        )
        logger.info(f"Premier paiement enregistré: {payment_id} ({first_payment} CFA)")
    
    # 5. Vérifier que le dashboard est accessible
    dashboard_ready = await verify_client_dashboard_accessible(db, user_id)
    
    # 6. Logger l'activité
    from .user_service import log_user_activity
    await log_user_activity(
        db=db,
        user_id=created_by_id,
        action="client_created",
        details={
            "client_id": client_id,
            "client_name": full_name,
            "client_email": email,
            "country": country,
            "visa_type": visa_type,
            "assigned_employee_id": assigned_employee_id
        }
    )
    
    return {
        "client_id": client_id,
        "case_id": case_id,
        "workflow_steps": workflow_steps,
        "dashboard_ready": dashboard_ready,
        "payment_id": payment_id,
        "assigned_employee_id": assigned_employee_id,
        "assigned_employee_name": assigned_employee_name
    }


async def get_workflow_for_client(db, country: str, visa_type: str) -> List[Dict]:
    """
    Récupère le workflow approprié pour un client.
    
    Cherche d'abord dans la base de données (workflows personnalisés),
    puis utilise les workflows par défaut si non trouvé.
    
    Args:
        db: Instance de la base de données
        country: Pays de destination
        visa_type: Type de visa (doit être en français)
    
    Returns:
        List[Dict]: Liste des étapes du workflow
    """
    # Chercher workflow personnalisé dans la base
    workflows_data = await db.workflows.find_one({"country": country})
    
    if workflows_data:
        workflow_steps = workflows_data.get("workflows", {}).get(visa_type, [])
        if workflow_steps:
            logger.info(f"✅ Workflow personnalisé trouvé pour {country} - {visa_type} ({len(workflow_steps)} étapes)")
            return workflow_steps
    
    # Utiliser workflow par défaut
    workflow_steps = WORKFLOWS.get(country, {}).get(visa_type, [])
    
    if workflow_steps:
        logger.info(f"✅ Workflow par défaut trouvé pour {country} - {visa_type} ({len(workflow_steps)} étapes)")
    else:
        logger.warning(f"⚠️ AUCUN workflow trouvé pour {country} - {visa_type}. Workflows disponibles: {list(WORKFLOWS.get(country, {}).keys())}")
    
    return workflow_steps


async def record_first_payment(
    db,
    user_id: str,
    client_id: str,
    client_name: str,
    amount: float,
    payment_method: str,
    confirmed_by: str
) -> str:
    """
    Enregistre le premier paiement d'un client.
    
    Args:
        db: Instance de la base de données
        user_id: ID de l'utilisateur client
        client_id: ID du profil client
        client_name: Nom du client
        amount: Montant du paiement
        payment_method: Méthode de paiement
        confirmed_by: ID de l'utilisateur qui confirme le paiement
    
    Returns:
        str: ID du paiement créé
    """
    payment_id = str(uuid.uuid4())
    invoice_num = f"ALO-{datetime.now(timezone.utc).strftime('%Y%m%d')}-{uuid.uuid4().hex[:8].upper()}"
    
    payment_dict = {
        "id": payment_id,
        "user_id": user_id,
        "client_id": client_id,
        "client_name": client_name,
        "amount": amount,
        "currency": "CFA",
        "payment_method": payment_method,
        "description": "Premier versement pour création de dossier client",
        "status": "confirmed",
        "invoice_number": invoice_num,
        "created_at": datetime.now(timezone.utc).isoformat(),
        "declared_at": datetime.now(timezone.utc).isoformat(),
        "confirmed_at": datetime.now(timezone.utc).isoformat(),
        "confirmed_by": confirmed_by
    }
    
    await db.payment_declarations.insert_one(payment_dict)
    return payment_id


async def verify_client_dashboard_accessible(db, user_id: str) -> bool:
    """
    Vérifie que le dashboard client a tous les composants nécessaires.
    
    Vérifie la présence de:
    - Profil client dans 'clients'
    - Au moins un dossier (case) dans 'cases'
    
    Args:
        db: Instance de la base de données
        user_id: ID de l'utilisateur client
    
    Returns:
        bool: True si le dashboard est accessible
    """
    # Vérifier profil client
    client = await db.clients.find_one({"user_id": user_id})
    if not client:
        logger.warning(f"Profil client non trouvé pour user_id: {user_id}")
        return False
    
    # Vérifier case
    case = await db.cases.find_one({"client_id": user_id})
    if not case:
        logger.warning(f"Dossier (case) non trouvé pour user_id: {user_id}")
        return False
    
    logger.info(f"Dashboard client vérifié et accessible pour user_id: {user_id}")
    return True


async def get_client_dashboard_data(db, user_id: str) -> Dict:
    """
    Récupère toutes les données nécessaires pour le dashboard client.
    
    Args:
        db: Instance de la base de données
        user_id: ID de l'utilisateur client
    
    Returns:
        Dict contenant toutes les données du dashboard
    """
    # Profil client
    client = await db.clients.find_one({"user_id": user_id})
    
    # Dossier(s)
    cases = await db.cases.find({"client_id": user_id}).to_list(100)
    
    # Paiements
    payments = await db.payment_declarations.find({"user_id": user_id}).to_list(100)
    
    # Notifications
    notifications = await db.notifications.find({"user_id": user_id}).sort("created_at", -1).limit(20).to_list(20)
    
    return {
        "client": client,
        "cases": cases,
        "payments": payments,
        "notifications": notifications
    }
