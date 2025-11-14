"""
Service de gestion des affectations - ALORIA AGENCY

Ce service centralise TOUTE la logique d'affectation de clients aux employés.
Gère l'auto-affectation, l'affectation manuelle et le load balancing.
"""

import logging
from typing import Dict, Optional

logger = logging.getLogger(__name__)


async def assign_client_to_employee(
    db,
    client_id: str,
    employee_id: str = None,
    created_by_id: str = None,
    created_by_role: str = None,
    use_load_balancing: bool = False
) -> Dict:
    """
    Fonction UNIVERSELLE pour l'affectation de clients aux employés.
    
    LOGIQUE D'AFFECTATION INTELLIGENTE:
    
    1. Si employee_id est fourni → Affectation directe à cet employé
    
    2. Si created_by_role == "EMPLOYEE" → Auto-affectation à l'employé créateur
       (L'employé qui crée un client se l'affecte automatiquement)
    
    3. Si created_by_role == "MANAGER" et employee_id fourni → Affectation à l'employé spécifié
    
    4. Si created_by_role == "MANAGER" et employee_id == None → Auto-affectation au manager
       (Le manager qui crée un client sans spécifier d'employé se l'affecte)
    
    5. Si use_load_balancing == True → Affectation à l'employé avec le moins de clients
    
    6. Si created_by_role == "SUPERADMIN" → DOIT fournir employee_id ou use_load_balancing
    
    Args:
        db: Instance de la base de données
        client_id: ID du profil client (dans collection 'clients')
        employee_id: ID de l'employé (optionnel)
        created_by_id: ID de l'utilisateur créateur
        created_by_role: Rôle de l'utilisateur créateur
        use_load_balancing: Utiliser le load balancing automatique
    
    Returns:
        Dict contenant:
        - assigned_employee_id: ID de l'employé assigné
        - assigned_employee_name: Nom de l'employé assigné
        - assignment_type: Type d'affectation ('auto', 'manual', 'load_balanced', 'manager_self')
    
    Raises:
        HTTPException: Si aucune méthode d'affectation n'est possible
    """
    from fastapi import HTTPException
    from .user_service import get_user_by_id
    
    assigned_employee_id = None
    assignment_type = None
    
    # LOGIQUE 1: Affectation directe (employee_id fourni)
    if employee_id:
        assigned_employee_id = employee_id
        assignment_type = "manual"
        logger.info(f"Affectation manuelle du client {client_id} à l'employé {employee_id}")
    
    # LOGIQUE 2: Auto-affectation EMPLOYEE
    elif created_by_role == "EMPLOYEE" and created_by_id:
        assigned_employee_id = created_by_id
        assignment_type = "auto"
        logger.info(f"Auto-affectation: Employé {created_by_id} s'affecte le client {client_id}")
    
    # LOGIQUE 3: Auto-affectation MANAGER (si pas d'employé spécifié)
    elif created_by_role == "MANAGER" and created_by_id and not employee_id:
        assigned_employee_id = created_by_id
        assignment_type = "manager_self"
        logger.info(f"Auto-affectation: Manager {created_by_id} s'affecte le client {client_id}")
    
    # LOGIQUE 4: Load balancing
    elif use_load_balancing:
        assigned_employee_id = await find_least_busy_employee(db)
        assignment_type = "load_balanced"
        logger.info(f"Load balancing: Client {client_id} affecté à l'employé {assigned_employee_id}")
    
    # LOGIQUE 5: Aucune méthode d'affectation disponible
    else:
        # Essayer load balancing par défaut
        assigned_employee_id = await find_least_busy_employee(db)
        if assigned_employee_id:
            assignment_type = "load_balanced_default"
            logger.info(f"Affectation par défaut (load balancing): Client {client_id} affecté à {assigned_employee_id}")
        else:
            logger.warning(f"Impossible d'affecter le client {client_id}: aucun employé disponible")
            # Ne pas lever d'erreur, juste ne pas affecter
            return {
                "assigned_employee_id": None,
                "assigned_employee_name": None,
                "assignment_type": "unassigned"
            }
    
    # Récupérer le nom de l'employé assigné
    assigned_employee_name = None
    if assigned_employee_id:
        employee = await get_user_by_id(db, assigned_employee_id)
        if employee:
            assigned_employee_name = employee["full_name"]
    
    return {
        "assigned_employee_id": assigned_employee_id,
        "assigned_employee_name": assigned_employee_name,
        "assignment_type": assignment_type
    }


async def find_least_busy_employee(db) -> Optional[str]:
    """
    Trouve l'employé avec le moins de clients assignés (load balancing).
    
    Args:
        db: Instance de la base de données
    
    Returns:
        str: ID de l'employé le moins chargé, ou None si aucun employé disponible
    """
    # Récupérer tous les employés actifs
    employees = await db.users.find({"role": "EMPLOYEE", "is_active": True}).to_list(100)
    
    if not employees:
        logger.warning("Aucun employé actif trouvé pour le load balancing")
        return None
    
    # Compter les clients par employé
    employee_loads = []
    for emp in employees:
        count = await db.clients.count_documents({"assigned_employee_id": emp["id"]})
        employee_loads.append((emp["id"], count, emp["full_name"]))
    
    # Trier par charge (nombre de clients)
    employee_loads.sort(key=lambda x: x[1])
    
    least_busy = employee_loads[0]
    logger.info(f"Employé le moins chargé: {least_busy[2]} (ID: {least_busy[0]}) avec {least_busy[1]} clients")
    
    return least_busy[0]


async def reassign_client(
    db,
    client_id: str,
    old_employee_id: str,
    new_employee_id: str,
    reassigned_by_id: str
) -> Dict:
    """
    Réaffecte un client d'un employé à un autre.
    
    Args:
        db: Instance de la base de données
        client_id: ID du profil client
        old_employee_id: ID de l'ancien employé
        new_employee_id: ID du nouvel employé
        reassigned_by_id: ID de l'utilisateur qui effectue la réaffectation
    
    Returns:
        Dict contenant les informations de la réaffectation
    """
    from datetime import datetime, timezone
    from .user_service import get_user_by_id, log_user_activity
    
    # Récupérer les noms des employés
    old_employee = await get_user_by_id(db, old_employee_id) if old_employee_id else None
    new_employee = await get_user_by_id(db, new_employee_id)
    
    if not new_employee:
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail="Nouvel employé non trouvé")
    
    # Mettre à jour le client
    await db.clients.update_one(
        {"id": client_id},
        {
            "$set": {
                "assigned_employee_id": new_employee_id,
                "assigned_employee_name": new_employee["full_name"],
                "updated_at": datetime.now(timezone.utc).isoformat()
            }
        }
    )
    
    # Mettre à jour les cases associés
    client = await db.clients.find_one({"id": client_id})
    if client:
        await db.cases.update_many(
            {"client_id": client["user_id"]},
            {
                "$set": {
                    "assigned_employee_id": new_employee_id,
                    "assigned_employee_name": new_employee["full_name"],
                    "updated_at": datetime.now(timezone.utc).isoformat()
                }
            }
        )
    
    # Logger l'activité
    await log_user_activity(
        db=db,
        user_id=reassigned_by_id,
        action="client_reassigned",
        details={
            "client_id": client_id,
            "old_employee_id": old_employee_id,
            "old_employee_name": old_employee["full_name"] if old_employee else None,
            "new_employee_id": new_employee_id,
            "new_employee_name": new_employee["full_name"]
        }
    )
    
    logger.info(f"Client {client_id} réaffecté de {old_employee_id} à {new_employee_id}")
    
    return {
        "client_id": client_id,
        "old_employee_id": old_employee_id,
        "old_employee_name": old_employee["full_name"] if old_employee else None,
        "new_employee_id": new_employee_id,
        "new_employee_name": new_employee["full_name"],
        "reassigned_at": datetime.now(timezone.utc).isoformat()
    }


async def get_employee_workload(db, employee_id: str) -> Dict:
    """
    Retourne la charge de travail d'un employé.
    
    Args:
        db: Instance de la base de données
        employee_id: ID de l'employé
    
    Returns:
        Dict contenant les statistiques de charge
    """
    # Compter les clients assignés
    total_clients = await db.clients.count_documents({"assigned_employee_id": employee_id})
    
    # Compter les cases actifs
    active_cases = await db.cases.count_documents({
        "assigned_employee_id": employee_id,
        "status": {"$in": ["Nouveau", "En cours"]}
    })
    
    # Compter les cases terminés
    completed_cases = await db.cases.count_documents({
        "assigned_employee_id": employee_id,
        "status": "Terminé"
    })
    
    return {
        "employee_id": employee_id,
        "total_clients": total_clients,
        "active_cases": active_cases,
        "completed_cases": completed_cases
    }
