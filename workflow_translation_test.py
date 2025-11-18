#!/usr/bin/env python3
"""
Test spécifique pour vérifier que les workflows traduits fonctionnent correctement
Teste que GET /api/workflows retourne bien les données en français
"""

import requests
import json
import os
from datetime import datetime

# Get backend URL from environment
BACKEND_URL = os.environ.get('REACT_APP_BACKEND_URL', 'https://aloria-dev.preview.emergentagent.com')
API_BASE = f"{BACKEND_URL}/api"

# Test credentials
TEST_CREDENTIALS = {
    'manager': {'email': 'manager@test.com', 'password': 'password123'}
}

class WorkflowTranslationTester:
    def __init__(self):
        self.session = requests.Session()
        self.manager_token = None
        self.results = {
            'passed': 0,
            'failed': 0,
            'errors': []
        }

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

    def authenticate(self):
        """Authenticate as manager"""
        print("=== AUTHENTICATION ===")
        
        try:
            response = self.session.post(f"{API_BASE}/auth/login", json=TEST_CREDENTIALS['manager'])
            if response.status_code == 200:
                data = response.json()
                self.manager_token = data['access_token']
                self.log_result("Manager Login", True, f"Logged in as {TEST_CREDENTIALS['manager']['email']}")
                return True
            else:
                self.log_result("Manager Login", False, f"Status: {response.status_code}", response.text)
                return False
        except Exception as e:
            self.log_result("Manager Login", False, "Exception occurred", str(e))
            return False

    def test_workflows_api_french(self):
        """Test 1: Vérifier que GET /api/workflows retourne bien les données en français"""
        print("=== TEST 1: API WORKFLOWS EN FRANÇAIS ===")
        
        try:
            response = self.session.get(f"{API_BASE}/workflows")
            if response.status_code == 200:
                workflows = response.json()
                self.log_result("1.1 GET /api/workflows", True, f"API accessible, {len(workflows)} pays trouvés")
                
                # Vérifier que "Permis de travail" existe pour Canada
                canada_workflows = workflows.get('Canada', {})
                if 'Permis de travail' in canada_workflows:
                    self.log_result("1.2 Permis de travail Canada", True, "Workflow 'Permis de travail' trouvé pour Canada")
                    
                    # Vérifier qu'une étape contient "Consultation initiale" et "jours"
                    permis_travail_steps = canada_workflows['Permis de travail']
                    consultation_found = False
                    jours_found = False
                    
                    for step in permis_travail_steps:
                        if 'Consultation initiale' in step.get('title', ''):
                            consultation_found = True
                        if 'jours' in step.get('duration', ''):
                            jours_found = True
                    
                    if consultation_found:
                        self.log_result("1.3 Consultation initiale", True, "Étape 'Consultation initiale' trouvée")
                    else:
                        self.log_result("1.3 Consultation initiale", False, "Étape 'Consultation initiale' non trouvée")
                    
                    if jours_found:
                        self.log_result("1.4 Durée en jours", True, "Durée contenant 'jours' trouvée")
                    else:
                        self.log_result("1.4 Durée en jours", False, "Aucune durée contenant 'jours' trouvée")
                        
                else:
                    self.log_result("1.2 Permis de travail Canada", False, "Workflow 'Permis de travail' non trouvé pour Canada")
                
                # Vérifier que "Visa étudiant" existe pour France
                france_workflows = workflows.get('France', {})
                if 'Visa étudiant' in france_workflows:
                    self.log_result("1.5 Visa étudiant France", True, "Workflow 'Visa étudiant' trouvé pour France")
                    
                    # Vérifier qu'une étape contient "Consultation initiale"
                    visa_etudiant_steps = france_workflows['Visa étudiant']
                    consultation_found = False
                    
                    for step in visa_etudiant_steps:
                        if 'Consultation initiale' in step.get('title', ''):
                            consultation_found = True
                            break
                    
                    if consultation_found:
                        self.log_result("1.6 Consultation initiale France", True, "Étape 'Consultation initiale' trouvée pour Visa étudiant France")
                    else:
                        self.log_result("1.6 Consultation initiale France", False, "Étape 'Consultation initiale' non trouvée pour Visa étudiant France")
                        
                else:
                    self.log_result("1.5 Visa étudiant France", False, "Workflow 'Visa étudiant' non trouvé pour France")
                    
            else:
                self.log_result("1.1 GET /api/workflows", False, f"Status: {response.status_code}", response.text)
        except Exception as e:
            self.log_result("1.1 GET /api/workflows", False, "Exception occurred", str(e))

    def test_case_creation_french(self):
        """Test 2: Vérifier qu'un nouveau dossier créé utilise les nouveaux noms français"""
        print("=== TEST 2: CRÉATION DE DOSSIER AVEC NOMS FRANÇAIS ===")
        
        if not self.manager_token:
            self.log_result("2.1 Case Creation Test", False, "No manager token available")
            return
        
        try:
            headers = {"Authorization": f"Bearer {self.manager_token}"}
            
            # Créer un client avec workflow français
            timestamp = int(datetime.now().timestamp())
            client_data = {
                "email": f"test.client.french.{timestamp}@example.com",
                "full_name": "Client Test Français",
                "phone": "+33123456789",
                "country": "France",
                "visa_type": "Visa étudiant",
                "message": "Test création dossier avec workflow français"
            }
            
            response = self.session.post(f"{API_BASE}/clients", json=client_data, headers=headers)
            if response.status_code in [200, 201]:
                client_result = response.json()
                client_id = client_result['id']
                self.log_result("2.1 Client Creation", True, f"Client créé avec ID: {client_id}")
                
                # Récupérer les dossiers pour vérifier le workflow
                cases_response = self.session.get(f"{API_BASE}/cases", headers=headers)
                if cases_response.status_code == 200:
                    cases = cases_response.json()
                    
                    # Trouver le dossier du client créé
                    test_case = None
                    for case in cases:
                        if case['client_id'] == client_id:
                            test_case = case
                            break
                    
                    if test_case:
                        workflow_steps = test_case.get('workflow_steps', [])
                        if workflow_steps:
                            # Vérifier que les étapes sont en français
                            french_terms_found = []
                            
                            for step in workflow_steps:
                                title = step.get('title', '')
                                if 'Consultation initiale' in title:
                                    french_terms_found.append('Consultation initiale')
                                if 'visa' in title.lower():
                                    french_terms_found.append('visa')
                                if 'étudiant' in title.lower():
                                    french_terms_found.append('étudiant')
                            
                            if french_terms_found:
                                self.log_result("2.2 Workflow Steps French", True, f"Termes français trouvés: {', '.join(french_terms_found)}")
                            else:
                                self.log_result("2.2 Workflow Steps French", False, "Aucun terme français spécifique trouvé dans les étapes")
                            
                            # Vérifier le visa_type du dossier
                            if test_case.get('visa_type') == 'Visa étudiant':
                                self.log_result("2.3 Case Visa Type", True, f"Type de visa: '{test_case['visa_type']}'")
                            else:
                                self.log_result("2.3 Case Visa Type", False, f"Type de visa attendu: 'Visa étudiant', trouvé: '{test_case.get('visa_type')}'")
                                
                        else:
                            self.log_result("2.2 Workflow Steps", False, "Aucune étape de workflow trouvée")
                    else:
                        self.log_result("2.2 Find Case", False, "Dossier du client créé non trouvé")
                else:
                    self.log_result("2.2 Get Cases", False, f"Status: {cases_response.status_code}", cases_response.text)
                    
            else:
                self.log_result("2.1 Client Creation", False, f"Status: {response.status_code}", response.text)
                
        except Exception as e:
            self.log_result("2.1 Case Creation Test", False, "Exception occurred", str(e))

    def run_all_tests(self):
        """Exécuter tous les tests"""
        print("🇫🇷 TESTS DE TRADUCTION DES WORKFLOWS - ALORIA AGENCY")
        print("=" * 60)
        
        if not self.authenticate():
            print("❌ Impossible de s'authentifier, arrêt des tests")
            return
        
        self.test_workflows_api_french()
        self.test_case_creation_french()
        
        # Résumé final
        print("=" * 60)
        print("📊 RÉSUMÉ DES TESTS")
        print(f"✅ Tests réussis: {self.results['passed']}")
        print(f"❌ Tests échoués: {self.results['failed']}")
        
        if self.results['errors']:
            print("\n🔍 DÉTAILS DES ÉCHECS:")
            for error in self.results['errors']:
                print(f"  - {error['test']}: {error['message']}")
                if error['error']:
                    print(f"    Erreur: {error['error']}")
        
        success_rate = (self.results['passed'] / (self.results['passed'] + self.results['failed'])) * 100 if (self.results['passed'] + self.results['failed']) > 0 else 0
        print(f"\n🎯 Taux de réussite: {success_rate:.1f}%")
        
        if success_rate >= 90:
            print("🎉 EXCELLENT! Les workflows traduits fonctionnent parfaitement!")
        elif success_rate >= 70:
            print("✅ BON! Les workflows traduits fonctionnent bien avec quelques points mineurs.")
        else:
            print("⚠️ ATTENTION! Des problèmes ont été détectés avec les workflows traduits.")

if __name__ == "__main__":
    tester = WorkflowTranslationTester()
    tester.run_all_tests()