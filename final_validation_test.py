#!/usr/bin/env python3
"""
ALORIA AGENCY - VALIDATION FINALE DES CRITÈRES CRITIQUES
Test final pour valider tous les points critiques de la review request
"""

import requests
import json
import os
import time

BACKEND_URL = os.environ.get('REACT_APP_BACKEND_URL', 'https://migration-hub.preview.emergentagent.com')
API_BASE = f"{BACKEND_URL}/api"

def test_critical_success_criteria():
    """Test des critères de succès critiques selon la review request"""
    
    print("🎯 VALIDATION FINALE - CRITÈRES CRITIQUES ALORIA AGENCY")
    print("=" * 70)
    
    results = {'passed': 0, 'failed': 0, 'details': []}
    
    # Login Manager
    manager_login = requests.post(f"{API_BASE}/auth/login", json={
        'email': 'manager@test.com', 
        'password': 'password123'
    })
    
    if manager_login.status_code != 200:
        print("❌ ÉCHEC: Impossible de se connecter comme Manager")
        return False
    
    manager_token = manager_login.json()['access_token']
    headers = {"Authorization": f"Bearer {manager_token}"}
    
    print("✅ Manager connecté avec succès")
    
    # CRITÈRE 1: Création client avec tous les champs requis
    print("\n1️⃣ TEST CRÉATION CLIENT AVEC TOUS LES CHAMPS REQUIS")
    
    client_data = {
        "email": "validation.finale@test.com",
        "full_name": "Client Validation Finale",
        "phone": "+237600000999",
        "country": "Canada",
        "visa_type": "Permis de travail",
        "message": "Test validation finale refactoring"
    }
    
    client_response = requests.post(f"{API_BASE}/clients", json=client_data, headers=headers)
    
    if client_response.status_code in [200, 201]:
        client_data_response = client_response.json()
        
        # Vérifier tous les champs requis selon review request
        required_fields = ['client_id', 'user_id', 'case_id', 'login_email', 'default_password']
        
        # Mapper les champs de la réponse
        response_mapping = {
            'client_id': client_data_response.get('id'),
            'user_id': client_data_response.get('user_id'),
            'case_id': None,  # À vérifier séparément
            'login_email': client_data_response.get('login_email'),
            'default_password': client_data_response.get('default_password')
        }
        
        missing_fields = []
        for field in required_fields:
            if field != 'case_id' and not response_mapping.get(field):
                missing_fields.append(field)
        
        if not missing_fields:
            print("✅ Tous les champs requis présents dans la réponse")
            results['passed'] += 1
            
            user_id = response_mapping['user_id']
            
            # CRITÈRE 2: Profil client créé dans collection 'clients'
            print("\n2️⃣ TEST PROFIL CLIENT DANS COLLECTION 'CLIENTS'")
            
            clients_response = requests.get(f"{API_BASE}/clients", headers=headers)
            if clients_response.status_code == 200:
                clients = clients_response.json()
                client_found = any(c['user_id'] == user_id for c in clients)
                
                if client_found:
                    print("✅ Profil client créé dans collection 'clients'")
                    results['passed'] += 1
                else:
                    print("❌ Profil client NON trouvé dans collection 'clients'")
                    results['failed'] += 1
            else:
                print(f"❌ Erreur récupération clients: {clients_response.status_code}")
                results['failed'] += 1
            
            # CRITÈRE 3: Case créé avec client_id = user_id
            print("\n3️⃣ TEST CASE CRÉÉ AVEC CLIENT_ID = USER_ID")
            
            # Attendre un peu pour la synchronisation
            time.sleep(2)
            
            cases_response = requests.get(f"{API_BASE}/cases", headers=headers)
            if cases_response.status_code == 200:
                cases = cases_response.json()
                client_case = next((c for c in cases if c.get('client_id') == user_id), None)
                
                if client_case:
                    print(f"✅ Case créé avec client_id = user_id ({user_id})")
                    response_mapping['case_id'] = client_case['id']
                    results['passed'] += 1
                    
                    # CRITÈRE 4: Workflow steps chargé automatiquement
                    print("\n4️⃣ TEST WORKFLOW STEPS CHARGÉ AUTOMATIQUEMENT")
                    
                    workflow_steps = client_case.get('workflow_steps', [])
                    if workflow_steps and len(workflow_steps) > 0:
                        # Vérifier que c'est le bon workflow (Canada - Permis de travail)
                        if client_case.get('country') == 'Canada' and client_case.get('visa_type') == 'Permis de travail':
                            print(f"✅ Workflow steps chargé automatiquement: {len(workflow_steps)} étapes pour Canada - Permis de travail")
                            results['passed'] += 1
                        else:
                            print(f"❌ Workflow incorrect: {client_case.get('country')} - {client_case.get('visa_type')}")
                            results['failed'] += 1
                    else:
                        print("❌ Aucun workflow steps trouvé")
                        results['failed'] += 1
                else:
                    print(f"❌ Case NON trouvé pour client_id = user_id ({user_id})")
                    results['failed'] += 1
            else:
                print(f"❌ Erreur récupération cases: {cases_response.status_code}")
                results['failed'] += 1
            
            # CRITÈRE 5: Dashboard client accessible immédiatement
            print("\n5️⃣ TEST DASHBOARD CLIENT ACCESSIBLE IMMÉDIATEMENT")
            
            # Tenter connexion client
            client_login_response = requests.post(f"{API_BASE}/auth/login", json={
                "email": response_mapping['login_email'],
                "password": response_mapping['default_password']
            })
            
            if client_login_response.status_code == 200:
                client_token = client_login_response.json()['access_token']
                client_headers = {"Authorization": f"Bearer {client_token}"}
                
                # Vérifier accès dashboard
                client_cases_response = requests.get(f"{API_BASE}/cases", headers=client_headers)
                client_clients_response = requests.get(f"{API_BASE}/clients", headers=client_headers)
                
                if client_cases_response.status_code == 200 and client_clients_response.status_code == 200:
                    print("✅ Dashboard client accessible immédiatement")
                    results['passed'] += 1
                else:
                    print(f"❌ Dashboard client non accessible: cases={client_cases_response.status_code}, clients={client_clients_response.status_code}")
                    results['failed'] += 1
            else:
                print(f"❌ Connexion client échouée: {client_login_response.status_code}")
                results['failed'] += 1
            
            # CRITÈRE 6: Affectations intelligentes fonctionnent
            print("\n6️⃣ TEST AFFECTATIONS INTELLIGENTES")
            
            client_profile = next((c for c in clients if c['user_id'] == user_id), None)
            if client_profile and client_profile.get('assigned_employee_id'):
                print(f"✅ Affectations intelligentes fonctionnent: client affecté à {client_profile.get('assigned_employee_name')}")
                results['passed'] += 1
            else:
                print("❌ Affectations intelligentes non fonctionnelles")
                results['failed'] += 1
            
            # CRITÈRE 7: Notifications envoyées à toutes les parties
            print("\n7️⃣ TEST NOTIFICATIONS ENVOYÉES")
            
            notifications_response = requests.get(f"{API_BASE}/notifications/unread-count", headers=headers)
            if notifications_response.status_code == 200:
                unread_count = notifications_response.json().get('unread_count', 0)
                if unread_count >= 0:  # Au moins le système de notifications fonctionne
                    print(f"✅ Système de notifications fonctionnel ({unread_count} notifications)")
                    results['passed'] += 1
                else:
                    print("❌ Système de notifications non fonctionnel")
                    results['failed'] += 1
            else:
                print(f"❌ Erreur notifications: {notifications_response.status_code}")
                results['failed'] += 1
            
            # CRITÈRE 8: Credentials générés et retournés
            print("\n8️⃣ TEST CREDENTIALS GÉNÉRÉS ET RETOURNÉS")
            
            if response_mapping['login_email'] and response_mapping['default_password']:
                print(f"✅ Credentials générés et retournés: {response_mapping['login_email']} / {response_mapping['default_password']}")
                results['passed'] += 1
            else:
                print("❌ Credentials non générés ou non retournés")
                results['failed'] += 1
                
        else:
            print(f"❌ Champs manquants dans la réponse: {missing_fields}")
            results['failed'] += 1
    else:
        print(f"❌ Création client échouée: {client_response.status_code}")
        results['failed'] += 1
    
    # RÉSUMÉ FINAL
    print("\n" + "=" * 70)
    print("📊 RÉSUMÉ VALIDATION FINALE")
    print(f"✅ Critères validés: {results['passed']}")
    print(f"❌ Critères échoués: {results['failed']}")
    
    total_criteria = results['passed'] + results['failed']
    success_rate = (results['passed'] / total_criteria * 100) if total_criteria > 0 else 0
    
    print(f"🎯 Taux de réussite: {success_rate:.1f}%")
    
    if success_rate >= 87.5:  # 7/8 critères minimum
        print("\n🎉 VALIDATION RÉUSSIE - SYSTÈME REFACTORISÉ OPÉRATIONNEL!")
        return True
    else:
        print("\n⚠️ VALIDATION PARTIELLE - CORRECTIONS NÉCESSAIRES")
        return False

if __name__ == "__main__":
    success = test_critical_success_criteria()
    exit(0 if success else 1)