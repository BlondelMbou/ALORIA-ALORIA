"""
Service de génération de credentials - ALORIA AGENCY

Ce service centralise la génération de mots de passe temporaires
et la création de réponses uniformes avec credentials pour les popups.
"""

import random
import string
import logging
from typing import Dict, Optional

logger = logging.getLogger(__name__)


def generate_temporary_password(length: int = 12) -> str:
    """
    Génère un mot de passe temporaire sécurisé.
    
    Le mot de passe contient:
    - Des lettres minuscules
    - Des lettres majuscules
    - Des chiffres
    - Des caractères spéciaux
    
    Args:
        length: Longueur du mot de passe (défaut: 12)
    
    Returns:
        str: Mot de passe temporaire généré
    """
    # Définir les caractères disponibles
    lowercase = string.ascii_lowercase
    uppercase = string.ascii_uppercase
    digits = string.digits
    special_chars = "!@#$%^&*"
    
    # Garantir au moins un caractère de chaque type
    password_chars = [
        random.choice(lowercase),
        random.choice(uppercase),
        random.choice(digits),
        random.choice(special_chars)
    ]
    
    # Compléter avec des caractères aléatoires
    all_chars = lowercase + uppercase + digits + special_chars
    password_chars += [random.choice(all_chars) for _ in range(length - 4)]
    
    # Mélanger les caractères
    random.shuffle(password_chars)
    
    password = ''.join(password_chars)
    logger.info(f"Mot de passe temporaire généré (longueur: {length})")
    
    return password


def generate_credentials_response(
    user_id: str,
    email: str,
    full_name: str,
    role: str,
    temporary_password: str,
    additional_info: Dict = None
) -> Dict:
    """
    Génère la réponse standardisée avec credentials pour affichage popup.
    
    Format UNIFORME pour TOUS les rôles (CLIENT, EMPLOYEE, MANAGER, CONSULTANT).
    
    Args:
        user_id: ID de l'utilisateur créé
        email: Email de connexion
        full_name: Nom complet
        role: Rôle de l'utilisateur
        temporary_password: Mot de passe temporaire
        additional_info: Informations supplémentaires (ex: pour client: case_id, workflow)
    
    Returns:
        Dict au format standardisé pour popup:
        {
            "user_id": str,
            "email": str,
            "temporary_password": str,
            "full_name": str,
            "role": str,
            "login_url": str,
            "must_change_password": bool,
            "additional_info": dict
        }
    """
    credentials = {
        "user_id": user_id,
        "email": email,
        "login_email": email,  # Alias pour compatibilité
        "temporary_password": temporary_password,
        "default_password": temporary_password,  # Alias pour compatibilité
        "full_name": full_name,
        "role": role,
        "login_url": "/login",
        "must_change_password": True,
        "created_at": None  # Sera rempli par le service appelant
    }
    
    # Ajouter les informations supplémentaires si fournies
    if additional_info:
        credentials["additional_info"] = additional_info
        
        # Pour les clients, ajouter des champs spécifiques
        if role == "CLIENT" and additional_info:
            if "case_id" in additional_info:
                credentials["case_id"] = additional_info["case_id"]
            if "workflow_steps" in additional_info:
                credentials["workflow_steps"] = additional_info["workflow_steps"]
            if "country" in additional_info:
                credentials["country"] = additional_info["country"]
            if "visa_type" in additional_info:
                credentials["visa_type"] = additional_info["visa_type"]
    
    logger.info(f"Credentials générés pour {role}: {email}")
    return credentials


def format_credentials_for_display(credentials: Dict) -> str:
    """
    Formate les credentials pour affichage lisible (email, logs, etc.).
    
    Args:
        credentials: Dict des credentials
    
    Returns:
        str: Texte formaté
    """
    text = f"""
===========================================
🎉 NOUVEAU COMPTE CRÉÉ - ALORIA AGENCY
===========================================

Nom: {credentials['full_name']}
Rôle: {credentials['role']}

📧 EMAIL DE CONNEXION:
{credentials['email']}

🔐 MOT DE PASSE TEMPORAIRE:
{credentials['temporary_password']}

⚠️  IMPORTANT:
Ce mot de passe est temporaire.
Vous devrez le changer lors de votre première connexion.

🌐 URL DE CONNEXION:
{credentials.get('login_url', '/login')}

===========================================
    """
    
    # Ajouter informations spécifiques pour clients
    if credentials['role'] == 'CLIENT' and 'additional_info' in credentials:
        info = credentials['additional_info']
        if 'case_id' in info:
            text += f"\n📁 NUMÉRO DE DOSSIER: {info['case_id']}"
        if 'country' in info and 'visa_type' in info:
            text += f"\n🌍 DESTINATION: {info['country']} - {info['visa_type']}"
    
    text += "\n===========================================\n"
    
    return text
