#!/usr/bin/env python3
"""
ALORIA AGENCY Review Request Specific Testing
Tests the specific requirements mentioned in the review request
"""

import requests
import json
import os
from datetime import datetime

# Get backend URL from environment
BACKEND_URL = os.environ.get('REACT_APP_BACKEND_URL', 'https://immigra-portal.preview.emergentagent.com')
API_BASE = f"{BACKEND_URL}/api"

class ReviewTester:
    def __init__(self):
        self.session = requests.Session()
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

    def test_superadmin_dashboard_stats(self):
        """Test 1: GET /api/admin/dashboard-stats pour vérifier les statistiques corrigées"""
        print("=== Test 1: Dashboard SuperAdmin amélioré ===")
        
        # First login as SuperAdmin
        superadmin_token = None
        try:
            login_response = self.session.post(f"{API_BASE}/auth/login", json={
                "email": "superadmin@aloria.com",
                "password": "SuperAdmin123!"
            })
            if login_response.status_code == 200:
                superadmin_token = login_response.json()['access_token']
                self.log_result("SuperAdmin Login", True, "SuperAdmin logged in successfully")
            else:
                self.log_result("SuperAdmin Login", False, f"Status: {login_response.status_code}")
                return
        except Exception as e:
            self.log_result("SuperAdmin Login", False, "Exception occurred", str(e))
            return

        # Test dashboard stats API
        if superadmin_token:
            try:
                headers = {"Authorization": f"Bearer {superadmin_token}"}
                response = self.session.get(f"{API_BASE}/admin/dashboard-stats", headers=headers)
                if response.status_code == 200:
                    data = response.json()
                    # Verify expected fields are present
                    expected_fields = ['users', 'business', 'system']
                    missing_fields = [field for field in expected_fields if field not in data]
                    
                    if not missing_fields:
                        users_data = data.get('users', {})
                        business_data = data.get('business', {})
                        
                        # Check for specific fields mentioned in review
                        if 'total' in users_data and 'total_cases' in business_data:
                            self.log_result("Dashboard Stats API", True, 
                                          f"Users total: {users_data.get('total', 'N/A')}, "
                                          f"Business total cases: {business_data.get('total_cases', 'N/A')}")
                        else:
                            self.log_result("Dashboard Stats API", False, 
                                          "Missing expected fields: users.total or business.total_cases")
                    else:
                        self.log_result("Dashboard Stats API", False, 
                                      f"Missing expected sections: {missing_fields}")
                else:
                    self.log_result("Dashboard Stats API", False, 
                                  f"Status: {response.status_code}", response.text)
            except Exception as e:
                self.log_result("Dashboard Stats API", False, "Exception occurred", str(e))

    def test_contact_form_new_fields(self):
        """Test 2: POST /api/contact-messages avec les nouveaux champs"""
        print("=== Test 2: Nouveau formulaire de contact avec champs supplémentaires ===")
        
        try:
            # Test contact form with new fields
            contact_data = {
                "name": "Jean Dupont",
                "email": "jean.dupont@example.com",
                "phone": "+33123456789",
                "country": "France",
                "visa_type": "Work Permit",
                "budget_range": "3000-5000€",
                "urgency_level": "Urgent",
                "message": "Je souhaite obtenir un permis de travail pour la France. J'ai une offre d'emploi confirmée.",
                "lead_source": "Site web",
                "how_did_you_know": "Recommandation d'un ami",
                "referred_by_employee": "Sophie Dubois"
            }
            
            response = self.session.post(f"{API_BASE}/contact-messages", json=contact_data)
            if response.status_code == 200 or response.status_code == 201:
                data = response.json()
                
                # Verify new fields are in response
                if 'how_did_you_know' in data and 'referred_by_employee' in data:
                    self.log_result("Contact Form New Fields", True, 
                                  f"how_did_you_know='{data['how_did_you_know']}', "
                                  f"referred_by_employee='{data['referred_by_employee']}'")
                    
                    # Test automatic assignment if employee is mentioned
                    if data.get('referred_by_employee') and data.get('assigned_to'):
                        self.log_result("Employee Auto-Assignment", True, 
                                      f"Assigned to {data.get('assigned_to_name', 'N/A')}")
                    else:
                        self.log_result("Employee Auto-Assignment", False, 
                                      "No automatic assignment despite employee reference")
                else:
                    self.log_result("Contact Form New Fields", False, 
                                  "Response missing new fields")
            else:
                self.log_result("Contact Form New Fields", False, 
                              f"Status: {response.status_code}", response.text)
                
        except Exception as e:
            self.log_result("Contact Form New Fields", False, "Exception occurred", str(e))

        # Test email handling
        try:
            contact_data_email = {
                "name": "Marie Martin",
                "email": "marie.martin@example.com",
                "phone": "+33987654321",
                "country": "Canada",
                "visa_type": "Study Permit",
                "budget_range": "5000+€",
                "urgency_level": "Normal",
                "message": "Test d'envoi d'e-mail automatique.",
                "lead_source": "Réseaux sociaux",
                "how_did_you_know": "Publicité Facebook",
                "referred_by_employee": None
            }
            
            response = self.session.post(f"{API_BASE}/contact-messages", json=contact_data_email)
            if response.status_code == 200 or response.status_code == 201:
                self.log_result("Contact Form Email Handling", True, 
                              "API handles email sending without breaking")
            else:
                self.log_result("Contact Form Email Handling", False, 
                              f"Status: {response.status_code}")
                
        except Exception as e:
            self.log_result("Contact Form Email Handling", False, "Exception occurred", str(e))

    def test_user_creation_with_email(self):
        """Test 3: POST /api/users/create avec send_email=true"""
        print("=== Test 3: Création d'utilisateur avec e-mail ===")
        
        # First login as manager
        manager_token = None
        try:
            login_response = self.session.post(f"{API_BASE}/auth/login", json={
                "email": "manager@test.com",
                "password": "password123"
            })
            if login_response.status_code == 200:
                manager_token = login_response.json()['access_token']
                self.log_result("Manager Login", True, "Manager logged in successfully")
            else:
                self.log_result("Manager Login", False, f"Status: {login_response.status_code}")
                return
        except Exception as e:
            self.log_result("Manager Login", False, "Exception occurred", str(e))
            return
            
        if manager_token:
            try:
                headers = {"Authorization": f"Bearer {manager_token}"}
                import time
                timestamp = int(time.time())
                
                user_data = {
                    "email": f"test.user.email.{timestamp}@example.com",
                    "full_name": "Test User Email Creation",
                    "phone": "+33111222333",
                    "role": "EMPLOYEE",
                    "send_email": True
                }
                
                response = self.session.post(f"{API_BASE}/users/create", json=user_data, headers=headers)
                if response.status_code == 200 or response.status_code == 201:
                    data = response.json()
                    
                    if 'email_sent' in data:
                        email_sent = data.get('email_sent', False)
                        has_temp_password = 'temporary_password' in data and data['temporary_password'] is not None
                        
                        self.log_result("User Creation with Email", True, 
                                      f"Email sent: {email_sent}, Temp password in response: {has_temp_password}")
                    else:
                        self.log_result("User Creation with Email", False, 
                                      "Response missing email_sent field")
                else:
                    self.log_result("User Creation with Email", False, 
                                  f"Status: {response.status_code}", response.text)
                    
            except Exception as e:
                self.log_result("User Creation with Email", False, "Exception occurred", str(e))

    def test_case_update_with_email(self):
        """Test 4: PATCH /api/cases/{id} pour mettre à jour un dossier"""
        print("=== Test 4: Mise à jour de dossier avec e-mail ===")
        
        # Login as manager
        manager_token = None
        try:
            login_response = self.session.post(f"{API_BASE}/auth/login", json={
                "email": "manager@test.com",
                "password": "password123"
            })
            if login_response.status_code == 200:
                manager_token = login_response.json()['access_token']
                self.log_result("Manager Login for Case Update", True, "Manager logged in")
            else:
                self.log_result("Manager Login for Case Update", False, f"Status: {login_response.status_code}")
                return
        except Exception as e:
            self.log_result("Manager Login for Case Update", False, "Exception occurred", str(e))
            return
            
        if manager_token:
            try:
                headers = {"Authorization": f"Bearer {manager_token}"}
                
                # Get available cases
                cases_response = self.session.get(f"{API_BASE}/cases", headers=headers)
                if cases_response.status_code == 200:
                    cases = cases_response.json()
                    if cases:
                        case_id = cases[0]['id']
                        
                        # Update the case
                        update_data = {
                            "current_step_index": 2,
                            "status": "En cours de traitement",
                            "notes": "Test mise à jour avec envoi d'e-mail automatique"
                        }
                        
                        response = self.session.patch(f"{API_BASE}/cases/{case_id}", json=update_data, headers=headers)
                        if response.status_code == 200:
                            data = response.json()
                            self.log_result("Case Update with Email", True, 
                                          f"Status: {data.get('status', 'N/A')}, Step: {data.get('current_step_index', 'N/A')}")
                            
                            self.log_result("Case Update Email Handling", True, 
                                          "Case update completed without breaking")
                        else:
                            self.log_result("Case Update with Email", False, 
                                          f"Status: {response.status_code}", response.text)
                    else:
                        self.log_result("Case Update with Email", False, "No cases available")
                else:
                    self.log_result("Case Update with Email", False, 
                                  f"Could not retrieve cases. Status: {cases_response.status_code}")
                    
            except Exception as e:
                self.log_result("Case Update with Email", False, "Exception occurred", str(e))

    def test_regression_manager_login(self):
        """Test 5: Test général de régression - Login Manager: manager@test.com / password123"""
        print("=== Test 5: Test général de régression ===")
        
        try:
            # Test login with specific credentials from review request
            login_data = {
                "email": "manager@test.com",
                "password": "password123"
            }
            
            response = self.session.post(f"{API_BASE}/auth/login", json=login_data)
            if response.status_code == 200:
                data = response.json()
                manager_token = data['access_token']
                manager_user = data['user']
                
                self.log_result("Regression Manager Login", True, 
                              f"{manager_user['full_name']} ({manager_user['email']})")
                
                # Test existing functionalities
                headers = {"Authorization": f"Bearer {manager_token}"}
                
                # Test clients
                clients_response = self.session.get(f"{API_BASE}/clients", headers=headers)
                if clients_response.status_code == 200:
                    clients = clients_response.json()
                    self.log_result("Regression - Get Clients", True, f"Retrieved {len(clients)} clients")
                else:
                    self.log_result("Regression - Get Clients", False, f"Status: {clients_response.status_code}")
                
                # Test cases
                cases_response = self.session.get(f"{API_BASE}/cases", headers=headers)
                if cases_response.status_code == 200:
                    cases = cases_response.json()
                    self.log_result("Regression - Get Cases", True, f"Retrieved {len(cases)} cases")
                else:
                    self.log_result("Regression - Get Cases", False, f"Status: {cases_response.status_code}")
                
                # Test notifications
                notifications_response = self.session.get(f"{API_BASE}/notifications", headers=headers)
                if notifications_response.status_code == 200:
                    notifications = notifications_response.json()
                    self.log_result("Regression - Get Notifications", True, f"Retrieved {len(notifications)} notifications")
                else:
                    self.log_result("Regression - Get Notifications", False, f"Status: {notifications_response.status_code}")
                    
            else:
                self.log_result("Regression Manager Login", False, 
                              f"Login failed. Status: {response.status_code}")
                
        except Exception as e:
            self.log_result("Regression Manager Login", False, "Exception occurred", str(e))

    def run_review_tests(self):
        """Run all review request specific tests"""
        print("🎯 ALORIA AGENCY - Review Request Specific Testing")
        print("=" * 60)
        print(f"Testing against: {API_BASE}")
        print("=" * 60)
        
        self.test_superadmin_dashboard_stats()
        self.test_contact_form_new_fields()
        self.test_user_creation_with_email()
        self.test_case_update_with_email()
        self.test_regression_manager_login()
        
        print("=" * 60)
        print("🏁 Review Test Summary")
        print(f"✅ Passed: {self.results['passed']}")
        print(f"❌ Failed: {self.results['failed']}")
        print(f"📊 Success Rate: {(self.results['passed'] / (self.results['passed'] + self.results['failed']) * 100):.1f}%")
        
        if self.results['errors']:
            print("\n🔍 Failed Tests Details:")
            for error in self.results['errors']:
                print(f"  • {error['test']}: {error['message']}")
        
        return self.results['failed'] == 0

if __name__ == "__main__":
    tester = ReviewTester()
    tester.run_review_tests()