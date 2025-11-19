#!/usr/bin/env python3
"""
ALORIA AGENCY - Test Correction Bug Manager Case Update - Erreur 404

CONTEXTE:
L'utilisateur rapporte toujours l'erreur "Erreur lors de la mise à jour" quand il essaie de mettre à jour un dossier client en tant que Manager. Les logs montrent que toutes les requêtes PATCH /api/cases/{case_id} retournent 404 Not Found.

PROBLÈME IDENTIFIÉ:
Dans l'endpoint GET /api/cases (ligne 1396), le code cherchait les cases avec:
```python
client_user_ids = [c["user_id"] for c in clients]  # Liste de user_id
cases = await db.cases.find({"client_id": {"$in": client_user_ids}}, ...)  # Cherche cases par client_id
```

Le problème : `client_user_ids` contient des **user_id**, mais les cases dans la BDD ont `client_id` qui correspond à `client["id"]` (l'ID du client), pas au `user_id`.

CORRECTION APPLIQUÉE:
Ligne 1396 de server.py :
- **AVANT** : `client_user_ids = [c["user_id"] for c in clients]`
- **APRÈS** : `client_ids = [c["id"] for c in clients]`

Cette correction fait que:
1. GET /api/cases récupère maintenant les VRAIS cases (avec les bons client_ids)
2. Le frontend affiche les vrais cases avec leurs vrais IDs
3. PATCH /api/cases/{case_id} peut maintenant trouver les cases et les mettre à jour

TESTS REQUIS:

**Test 1 - GET /api/cases avec Manager**
1. Login Manager (manager@test.com / password123)
2. GET /api/cases
3. Vérifier que la réponse contient des cases valides (pas une liste vide)
4. Vérifier que chaque case a un `id` valide
5. Noter un `case_id` pour le test suivant

**Test 2 - PATCH /api/cases/{case_id} avec Manager**
1. Utiliser le case_id du test précédent
2. PATCH /api/cases/{case_id} avec:
   ```json
   {
     "current_step_index": 2,
     "status": "En cours"
   }
   ```
3. Vérifier que la réponse est 200 OK (PAS 404 Not Found)
4. Vérifier que le case est bien mis à jour

**Test 3 - Vérification de la mise à jour**
1. GET /api/cases/{case_id}
2. Vérifier que current_step_index = 2
3. Vérifier que status = "En cours"

CREDENTIALS:
- **Manager**: manager@test.com / password123
- **Backend URL**: https://aloria-dev.preview.emergentagent.com

RÉSULTAT ATTENDU:
✅ GET /api/cases retourne les vrais cases avec leurs vrais IDs
✅ PATCH /api/cases/{case_id} retourne 200 OK (pas 404)
✅ Le Manager peut maintenant mettre à jour les dossiers sans erreur
"""

import requests
import json
import os
from datetime import datetime
import sys
import time

# Get backend URL from environment
BACKEND_URL = os.environ.get('REACT_APP_BACKEND_URL', 'https://aloria-dev.preview.emergentagent.com')
API_BASE = f"{BACKEND_URL}/api"

# Test credentials from review request
MANAGER_CREDENTIALS = {
    'email': 'manager@test.com',
    'password': 'password123'
}

class ManagerCaseUpdateTester:
    def __init__(self):
        self.session = requests.Session()
        self.manager_token = None
        self.test_case_id = None
        self.test_case_client_name = None
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

    def authenticate_manager(self):
        """Authenticate Manager with review credentials"""
        print("=== AUTHENTICATION SETUP ===")
        
        try:
            print(f"🔍 TESTING POST /api/auth/login with {MANAGER_CREDENTIALS['email']}")
            response = self.session.post(f"{API_BASE}/auth/login", json=MANAGER_CREDENTIALS)
            
            print(f"📊 RESPONSE STATUS: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                self.manager_token = data['access_token']
                manager_user = data['user']
                self.log_result("Manager Authentication", True, 
                              f"Logged in as {MANAGER_CREDENTIALS['email']} - Role: {manager_user.get('role')}")
                return True
            else:
                self.log_result("Manager Authentication", False, 
                              f"Status: {response.status_code}", response.text)
                return False
        except Exception as e:
            self.log_result("Manager Authentication", False, "Exception occurred", str(e))
            return False

    def test_1_get_cases_with_manager(self):
        """TEST 1 - GET /api/cases avec Manager"""
        print("=== TEST 1 - GET /api/cases avec Manager ===")
        
        if not self.manager_token:
            self.log_result("1.0 Manager Token Check", False, "❌ Aucun token manager disponible")
            return False
            
        headers = {"Authorization": f"Bearer {self.manager_token}"}
        
        try:
            print("🔍 TESTING GET /api/cases")
            response = self.session.get(f"{API_BASE}/cases", headers=headers)
            
            print(f"📊 RESPONSE STATUS: {response.status_code}")
            
            if response.status_code == 200:
                try:
                    cases_data = response.json()
                    
                    if isinstance(cases_data, list):
                        if len(cases_data) > 0:
                            self.log_result("1.1 GET Cases - Data Available", True, 
                                          f"✅ {len(cases_data)} cases trouvés (pas une liste vide)")
                            
                            # Vérifier que chaque case a un ID valide
                            valid_cases = []
                            for case in cases_data:
                                case_id = case.get('id')
                                if case_id and isinstance(case_id, str) and len(case_id) > 0:
                                    valid_cases.append(case)
                            
                            if valid_cases:
                                self.log_result("1.2 GET Cases - Valid IDs", True, 
                                              f"✅ {len(valid_cases)} cases avec IDs valides")
                                
                                # Noter un case_id pour le test suivant
                                self.test_case_id = valid_cases[0]['id']
                                self.test_case_client_name = valid_cases[0].get('client_name', 'Unknown')
                                
                                print(f"🔑 CASE ID SELECTED FOR UPDATE TEST: {self.test_case_id}")
                                print(f"👤 CLIENT NAME: {self.test_case_client_name}")
                                
                                return True
                            else:
                                self.log_result("1.2 GET Cases - Valid IDs", False, 
                                              "❌ Aucun case avec ID valide trouvé")
                                return False
                        else:
                            self.log_result("1.1 GET Cases - Data Available", False, 
                                          "❌ Liste vide - aucun case trouvé (PROBLÈME IDENTIFIÉ)")
                            print("🚨 DIAGNOSTIC: GET /api/cases retourne une liste vide - le bug n'est pas corrigé")
                            return False
                    else:
                        self.log_result("1.1 GET Cases - Response Type", False, 
                                      f"❌ Response type incorrect: {type(cases_data)}")
                        return False
                        
                except Exception as e:
                    self.log_result("1.1 GET Cases - Parse Response", False, 
                                  f"❌ Cannot parse JSON: {str(e)}")
                    print(f"📋 RAW RESPONSE: {response.text}")
                    return False
                    
            else:
                self.log_result("1.1 GET Cases - Status Code", False, 
                              f"❌ Status code: {response.status_code}")
                print(f"📋 RESPONSE: {response.text}")
                return False
                
        except Exception as e:
            self.log_result("1.1 GET Cases - Request", False, f"❌ Exception: {str(e)}")
            return False

    def test_2_patch_case_with_manager(self):
        """TEST 2 - PATCH /api/cases/{case_id} avec Manager"""
        print("=== TEST 2 - PATCH /api/cases/{case_id} avec Manager ===")
        
        # Vérifier qu'on a un case_id à tester
        if not self.test_case_id:
            self.log_result("2.0 Case ID Available", False, "❌ Aucun case_id disponible - Test 1 a échoué")
            return False
            
        headers = {"Authorization": f"Bearer {self.manager_token}"}
        case_id = self.test_case_id
        
        try:
            print(f"🔍 TESTING PATCH /api/cases/{case_id}")
            
            # Données de mise à jour selon la demande de révision
            update_data = {
                "current_step_index": 2,
                "status": "En cours"
            }
            
            print(f"📋 UPDATE DATA: {update_data}")
            
            response = self.session.patch(f"{API_BASE}/cases/{case_id}", json=update_data, headers=headers)
            
            print(f"📊 RESPONSE STATUS: {response.status_code}")
            
            if response.status_code == 200:
                try:
                    response_data = response.json()
                    self.log_result("2.1 PATCH Case - Success", True, 
                                  "✅ Status 200 OK - Case mis à jour avec succès (PAS 404 Not Found)")
                    
                    # Vérifier que les données ont été mises à jour
                    if response_data.get('current_step_index') == 2:
                        self.log_result("2.2 PATCH Case - Data Updated", True, 
                                      "✅ current_step_index mis à jour correctement")
                    else:
                        self.log_result("2.2 PATCH Case - Data Updated", False, 
                                      f"❌ current_step_index incorrect: {response_data.get('current_step_index')}")
                        
                    if response_data.get('status') == "En cours":
                        self.log_result("2.3 PATCH Case - Status Updated", True, 
                                      "✅ status mis à jour correctement")
                    else:
                        self.log_result("2.3 PATCH Case - Status Updated", False, 
                                      f"❌ status incorrect: {response_data.get('status')}")
                    
                    return True
                        
                except Exception as e:
                    self.log_result("2.1 PATCH Case - Parse Response", False, 
                                  f"❌ Cannot parse JSON: {str(e)}")
                    return False
                    
            elif response.status_code == 404:
                self.log_result("2.1 PATCH Case - 404 Error", False, 
                              "❌ Status 404 Not Found - LE BUG N'EST PAS CORRIGÉ")
                print("🚨 DIAGNOSTIC: PATCH /api/cases/{case_id} retourne toujours 404 - la correction n'a pas fonctionné")
                try:
                    error_data = response.json()
                    print(f"📋 ERROR DETAILS: {error_data}")
                except:
                    print(f"📋 RAW ERROR: {response.text}")
                return False
                    
            elif response.status_code == 403:
                self.log_result("2.1 PATCH Case - 403 Error", False, 
                              "❌ Status 403 Forbidden - Problème de permissions")
                return False
                
            else:
                self.log_result("2.1 PATCH Case - Unexpected Status", False, 
                              f"❌ Status code inattendu: {response.status_code}")
                print(f"📋 RESPONSE: {response.text}")
                return False
                
        except Exception as e:
            self.log_result("2.1 PATCH Case - Request", False, f"❌ Exception: {str(e)}")
            return False

    def test_3_verify_case_update(self):
        """TEST 3 - Vérification de la mise à jour"""
        print("=== TEST 3 - Vérification de la mise à jour ===")
        
        if not self.test_case_id:
            self.log_result("3.0 Case ID Available", False, "❌ Aucun case_id disponible")
            return False
            
        headers = {"Authorization": f"Bearer {self.manager_token}"}
        
        try:
            print(f"🔍 TESTING GET /api/cases/{self.test_case_id}")
            
            response = self.session.get(f"{API_BASE}/cases/{self.test_case_id}", headers=headers)
            
            if response.status_code == 200:
                try:
                    case_data = response.json()
                    
                    # Vérifier current_step_index = 2
                    if case_data.get('current_step_index') == 2:
                        self.log_result("3.1 Verify Update - Step Index", True, 
                                      "✅ current_step_index = 2 confirmé")
                    else:
                        self.log_result("3.1 Verify Update - Step Index", False, 
                                      f"❌ current_step_index = {case_data.get('current_step_index')} (attendu: 2)")
                    
                    # Vérifier status = "En cours"
                    if case_data.get('status') == "En cours":
                        self.log_result("3.2 Verify Update - Status", True, 
                                      "✅ status = 'En cours' confirmé")
                    else:
                        self.log_result("3.2 Verify Update - Status", False, 
                                      f"❌ status = '{case_data.get('status')}' (attendu: 'En cours')")
                    
                    return True
                        
                except Exception as e:
                    self.log_result("3.1 Verify Update - Parse Response", False, 
                                  f"❌ Cannot parse JSON: {str(e)}")
                    return False
                    
            else:
                self.log_result("3.1 Verify Update - Get Case", False, 
                              f"❌ Status code: {response.status_code}")
                return False
                
        except Exception as e:
            self.log_result("3.1 Verify Update - Request", False, f"❌ Exception: {str(e)}")
            return False

    def run_all_tests(self):
        """Run all tests in sequence"""
        print("🚀 TESTING CORRECTION BUG MANAGER CASE UPDATE - ERREUR 404")
        print("=" * 80)
        
        # Step 1: Authenticate Manager
        if not self.authenticate_manager():
            print("❌ AUTHENTICATION FAILED - Cannot proceed with tests")
            return self.results
        
        # Step 2: Test GET /api/cases
        if not self.test_1_get_cases_with_manager():
            print("❌ GET CASES FAILED - Cannot proceed with update tests")
            return self.results
        
        # Step 3: Test PATCH /api/cases/{case_id}
        if not self.test_2_patch_case_with_manager():
            print("❌ PATCH CASE FAILED - Update functionality broken")
            return self.results
        
        # Step 4: Verify the update was applied
        self.test_3_verify_case_update()
        
        # Print final results
        print("=" * 80)
        print("🏁 FINAL RESULTS")
        print(f"✅ PASSED: {self.results['passed']}")
        print(f"❌ FAILED: {self.results['failed']}")
        if self.results['passed'] + self.results['failed'] > 0:
            print(f"📊 SUCCESS RATE: {(self.results['passed'] / (self.results['passed'] + self.results['failed']) * 100):.1f}%")
        
        if self.results['errors']:
            print("\n🚨 FAILED TESTS SUMMARY:")
            for error in self.results['errors']:
                print(f"   - {error['test']}: {error['message']}")
        
        # Final diagnostic
        if self.results['failed'] == 0:
            print("\n🎉 CORRECTION VALIDÉE - Le bug Manager Case Update est RÉSOLU!")
            print("✅ GET /api/cases retourne les vrais cases avec leurs vrais IDs")
            print("✅ PATCH /api/cases/{case_id} retourne 200 OK (pas 404)")
            print("✅ Le Manager peut maintenant mettre à jour les dossiers sans erreur")
        else:
            print("\n🚨 CORRECTION NON VALIDÉE - Le bug Manager Case Update PERSISTE!")
            print("❌ Des problèmes ont été détectés dans le système de mise à jour des cases")
        
        return self.results

def main():
    """Main function to run the Manager Case Update bug fix test"""
    tester = ManagerCaseUpdateTester()
    return tester.run_all_tests()

if __name__ == "__main__":
    main()