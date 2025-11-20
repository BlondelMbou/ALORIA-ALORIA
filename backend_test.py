#!/usr/bin/env python3
"""
ALORIA AGENCY - Test Changement de Mot de Passe - Tous les Rôles
Test complet du système de changement de mot de passe pour tous les rôles

TESTS À EFFECTUER:
- TEST 1: CLIENT Change Son Mot de Passe
- TEST 2: EMPLOYEE Change Son Mot de Passe  
- TEST 3: MANAGER Change Son Mot de Passe
- TEST 4: SUPERADMIN Change Son Mot de Passe
- TEST 5: Erreurs de Validation (mot de passe incorrect, trop court, champs manquants)
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
    'superadmin': {'email': 'superadmin@aloria.com', 'password': 'SuperAdmin123!'}
}

class PasswordChangeTester:
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
        """Authenticate all required users"""
        print("=== AUTHENTICATION SETUP ===")
        
        for role, credentials in CREDENTIALS.items():
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

    def find_active_client(self):
        """Find an active client in the database"""
        print("\n=== FINDING ACTIVE CLIENT ===")
        
        try:
            # Use manager token to get all clients
            headers = {"Authorization": f"Bearer {self.tokens['manager']}"}
            response = self.session.get(f"{API_BASE}/clients", headers=headers)
            
            if response.status_code == 200:
                clients = response.json()
                if clients:
                    # Find a client with complete data
                    for client in clients:
                        if client.get('email') and client.get('user_id'):
                            self.test_data['client_email'] = client['email']
                            self.test_data['client_user_id'] = client['user_id']
                            self.test_data['client_full_name'] = client.get('full_name', 'Client Test')
                            
                            self.log_result("Find Active Client", True, 
                                          f"Found client: {client['email']} (ID: {client['user_id']})")
                            return True
                    
                    self.log_result("Find Active Client", False, "No client with complete data found")
                    return False
                else:
                    self.log_result("Find Active Client", False, "No clients found in database")
                    return False
            else:
                self.log_result("Find Active Client", False, 
                              f"Status: {response.status_code}", response.text)
                return False
                
        except Exception as e:
            self.log_result("Find Active Client", False, "Exception occurred", str(e))
            return False

    def test_client_password_change(self):
        """TEST 1 - CLIENT Change Son Mot de Passe"""
        print("\n" + "="*60)
        print("TEST 1 - CLIENT CHANGE SON MOT DE PASSE")
        print("="*60)
        
        if not self.test_data.get('client_email'):
            self.log_result("Test 1 Setup", False, "Client email not available")
            return False
        
        try:
            # 1. Login CLIENT avec mot de passe par défaut
            print("\n🔸 ÉTAPE 1.1 - Login CLIENT avec mot de passe par défaut")
            client_credentials = {
                "email": self.test_data['client_email'],
                "password": "Aloria2024!"  # Mot de passe par défaut
            }
            
            login_response = self.session.post(f"{API_BASE}/auth/login", json=client_credentials)
            
            if login_response.status_code == 200:
                client_data = login_response.json()
                client_token = client_data['access_token']
                
                self.log_result("1.1 Client Login", True, 
                              f"Client connecté: {client_data['user']['full_name']}")
                
                # 2. Changer le mot de passe
                print("\n🔸 ÉTAPE 1.2 - Changer le mot de passe CLIENT")
                headers = {"Authorization": f"Bearer {client_token}"}
                
                password_change_data = {
                    "current_password": "Aloria2024!",
                    "new_password": "NewClientPass123!"
                }
                
                change_response = self.session.post(f"{API_BASE}/users/change-password", 
                                                  json=password_change_data, headers=headers)
                
                if change_response.status_code == 200:
                    response_data = change_response.json()
                    
                    if "succès" in response_data.get('message', '').lower():
                        self.log_result("1.2 Client Password Change", True, 
                                      f"Message: {response_data.get('message')}")
                        
                        # 3. Vérifier que le nouveau mot de passe fonctionne
                        print("\n🔸 ÉTAPE 1.3 - Vérifier nouveau mot de passe CLIENT")
                        new_credentials = {
                            "email": self.test_data['client_email'],
                            "password": "NewClientPass123!"
                        }
                        
                        verify_response = self.session.post(f"{API_BASE}/auth/login", json=new_credentials)
                        
                        if verify_response.status_code == 200:
                            self.log_result("1.3 Client New Password Verification", True, 
                                          "Re-login avec nouveau mot de passe réussi")
                            
                            # Restore original password for other tests
                            restore_headers = {"Authorization": f"Bearer {verify_response.json()['access_token']}"}
                            restore_data = {
                                "current_password": "NewClientPass123!",
                                "new_password": "Aloria2024!"
                            }
                            self.session.post(f"{API_BASE}/users/change-password", 
                                            json=restore_data, headers=restore_headers)
                            
                        else:
                            self.log_result("1.3 Client New Password Verification", False, 
                                          f"Re-login échoué - Status: {verify_response.status_code}")
                    else:
                        self.log_result("1.2 Client Password Change", False, 
                                      f"Message inattendu: {response_data.get('message')}")
                else:
                    self.log_result("1.2 Client Password Change", False, 
                                  f"Status: {change_response.status_code}", change_response.text)
            else:
                self.log_result("1.1 Client Login", False, 
                              f"Status: {login_response.status_code}", login_response.text)
                return False
                
        except Exception as e:
            self.log_result("Test 1 Client Password Change", False, "Exception occurred", str(e))
            return False
        
        return True

    def test_employee_password_change(self):
        """TEST 2 - EMPLOYEE Change Son Mot de Passe"""
        print("\n" + "="*60)
        print("TEST 2 - EMPLOYEE CHANGE SON MOT DE PASSE")
        print("="*60)
        
        if 'employee' not in self.tokens:
            self.log_result("Test 2 Setup", False, "Employee token not available")
            return False
        
        try:
            # 1. Changer le mot de passe EMPLOYEE
            print("\n🔸 ÉTAPE 2.1 - Changer le mot de passe EMPLOYEE")
            headers = {"Authorization": f"Bearer {self.tokens['employee']}"}
            
            password_change_data = {
                "current_password": "emp123",
                "new_password": "EmpNewPass123!"
            }
            
            change_response = self.session.post(f"{API_BASE}/users/change-password", 
                                              json=password_change_data, headers=headers)
            
            if change_response.status_code == 200:
                response_data = change_response.json()
                
                if "succès" in response_data.get('message', '').lower():
                    self.log_result("2.1 Employee Password Change", True, 
                                  f"Message: {response_data.get('message')}")
                    
                    # 2. Vérifier que le nouveau mot de passe fonctionne
                    print("\n🔸 ÉTAPE 2.2 - Vérifier nouveau mot de passe EMPLOYEE")
                    new_credentials = {
                        "email": "employee@aloria.com",
                        "password": "EmpNewPass123!"
                    }
                    
                    verify_response = self.session.post(f"{API_BASE}/auth/login", json=new_credentials)
                    
                    if verify_response.status_code == 200:
                        self.log_result("2.2 Employee New Password Verification", True, 
                                      "Re-login avec nouveau mot de passe réussi")
                        
                        # Restore original password for other tests
                        restore_headers = {"Authorization": f"Bearer {verify_response.json()['access_token']}"}
                        restore_data = {
                            "current_password": "EmpNewPass123!",
                            "new_password": "emp123"
                        }
                        self.session.post(f"{API_BASE}/users/change-password", 
                                        json=restore_data, headers=restore_headers)
                        
                    else:
                        self.log_result("2.2 Employee New Password Verification", False, 
                                      f"Re-login échoué - Status: {verify_response.status_code}")
                else:
                    self.log_result("2.1 Employee Password Change", False, 
                                  f"Message inattendu: {response_data.get('message')}")
            else:
                self.log_result("2.1 Employee Password Change", False, 
                              f"Status: {change_response.status_code}", change_response.text)
                return False
                
        except Exception as e:
            self.log_result("Test 2 Employee Password Change", False, "Exception occurred", str(e))
            return False
        
        return True

    def test_manager_password_change(self):
        """TEST 3 - MANAGER Change Son Mot de Passe"""
        print("\n" + "="*60)
        print("TEST 3 - MANAGER CHANGE SON MOT DE PASSE")
        print("="*60)
        
        if 'manager' not in self.tokens:
            self.log_result("Test 3 Setup", False, "Manager token not available")
            return False
        
        try:
            # 1. Changer le mot de passe MANAGER
            print("\n🔸 ÉTAPE 3.1 - Changer le mot de passe MANAGER")
            headers = {"Authorization": f"Bearer {self.tokens['manager']}"}
            
            password_change_data = {
                "current_password": "password123",
                "new_password": "MgrNewPass123!"
            }
            
            change_response = self.session.post(f"{API_BASE}/users/change-password", 
                                              json=password_change_data, headers=headers)
            
            if change_response.status_code == 200:
                response_data = change_response.json()
                
                if "succès" in response_data.get('message', '').lower():
                    self.log_result("3.1 Manager Password Change", True, 
                                  f"Message: {response_data.get('message')}")
                    
                    # 2. Vérifier que le nouveau mot de passe fonctionne
                    print("\n🔸 ÉTAPE 3.2 - Vérifier nouveau mot de passe MANAGER")
                    new_credentials = {
                        "email": "manager@test.com",
                        "password": "MgrNewPass123!"
                    }
                    
                    verify_response = self.session.post(f"{API_BASE}/auth/login", json=new_credentials)
                    
                    if verify_response.status_code == 200:
                        self.log_result("3.2 Manager New Password Verification", True, 
                                      "Re-login avec nouveau mot de passe réussi")
                        
                        # Restore original password for other tests
                        restore_headers = {"Authorization": f"Bearer {verify_response.json()['access_token']}"}
                        restore_data = {
                            "current_password": "MgrNewPass123!",
                            "new_password": "password123"
                        }
                        self.session.post(f"{API_BASE}/users/change-password", 
                                        json=restore_data, headers=restore_headers)
                        
                    else:
                        self.log_result("3.2 Manager New Password Verification", False, 
                                      f"Re-login échoué - Status: {verify_response.status_code}")
                else:
                    self.log_result("3.1 Manager Password Change", False, 
                                  f"Message inattendu: {response_data.get('message')}")
            else:
                self.log_result("3.1 Manager Password Change", False, 
                              f"Status: {change_response.status_code}", change_response.text)
                return False
                
        except Exception as e:
            self.log_result("Test 3 Manager Password Change", False, "Exception occurred", str(e))
            return False
        
        return True

    def test_superadmin_password_change(self):
        """TEST 4 - SUPERADMIN Change Son Mot de Passe"""
        print("\n" + "="*60)
        print("TEST 4 - SUPERADMIN CHANGE SON MOT DE PASSE")
        print("="*60)
        
        if 'superadmin' not in self.tokens:
            self.log_result("Test 4 Setup", False, "SuperAdmin token not available")
            return False
        
        try:
            # 1. Changer le mot de passe SUPERADMIN
            print("\n🔸 ÉTAPE 4.1 - Changer le mot de passe SUPERADMIN")
            headers = {"Authorization": f"Bearer {self.tokens['superadmin']}"}
            
            password_change_data = {
                "current_password": "SuperAdmin123!",
                "new_password": "SuperNewPass123!"
            }
            
            change_response = self.session.post(f"{API_BASE}/users/change-password", 
                                              json=password_change_data, headers=headers)
            
            if change_response.status_code == 200:
                response_data = change_response.json()
                
                if "succès" in response_data.get('message', '').lower():
                    self.log_result("4.1 SuperAdmin Password Change", True, 
                                  f"Message: {response_data.get('message')}")
                    
                    # 2. Vérifier que le nouveau mot de passe fonctionne
                    print("\n🔸 ÉTAPE 4.2 - Vérifier nouveau mot de passe SUPERADMIN")
                    new_credentials = {
                        "email": "superadmin@aloria.com",
                        "password": "SuperNewPass123!"
                    }
                    
                    verify_response = self.session.post(f"{API_BASE}/auth/login", json=new_credentials)
                    
                    if verify_response.status_code == 200:
                        self.log_result("4.2 SuperAdmin New Password Verification", True, 
                                      "Re-login avec nouveau mot de passe réussi")
                        
                        # Restore original password for other tests
                        restore_headers = {"Authorization": f"Bearer {verify_response.json()['access_token']}"}
                        restore_data = {
                            "current_password": "SuperNewPass123!",
                            "new_password": "SuperAdmin123!"
                        }
                        self.session.post(f"{API_BASE}/users/change-password", 
                                        json=restore_data, headers=restore_headers)
                        
                    else:
                        self.log_result("4.2 SuperAdmin New Password Verification", False, 
                                      f"Re-login échoué - Status: {verify_response.status_code}")
                else:
                    self.log_result("4.1 SuperAdmin Password Change", False, 
                                  f"Message inattendu: {response_data.get('message')}")
            else:
                self.log_result("4.1 SuperAdmin Password Change", False, 
                              f"Status: {change_response.status_code}", change_response.text)
                return False
                
        except Exception as e:
            self.log_result("Test 4 SuperAdmin Password Change", False, "Exception occurred", str(e))
            return False
        
        return True

    def test_password_validation_errors(self):
        """TEST 5 - Erreurs de Validation"""
        print("\n" + "="*60)
        print("TEST 5 - ERREURS DE VALIDATION")
        print("="*60)
        
        if 'manager' not in self.tokens:
            self.log_result("Test 5 Setup", False, "Manager token not available")
            return False
        
        headers = {"Authorization": f"Bearer {self.tokens['manager']}"}
        
        # Test 5.1: Mot de passe actuel incorrect
        print("\n🔸 ÉTAPE 5.1 - Mot de passe actuel incorrect")
        try:
            wrong_password_data = {
                "current_password": "wrong_password_123",
                "new_password": "NewValidPass123!"
            }
            
            response = self.session.post(f"{API_BASE}/users/change-password", 
                                       json=wrong_password_data, headers=headers)
            
            if response.status_code == 400:
                response_data = response.json()
                if "incorrect" in response_data.get('detail', '').lower():
                    self.log_result("5.1 Wrong Current Password", True, 
                                  f"Erreur attendue: {response_data.get('detail')}")
                else:
                    self.log_result("5.1 Wrong Current Password", False, 
                                  f"Message d'erreur inattendu: {response_data.get('detail')}")
            else:
                self.log_result("5.1 Wrong Current Password", False, 
                              f"Status inattendu: {response.status_code} (attendu: 400)")
                
        except Exception as e:
            self.log_result("5.1 Wrong Current Password", False, "Exception occurred", str(e))
        
        # Test 5.2: Nouveau mot de passe trop court
        print("\n🔸 ÉTAPE 5.2 - Nouveau mot de passe trop court")
        try:
            short_password_data = {
                "current_password": "password123",
                "new_password": "12345"  # < 6 caractères
            }
            
            response = self.session.post(f"{API_BASE}/users/change-password", 
                                       json=short_password_data, headers=headers)
            
            if response.status_code == 400:
                response_data = response.json()
                if "6 caractères" in response_data.get('detail', ''):
                    self.log_result("5.2 Short Password", True, 
                                  f"Erreur attendue: {response_data.get('detail')}")
                else:
                    self.log_result("5.2 Short Password", False, 
                                  f"Message d'erreur inattendu: {response_data.get('detail')}")
            else:
                self.log_result("5.2 Short Password", False, 
                              f"Status inattendu: {response.status_code} (attendu: 400)")
                
        except Exception as e:
            self.log_result("5.2 Short Password", False, "Exception occurred", str(e))
        
        # Test 5.3: Champs manquants
        print("\n🔸 ÉTAPE 5.3 - Champs manquants")
        try:
            missing_fields_data = {
                "current_password": "password123"
                # new_password manquant
            }
            
            response = self.session.post(f"{API_BASE}/users/change-password", 
                                       json=missing_fields_data, headers=headers)
            
            if response.status_code == 400 or response.status_code == 422:
                response_data = response.json()
                error_message = response_data.get('detail', '')
                if isinstance(error_message, list):
                    error_message = str(error_message)
                
                if "requis" in error_message.lower() or "required" in error_message.lower():
                    self.log_result("5.3 Missing Fields", True, 
                                  f"Erreur attendue: {error_message}")
                else:
                    self.log_result("5.3 Missing Fields", False, 
                                  f"Message d'erreur inattendu: {error_message}")
            else:
                self.log_result("5.3 Missing Fields", False, 
                              f"Status inattendu: {response.status_code} (attendu: 400 ou 422)")
                
        except Exception as e:
            self.log_result("5.3 Missing Fields", False, "Exception occurred", str(e))
        
        return True

    def run_password_change_tests(self):
        """Exécuter tous les tests de changement de mot de passe"""
        print("ALORIA AGENCY - Test Changement de Mot de Passe - Tous les Rôles")
        print("Test complet du système de changement de mot de passe pour tous les rôles")
        print("="*80)
        
        # Authentication
        if not self.authenticate_users():
            print("❌ ÉCHEC: Impossible d'authentifier les utilisateurs")
            return False
        
        # Find active client
        if not self.find_active_client():
            print("❌ ÉCHEC: Impossible de trouver un client actif")
            return False
        
        # Test 1: CLIENT Change Son Mot de Passe
        if not self.test_client_password_change():
            print("❌ ÉCHEC: Test 1 - CLIENT Change Son Mot de Passe")
        
        # Test 2: EMPLOYEE Change Son Mot de Passe
        if not self.test_employee_password_change():
            print("❌ ÉCHEC: Test 2 - EMPLOYEE Change Son Mot de Passe")
        
        # Test 3: MANAGER Change Son Mot de Passe
        if not self.test_manager_password_change():
            print("❌ ÉCHEC: Test 3 - MANAGER Change Son Mot de Passe")
        
        # Test 4: SUPERADMIN Change Son Mot de Passe
        if not self.test_superadmin_password_change():
            print("❌ ÉCHEC: Test 4 - SUPERADMIN Change Son Mot de Passe")
        
        # Test 5: Erreurs de Validation
        if not self.test_password_validation_errors():
            print("❌ ÉCHEC: Test 5 - Erreurs de Validation")
        
        # Résultats finaux
        print("\n" + "="*80)
        print("RÉSULTATS FINAUX")
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
        
        return success_rate >= 80  # Considérer comme succès si >= 80%

if __name__ == "__main__":
    tester = PasswordChangeTester()
    success = tester.run_password_change_tests()
    
    if success:
        print("\n🎉 TEST CHANGEMENT DE MOT DE PASSE: SUCCÈS")
        sys.exit(0)
    else:
        print("\n💥 TEST CHANGEMENT DE MOT DE PASSE: ÉCHEC")
        sys.exit(1)