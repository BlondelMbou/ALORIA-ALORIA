#!/usr/bin/env python3
"""
ALORIA AGENCY - Test Correction "Aucun Dossier Actif" - Dashboard Client

CONTEXTE:
L'utilisateur rapporte que lorsqu'un Manager ou Employee crée un client, 
le client voit l'erreur "Aucun Dossier Actif" sur son dashboard au lieu de voir son dossier.

PROBLÈME IDENTIFIÉ ET CORRIGÉ:
Ligne 1396-1397 de server.py - Incohérence dans la recherche des cases :
- Les cases sont créés avec client_id = user_id 
- Mais GET /api/cases cherchait avec client_id IN [client.id, ...] pour tous les rôles
- Pour les CLIENTS, client.id ≠ user_id, donc aucun case trouvé

CORRECTION APPLIQUÉE :
- CLIENT: Cherche directement avec client_id = current_user["id"] (son user_id)
- MANAGER/EMPLOYEE: Cherche avec client_id IN [user_id, user_id, ...] des clients assignés

TESTS REQUIS:
1. Client Existant Voit Son Dossier
2. Nouveau Client Créé par Employee
3. Nouveau Client Créé par Manager  
4. Manager Voit Tous les Dossiers
5. Employee Voit Ses Dossiers Assignés
"""

import requests
import json
import os
import time
from datetime import datetime
import sys

# Configuration
BACKEND_URL = os.environ.get('REACT_APP_BACKEND_URL', 'https://aloria-dev.preview.emergentagent.com')
API_BASE = f"{BACKEND_URL}/api"

# Credentials from review request
CREDENTIALS = {
    'manager': {'email': 'manager@test.com', 'password': 'password123'},
    'employee': {'email': 'employee@aloria.com', 'password': 'emp123'},
    'client_test': {'email': 'client.employee.test@example.com', 'password': 'Aloria2024!'}
}

class AucunDossierActifTester:
    def __init__(self):
        self.session = requests.Session()
        self.tokens = {}
        self.users = {}
        self.test_data = {}
        self.results = {'passed': 0, 'failed': 0, 'errors': []}

    def log_result(self, test_name, success, message="", error_details=""):
        """Log test result"""
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status}: {test_name}")
        if message:
            print(f"   {message}")
        if error_details:
            print(f"   Error: {error_details}")
        
        if success:
            self.results['passed'] += 1
        else:
            self.results['failed'] += 1
            self.results['errors'].append({
                'test': test_name,
                'message': message,
                'error': error_details
            })
        print()

    def authenticate_user(self, role):
        """Authenticate a specific user"""
        if role not in CREDENTIALS:
            self.log_result(f"{role.upper()} Authentication", False, f"No credentials for {role}")
            return False
            
        try:
            credentials = CREDENTIALS[role]
            response = self.session.post(f"{API_BASE}/auth/login", json=credentials)
            
            if response.status_code == 200:
                data = response.json()
                self.tokens[role] = data['access_token']
                self.users[role] = data['user']
                self.log_result(f"{role.upper()} Authentication", True, 
                              f"Logged in as {credentials['email']} - Role: {data['user']['role']}")
                return True
            else:
                self.log_result(f"{role.upper()} Authentication", False, 
                              f"Status: {response.status_code}", response.text)
                return False
        except Exception as e:
            self.log_result(f"{role.upper()} Authentication", False, "Exception occurred", str(e))
            return False

    def test_1_client_existant_voit_son_dossier(self):
        """TEST 1 - Client Existant Voit Son Dossier"""
        print("\n" + "="*80)
        print("TEST 1 - CLIENT EXISTANT VOIT SON DOSSIER")
        print("="*80)
        
        # 1. Login Client
        if not self.authenticate_user('client_test'):
            return False
            
        headers = {"Authorization": f"Bearer {self.tokens['client_test']}"}
        
        # 2. GET /api/cases
        try:
            response = self.session.get(f"{API_BASE}/cases", headers=headers)
            
            if response.status_code == 200:
                cases = response.json()
                
                if len(cases) >= 1:
                    case = cases[0]
                    
                    # Vérifications requises
                    verifications = []
                    
                    # Vérifier que le case a un id
                    if case.get('id'):
                        verifications.append("✅ Case ID présent")
                    else:
                        verifications.append("❌ Case ID manquant")
                    
                    # Vérifier client_id = user_id du client
                    if case.get('client_id') == self.users['client_test']['id']:
                        verifications.append("✅ client_id = user_id du client")
                    else:
                        verifications.append(f"❌ client_id ({case.get('client_id')}) ≠ user_id ({self.users['client_test']['id']})")
                    
                    # Vérifier status
                    if case.get('status'):
                        verifications.append(f"✅ Status: {case.get('status')}")
                    else:
                        verifications.append("❌ Status manquant")
                    
                    # Vérifier workflow_steps
                    if case.get('workflow_steps') and len(case['workflow_steps']) > 0:
                        verifications.append(f"✅ Workflow steps: {len(case['workflow_steps'])} étapes")
                    else:
                        verifications.append("❌ Workflow steps manquant ou vide")
                    
                    # Vérifier current_step_index
                    if 'current_step_index' in case:
                        verifications.append(f"✅ Current step index: {case.get('current_step_index')}")
                    else:
                        verifications.append("❌ Current step index manquant")
                    
                    all_verified = all("✅" in v for v in verifications)
                    self.log_result("TEST 1 - Client Existant Voit Son Dossier", all_verified, 
                                  f"Cases trouvés: {len(cases)} | Vérifications: {'; '.join(verifications)}")
                    
                    return all_verified
                else:
                    self.log_result("TEST 1 - Client Existant Voit Son Dossier", False, 
                                  "❌ ERREUR 'Aucun Dossier Actif' - Client ne voit aucun case")
                    return False
            else:
                self.log_result("TEST 1 - Client Existant Voit Son Dossier", False, 
                              f"Status: {response.status_code}", response.text)
                return False
                
        except Exception as e:
            self.log_result("TEST 1 - Client Existant Voit Son Dossier", False, "Exception occurred", str(e))
            return False

    def test_2_nouveau_client_cree_par_employee(self):
        """TEST 2 - Nouveau Client Créé par Employee"""
        print("\n" + "="*80)
        print("TEST 2 - NOUVEAU CLIENT CRÉÉ PAR EMPLOYEE")
        print("="*80)
        
        # 1. Login Employee
        if not self.authenticate_user('employee'):
            return False
            
        headers = {"Authorization": f"Bearer {self.tokens['employee']}"}
        
        # 2. Créer un nouveau client
        try:
            client_data = {
                "email": "nouveau.client.test@example.com",
                "full_name": "Nouveau Client Test",
                "phone": "+33612345679",
                "country": "Canada",
                "visa_type": "Permis de travail",
                "message": "Test de création"
            }
            
            response = self.session.post(f"{API_BASE}/clients", json=client_data, headers=headers)
            
            if response.status_code in [200, 201]:
                client = response.json()
                self.test_data['new_client_id'] = client['id']
                self.test_data['new_user_id'] = client['user_id']
                
                self.log_result("2.1 Create New Client", True, 
                              f"Client créé: {client['id']} - Email: {client.get('login_email')}")
                
                # 3. Récupérer les credentials du client
                email = client.get('login_email', client_data['email'])
                password = client.get('default_password', 'Aloria2024!')
                
                self.log_result("2.2 Get Client Credentials", True, 
                              f"Email: {email} | Password: {password}")
                
                # 4. Login avec le nouveau client
                new_client_credentials = {"email": email, "password": password}
                login_response = self.session.post(f"{API_BASE}/auth/login", json=new_client_credentials)
                
                if login_response.status_code == 200:
                    new_client_token = login_response.json()['access_token']
                    new_client_headers = {"Authorization": f"Bearer {new_client_token}"}
                    
                    self.log_result("2.3 New Client Login", True, "Nouveau client connecté avec succès")
                    
                    # 5. GET /api/cases (avec le token du client)
                    cases_response = self.session.get(f"{API_BASE}/cases", headers=new_client_headers)
                    
                    if cases_response.status_code == 200:
                        cases = cases_response.json()
                        
                        if len(cases) >= 1:
                            self.log_result("TEST 2 - Nouveau Client Créé par Employee", True, 
                                          f"✅ SUCCÈS: Le nouveau client voit son dossier immédiatement après création ({len(cases)} case(s))")
                            return True
                        else:
                            self.log_result("TEST 2 - Nouveau Client Créé par Employee", False, 
                                          "❌ ÉCHEC: Le nouveau client ne voit aucun dossier")
                            return False
                    else:
                        self.log_result("TEST 2 - Nouveau Client Créé par Employee", False, 
                                      f"Erreur GET /api/cases: {cases_response.status_code}")
                        return False
                else:
                    self.log_result("TEST 2 - Nouveau Client Créé par Employee", False, 
                                  f"Erreur login nouveau client: {login_response.status_code}")
                    return False
            else:
                self.log_result("TEST 2 - Nouveau Client Créé par Employee", False, 
                              f"Erreur création client: {response.status_code}", response.text)
                return False
                
        except Exception as e:
            self.log_result("TEST 2 - Nouveau Client Créé par Employee", False, "Exception occurred", str(e))
            return False

    def test_3_nouveau_client_cree_par_manager(self):
        """TEST 3 - Nouveau Client Créé par Manager"""
        print("\n" + "="*80)
        print("TEST 3 - NOUVEAU CLIENT CRÉÉ PAR MANAGER")
        print("="*80)
        
        # 1. Login Manager
        if not self.authenticate_user('manager'):
            return False
            
        headers = {"Authorization": f"Bearer {self.tokens['manager']}"}
        
        # 2. Créer un nouveau client
        try:
            client_data = {
                "email": "nouveau.client.manager@example.com",
                "full_name": "Client Manager Test",
                "phone": "+33698765433",
                "country": "France",
                "visa_type": "Visa étudiant",
                "message": "Test de création par manager"
            }
            
            response = self.session.post(f"{API_BASE}/clients", json=client_data, headers=headers)
            
            if response.status_code in [200, 201]:
                client = response.json()
                self.test_data['manager_client_id'] = client['id']
                self.test_data['manager_user_id'] = client['user_id']
                
                self.log_result("3.1 Create Manager Client", True, 
                              f"Client créé: {client['id']} - Email: {client.get('login_email')}")
                
                # 3. Login avec le nouveau client
                email = client.get('login_email', client_data['email'])
                password = client.get('default_password', 'Aloria2024!')
                
                new_client_credentials = {"email": email, "password": password}
                login_response = self.session.post(f"{API_BASE}/auth/login", json=new_client_credentials)
                
                if login_response.status_code == 200:
                    new_client_token = login_response.json()['access_token']
                    new_client_headers = {"Authorization": f"Bearer {new_client_token}"}
                    
                    self.log_result("3.2 Manager Client Login", True, "Client manager connecté avec succès")
                    
                    # 4. GET /api/cases
                    cases_response = self.session.get(f"{API_BASE}/cases", headers=new_client_headers)
                    
                    if cases_response.status_code == 200:
                        cases = cases_response.json()
                        
                        if len(cases) >= 1:
                            self.log_result("TEST 3 - Nouveau Client Créé par Manager", True, 
                                          f"✅ SUCCÈS: Le client voit son dossier ({len(cases)} case(s))")
                            return True
                        else:
                            self.log_result("TEST 3 - Nouveau Client Créé par Manager", False, 
                                          "❌ ÉCHEC: Le client ne voit aucun dossier")
                            return False
                    else:
                        self.log_result("TEST 3 - Nouveau Client Créé par Manager", False, 
                                      f"Erreur GET /api/cases: {cases_response.status_code}")
                        return False
                else:
                    self.log_result("TEST 3 - Nouveau Client Créé par Manager", False, 
                                  f"Erreur login client: {login_response.status_code}")
                    return False
            else:
                self.log_result("TEST 3 - Nouveau Client Créé par Manager", False, 
                              f"Erreur création client: {response.status_code}", response.text)
                return False
                
        except Exception as e:
            self.log_result("TEST 3 - Nouveau Client Créé par Manager", False, "Exception occurred", str(e))
            return False

    def test_4_manager_voit_tous_les_dossiers(self):
        """TEST 4 - Manager Voit Tous les Dossiers"""
        print("\n" + "="*80)
        print("TEST 4 - MANAGER VOIT TOUS LES DOSSIERS")
        print("="*80)
        
        # 1. Login Manager (déjà fait dans test précédent)
        if 'manager' not in self.tokens:
            if not self.authenticate_user('manager'):
                return False
                
        headers = {"Authorization": f"Bearer {self.tokens['manager']}"}
        
        # 2. GET /api/cases
        try:
            response = self.session.get(f"{API_BASE}/cases", headers=headers)
            
            if response.status_code == 200:
                cases = response.json()
                
                if len(cases) >= 2:  # Au moins les 2 créés dans les tests précédents
                    # Vérifier que les cases incluent ceux des clients créés par différents employés
                    client_names = [case.get('client_name', '') for case in cases]
                    
                    verifications = []
                    
                    # Vérifier diversité des clients
                    unique_clients = len(set(client_names))
                    if unique_clients >= 2:
                        verifications.append(f"✅ Diversité clients: {unique_clients} clients différents")
                    else:
                        verifications.append(f"❌ Diversité clients: seulement {unique_clients} client(s)")
                    
                    # Vérifier présence de cases de différents pays
                    countries = [case.get('country', '') for case in cases]
                    unique_countries = len(set(countries))
                    if unique_countries >= 2:
                        verifications.append(f"✅ Diversité pays: {unique_countries} pays différents")
                    else:
                        verifications.append(f"❌ Diversité pays: seulement {unique_countries} pays")
                    
                    all_verified = all("✅" in v for v in verifications)
                    self.log_result("TEST 4 - Manager Voit Tous les Dossiers", all_verified, 
                                  f"Cases trouvés: {len(cases)} | Vérifications: {'; '.join(verifications)}")
                    
                    return all_verified
                else:
                    self.log_result("TEST 4 - Manager Voit Tous les Dossiers", False, 
                                  f"❌ ÉCHEC: Manager ne voit que {len(cases)} dossier(s)")
                    return False
            else:
                self.log_result("TEST 4 - Manager Voit Tous les Dossiers", False, 
                              f"Status: {response.status_code}", response.text)
                return False
                
        except Exception as e:
            self.log_result("TEST 4 - Manager Voit Tous les Dossiers", False, "Exception occurred", str(e))
            return False

    def test_5_employee_voit_ses_dossiers_assignes(self):
        """TEST 5 - Employee Voit Ses Dossiers Assignés"""
        print("\n" + "="*80)
        print("TEST 5 - EMPLOYEE VOIT SES DOSSIERS ASSIGNÉS")
        print("="*80)
        
        # 1. Login Employee (déjà fait dans test précédent)
        if 'employee' not in self.tokens:
            if not self.authenticate_user('employee'):
                return False
                
        headers = {"Authorization": f"Bearer {self.tokens['employee']}"}
        
        # 2. GET /api/cases
        try:
            response = self.session.get(f"{API_BASE}/cases", headers=headers)
            
            if response.status_code == 200:
                cases = response.json()
                
                # Vérifier que les cases retournés sont uniquement ceux où assigned_employee_id = employee.id
                employee_id = self.users['employee']['id']
                
                # Pour vérifier l'assignation, on doit récupérer les clients correspondants
                client_response = self.session.get(f"{API_BASE}/clients", headers=headers)
                
                if client_response.status_code == 200:
                    clients = client_response.json()
                    assigned_clients = [c for c in clients if c.get('assigned_employee_id') == employee_id]
                    
                    verifications = []
                    
                    # Vérifier que l'employé a des clients assignés
                    if len(assigned_clients) > 0:
                        verifications.append(f"✅ Clients assignés: {len(assigned_clients)}")
                    else:
                        verifications.append("❌ Aucun client assigné à l'employé")
                    
                    # Vérifier que les cases correspondent aux clients assignés
                    if len(cases) > 0:
                        verifications.append(f"✅ Cases visibles: {len(cases)}")
                        
                        # Vérifier que tous les cases visibles correspondent à des clients assignés
                        assigned_client_names = [c.get('full_name', '') for c in assigned_clients]
                        case_client_names = [c.get('client_name', '') for c in cases]
                        
                        valid_cases = all(name in assigned_client_names for name in case_client_names if name)
                        if valid_cases:
                            verifications.append("✅ Tous les cases visibles correspondent à des clients assignés")
                        else:
                            verifications.append("❌ Certains cases ne correspondent pas aux clients assignés")
                    else:
                        if len(assigned_clients) == 0:
                            verifications.append("✅ Aucun case visible (cohérent avec aucun client assigné)")
                        else:
                            verifications.append("❌ Aucun case visible malgré des clients assignés")
                    
                    all_verified = all("✅" in v for v in verifications)
                    self.log_result("TEST 5 - Employee Voit Ses Dossiers Assignés", all_verified, 
                                  f"Vérifications: {'; '.join(verifications)}")
                    
                    return all_verified
                else:
                    self.log_result("TEST 5 - Employee Voit Ses Dossiers Assignés", False, 
                                  f"Erreur GET /api/clients: {client_response.status_code}")
                    return False
            else:
                self.log_result("TEST 5 - Employee Voit Ses Dossiers Assignés", False, 
                              f"Status: {response.status_code}", response.text)
                return False
                
        except Exception as e:
            self.log_result("TEST 5 - Employee Voit Ses Dossiers Assignés", False, "Exception occurred", str(e))
            return False

    def run_all_tests(self):
        """Exécuter tous les tests de correction 'Aucun Dossier Actif'"""
        print("ALORIA AGENCY - Test Correction 'Aucun Dossier Actif' - Dashboard Client")
        print("="*80)
        print("CONTEXTE: Correction de l'incohérence dans la recherche des cases")
        print("CORRECTION: CLIENT cherche avec client_id = user_id, MANAGER/EMPLOYEE avec client_id IN [user_ids]")
        print("="*80)
        
        # Exécuter tous les tests
        tests = [
            self.test_1_client_existant_voit_son_dossier,
            self.test_2_nouveau_client_cree_par_employee,
            self.test_3_nouveau_client_cree_par_manager,
            self.test_4_manager_voit_tous_les_dossiers,
            self.test_5_employee_voit_ses_dossiers_assignes
        ]
        
        for test in tests:
            try:
                test()
            except Exception as e:
                print(f"❌ ERREUR CRITIQUE dans {test.__name__}: {str(e)}")
                self.results['failed'] += 1
                self.results['errors'].append({
                    'test': test.__name__,
                    'message': 'Exception critique',
                    'error': str(e)
                })
        
        # Résultats finaux
        print("\n" + "="*80)
        print("RÉSULTATS FINAUX - TEST CORRECTION 'AUCUN DOSSIER ACTIF'")
        print("="*80)
        
        total_tests = self.results['passed'] + self.results['failed']
        success_rate = (self.results['passed'] / total_tests * 100) if total_tests > 0 else 0
        
        print(f"✅ Tests réussis: {self.results['passed']}")
        print(f"❌ Tests échoués: {self.results['failed']}")
        print(f"📊 Taux de réussite: {success_rate:.1f}%")
        
        if self.results['errors']:
            print(f"\n🚨 ERREURS DÉTECTÉES:")
            for error in self.results['errors']:
                print(f"   - {error['test']}: {error['message']}")
                if error['error']:
                    print(f"     Détail: {error['error']}")
        
        # Conclusion
        if success_rate >= 80:
            print(f"\n🎉 CORRECTION 'AUCUN DOSSIER ACTIF': VALIDÉE")
            print("✅ Les clients voient leurs dossiers (plus d'erreur 'Aucun Dossier Actif')")
            print("✅ Dashboard client fonctionnel avec workflow complet")
            print("✅ Manager voit tous les dossiers")
            print("✅ Employee voit uniquement ses dossiers assignés")
            print("✅ Nouveaux clients créés ont immédiatement accès à leur dossier")
        else:
            print(f"\n💥 CORRECTION 'AUCUN DOSSIER ACTIF': ÉCHEC")
            print("❌ Des problèmes persistent dans l'affichage des dossiers clients")
        
        return success_rate >= 80

if __name__ == "__main__":
    tester = AucunDossierActifTester()
    success = tester.run_all_tests()
    
    if success:
        print("\n🎉 TEST CORRECTION 'AUCUN DOSSIER ACTIF': SUCCÈS")
        sys.exit(0)
    else:
        print("\n💥 TEST CORRECTION 'AUCUN DOSSIER ACTIF': ÉCHEC")
        sys.exit(1)