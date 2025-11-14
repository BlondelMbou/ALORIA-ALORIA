"""
Service de notifications - ALORIA AGENCY

Ce service centralise l'envoi de TOUTES les notifications lors de la création d'utilisateurs.
Garantit que toutes les parties prenantes sont notifiées de manière cohérente.
"""

import uuid
import logging
from datetime import datetime, timezone
from typing import Dict, Optional

logger = logging.getLogger(__name__)

# Import du service d'e-mails (si disponible)
try:
    from email_service import send_user_welcome_email
    EMAIL_SERVICE_AVAILABLE = True
except ImportError:
    EMAIL_SERVICE_AVAILABLE = False
    logger.warning("Service d'e-mails non disponible")


async def create_notification(
    db,
    user_id: str,
    title: str,
    message: str,
    notification_type: str = "info",
    related_id: str = None
):
    """
    Crée une notification dans la base de données.
    
    Args:
        db: Instance de la base de données
        user_id: ID de l'utilisateur destinataire
        title: Titre de la notification
        message: Message de la notification
        notification_type: Type de notification
        related_id: ID de l'entité liée (optionnel)
    """
    notification = {
        "id": str(uuid.uuid4()),
        "user_id": user_id,
        "title": title,
        "message": message,
        "type": notification_type,
        "related_id": related_id,
        "read": False,
        "created_at": datetime.now(timezone.utc).isoformat()
    }
    await db.notifications.insert_one(notification)
    logger.info(f"Notification créée pour {user_id}: {title}")


async def send_creation_notifications(
    db,
    created_user_id: str,
    created_user_role: str,
    created_user_name: str,
    created_user_email: str,
    created_by_id: str,
    created_by_role: str,
    created_by_name: str,
    additional_context: Dict = None
):
    """
    Envoie TOUTES les notifications nécessaires lors de la création d'un utilisateur.
    
    NOTIFICATIONS ENVOYÉES SELON LE RÔLE:
    
    - CLIENT créé:
      → Notifier: le client lui-même, l'employé assigné, le manager, les superadmins
    
    - EMPLOYEE créé:
      → Notifier: l'employé lui-même, le manager créateur, les superadmins
    
    - MANAGER créé:
      → Notifier: le manager lui-même, les superadmins
    
    - CONSULTANT créé:
      → Notifier: le consultant lui-même, les superadmins
    
    Args:
        db: Instance de la base de données
        created_user_id: ID de l'utilisateur créé
        created_user_role: Rôle de l'utilisateur créé
        created_user_name: Nom de l'utilisateur créé
        created_user_email: Email de l'utilisateur créé
        created_by_id: ID de l'utilisateur créateur
        created_by_role: Rôle de l'utilisateur créateur
        created_by_name: Nom de l'utilisateur créateur
        additional_context: Contexte supplémentaire (pays, visa_type, etc.)
    """
    context = additional_context or {}
    
    # 1. NOTIFICATION À L'UTILISATEUR CRÉÉ (bienvenue)
    await create_notification(
        db=db,
        user_id=created_user_id,
        title=f"🎉 Bienvenue chez ALORIA AGENCY!",
        message=f"Votre compte {created_user_role} a été créé avec succès. Vous pouvez maintenant accéder à votre espace personnel.",
        notification_type="user_created"
    )
    
    # 2. NOTIFICATIONS SPÉCIFIQUES SELON LE RÔLE
    if created_user_role == "CLIENT":
        await send_client_creation_notifications(
            db=db,
            client_id=created_user_id,
            client_name=created_user_name,
            client_email=created_user_email,
            created_by_id=created_by_id,
            created_by_name=created_by_name,
            context=context
        )
    
    elif created_user_role == "EMPLOYEE":
        await send_employee_creation_notifications(
            db=db,
            employee_id=created_user_id,
            employee_name=created_user_name,
            created_by_id=created_by_id,
            created_by_name=created_by_name,
            created_by_role=created_by_role
        )
    
    elif created_user_role == "MANAGER":
        await send_manager_creation_notifications(
            db=db,
            manager_id=created_user_id,
            manager_name=created_user_name,
            created_by_id=created_by_id,
            created_by_name=created_by_name
        )
    
    elif created_user_role == "CONSULTANT":
        await send_consultant_creation_notifications(
            db=db,
            consultant_id=created_user_id,
            consultant_name=created_user_name,
            created_by_id=created_by_id,
            created_by_name=created_by_name
        )
    
    logger.info(f"Toutes les notifications envoyées pour la création de {created_user_role}: {created_user_name}")


async def send_client_creation_notifications(
    db,
    client_id: str,
    client_name: str,
    client_email: str,
    created_by_id: str,
    created_by_name: str,
    context: Dict
):
    """Notifications pour création de client"""
    country = context.get("country", "")
    visa_type = context.get("visa_type", "")
    assigned_employee_id = context.get("assigned_employee_id")
    
    # Notifier l'employé assigné
    if assigned_employee_id and assigned_employee_id != created_by_id:
        await create_notification(
            db=db,
            user_id=assigned_employee_id,
            title="👤 Nouveau client assigné",
            message=f"Un nouveau client vous a été assigné: {client_name} ({country} - {visa_type})",
            notification_type="client_assigned",
            related_id=client_id
        )
    
    # Notifier le créateur si c'est un employé
    if created_by_id != client_id:
        await create_notification(
            db=db,
            user_id=created_by_id,
            title="✅ Client créé avec succès",
            message=f"Vous avez créé le client {client_name} ({country} - {visa_type})",
            notification_type="client_created_confirmation",
            related_id=client_id
        )
    
    # Notifier les superadmins
    await notify_superadmins(
        db=db,
        title="👤 Nouveau client créé",
        message=f"{created_by_name} a créé un nouveau client: {client_name} ({country} - {visa_type})",
        notification_type="admin_client_created",
        related_id=client_id
    )


async def send_employee_creation_notifications(
    db,
    employee_id: str,
    employee_name: str,
    created_by_id: str,
    created_by_name: str,
    created_by_role: str
):
    """Notifications pour création d'employé"""
    # Notifier le créateur (manager ou superadmin)
    await create_notification(
        db=db,
        user_id=created_by_id,
        title="✅ Employé créé avec succès",
        message=f"Vous avez créé l'employé: {employee_name}",
        notification_type="employee_created_confirmation",
        related_id=employee_id
    )
    
    # Notifier les superadmins
    await notify_superadmins(
        db=db,
        title="👥 Nouvel employé créé",
        message=f"{created_by_name} ({created_by_role}) a créé un nouvel employé: {employee_name}",
        notification_type="admin_employee_created",
        related_id=employee_id
    )


async def send_manager_creation_notifications(
    db,
    manager_id: str,
    manager_name: str,
    created_by_id: str,
    created_by_name: str
):
    """Notifications pour création de manager"""
    # Notifier le superadmin créateur
    await create_notification(
        db=db,
        user_id=created_by_id,
        title="✅ Manager créé avec succès",
        message=f"Vous avez créé le manager: {manager_name}",
        notification_type="manager_created_confirmation",
        related_id=manager_id
    )
    
    # Notifier tous les superadmins
    await notify_superadmins(
        db=db,
        title="👔 Nouveau manager créé",
        message=f"{created_by_name} a créé un nouveau manager: {manager_name}",
        notification_type="admin_manager_created",
        related_id=manager_id
    )


async def send_consultant_creation_notifications(
    db,
    consultant_id: str,
    consultant_name: str,
    created_by_id: str,
    created_by_name: str
):
    """Notifications pour création de consultant"""
    # Notifier le superadmin créateur
    await create_notification(
        db=db,
        user_id=created_by_id,
        title="✅ Consultant créé avec succès",
        message=f"Vous avez créé le consultant: {consultant_name}",
        notification_type="consultant_created_confirmation",
        related_id=consultant_id
    )
    
    # Notifier tous les superadmins
    await notify_superadmins(
        db=db,
        title="💼 Nouveau consultant créé",
        message=f"{created_by_name} a créé un nouveau consultant: {consultant_name}",
        notification_type="admin_consultant_created",
        related_id=consultant_id
    )


async def notify_superadmins(
    db,
    title: str,
    message: str,
    notification_type: str,
    related_id: str = None
):
    """Envoie une notification à tous les superadmins actifs"""
    superadmins = await db.users.find({"role": "SUPERADMIN", "is_active": True}).to_list(20)
    
    for superadmin in superadmins:
        await create_notification(
            db=db,
            user_id=superadmin["id"],
            title=title,
            message=message,
            notification_type=notification_type,
            related_id=related_id
        )
    
    logger.info(f"Notification envoyée à {len(superadmins)} superadmin(s)")


async def send_welcome_email_notification(
    email: str,
    full_name: str,
    role: str,
    temporary_password: str
) -> bool:
    """
    Envoie l'email de bienvenue avec credentials.
    
    Args:
        email: Email du destinataire
        full_name: Nom complet
        role: Rôle de l'utilisateur
        temporary_password: Mot de passe temporaire
    
    Returns:
        bool: True si l'email a été envoyé avec succès
    """
    if not EMAIL_SERVICE_AVAILABLE:
        logger.warning("Service d'e-mails non disponible - email non envoyé")
        return False
    
    try:
        user_data = {
            "email": email,
            "full_name": full_name,
            "role": role,
            "login_email": email,
            "default_password": temporary_password
        }
        
        email_sent = await send_user_welcome_email(user_data)
        
        if email_sent:
            logger.info(f"Email de bienvenue envoyé à {email} ({role})")
        else:
            logger.warning(f"Échec envoi email de bienvenue à {email}")
        
        return email_sent
    
    except Exception as e:
        logger.error(f"Erreur envoi email à {email}: {e}")
        return False
