#!/usr/bin/env python3
"""
ALORIA AGENCY Critical Bug Fixes Testing Suite

TESTING 2 CRITICAL BUG FIXES:
1. Manager Case Update Error (server.py lines 1486, 1496) - create_notification() missing db parameter
2. Employee Dashboard Client Data N/A (EmployeeDashboard.js lines 701, 704, 705) - wrong data source
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

class CriticalBugTester:
    def __init__(self):
        self.session = requests.Session()
        self.tokens = {}
        self.users = {}
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

    def test_critical_bug_1_manager_case_update(self):
        """TEST CRITIQUE 1: MANAGER CASE UPDATE ERROR - Test des corrections lignes 1486, 1496"""
        print("=== TEST CRITIQUE 1: MANAGER CASE UPDATE ERROR ===")
        
        # Login with Manager (manager@test.com / password123)
        try:
            print("🔍 ÉTAPE 1: Login Manager")
            login_response = self.session.post(f"{API_BASE}/auth/login", json={
                "email": "manager@test.com",
                "password": "password123"
            })
            
            if login_response.status_code == 200:
                login_data = login_response.json()
                manager_token = login_data['access_token']
                self.log_result("1.1 Manager Login", True, "Manager logged in successfully")
            else:
                self.log_result("1.1 Manager Login", False, f"Status: {login_response.status_code}", login_response.text)
                return
        except Exception as e:
            self.log_result("1.1 Manager Login", False, "Exception occurred", str(e))
            return
        
        headers = {"Authorization": f"Bearer {manager_token}"}
        
        # ÉTAPE 2: Récupérer la liste des dossiers via GET /api/cases
        try:
            print("🔍 ÉTAPE 2: Récupération des dossiers via GET /api/cases")
            cases_response = self.session.get(f"{API_BASE}/cases", headers=headers)
            
            if cases_response.status_code == 200:
                cases = cases_response.json()
                self.log_result("1.2 Get Cases List", True, f"✅ {len(cases)} dossiers récupérés")
                
                if len(cases) > 0:
                    # Sélectionner un dossier existant (par exemple le premier)
                    test_case = cases[0]
                    case_id = test_case['id']
                    client_name = test_case.get('client_name', 'Unknown')
                    
                    print(f"📋 DOSSIER SÉLECTIONNÉ: {case_id} - Client: {client_name}")
                    
                    # ÉTAPE 3: Effectuer une mise à jour via PATCH /api/cases/{case_id}
                    print("🔍 ÉTAPE 3: Mise à jour du dossier")
                    
                    update_data = {
                        "current_step_index": 2,
                        "status": "En cours",
                        "notes": f"Test de mise à jour - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
                    }
                    
                    print(f"📋 DONNÉES DE MISE À JOUR: {update_data}")
                    
                    update_response = self.session.patch(f"{API_BASE}/cases/{case_id}", 
                                                       json=update_data, headers=headers)
                    
                    print(f"📊 RESPONSE STATUS: {update_response.status_code}")
                    
                    # ÉTAPE 4: Vérifier que la réponse est 200 OK (pas d'erreur)
                    if update_response.status_code == 200:
                        self.log_result("1.3 Case Update Success", True, 
                                      "✅ Mise à jour du dossier réussie - Pas d'erreur de notification")
                        
                        # ÉTAPE 5: Vérifier que le dossier est bien mis à jour
                        updated_case_response = self.session.get(f"{API_BASE}/cases/{case_id}", headers=headers)
                        if updated_case_response.status_code == 200:
                            updated_case = updated_case_response.json()
                            
                            verification_results = []
                            
                            if updated_case.get('current_step_index') == 2:
                                verification_results.append("✅ current_step_index mis à jour")
                            else:
                                verification_results.append(f"❌ current_step_index: {updated_case.get('current_step_index')} (attendu: 2)")
                            
                            if updated_case.get('status') == "En cours":
                                verification_results.append("✅ status mis à jour")
                            else:
                                verification_results.append(f"❌ status: {updated_case.get('status')} (attendu: En cours)")
                            
                            if update_data['notes'] in updated_case.get('notes', ''):
                                verification_results.append("✅ notes mises à jour")
                            else:
                                verification_results.append("❌ notes non mises à jour")
                            
                            all_verified = all("✅" in result for result in verification_results)
                            self.log_result("1.4 Case Update Verification", all_verified, 
                                          f"Vérifications: {'; '.join(verification_results)}")
                        else:
                            self.log_result("1.4 Case Update Verification", False, 
                                          f"Cannot retrieve updated case: {updated_case_response.status_code}")
                        
                        # ÉTAPE 6: Vérifier qu'une notification a été créée pour le client
                        print("🔍 ÉTAPE 6: Vérification des notifications créées")
                        
                        # Get notifications for the current user (manager)
                        notifications_response = self.session.get(f"{API_BASE}/notifications", headers=headers)
                        if notifications_response.status_code == 200:
                            notifications = notifications_response.json()
                            
                            # Look for recent case_update notifications
                            recent_notifications = [n for n in notifications 
                                                  if n.get('type') == 'case_update' 
                                                  and n.get('related_id') == case_id]
                            
                            if recent_notifications:
                                self.log_result("1.5 Notification Creation", True, 
                                              f"✅ {len(recent_notifications)} notifications créées pour la mise à jour")
                            else:
                                self.log_result("1.5 Notification Creation", False, 
                                              "❌ Aucune notification case_update trouvée")
                        else:
                            self.log_result("1.5 Notification Creation", False, 
                                          f"Cannot retrieve notifications: {notifications_response.status_code}")
                    
                    elif update_response.status_code == 500:
                        # This would indicate the bug is still present
                        try:
                            error_data = update_response.json()
                            error_detail = error_data.get('detail', 'Unknown error')
                            
                            if 'notification' in error_detail.lower() or 'create_notification' in error_detail.lower():
                                self.log_result("1.3 Case Update Success", False, 
                                              "❌ ERREUR DE NOTIFICATION DÉTECTÉE - Bug non corrigé", 
                                              f"Erreur: {error_detail}")
                            else:
                                self.log_result("1.3 Case Update Success", False, 
                                              f"❌ Erreur 500 inattendue: {error_detail}")
                        except:
                            self.log_result("1.3 Case Update Success", False, 
                                          "❌ Erreur 500 - Cannot parse error response", 
                                          update_response.text)
                    
                    else:
                        self.log_result("1.3 Case Update Success", False, 
                                      f"❌ Status code inattendu: {update_response.status_code}", 
                                      update_response.text)
                
                else:
                    self.log_result("1.2 Get Cases List", False, "❌ Aucun dossier disponible pour le test")
            
            else:
                self.log_result("1.2 Get Cases List", False, 
                              f"❌ Cannot retrieve cases: {cases_response.status_code}", 
                              cases_response.text)
        
        except Exception as e:
            self.log_result("1.2 Get Cases List", False, "Exception occurred", str(e))

    def test_critical_bug_2_employee_client_data(self):
        """TEST CRITIQUE 2: EMPLOYEE DASHBOARD CLIENT DATA N/A - Test des corrections lignes 701, 704, 705"""
        print("=== TEST CRITIQUE 2: EMPLOYEE DASHBOARD CLIENT DATA N/A ===")
        
        # ÉTAPE 1: Login avec Employee (employee@aloria.com / emp123 OU tout autre employé)
        employee_token = None
        employee_user = None
        try:
            print("🔍 ÉTAPE 1: Login Employee")
            
            # Try multiple employee credentials as mentioned in review
            employee_credentials = [
                {"email": "employee@aloria.com", "password": "emp123"},
                {"email": "employer", "password": "emp123"},  # Alternative from review
            ]
            
            for creds in employee_credentials:
                login_response = self.session.post(f"{API_BASE}/auth/login", json=creds)
                if login_response.status_code == 200:
                    login_data = login_response.json()
                    employee_token = login_data['access_token']
                    employee_user = login_data['user']
                    self.log_result("2.1 Employee Login", True, 
                                  f"✅ Employee logged in: {creds['email']}")
                    print(f"📋 EMPLOYEE INFO: {employee_user.get('full_name')} (ID: {employee_user.get('id')})")
                    break
            
            if not employee_token:
                self.log_result("2.1 Employee Login", False, 
                              "❌ Cannot login with any employee credentials")
                return
        
        except Exception as e:
            self.log_result("2.1 Employee Login", False, "Exception occurred", str(e))
            return
        
        # ÉTAPE 2: Récupérer la liste des clients via GET /api/clients
        try:
            print("🔍 ÉTAPE 2: Récupération des clients assignés à l'employé")
            headers = {"Authorization": f"Bearer {employee_token}"}
            
            clients_response = self.session.get(f"{API_BASE}/clients", headers=headers)
            
            if clients_response.status_code == 200:
                clients = clients_response.json()
                self.log_result("2.2 Get Employee Clients", True, 
                              f"✅ {len(clients)} clients récupérés pour l'employé")
                
                if len(clients) > 0:
                    # ÉTAPE 3: Vérifier que les clients retournés contiennent les champs requis
                    print("🔍 ÉTAPE 3: Vérification des données clients")
                    
                    clients_with_issues = []
                    
                    for i, client in enumerate(clients[:10]):  # Test first 10 clients
                        client_issues = []
                        
                        # Vérifier full_name (pas null, pas vide)
                        full_name = client.get('full_name')
                        if not full_name or full_name == 'N/A' or full_name.strip() == '':
                            client_issues.append(f"full_name: '{full_name}'")
                        
                        # Vérifier email (pas null, pas vide)
                        email = client.get('email')
                        if not email or email == 'N/A' or email.strip() == '' or '@' not in str(email):
                            client_issues.append(f"email: '{email}'")
                        
                        # Vérifier phone (peut être optionnel mais doit être présent si disponible)
                        phone = client.get('phone')
                        if phone == 'N/A':  # N/A is not acceptable, but null/empty is OK
                            client_issues.append(f"phone: '{phone}'")
                        
                        if client_issues:
                            clients_with_issues.append(f"Client {i+1} ({client.get('id', 'unknown')}): {', '.join(client_issues)}")
                    
                    if clients_with_issues:
                        self.log_result("2.3 Client Data Validation", False, 
                                      f"❌ {len(clients_with_issues)} clients avec données N/A détectés", 
                                      f"Problèmes: {'; '.join(clients_with_issues[:3])}")  # Show first 3
                    else:
                        self.log_result("2.3 Client Data Validation", True, 
                                      "✅ Tous les clients ont des données complètes (pas de N/A)")
                    
                    # ÉTAPE 4: Tester un client spécifique mentionné dans la review
                    print("🔍 ÉTAPE 4: Recherche du client test spécifique")
                    
                    # Look for the specific client mentioned: Blondel MBOU SONGMENE
                    test_client = None
                    for client in clients:
                        if ('blondel' in client.get('full_name', '').lower() or 
                            'mbou' in client.get('full_name', '').lower() or
                            'blondel.mbou@gmail.com' in client.get('email', '').lower()):
                            test_client = client
                            break
                    
                    if test_client:
                        print(f"📋 CLIENT TEST TROUVÉ: {test_client.get('full_name')}")
                        
                        expected_data = {
                            'full_name': 'Blondel MBOU SONGMENE',
                            'email': 'blondel.mbou@gmail.com',
                            'phone': '+33784801254'
                        }
                        
                        test_verification = []
                        for field, expected_value in expected_data.items():
                            actual_value = test_client.get(field)
                            if actual_value == expected_value:
                                test_verification.append(f"✅ {field}: '{actual_value}'")
                            else:
                                test_verification.append(f"❌ {field}: '{actual_value}' (attendu: '{expected_value}')")
                        
                        all_test_verified = all("✅" in result for result in test_verification)
                        self.log_result("2.4 Specific Client Test", all_test_verified, 
                                      f"Vérifications client test: {'; '.join(test_verification)}")
                    else:
                        self.log_result("2.4 Specific Client Test", False, 
                                      "❌ Client test 'Blondel MBOU SONGMENE' non trouvé dans les clients assignés")
                        
                        # Show some sample client data for debugging
                        if len(clients) > 0:
                            sample_client = clients[0]
                            print(f"📋 SAMPLE CLIENT DATA: full_name='{sample_client.get('full_name')}', email='{sample_client.get('email')}', phone='{sample_client.get('phone')}'")
                
                else:
                    self.log_result("2.2 Get Employee Clients", False, 
                                  "❌ Aucun client assigné à cet employé - Impossible de tester les données")
                    
                    # This might be expected - let's check if the employee has any clients assigned
                    print("🔍 INFO: L'employé n'a aucun client assigné. Ceci peut être normal selon l'assignation.")
                    print(f"📋 EMPLOYEE ID: {employee_user.get('id')} - Vérifiez l'assignation des clients dans la base de données")
            
            else:
                self.log_result("2.2 Get Employee Clients", False, 
                              f"❌ Cannot retrieve clients: {clients_response.status_code}", 
                              clients_response.text)
        
        except Exception as e:
            self.log_result("2.2 Get Employee Clients", False, "Exception occurred", str(e))

    def print_final_summary(self):
        """Print final test summary"""
        print("\n" + "=" * 80)
        print("🏁 FINAL TEST SUMMARY")
        print("=" * 80)
        
        total_tests = self.results['passed'] + self.results['failed']
        success_rate = (self.results['passed'] / total_tests * 100) if total_tests > 0 else 0
        
        print(f"📊 TOTAL TESTS: {total_tests}")
        print(f"✅ PASSED: {self.results['passed']}")
        print(f"❌ FAILED: {self.results['failed']}")
        print(f"📈 SUCCESS RATE: {success_rate:.1f}%")
        
        if self.results['errors']:
            print(f"\n🚨 FAILED TESTS DETAILS:")
            for error in self.results['errors']:
                print(f"   ❌ {error['test']}: {error['message']}")
                if error['error']:
                    print(f"      Error: {error['error']}")
        
        print("\n" + "=" * 80)
        
        # Determine overall result
        if self.results['failed'] == 0:
            print("🎉 ALL CRITICAL BUG FIXES WORKING CORRECTLY!")
        elif self.results['failed'] <= 2:
            print("⚠️  SOME ISSUES DETECTED - REVIEW NEEDED")
        else:
            print("🚨 CRITICAL ISSUES DETECTED - IMMEDIATE ACTION REQUIRED")
        
        print("=" * 80)

    def run_all_tests(self):
        """Run all critical bug fix tests"""
        print("🚀 STARTING ALORIA AGENCY CRITICAL BUG FIXES TESTING")
        print("=" * 80)
        print("TESTING 2 CRITICAL BUG FIXES:")
        print("1. Manager Case Update Error (server.py lines 1486, 1496)")
        print("2. Employee Dashboard Client Data N/A (EmployeeDashboard.js lines 701, 704, 705)")
        print("=" * 80)
        
        # Run the two critical bug fix tests
        self.test_critical_bug_1_manager_case_update()
        print("\n" + "-" * 80 + "\n")
        self.test_critical_bug_2_employee_client_data()
        
        # Print final summary
        self.print_final_summary()

if __name__ == "__main__":
    tester = CriticalBugTester()
    tester.run_all_tests()