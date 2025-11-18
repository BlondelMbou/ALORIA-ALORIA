"""
Script de migration pour enrichir les clients existants avec les données des users.

Ce script corrige le problème où les clients n'ont pas de full_name, email, phone
en les récupérant depuis la collection users.
"""

import asyncio
import sys
import os
from motor.motor_asyncio import AsyncIOMotorClient

# Ajouter le répertoire parent au path pour importer les modules
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from dotenv import load_dotenv

# Charger les variables d'environnement
load_dotenv()

MONGO_URL = os.environ.get('MONGO_URL', 'mongodb://localhost:27017')
DB_NAME = os.environ.get('DB_NAME', 'aloria_agency')


async def fix_clients_data():
    """
    Enrichit tous les clients avec les données manquantes depuis users.
    """
    client = AsyncIOMotorClient(MONGO_URL)
    db = client[DB_NAME]
    
    print("🔧 Démarrage de la migration des données clients...")
    
    # Récupérer tous les clients
    clients = await db.clients.find({}).to_list(1000)
    print(f"📊 {len(clients)} clients trouvés")
    
    fixed_count = 0
    already_ok_count = 0
    error_count = 0
    
    for client_doc in clients:
        client_id = client_doc.get('id')
        user_id = client_doc.get('user_id')
        
        # Vérifier si les données sont manquantes
        missing_full_name = not client_doc.get('full_name') or client_doc.get('full_name') == ''
        missing_email = not client_doc.get('email') or client_doc.get('email') == ''
        missing_phone = not client_doc.get('phone') or client_doc.get('phone') == ''
        
        if not (missing_full_name or missing_email or missing_phone):
            already_ok_count += 1
            continue
        
        print(f"\n⚠️  Client {client_id[:8]}... manque des données:")
        print(f"   - full_name: {'❌' if missing_full_name else '✅'} '{client_doc.get('full_name')}'")
        print(f"   - email: {'❌' if missing_email else '✅'} '{client_doc.get('email')}'")
        print(f"   - phone: {'❌' if missing_phone else '✅'} '{client_doc.get('phone')}'")
        print(f"   - user_id: {user_id}")
        
        # Récupérer les données depuis users
        if not user_id:
            print(f"   ❌ PAS DE user_id pour ce client!")
            error_count += 1
            continue
        
        user = await db.users.find_one({"id": user_id})
        
        if not user:
            print(f"   ❌ User {user_id} NOT FOUND dans la collection users!")
            error_count += 1
            continue
        
        print(f"   ✅ User trouvé: {user.get('full_name')} <{user.get('email')}>")
        
        # Préparer les mises à jour
        updates = {}
        if missing_full_name and user.get('full_name'):
            updates['full_name'] = user.get('full_name')
        if missing_email and user.get('email'):
            updates['email'] = user.get('email')
        if missing_phone and user.get('phone'):
            updates['phone'] = user.get('phone')
        
        if updates:
            # Mettre à jour le client
            result = await db.clients.update_one(
                {"id": client_id},
                {"$set": updates}
            )
            
            if result.modified_count > 0:
                print(f"   ✅ Client mis à jour avec: {updates}")
                fixed_count += 1
            else:
                print(f"   ⚠️  Aucune modification (peut-être déjà à jour)")
        else:
            print(f"   ⚠️  Aucune donnée à mettre à jour depuis user")
    
    print(f"\n" + "="*60)
    print(f"📊 RÉSUMÉ:")
    print(f"   ✅ Clients corrigés: {fixed_count}")
    print(f"   ✓  Clients déjà OK: {already_ok_count}")
    print(f"   ❌ Erreurs: {error_count}")
    print(f"   📋 Total: {len(clients)}")
    print("="*60)
    
    client.close()
    print("\n✅ Migration terminée!")


if __name__ == "__main__":
    asyncio.run(fix_clients_data())
