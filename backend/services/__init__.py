"""Services réutilisables pour ALORIA AGENCY"""

from .user_service import create_user_account, verify_user_permissions, get_user_by_id
from .client_service import create_client_profile, verify_client_dashboard_accessible
from .assignment_service import assign_client_to_employee, find_least_busy_employee, reassign_client
from .credentials_service import generate_temporary_password, generate_credentials_response
from .notification_service import send_creation_notifications, send_welcome_email_notification

__all__ = [
    'create_user_account',
    'verify_user_permissions',
    'get_user_by_id',
    'create_client_profile',
    'verify_client_dashboard_accessible',
    'assign_client_to_employee',
    'find_least_busy_employee',
    'reassign_client',
    'generate_temporary_password',
    'generate_credentials_response',
    'send_creation_notifications',
    'send_welcome_email_notification'
]
