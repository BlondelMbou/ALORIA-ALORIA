#!/usr/bin/env python3
"""
ALORIA AGENCY - Service d'e-mails automatiques avec SendGrid
Gestion des e-mails pour prospects, utilisateurs et clients
"""

import os
import logging
from typing import Optional, Dict, Any
from datetime import datetime
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail, To, From, Subject, HtmlContent, PlainTextContent

# Configuration du logger
logger = logging.getLogger(__name__)

class EmailDeliveryError(Exception):
    """Exception levée lors d'erreurs d'envoi d'e-mail"""
    pass

class AloriaEmailService:
    """Service d'e-mails pour ALORIA AGENCY avec SendGrid"""
    
    def __init__(self):
        self.api_key = os.getenv('SENDGRID_API_KEY')
        self.sender_email = os.getenv('SENDER_EMAIL', 'contact@aloria-agency.com')
        self.sender_name = "ALORIA AGENCY"
        
        if not self.api_key:
            raise ValueError("SENDGRID_API_KEY est requis dans les variables d'environnement")
        
        self.sg = SendGridAPIClient(self.api_key)
    
    def _send_email(self, to_email: str, subject: str, html_content: str, plain_content: Optional[str] = None) -> bool:
        """Envoyer un e-mail via SendGrid"""
        try:
            from_email = From(self.sender_email, self.sender_name)
            to = To(to_email)
            
            mail = Mail(
                from_email=from_email,
                to_emails=to,
                subject=Subject(subject),
                html_content=HtmlContent(html_content)
            )
            
            if plain_content:
                mail.plain_text_content = PlainTextContent(plain_content)
            
            response = self.sg.send(mail)
            
            if response.status_code == 202:
                logger.info(f"E-mail envoyé avec succès à {to_email}")
                return True
            else:
                logger.warning(f"Statut de réponse SendGrid inhabituel: {response.status_code}")
                return False
                
        except Exception as e:
            logger.error(f"Erreur lors de l'envoi d'e-mail à {to_email}: {str(e)}")
            raise EmailDeliveryError(f"Échec d'envoi e-mail: {str(e)}")
    
    def send_prospect_welcome_email(self, prospect_data: Dict[str, Any]) -> bool:
        """
        E-mail de bienvenue pour les prospects qui soumettent le formulaire de contact
        """
        name = prospect_data.get('name', 'Cher prospect')
        email = prospect_data.get('email')
        country = prospect_data.get('country', '')
        visa_type = prospect_data.get('visa_type', '')
        urgency = prospect_data.get('urgency_level', 'Normal')
        
        # Personnalisation selon le pays et le type de visa
        country_info = self._get_country_specific_info(country)
        visa_info = self._get_visa_specific_info(visa_type, country)
        
        subject = f"🌟 Bienvenue chez ALORIA AGENCY - Votre projet d'immigration vers {country}"
        
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <style>
                body {{ font-family: 'Arial', sans-serif; line-height: 1.6; color: #333; margin: 0; padding: 0; }}
                .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
                .header {{ background: linear-gradient(135deg, #1E293B 0%, #334155 100%); color: white; padding: 30px; text-align: center; border-radius: 10px 10px 0 0; }}
                .logo {{ font-size: 28px; font-weight: bold; margin-bottom: 10px; }}
                .content {{ background: #f8fafc; padding: 30px; border-radius: 0 0 10px 10px; }}
                .highlight {{ background: #fef3c7; border-left: 4px solid #f59e0b; padding: 15px; margin: 20px 0; border-radius: 5px; }}
                .info-box {{ background: white; border: 1px solid #e2e8f0; border-radius: 8px; padding: 20px; margin: 15px 0; }}
                .btn {{ background: linear-gradient(135deg, #f97316 0%, #ea580c 100%); color: white; padding: 12px 30px; text-decoration: none; border-radius: 25px; display: inline-block; margin: 10px 0; }}
                .contact-info {{ background: #1E293B; color: white; padding: 20px; border-radius: 8px; margin: 20px 0; }}
                .footer {{ text-align: center; margin-top: 30px; padding: 20px; background: #f1f5f9; border-radius: 8px; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <div class="logo">🌟 ALORIA AGENCY</div>
                    <p>Votre partenaire de confiance pour l'immigration</p>
                </div>
                
                <div class="content">
                    <h2>Bonjour {name},</h2>
                    
                    <p>Merci d'avoir choisi <strong>ALORIA AGENCY</strong> pour votre projet d'immigration vers <strong>{country}</strong>. Nous avons bien reçu votre demande concernant <strong>{visa_type}</strong>.</p>
                    
                    <div class="highlight">
                        <h3>🎯 Prochaines étapes</h3>
                        <p><strong>Notre équipe d'experts va examiner votre profil et vous contacter dans les 24 heures</strong> pour :</p>
                        <ul>
                            <li>Analyser votre éligibilité</li>
                            <li>Vous proposer un plan d'action personnalisé</li>
                            <li>Répondre à toutes vos questions</li>
                        </ul>
                    </div>
                    
                    <div class="info-box">
                        <h3>📋 Récapitulatif de votre demande</h3>
                        <p><strong>Destination:</strong> {country} {country_info.get('flag', '')}</p>
                        <p><strong>Type de visa:</strong> {visa_type}</p>
                        <p><strong>Urgence:</strong> {urgency}</p>
                        <p><strong>Date de contact:</strong> {datetime.now().strftime('%d/%m/%Y à %H:%M')}</p>
                    </div>
                    
                    {visa_info}
                    
                    {country_info.get('content', '')}
                    
                    <div class="contact-info">
                        <h3>📞 Contacts utiles</h3>
                        <p><strong>Téléphone:</strong> +33 1 75 43 89 12</p>
                        <p><strong>E-mail:</strong> contact@aloria-agency.com</p>
                        <p><strong>Horaires:</strong> Lun-Ven 9h-18h, Sam 9h-13h</p>
                        <p><strong>Urgences:</strong> +33 6 12 34 56 78 (uniquement pour clients actuels)</p>
                    </div>
                    
                    <center>
                        <a href="https://aloria-agency.com/suivi" class="btn">🔍 Suivre mon dossier</a>
                    </center>
                </div>
                
                <div class="footer">
                    <p>Cordialement,<br><strong>L'équipe ALORIA AGENCY</strong></p>
                    <p style="font-size: 12px; color: #64748b;">
                        Cet e-mail a été envoyé automatiquement. Pour toute question, contactez-nous directement.
                    </p>
                </div>
            </div>
        </body>
        </html>
        """
        
        return self._send_email(email, subject, html_content)
    
    def send_user_creation_welcome_email(self, user_data: Dict[str, Any]) -> bool:
        """
        E-mail de bienvenue pour les nouveaux utilisateurs (managers, employés, clients)
        """
        name = user_data.get('full_name', 'Nouvel utilisateur')
        email = user_data.get('email')
        role = user_data.get('role', 'USER')
        login_email = user_data.get('login_email', email)
        default_password = user_data.get('default_password', 'Aloria2024!')
        
        role_info = self._get_role_specific_info(role)
        
        subject = f"🎉 Bienvenue dans l'équipe ALORIA AGENCY - Accès {role_info['title']}"
        
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <style>
                body {{ font-family: 'Arial', sans-serif; line-height: 1.6; color: #333; margin: 0; padding: 0; }}
                .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
                .header {{ background: linear-gradient(135deg, #1E293B 0%, #334155 100%); color: white; padding: 30px; text-align: center; border-radius: 10px 10px 0 0; }}
                .logo {{ font-size: 28px; font-weight: bold; margin-bottom: 10px; }}
                .content {{ background: #f8fafc; padding: 30px; border-radius: 0 0 10px 10px; }}
                .credentials {{ background: #fef3c7; border: 2px solid #f59e0b; padding: 20px; margin: 20px 0; border-radius: 8px; text-align: center; }}
                .info-box {{ background: white; border: 1px solid #e2e8f0; border-radius: 8px; padding: 20px; margin: 15px 0; }}
                .btn {{ background: linear-gradient(135deg, #f97316 0%, #ea580c 100%); color: white; padding: 12px 30px; text-decoration: none; border-radius: 25px; display: inline-block; margin: 10px 0; }}
                .security-note {{ background: #fecaca; border: 1px solid #f87171; padding: 15px; border-radius: 8px; margin: 15px 0; }}
                .footer {{ text-align: center; margin-top: 30px; padding: 20px; background: #f1f5f9; border-radius: 8px; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <div class="logo">🎉 ALORIA AGENCY</div>
                    <p>{role_info['welcome']}</p>
                </div>
                
                <div class="content">
                    <h2>Bienvenue {name} !</h2>
                    
                    <p>Votre compte <strong>{role_info['title']}</strong> a été créé avec succès. Vous faites désormais partie de l'équipe ALORIA AGENCY !</p>
                    
                    <div class="credentials">
                        <h3>🔐 Vos informations de connexion</h3>
                        <p><strong>URL de connexion:</strong> <a href="https://aloria-agency.com/login">aloria-agency.com/login</a></p>
                        <p><strong>E-mail:</strong> {login_email}</p>
                        <p><strong>Mot de passe temporaire:</strong> <code>{default_password}</code></p>
                    </div>
                    
                    <div class="security-note">
                        <h4>🔒 Important - Sécurité</h4>
                        <p><strong>Changez immédiatement votre mot de passe</strong> lors de votre première connexion pour sécuriser votre compte.</p>
                    </div>
                    
                    {role_info['content']}
                    
                    <div class="info-box">
                        <h3>📚 Ressources utiles</h3>
                        <ul>
                            <li><strong>Guide d'utilisation:</strong> Documentation complète de la plateforme</li>
                            <li><strong>Formation:</strong> Sessions de formation disponibles sur demande</li>
                            <li><strong>Support technique:</strong> support@aloria-agency.com</li>
                            <li><strong>Assistance:</strong> +33 1 75 43 89 12 (poste technique)</li>
                        </ul>
                    </div>
                    
                    <center>
                        <a href="https://aloria-agency.com/login" class="btn">🚀 Se connecter maintenant</a>
                    </center>
                </div>
                
                <div class="footer">
                    <p>Excellente journée dans l'équipe !<br><strong>L'équipe ALORIA AGENCY</strong></p>
                    <p style="font-size: 12px; color: #64748b;">
                        Pour toute question sur votre accès, contactez l'administrateur système.
                    </p>
                </div>
            </div>
        </body>
        </html>
        """
        
        return self._send_email(email, subject, html_content)
    
    def send_case_status_update_email(self, client_data: Dict[str, Any], case_data: Dict[str, Any]) -> bool:
        """
        E-mail de notification de changement de statut de dossier client
        """
        name = client_data.get('full_name', 'Cher client')
        email = client_data.get('email')
        case_id = case_data.get('id', 'N/A')
        current_step = case_data.get('current_step_name', 'En cours')
        status = case_data.get('status', 'En cours')
        country = case_data.get('country', '')
        visa_type = case_data.get('visa_type', '')
        progress = case_data.get('progress_percentage', 0)
        manager_name = case_data.get('manager_name', 'Votre gestionnaire')
        notes = case_data.get('notes', '')
        
        status_info = self._get_status_info(status, progress)
        
        subject = f"📋 Mise à jour de votre dossier ALORIA - {current_step}"
        
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <style>
                body {{ font-family: 'Arial', sans-serif; line-height: 1.6; color: #333; margin: 0; padding: 0; }}
                .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
                .header {{ background: linear-gradient(135deg, #1E293B 0%, #334155 100%); color: white; padding: 30px; text-align: center; border-radius: 10px 10px 0 0; }}
                .logo {{ font-size: 28px; font-weight: bold; margin-bottom: 10px; }}
                .content {{ background: #f8fafc; padding: 30px; border-radius: 0 0 10px 10px; }}
                .status-update {{ background: {status_info['bg_color']}; border-left: 6px solid {status_info['border_color']}; padding: 20px; margin: 20px 0; border-radius: 8px; }}
                .progress-bar {{ background: #e2e8f0; border-radius: 10px; height: 20px; margin: 15px 0; overflow: hidden; }}
                .progress-fill {{ background: linear-gradient(90deg, #f97316 0%, #ea580c 100%); height: 100%; width: {progress}%; border-radius: 10px; }}
                .info-box {{ background: white; border: 1px solid #e2e8f0; border-radius: 8px; padding: 20px; margin: 15px 0; }}
                .btn {{ background: linear-gradient(135deg, #f97316 0%, #ea580c 100%); color: white; padding: 12px 30px; text-decoration: none; border-radius: 25px; display: inline-block; margin: 10px 0; }}
                .contact-box {{ background: #1E293B; color: white; padding: 20px; border-radius: 8px; margin: 20px 0; }}
                .footer {{ text-align: center; margin-top: 30px; padding: 20px; background: #f1f5f9; border-radius: 8px; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <div class="logo">📋 ALORIA AGENCY</div>
                    <p>Mise à jour de votre dossier d'immigration</p>
                </div>
                
                <div class="content">
                    <h2>Bonjour {name},</h2>
                    
                    <p>Nous avons une excellente nouvelle concernant l'avancement de votre dossier d'immigration !</p>
                    
                    <div class="status-update">
                        <h3>{status_info['icon']} Nouvelle étape atteinte</h3>
                        <p><strong>Étape actuelle:</strong> {current_step}</p>
                        <p><strong>Statut:</strong> {status}</p>
                        <p><strong>Date de mise à jour:</strong> {datetime.now().strftime('%d/%m/%Y à %H:%M')}</p>
                    </div>
                    
                    <div class="info-box">
                        <h3>📊 Progression de votre dossier</h3>
                        <div class="progress-bar">
                            <div class="progress-fill"></div>
                        </div>
                        <p style="text-align: center;"><strong>{progress}% complété</strong></p>
                        
                        <p><strong>Dossier:</strong> {case_id}</p>
                        <p><strong>Destination:</strong> {country}</p>
                        <p><strong>Type de visa:</strong> {visa_type}</p>
                        <p><strong>Gestionnaire:</strong> {manager_name}</p>
                    </div>
                    
                    {f'''
                    <div class="info-box">
                        <h4>📝 Notes de votre gestionnaire</h4>
                        <p style="font-style: italic;">"{notes}"</p>
                    </div>
                    ''' if notes else ''}
                    
                    {status_info['content']}
                    
                    <div class="contact-box">
                        <h3>💬 Besoin d'aide ou de précisions ?</h3>
                        <p>Votre gestionnaire <strong>{manager_name}</strong> est là pour vous accompagner :</p>
                        <p><strong>E-mail direct:</strong> {manager_name.lower().replace(' ', '.')}@aloria-agency.com</p>
                        <p><strong>Téléphone:</strong> +33 1 75 43 89 12</p>
                        <p><strong>Rendez-vous:</strong> Disponible sur demande</p>
                    </div>
                    
                    <center>
                        <a href="https://aloria-agency.com/client-dashboard" class="btn">👀 Voir mon dossier complet</a>
                    </center>
                </div>
                
                <div class="footer">
                    <p>Nous restons à votre disposition,<br><strong>L'équipe ALORIA AGENCY</strong></p>
                    <p style="font-size: 12px; color: #64748b;">
                        Cet e-mail est automatique. Connectez-vous à votre espace client pour plus de détails.
                    </p>
                </div>
            </div>
        </body>
        </html>
        """
        
        return self._send_email(email, subject, html_content)
    
    def _get_country_specific_info(self, country: str) -> Dict[str, str]:
        """Informations spécifiques par pays de destination"""
        country_data = {
            "Canada": {
                "flag": "🇨🇦",
                "content": """
                <div class="info-box">
                    <h3>🇨🇦 Spécificités Canada</h3>
                    <ul>
                        <li><strong>Système Entrée Express:</strong> Traitement rapide en 6 mois</li>
                        <li><strong>Évaluation linguistique:</strong> TEF/IELTS requis</li>
                        <li><strong>Équivalence diplômes:</strong> ECA obligatoire</li>
                        <li><strong>Provinces populaires:</strong> Québec, Ontario, Colombie-Britannique</li>
                    </ul>
                </div>
                """
            },
            "France": {
                "flag": "🇫🇷",
                "content": """
                <div class="info-box">
                    <h3>🇫🇷 Spécificités France</h3>
                    <ul>
                        <li><strong>Passeport Talent:</strong> Profils qualifiés privilégiés</li>
                        <li><strong>Niveau français:</strong> B2 recommandé minimum</li>
                        <li><strong>Reconnaissance diplômes:</strong> ENIC-NARIC France</li>
                        <li><strong>Régions attractives:</strong> Île-de-France, PACA, Rhône-Alpes</li>
                    </ul>
                </div>
                """
            }
        }
        
        return country_data.get(country, {"flag": "🌍", "content": ""})
    
    def _get_visa_specific_info(self, visa_type: str, country: str) -> str:
        """Informations spécifiques par type de visa"""
        if not visa_type:
            return ""
        
        visa_info = {
            "Permis de Travail": "💼 Excellent choix pour une intégration professionnelle rapide !",
            "Résidence Permanente": "🏠 Parfait pour un projet d'installation durable !",
            "Visa Étudiant": "🎓 Une excellente porte d'entrée vers l'immigration !",
            "Passeport Talent": "⭐ Le visa privilégié pour les profils qualifiés !"
        }
        
        for key, value in visa_info.items():
            if key in visa_type:
                return f"""
                <div class="info-box">
                    <h4>{value}</h4>
                </div>
                """
        
        return ""
    
    def _get_role_specific_info(self, role: str) -> Dict[str, str]:
        """Informations spécifiques par rôle utilisateur"""
        role_data = {
            "MANAGER": {
                "title": "Gestionnaire",
                "welcome": "Bienvenue dans l'équipe de gestion",
                "content": """
                <div class="info-box">
                    <h3>🎯 Vos responsabilités</h3>
                    <ul>
                        <li><strong>Gestion d'équipe:</strong> Supervision des employés</li>
                        <li><strong>Validation dossiers:</strong> Approbation finale des demandes</li>
                        <li><strong>Relation client:</strong> Suivi des clients premium</li>
                        <li><strong>Reporting:</strong> Tableaux de bord et statistiques</li>
                    </ul>
                </div>
                """
            },
            "EMPLOYEE": {
                "title": "Conseiller Immigration",
                "welcome": "Bienvenue dans l'équipe conseil",
                "content": """
                <div class="info-box">
                    <h3>📋 Vos missions</h3>
                    <ul>
                        <li><strong>Accompagnement client:</strong> Suivi personnalisé des dossiers</li>
                        <li><strong>Expertise visa:</strong> Conseil sur les procédures</li>
                        <li><strong>Documentation:</strong> Vérification des pièces justificatives</li>
                        <li><strong>Relation prospects:</strong> Conversion des leads</li>
                    </ul>
                </div>
                """
            },
            "CLIENT": {
                "title": "Client",
                "welcome": "Bienvenue chez ALORIA AGENCY",
                "content": """
                <div class="info-box">
                    <h3>🎁 Vos avantages</h3>
                    <ul>
                        <li><strong>Suivi temps réel:</strong> Dashboard personnalisé</li>
                        <li><strong>Expert dédié:</strong> Un conseiller attitré</li>
                        <li><strong>Support 24/7:</strong> Assistance continue</li>
                        <li><strong>Garantie succès:</strong> Engagement de résultat</li>
                    </ul>
                </div>
                """
            }
        }
        
        return role_data.get(role, {
            "title": "Utilisateur",
            "welcome": "Bienvenue sur la plateforme",
            "content": ""
        })
    
    def _get_status_info(self, status: str, progress: int) -> Dict[str, str]:
        """Informations d'affichage selon le statut du dossier"""
        if progress >= 90:
            return {
                "icon": "🎉",
                "bg_color": "#dcfce7",
                "border_color": "#16a34a",
                "content": """
                <div class="info-box" style="background: #dcfce7; border: 1px solid #16a34a;">
                    <h4>🎊 Félicitations !</h4>
                    <p>Votre dossier est presque finalisé ! Nous sommes dans la dernière ligne droite. Restez disponible pour les éventuelles demandes finales des autorités.</p>
                </div>
                """
            }
        elif progress >= 70:
            return {
                "icon": "🚀",
                "bg_color": "#fef3c7",
                "border_color": "#f59e0b",
                "content": """
                <div class="info-box" style="background: #fef3c7; border: 1px solid #f59e0b;">
                    <h4>🎯 Excellente progression !</h4>
                    <p>Votre dossier avance très bien ! Nous sommes maintenant dans les étapes finales de traitement. Patience, le résultat approche !</p>
                </div>
                """
            }
        elif progress >= 40:
            return {
                "icon": "⚡",
                "bg_color": "#dbeafe",
                "border_color": "#3b82f6",
                "content": """
                <div class="info-box" style="background: #dbeafe; border: 1px solid #3b82f6;">
                    <h4>📈 Bonne avancée !</h4>
                    <p>Votre dossier progresse normalement. Nous travaillons activement sur les étapes suivantes. Tenez-vous prêt pour la prochaine phase !</p>
                </div>
                """
            }
        else:
            return {
                "icon": "📋",
                "bg_color": "#f1f5f9",
                "border_color": "#64748b",
                "content": """
                <div class="info-box" style="background: #f1f5f9; border: 1px solid #64748b;">
                    <h4>🔄 Traitement en cours</h4>
                    <p>Votre dossier est en cours de traitement par nos experts. Nous vous tiendrons informé de chaque étape importante !</p>
                </div>
                """
            }

# Instance globale du service d'e-mails
email_service = AloriaEmailService()

# Fonctions d'aide pour l'intégration dans l'application
async def send_prospect_email(prospect_data: Dict[str, Any]) -> bool:
    """Envoi e-mail prospect (fonction async pour FastAPI)"""
    try:
        return email_service.send_prospect_welcome_email(prospect_data)
    except Exception as e:
        logger.error(f"Erreur envoi e-mail prospect: {e}")
        return False

async def send_user_welcome_email(user_data: Dict[str, Any]) -> bool:
    """Envoi e-mail bienvenue utilisateur (fonction async pour FastAPI)"""
    try:
        return email_service.send_user_creation_welcome_email(user_data)
    except Exception as e:
        logger.error(f"Erreur envoi e-mail utilisateur: {e}")
        return False

async def send_case_update_email(client_data: Dict[str, Any], case_data: Dict[str, Any]) -> bool:
    """Envoi e-mail mise à jour dossier (fonction async pour FastAPI)"""
    try:
        return email_service.send_case_status_update_email(client_data, case_data)
    except Exception as e:
        logger.error(f"Erreur envoi e-mail mise à jour: {e}")
        return False