#!/usr/bin/env python3
"""
ALORIA AGENCY - Test Complet Création Client + Login + Dashboard - Workflow E2E

CONTEXTE:
L'utilisateur rapporte que quand un Manager ou Employee crée un client (ou convertit un prospect), 
le client est bien créé, mais quand il se connecte avec les identifiants fournis (email + mot de passe généré), 
il voit l'erreur "Aucun Dossier Actif" au lieu d'accéder au dashboard client avec workflow complet.

CORRECTION DÉJÀ APPLIQUÉE:
Ligne 1398-1404 de server.py - CLIENT cherche cases avec `client_id = current_user["id"]` (son user_id)

WORKFLOW COMPLET À TESTER:
1. SCÉNARIO 1 - Employee Crée un Client Nouveau
2. SCÉNARIO 2 - Manager Convertit un Prospect en Client
3. Tests de diagnostic MongoDB et API
"""

import requests
import json
import os
import time
from datetime import datetime
import sys
import uuid

# Configuration
BACKEND_URL = os.environ.get('REACT_APP_BACKEND_URL', 'https://aloria-dev.preview.emergentagent.com')
API_BASE = f"{BACKEND_URL}/api"

# Credentials from review request
CREDENTIALS = {
    'manager': {'email': 'manager@test.com', 'password': 'password123'},
    'employee': {'email': 'employee@aloria.com', 'password': 'emp123'},
    'default_client_password': 'Aloria2024!'
}

class ClientWorkflowTester:
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

    def authenticate_users(self):
        """Authenticate required users"""
        print("=== AUTHENTICATION SETUP ===")
        
        for role, credentials in CREDENTIALS.items():
            if role == 'default_client_password':
                continue
                
            try:
                response = self.session.post(f"{API_BASE}/auth/login", json=credentials)
                if response.status_code == 200:
                    data = response.json()
                    self.tokens[role] = data['access_token']
                    self.users[role] = data['user']
                    self.log_result(f"{role.upper()} Login", True, 
                                  f"Logged in as {credentials['email']} - Role: {data['user']['role']}")
                else:
                    self.log_result(f"{role.upper()} Login", False, 
                                  f"Status: {response.status_code}", response.text)
                    return False
            except Exception as e:
                self.log_result(f"{role.upper()} Login", False, "Exception occurred", str(e))
                return False
        return True

    def scenario_1_employee_creates_client(self):
        """SCÉNARIO 1 - Employee Crée un Client Nouveau"""
        print("\n" + "="*80)
        print("SCÉNARIO 1 - EMPLOYEE CRÉE UN CLIENT NOUVEAU")
        print("="*80)
        
        if 'employee' not in self.tokens:
            self.log_result("Scenario 1 Setup", False, "Employee token not available")
            return False
        
        try:
            # 1. Employee crée un nouveau client
            print("\n🔸 ÉTAPE 1.1 - Employee crée un nouveau client")
            headers = {"Authorization": f"Bearer {self.tokens['employee']}"}
            
            # Generate unique email for this test
            unique_id = str(uuid.uuid4())[:8]
            client_data = {
                "email": f"test.workflow.client.{unique_id}@example.com",
                "full_name": "Test Workflow Client",
                "phone": "+33699887766",
                "country": "Canada",
                "visa_type": "Permis de travail",
                "message": "Test création workflow complet"
            }
            
            create_response = self.session.post(f"{API_BASE}/clients", json=client_data, headers=headers)
            
            if create_response.status_code == 200:
                client_created = create_response.json()
                
                # Store client info for later tests
                self.test_data['scenario1_client'] = {
                    'email': client_data['email'],
                    'user_id': client_created['user_id'],
                    'client_id': client_created['id'],
                    'password': client_created.get('default_password', 'Aloria2024!')
                }
                
                self.log_result("1.1 Employee Creates Client", True, 
                              f"Client créé: {client_data['email']} (user_id: {client_created['user_id']})")
                
                # 2. Vérifier que le client a un case créé
                print("\n🔸 ÉTAPE 1.2 - Vérifier que le case est créé")
                
                # Use manager token to check cases (broader access)
                manager_headers = {"Authorization": f"Bearer {self.tokens['manager']}"}
                cases_response = self.session.get(f"{API_BASE}/cases", headers=manager_headers)
                
                if cases_response.status_code == 200:
                    all_cases = cases_response.json()
                    
                    # Find case for this client (client_id should match user_id)
                    client_cases = [case for case in all_cases if case.get('client_id') == client_created['user_id']]
                    
                    if client_cases:
                        case = client_cases[0]
                        self.test_data['scenario1_case'] = case
                        
                        # Verify case has workflow_steps
                        if case.get('workflow_steps') and len(case['workflow_steps']) > 0:
                            self.log_result("1.2 Case Created with Workflow", True, 
                                          f"Case trouvé avec {len(case['workflow_steps'])} étapes de workflow")
                        else:
                            self.log_result("1.2 Case Created with Workflow", False, 
                                          "Case trouvé mais workflow_steps vide ou manquant")
                            return False
                    else:
                        self.log_result("1.2 Case Created with Workflow", False, 
                                      f"Aucun case trouvé pour client_id={client_created['user_id']}")
                        return False
                else:
                    self.log_result("1.2 Case Created with Workflow", False, 
                                  f"Erreur récupération cases: {cases_response.status_code}")
                    return False
                
                # 3. Login CLIENT avec les credentials fournis
                print("\n🔸 ÉTAPE 1.3 - Login CLIENT avec credentials fournis")
                client_credentials = {
                    "email": client_data['email'],
                    "password": self.test_data['scenario1_client']['password']
                }
                
                client_login_response = self.session.post(f"{API_BASE}/auth/login", json=client_credentials)
                
                if client_login_response.status_code == 200:
                    client_auth = client_login_response.json()
                    client_token = client_auth['access_token']
                    
                    if client_auth['user']['role'] == 'CLIENT':
                        self.log_result("1.3 Client Login", True, 
                                      f"Client connecté: {client_auth['user']['full_name']} (role: {client_auth['user']['role']})")
                        
                        # 4. GET /api/cases avec token client - TEST CRITIQUE
                        print("\n🔸 ÉTAPE 1.4 - GET /api/cases avec token client (TEST CRITIQUE)")
                        client_headers = {"Authorization": f"Bearer {client_token}"}
                        client_cases_response = self.session.get(f"{API_BASE}/cases", headers=client_headers)
                        
                        if client_cases_response.status_code == 200:
                            client_cases = client_cases_response.json()
                            
                            if len(client_cases) >= 1:
                                case = client_cases[0]
                                
                                # Verify case details
                                required_fields = ['id', 'client_id', 'status', 'workflow_steps', 'current_step_index', 'country', 'visa_type']
                                missing_fields = [field for field in required_fields if field not in case]
                                
                                if not missing_fields:
                                    self.log_result("1.4 Client Cases Access - CRITIQUE", True, 
                                                  f"✅ SUCCESS: Client voit {len(client_cases)} case(s) avec workflow complet")
                                    
                                    # Log case details for verification
                                    print(f"   📋 Case Details:")
                                    print(f"      - ID: {case['id']}")
                                    print(f"      - Client ID: {case['client_id']}")
                                    print(f"      - Status: {case['status']}")
                                    print(f"      - Country: {case['country']}")
                                    print(f"      - Visa Type: {case['visa_type']}")
                                    print(f"      - Workflow Steps: {len(case['workflow_steps'])}")
                                    print(f"      - Current Step: {case['current_step_index']}")
                                    
                                else:
                                    self.log_result("1.4 Client Cases Access - CRITIQUE", False, 
                                                  f"Case trouvé mais champs manquants: {missing_fields}")
                                    return False
                            else:
                                self.log_result("1.4 Client Cases Access - CRITIQUE", False, 
                                              f"❌ PROBLÈME CRITIQUE: Client voit {len(client_cases)} cases (attendu: >= 1)")
                                print(f"   🔍 DIAGNOSTIC: Response content: {client_cases}")
                                return False
                        else:
                            self.log_result("1.4 Client Cases Access - CRITIQUE", False, 
                                          f"Erreur API: {client_cases_response.status_code}", client_cases_response.text)
                            return False
                    else:
                        self.log_result("1.3 Client Login", False, 
                                      f"Role incorrect: {client_auth['user']['role']} (attendu: CLIENT)")
                        return False
                else:
                    self.log_result("1.3 Client Login", False, 
                                  f"Login échoué: {client_login_response.status_code}", client_login_response.text)
                    return False
            else:
                self.log_result("1.1 Employee Creates Client", False, 
                              f"Création client échouée: {create_response.status_code}", create_response.text)
                return False
                
        except Exception as e:
            self.log_result("Scenario 1 Exception", False, "Exception occurred", str(e))
            return False
        
        return True

    def scenario_2_manager_converts_prospect(self):
        """SCÉNARIO 2 - Manager Convertit un Prospect en Client"""
        print("\n" + "="*80)
        print("SCÉNARIO 2 - MANAGER CONVERTIT UN PROSPECT EN CLIENT")
        print("="*80)
        
        if 'manager' not in self.tokens:
            self.log_result("Scenario 2 Setup", False, "Manager token not available")
            return False
        
        try:
            # 1. Manager crée un prospect
            print("\n🔸 ÉTAPE 2.1 - Manager crée un prospect")
            headers = {"Authorization": f"Bearer {self.tokens['manager']}"}
            
            # Generate unique email for this test
            unique_id = str(uuid.uuid4())[:8]
            prospect_data = {
                "name": "Prospect Conversion Test",
                "email": f"prospect.conversion.{unique_id}@example.com",
                "phone": "+33688776655",
                "country": "France",
                "visa_type": "Visa étudiant",
                "message": "Test conversion prospect → client",
                "urgency_level": "Normal",
                "lead_source": "Site web",
                "how_did_you_know": "Recherche Google"
            }
            
            prospect_response = self.session.post(f"{API_BASE}/contact-messages", json=prospect_data, headers=headers)
            
            if prospect_response.status_code == 200:
                prospect_created = prospect_response.json()
                message_id = prospect_created['id']
                
                self.log_result("2.1 Manager Creates Prospect", True, 
                              f"Prospect créé: {prospect_data['email']} (ID: {message_id})")
                
                # 2. Manager convertit le prospect en client
                print("\n🔸 ÉTAPE 2.2 - Manager convertit prospect en client")
                
                conversion_data = {
                    "first_payment_amount": 50000,
                    "payment_method": "Virement bancaire",
                    "country": "France",
                    "visa_type": "Visa étudiant"
                }
                
                convert_response = self.session.post(
                    f"{API_BASE}/contact-messages/{message_id}/convert-to-client", 
                    json=conversion_data, 
                    headers=headers
                )
                
                if convert_response.status_code == 200:
                    conversion_result = convert_response.json()
                    
                    # Store client info for later tests
                    self.test_data['scenario2_client'] = {
                        'email': prospect_data['email'],
                        'user_id': conversion_result.get('user_id'),
                        'client_id': conversion_result.get('client_id'),
                        'password': 'Aloria2024!'  # Default password
                    }
                    
                    self.log_result("2.2 Manager Converts Prospect", True, 
                                  f"Prospect converti en client (user_id: {conversion_result.get('user_id')})")
                    
                    # 3. Login CLIENT avec les credentials
                    print("\n🔸 ÉTAPE 2.3 - Login CLIENT converti")
                    client_credentials = {
                        "email": prospect_data['email'],
                        "password": 'Aloria2024!'
                    }
                    
                    client_login_response = self.session.post(f"{API_BASE}/auth/login", json=client_credentials)
                    
                    if client_login_response.status_code == 200:
                        client_auth = client_login_response.json()
                        client_token = client_auth['access_token']
                        
                        self.log_result("2.3 Converted Client Login", True, 
                                      f"Client converti connecté: {client_auth['user']['full_name']}")
                        
                        # 4. GET /api/cases avec token client - TEST CRITIQUE
                        print("\n🔸 ÉTAPE 2.4 - GET /api/cases pour client converti (TEST CRITIQUE)")
                        client_headers = {"Authorization": f"Bearer {client_token}"}
                        client_cases_response = self.session.get(f"{API_BASE}/cases", headers=client_headers)
                        
                        if client_cases_response.status_code == 200:
                            client_cases = client_cases_response.json()
                            
                            if len(client_cases) >= 1:
                                case = client_cases[0]
                                
                                # Verify France workflow for "Visa étudiant"
                                if (case.get('country') == 'France' and 
                                    case.get('visa_type') == 'Visa étudiant' and
                                    case.get('workflow_steps') and 
                                    len(case['workflow_steps']) > 0):
                                    
                                    self.log_result("2.4 Converted Client Cases Access - CRITIQUE", True, 
                                                  f"✅ SUCCESS: Client converti voit case avec workflow France ({len(case['workflow_steps'])} étapes)")
                                    
                                    # Log case details
                                    print(f"   📋 Converted Client Case Details:")
                                    print(f"      - Country: {case['country']}")
                                    print(f"      - Visa Type: {case['visa_type']}")
                                    print(f"      - Workflow Steps: {len(case['workflow_steps'])}")
                                    print(f"      - Status: {case['status']}")
                                    
                                else:
                                    self.log_result("2.4 Converted Client Cases Access - CRITIQUE", False, 
                                                  f"Case trouvé mais workflow France incorrect")
                                    return False
                            else:
                                self.log_result("2.4 Converted Client Cases Access - CRITIQUE", False, 
                                              f"❌ PROBLÈME CRITIQUE: Client converti voit {len(client_cases)} cases (attendu: >= 1)")
                                return False
                        else:
                            self.log_result("2.4 Converted Client Cases Access - CRITIQUE", False, 
                                          f"Erreur API: {client_cases_response.status_code}")
                            return False
                    else:
                        self.log_result("2.3 Converted Client Login", False, 
                                      f"Login client converti échoué: {client_login_response.status_code}")
                        return False
                else:
                    self.log_result("2.2 Manager Converts Prospect", False, 
                                  f"Conversion échouée: {convert_response.status_code}", convert_response.text)
                    return False
            else:
                self.log_result("2.1 Manager Creates Prospect", False, 
                              f"Création prospect échouée: {prospect_response.status_code}", prospect_response.text)
                return False
                
        except Exception as e:
            self.log_result("Scenario 2 Exception", False, "Exception occurred", str(e))
            return False
        
        return True

    def diagnostic_tests(self):
        """Tests de diagnostic pour identifier les problèmes"""
        print("\n" + "="*80)
        print("TESTS DE DIAGNOSTIC")
        print("="*80)
        
        try:
            # Test A - Vérifier endpoint GET /api/cases avec différents tokens
            print("\n🔸 TEST A - Vérifier endpoint GET /api/cases")
            
            for role in ['manager', 'employee']:
                if role in self.tokens:
                    headers = {"Authorization": f"Bearer {self.tokens[role]}"}
                    response = self.session.get(f"{API_BASE}/cases", headers=headers)
                    
                    if response.status_code == 200:
                        cases = response.json()
                        self.log_result(f"A.{role.upper()} Cases Access", True, 
                                      f"{role.upper()} voit {len(cases)} cases")
                    else:
                        self.log_result(f"A.{role.upper()} Cases Access", False, 
                                      f"Status: {response.status_code}")
            
            # Test B - Vérifier structure des cases
            if 'manager' in self.tokens:
                print("\n🔸 TEST B - Vérifier structure des cases")
                headers = {"Authorization": f"Bearer {self.tokens['manager']}"}
                response = self.session.get(f"{API_BASE}/cases", headers=headers)
                
                if response.status_code == 200:
                    cases = response.json()
                    if cases:
                        case = cases[0]
                        required_fields = ['id', 'client_id', 'workflow_steps', 'status']
                        missing_fields = [field for field in required_fields if field not in case]
                        
                        if not missing_fields:
                            self.log_result("B. Case Structure", True, 
                                          f"Structure case correcte: {list(case.keys())}")
                        else:
                            self.log_result("B. Case Structure", False, 
                                          f"Champs manquants: {missing_fields}")
                    else:
                        self.log_result("B. Case Structure", False, "Aucun case trouvé")
                else:
                    self.log_result("B. Case Structure", False, f"Status: {response.status_code}")
            
            # Test C - Vérifier create_client_profile function
            print("\n🔸 TEST C - Vérifier création de client simple")
            if 'manager' in self.tokens:
                headers = {"Authorization": f"Bearer {self.tokens['manager']}"}
                
                # Create a simple test client
                unique_id = str(uuid.uuid4())[:8]
                test_client_data = {
                    "email": f"diagnostic.test.{unique_id}@example.com",
                    "full_name": "Diagnostic Test Client",
                    "phone": "+33600000000",
                    "country": "Canada",
                    "visa_type": "Permis de travail",
                    "message": "Test diagnostic"
                }
                
                create_response = self.session.post(f"{API_BASE}/clients", json=test_client_data, headers=headers)
                
                if create_response.status_code == 200:
                    client_created = create_response.json()
                    
                    # Immediately check if case was created
                    time.sleep(2)  # Wait for case creation
                    cases_response = self.session.get(f"{API_BASE}/cases", headers=headers)
                    
                    if cases_response.status_code == 200:
                        all_cases = cases_response.json()
                        client_cases = [case for case in all_cases if case.get('client_id') == client_created['user_id']]
                        
                        if client_cases:
                            self.log_result("C. Client Creation with Case", True, 
                                          f"Client créé avec case automatique (user_id: {client_created['user_id']})")
                        else:
                            self.log_result("C. Client Creation with Case", False, 
                                          f"Client créé mais aucun case trouvé pour user_id: {client_created['user_id']}")
                    else:
                        self.log_result("C. Client Creation with Case", False, 
                                      "Erreur récupération cases après création client")
                else:
                    self.log_result("C. Client Creation with Case", False, 
                                  f"Création client échouée: {create_response.status_code}")
                    
        except Exception as e:
            self.log_result("Diagnostic Tests Exception", False, "Exception occurred", str(e))
            return False
        
        return True

    def run_complete_workflow_tests(self):
        """Exécuter tous les tests de workflow complet"""
        print("ALORIA AGENCY - Test Complet Création Client + Login + Dashboard - Workflow E2E")
        print("Test du workflow complet de création client et accès dashboard")
        print("="*80)
        
        # Authentication
        if not self.authenticate_users():
            print("❌ ÉCHEC: Impossible d'authentifier les utilisateurs")
            return False
        
        # Scenario 1: Employee Creates Client
        scenario1_success = self.scenario_1_employee_creates_client()
        
        # Scenario 2: Manager Converts Prospect
        scenario2_success = self.scenario_2_manager_converts_prospect()
        
        # Diagnostic Tests
        diagnostic_success = self.diagnostic_tests()
        
        # Résultats finaux
        print("\n" + "="*80)
        print("RÉSULTATS FINAUX")
        print("="*80)
        
        total_tests = self.results['passed'] + self.results['failed']
        success_rate = (self.results['passed'] / total_tests * 100) if total_tests > 0 else 0
        
        print(f"✅ Tests réussis: {self.results['passed']}")
        print(f"❌ Tests échoués: {self.results['failed']}")
        print(f"📊 Taux de réussite: {success_rate:.1f}%")
        
        # Summary of critical tests
        print(f"\n📋 RÉSUMÉ DES TESTS CRITIQUES:")
        print(f"   🔸 Scénario 1 (Employee → Client): {'✅ SUCCÈS' if scenario1_success else '❌ ÉCHEC'}")
        print(f"   🔸 Scénario 2 (Manager → Prospect → Client): {'✅ SUCCÈS' if scenario2_success else '❌ ÉCHEC'}")
        print(f"   🔸 Tests de diagnostic: {'✅ SUCCÈS' if diagnostic_success else '❌ ÉCHEC'}")
        
        if self.results['errors']:
            print(f"\n🚨 ERREURS CRITIQUES DÉTECTÉES:")
            for error in self.results['errors']:
                if 'CRITIQUE' in error['test']:
                    print(f"   ❌ {error['test']}: {error['message']}")
        
        # Provide diagnostic information if tests failed
        if not scenario1_success or not scenario2_success:
            print(f"\n🔍 INFORMATIONS DE DIAGNOSTIC:")
            if 'scenario1_client' in self.test_data:
                client = self.test_data['scenario1_client']
                print(f"   📧 Client Scénario 1: {client['email']} (user_id: {client['user_id']})")
            if 'scenario2_client' in self.test_data:
                client = self.test_data['scenario2_client']
                print(f"   📧 Client Scénario 2: {client['email']} (user_id: {client['user_id']})")
            
            print(f"\n💡 ACTIONS RECOMMANDÉES:")
            print(f"   1. Vérifier MongoDB: db.cases.find({{\"client_id\": \"{{user_id}}\"}}) pour les user_ids ci-dessus")
            print(f"   2. Vérifier que create_client_profile() crée bien un case avec workflow_steps")
            print(f"   3. Vérifier que GET /api/cases filtre correctement par client_id = current_user['id']")
        
        return success_rate >= 80  # Considérer comme succès si >= 80%

if __name__ == "__main__":
    tester = ClientWorkflowTester()
    success = tester.run_complete_workflow_tests()
    
    if success:
        print("\n🎉 TEST WORKFLOW CLIENT COMPLET: SUCCÈS")
        sys.exit(0)
    else:
        print("\n💥 TEST WORKFLOW CLIENT COMPLET: ÉCHEC")
        sys.exit(1)