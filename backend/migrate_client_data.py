#!/usr/bin/env python3
"""
Script de migration pour mettre à jour les données des clients existants
Ajoute les champs manquants: full_name, email, phone depuis la collection users
"""

import asyncio
import os
from motor.motor_asyncio import AsyncIOMotorClient
from datetime import datetime, timezone

async def migrate_clients():
    """Migrer les données des clients existants"""
    
    # Connexion à MongoDB
    mongo_url = os.environ.get('MONGO_URL', 'mongodb://localhost:27017')
    db_name = os.environ.get('DB_NAME', 'aloria')
    
    client = AsyncIOMotorClient(mongo_url)
    db = client[db_name]
    
    print("🔄 Début de la migration des données clients...")
    print(f"📊 Base de données: {db_name}")
    
    # Récupérer tous les clients
    clients = await db.clients.find({}).to_list(1000)
    print(f"📋 Nombre de clients trouvés: {len(clients)}")
    
    updated_count = 0
    skipped_count = 0
    error_count = 0
    
    for client in clients:
        client_id = client.get('id')
        user_id = client.get('user_id')
        
        # Vérifier si les champs sont déjà présents
        has_full_name = 'full_name' in client and client['full_name']
        has_email = 'email' in client and client['email']
        has_phone = 'phone' in client and client['phone']
        
        if has_full_name and has_email and has_phone:
            skipped_count += 1
            continue
        
        # Récupérer les données depuis users
        if not user_id:
            print(f"  ⚠️  Client {client_id} n'a pas de user_id - ignoré")
            error_count += 1
            continue
        
        user = await db.users.find_one({"id": user_id})
        if not user:
            print(f"  ⚠️  Utilisateur {user_id} non trouvé pour client {client_id}")
            error_count += 1
            continue
        
        # Préparer les mises à jour
        update_fields = {}
        
        if not has_full_name:
            update_fields['full_name'] = user.get('full_name', 'N/A')
        
        if not has_email:
            update_fields['email'] = user.get('email', 'N/A')
        
        if not has_phone:
            update_fields['phone'] = user.get('phone', '')
        
        # Ajouter aussi current_status, current_step, progress_percentage si manquants
        if 'current_status' not in client:
            update_fields['current_status'] = 'Nouveau'
        
        if 'current_step' not in client:
            update_fields['current_step'] = 0
        
        if 'progress_percentage' not in client:
            update_fields['progress_percentage'] = 0.0
        
        update_fields['updated_at'] = datetime.now(timezone.utc).isoformat()
        
        # Mettre à jour le client
        result = await db.clients.update_one(
            {"id": client_id},
            {"$set": update_fields}
        )
        
        if result.modified_count > 0:
            print(f"  ✅ Client {client_id} mis à jour: {user.get('full_name')} ({user.get('email')})")
            updated_count += 1
        else:
            print(f"  ⚠️  Échec mise à jour client {client_id}")
            error_count += 1
    
    print("\n" + "="*60)
    print(f"✅ Migration terminée!")
    print(f"📊 Statistiques:")
    print(f"   - Total de clients: {len(clients)}")
    print(f"   - Clients mis à jour: {updated_count}")
    print(f"   - Clients déjà à jour: {skipped_count}")
    print(f"   - Erreurs: {error_count}")
    print("="*60)
    
    client.close()

if __name__ == "__main__":
    asyncio.run(migrate_clients())
