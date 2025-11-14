"""
Service de gestion des utilisateurs - ALORIA AGENCY

Ce service centralise TOUTE la logique de création et gestion des utilisateurs.
Utilisé pour TOUS les rôles: CLIENT, EMPLOYEE, MANAGER, CONSULTANT, SUPERADMIN
"""

import uuid
import logging
from datetime import datetime, timezone
from typing import Dict, Optional
from passlib.context import CryptContext

logger = logging.getLogger(__name__)
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Hiérarchie des rôles - qui peut créer qui
ROLE_HIERARCHY = {
    "SUPERADMIN": ["MANAGER", "EMPLOYEE", "CONSULTANT"],
    "MANAGER": ["EMPLOYEE", "CLIENT"],
    "EMPLOYEE": ["CLIENT"],
    "CONSULTANT": [],
    "CLIENT": []
}


async def create_user_account(
    db,
    email: str,
    full_name: str,
    phone: str,
    role: str,
    created_by_id: str,
    password: str = None,
    additional_fields: Dict = None
) -> Dict:
    """
    Fonction UNIVERSELLE pour créer un compte utilisateur.
    
    Cette fonction est utilisée pour créer N'IMPORTE QUEL type d'utilisateur:
    - CLIENT
    - EMPLOYEE
    - MANAGER
    - CONSULTANT
    - SUPERADMIN
    
    Args:
        db: Instance de la base de données MongoDB
        email: Email de l'utilisateur
        full_name: Nom complet
        phone: Numéro de téléphone
        role: Rôle de l'utilisateur (CLIENT, EMPLOYEE, etc.)
        created_by_id: ID de l'utilisateur créateur
        password: Mot de passe (si None, un mot de passe temporaire sera généré)
        additional_fields: Champs supplémentaires optionnels
    
    Returns:
        Dict contenant:
        - user_id: ID du nouvel utilisateur
        - email: Email de l'utilisateur
        - temporary_password: Mot de passe temporaire généré
        - created_at: Date de création
    
    Raises:
        HTTPException: Si l'email existe déjà
    """
    from fastapi import HTTPException
    
    # 1. Vérifier si l'utilisateur existe déjà
    existing_user = await db.users.find_one({"email": email})
    if existing_user:
        raise HTTPException(
            status_code=400,
            detail=f"Un utilisateur avec l'email {email} existe déjà"
        )
    
    # 2. Générer ou utiliser le mot de passe fourni
    if password is None:
        from .credentials_service import generate_temporary_password
        temp_password = generate_temporary_password()
    else:
        temp_password = password
    
    # 3. Hasher le mot de passe
    hashed_password = pwd_context.hash(temp_password)
    
    # 4. Créer l'enregistrement utilisateur
    user_id = str(uuid.uuid4())
    user_dict = {
        "id": user_id,
        "email": email,
        "password": hashed_password,
        "full_name": full_name,
        "phone": phone,
        "role": role,
        "is_active": True,
        "created_at": datetime.now(timezone.utc).isoformat(),
        "created_by": created_by_id,
        "password_changed": False  # Pour forcer le changement au premier login
    }
    
    # Ajouter les champs supplémentaires si fournis
    if additional_fields:
        user_dict.update(additional_fields)
    
    # 5. Insérer dans la base de données
    await db.users.insert_one(user_dict)
    
    logger.info(f"Utilisateur créé avec succès: {email} (rôle: {role}, ID: {user_id})")
    
    # 6. Retourner les informations
    return {
        "user_id": user_id,
        "email": email,
        "full_name": full_name,
        "phone": phone,
        "role": role,
        "temporary_password": temp_password,
        "created_at": user_dict["created_at"]
    }


def verify_user_permissions(current_user_role: str, target_role: str) -> bool:
    """
    Vérifie si un utilisateur a la permission de créer un autre rôle.
    
    Hiérarchie:
    - SUPERADMIN peut créer: MANAGER, EMPLOYEE, CONSULTANT
    - MANAGER peut créer: EMPLOYEE, CLIENT
    - EMPLOYEE peut créer: CLIENT
    - CONSULTANT ne peut créer personne
    - CLIENT ne peut créer personne
    
    Args:
        current_user_role: Rôle de l'utilisateur actuel
        target_role: Rôle que l'on souhaite créer
    
    Returns:
        bool: True si la permission est accordée, False sinon
    """
    allowed_roles = ROLE_HIERARCHY.get(current_user_role, [])
    return target_role in allowed_roles


async def get_user_by_id(db, user_id: str) -> Optional[Dict]:
    """
    Récupère un utilisateur par son ID.
    
    Args:
        db: Instance de la base de données
        user_id: ID de l'utilisateur
    
    Returns:
        Dict contenant les informations de l'utilisateur ou None si non trouvé
    """
    user = await db.users.find_one({"id": user_id})
    return user


async def get_user_by_email(db, email: str) -> Optional[Dict]:
    """
    Récupère un utilisateur par son email.
    
    Args:
        db: Instance de la base de données
        email: Email de l'utilisateur
    
    Returns:
        Dict contenant les informations de l'utilisateur ou None si non trouvé
    """
    user = await db.users.find_one({"email": email})
    return user


async def deactivate_user(db, user_id: str) -> bool:
    """
    Désactive un utilisateur.
    
    Args:
        db: Instance de la base de données
        user_id: ID de l'utilisateur à désactiver
    
    Returns:
        bool: True si la désactivation a réussi
    """
    result = await db.users.update_one(
        {"id": user_id},
        {"$set": {"is_active": False, "deactivated_at": datetime.now(timezone.utc).isoformat()}}
    )
    return result.modified_count > 0


async def log_user_activity(
    db,
    user_id: str,
    action: str,
    details: Dict = None,
    ip_address: str = None
):
    """
    Enregistre l'activité utilisateur pour le monitoring SuperAdmin.
    
    Args:
        db: Instance de la base de données
        user_id: ID de l'utilisateur
        action: Action effectuée (ex: 'client_created', 'login', etc.)
        details: Détails supplémentaires de l'action
        ip_address: Adresse IP de l'utilisateur
    """
    try:
        # Gérer les ID spéciaux
        if user_id == "system":
            user_name = "System"
            user_role = "SYSTEM"
        elif user_id == "public":
            user_name = "Visiteur Public"
            user_role = "PUBLIC"
        else:
            user = await get_user_by_id(db, user_id)
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
        logger.info(f"Activité enregistrée: {action} par {user_name} ({user_role})")
    except Exception as e:
        logger.error(f"Erreur lors de l'enregistrement de l'activité: {e}")
