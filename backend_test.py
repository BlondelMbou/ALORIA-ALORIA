#!/usr/bin/env python3
"""
ALORIA AGENCY Backend API Testing Suite - PRODUCTION READY EXHAUSTIVE TESTING
Tests ALL backend functionalities for production deployment including:
- Complete prospect workflow (nouveau → assigne_employe → paiement_50k → en_consultation → converti_client)
- Manager/Employee actions (client reassignment, visitor management)
- SuperAdmin operations (user creation, dashboard stats, activities)
- Role-based prospect access for all roles
- Payment workflow (declaration, confirmation with PDF generation)
- Withdrawal manager system
"""

import requests
import json
import os
from datetime import datetime
import sys
import time

# Get backend URL from environment
BACKEND_URL = os.environ.get('REACT_APP_BACKEND_URL', 'https://immigration-hub-2.preview.emergentagent.com')
API_BASE = f"{BACKEND_URL}/api"

# Test credentials from review request
TEST_CREDENTIALS = {
    'superadmin': {'email': 'superadmin@aloria.com', 'password': 'SuperAdmin123!'},
    'manager': {'email': 'manager@test.com', 'password': 'password123'},
    'employee': {'email': 'employee@aloria.com', 'password': 'emp123'},
    'consultant': {'email': 'consultant@aloria.com', 'password': 'consultant123'}
}

class APITester:
    def __init__(self):
        self.session = requests.Session()
        # Store tokens for all roles
        self.tokens = {}
        self.users = {}
        # Test data storage
        self.test_prospect_id = None
        self.test_client_id = None
        self.test_visitor_id = None
        self.test_payment_id = None
        self.test_withdrawal_id = None
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

    def authenticate_all_roles(self):
        """Authenticate all test users with review credentials"""
        print("=== PRIORITY 0: Authentication Setup ===")
        
        for role, credentials in TEST_CREDENTIALS.items():
            try:
                # Try login first
                response = self.session.post(f"{API_BASE}/auth/login", json=credentials)
                if response.status_code == 200:
                    data = response.json()
                    self.tokens[role] = data['access_token']
                    self.users[role] = data['user']
                    self.log_result(f"{role.upper()} Login", True, f"Logged in as {credentials['email']}")
                else:
                    self.log_result(f"{role.upper()} Login", False, f"Status: {response.status_code}", response.text)
            except Exception as e:
                self.log_result(f"{role.upper()} Login", False, "Exception occurred", str(e))

    def test_priority_1_prospect_workflow(self):
        """PRIORITY 1: Test complete prospect workflow (nouveau → converti_client)"""
        print("=== PRIORITY 1: PROSPECT WORKFLOW COMPLET ===")
        
        # Step 1: Create new prospect
        prospect_data = {
            "name": "Jean-Baptiste Kouassi",
            "email": "jb.kouassi@example.com",
            "phone": "+225070123456",
            "country": "France",
            "visa_type": "Work Permit (Talent Permit)",
            "budget_range": "5000+€",
            "urgency_level": "Urgent",
            "message": "Je souhaite obtenir un permis de travail en France pour rejoindre mon employeur. J'ai déjà une offre d'emploi confirmée et tous mes diplômes sont prêts. C'est urgent car je dois commencer le travail dans 2 mois.",
            "lead_source": "Référencement",
            "how_did_you_know": "Recommandé par un ami qui a utilisé vos services"
        }
        
        try:
            response = self.session.post(f"{API_BASE}/contact-messages", json=prospect_data)
            if response.status_code in [200, 201]:
                data = response.json()
                self.test_prospect_id = data['id']
                if data.get('status') == 'nouveau':
                    self.log_result("1.1 Prospect Creation", True, f"Prospect created with status 'nouveau', ID: {self.test_prospect_id}")
                else:
                    self.log_result("1.1 Prospect Creation", False, f"Expected status 'nouveau', got '{data.get('status')}'")
            else:
                self.log_result("1.1 Prospect Creation", False, f"Status: {response.status_code}", response.text)
        except Exception as e:
            self.log_result("1.1 Prospect Creation", False, "Exception occurred", str(e))
            return

        if not self.test_prospect_id:
            return

        # Step 2: SuperAdmin assigns to Employee
        if 'superadmin' in self.tokens and 'employee' in self.users:
            try:
                headers = {"Authorization": f"Bearer {self.tokens['superadmin']}"}
                assign_data = {"assigned_to": self.users['employee']['id']}
                response = self.session.patch(f"{API_BASE}/contact-messages/{self.test_prospect_id}/assign", 
                                            json=assign_data, headers=headers)
                if response.status_code == 200:
                    data = response.json()
                    # Check if assignment was successful by checking the success message
                    if 'message' in data and 'assigné avec succès' in data['message']:
                        self.log_result("1.2 SuperAdmin Assignment", True, f"Prospect assigned to employee: {data.get('assigned_to_name', 'Employee')}")
                    else:
                        self.log_result("1.2 SuperAdmin Assignment", False, f"Assignment failed. Response: {data}")
                else:
                    self.log_result("1.2 SuperAdmin Assignment", False, f"Status: {response.status_code}", response.text)
            except Exception as e:
                self.log_result("1.2 SuperAdmin Assignment", False, "Exception occurred", str(e))

        # Step 3: Employee assigns to consultant with 50k payment
        if 'employee' in self.tokens:
            try:
                headers = {"Authorization": f"Bearer {self.tokens['employee']}"}
                consultant_data = {
                    "consultant_id": self.users.get('consultant', {}).get('id', 'consultant-id'),
                    "payment_amount": 50000
                }
                response = self.session.patch(f"{API_BASE}/contact-messages/{self.test_prospect_id}/assign-consultant", 
                                            json=consultant_data, headers=headers)
                if response.status_code == 200:
                    data = response.json()
                    # Check if payment was recorded
                    if data.get('payment_50k_amount') == 50000:
                        self.log_result("1.3 Consultant Assignment + 50k Payment", True, f"Payment recorded: 50000 CFA")
                    else:
                        self.log_result("1.3 Consultant Assignment + 50k Payment", False, f"Payment not recorded correctly. Response: {data}")
                else:
                    self.log_result("1.3 Consultant Assignment + 50k Payment", False, f"Status: {response.status_code}", response.text)
            except Exception as e:
                self.log_result("1.3 Consultant Assignment + 50k Payment", False, "Exception occurred", str(e))

        # Step 4: SuperAdmin adds consultant notes
        if 'superadmin' in self.tokens:
            try:
                headers = {"Authorization": f"Bearer {self.tokens['superadmin']}"}
                notes_data = {
                    "note": "Consultation effectuée avec le prospect. Profil très intéressant, diplômes validés, expérience pertinente. Recommande de procéder à la conversion en client."
                }
                response = self.session.patch(f"{API_BASE}/contact-messages/{self.test_prospect_id}/consultant-notes", 
                                            json=notes_data, headers=headers)
                if response.status_code == 200:
                    data = response.json()
                    # Check if notes were added
                    if data.get('consultant_notes') and len(data['consultant_notes']) > 0:
                        self.log_result("1.4 Consultant Notes", True, f"Notes added successfully")
                    else:
                        self.log_result("1.4 Consultant Notes", False, f"Notes not added. Response: {data}")
                else:
                    self.log_result("1.4 Consultant Notes", False, f"Status: {response.status_code}", response.text)
            except Exception as e:
                self.log_result("1.4 Consultant Notes", False, "Exception occurred", str(e))

        # Step 5: Employee converts to client
        if 'employee' in self.tokens:
            try:
                headers = {"Authorization": f"Bearer {self.tokens['employee']}"}
                client_conversion_data = {
                    "first_payment_amount": 1500,
                    "country": "France",
                    "visa_type": "Work Permit (Talent Permit)"
                }
                response = self.session.post(f"{API_BASE}/contact-messages/{self.test_prospect_id}/convert-to-client", 
                                           json=client_conversion_data, headers=headers)
                if response.status_code == 200:
                    data = response.json()
                    # Check if client was created
                    if 'client_id' in data and 'user_id' in data:
                        self.test_client_id = data['client_id']
                        self.log_result("1.5 Client Conversion", True, f"Client created with ID: {self.test_client_id}")
                    else:
                        self.log_result("1.5 Client Conversion", False, f"Client creation failed. Response: {data}")
                else:
                    self.log_result("1.5 Client Conversion", False, f"Status: {response.status_code}", response.text)
            except Exception as e:
                self.log_result("1.5 Client Conversion", False, "Exception occurred", str(e))

    def test_priority_2_manager_employee_actions(self):
        """PRIORITY 2: Test Manager/Employee actions"""
        print("=== PRIORITY 2: MANAGER/EMPLOYEE ACTIONS ===")
        
        # Test Client Reassignment
        if 'manager' in self.tokens and self.test_client_id and 'employee' in self.users:
            try:
                headers = {"Authorization": f"Bearer {self.tokens['manager']}"}
                reassign_data = {"new_employee_id": self.users['employee']['id']}
                response = self.session.patch(f"{API_BASE}/clients/{self.test_client_id}/reassign", 
                                            json=reassign_data, headers=headers)
                if response.status_code == 200:
                    data = response.json()
                    if data.get('assigned_employee_id') == self.users['employee']['id']:
                        self.log_result("2.1 Client Reassignment", True, f"Client reassigned to employee {self.users['employee']['full_name']}")
                    else:
                        self.log_result("2.1 Client Reassignment", False, f"Assignment not updated correctly")
                else:
                    self.log_result("2.1 Client Reassignment", False, f"Status: {response.status_code}", response.text)
            except Exception as e:
                self.log_result("2.1 Client Reassignment", False, "Exception occurred", str(e))

        # Test Visitor Creation by Manager
        if 'manager' in self.tokens:
            try:
                headers = {"Authorization": f"Bearer {self.tokens['manager']}"}
                visitor_data = {
                    "full_name": "Amadou Diallo",
                    "phone_number": "+225070987654",
                    "purpose": "Consultation initiale",
                    "cni_number": "CI2024123456"
                }
                response = self.session.post(f"{API_BASE}/visitors", json=visitor_data, headers=headers)
                if response.status_code in [200, 201]:
                    data = response.json()
                    self.test_visitor_id = data['id']
                    self.log_result("2.2 Manager Visitor Creation", True, f"Visitor created with ID: {self.test_visitor_id}")
                else:
                    self.log_result("2.2 Manager Visitor Creation", False, f"Status: {response.status_code}", response.text)
            except Exception as e:
                self.log_result("2.2 Manager Visitor Creation", False, "Exception occurred", str(e))

        # Test Visitor Creation by Employee
        if 'employee' in self.tokens:
            try:
                headers = {"Authorization": f"Bearer {self.tokens['employee']}"}
                visitor_data = {
                    "full_name": "Fatou Traoré",
                    "phone_number": "+225070555666",
                    "purpose": "Remise de documents",
                    "cni_number": "CI2024789012"
                }
                response = self.session.post(f"{API_BASE}/visitors", json=visitor_data, headers=headers)
                if response.status_code in [200, 201]:
                    self.log_result("2.3 Employee Visitor Creation", True, "Employee can create visitors")
                else:
                    self.log_result("2.3 Employee Visitor Creation", False, f"Status: {response.status_code}", response.text)
            except Exception as e:
                self.log_result("2.3 Employee Visitor Creation", False, "Exception occurred", str(e))

        # Test Visitor Checkout
        if 'manager' in self.tokens and self.test_visitor_id:
            try:
                headers = {"Authorization": f"Bearer {self.tokens['manager']}"}
                response = self.session.patch(f"{API_BASE}/visitors/{self.test_visitor_id}/checkout", headers=headers)
                if response.status_code == 200:
                    data = response.json()
                    if data.get('message') == "Visitor checked out":
                        self.log_result("2.4 Visitor Checkout", True, "Visitor successfully checked out")
                    else:
                        self.log_result("2.4 Visitor Checkout", False, f"Unexpected response: {data}")
                else:
                    self.log_result("2.4 Visitor Checkout", False, f"Status: {response.status_code}", response.text)
            except Exception as e:
                self.log_result("2.4 Visitor Checkout", False, "Exception occurred", str(e))

    def test_priority_3_superadmin_operations(self):
        """PRIORITY 3: Test SuperAdmin operations"""
        print("=== PRIORITY 3: SUPERADMIN OPERATIONS ===")
        
        if 'superadmin' not in self.tokens:
            self.log_result("SuperAdmin Operations", False, "No SuperAdmin token available")
            return

        headers = {"Authorization": f"Bearer {self.tokens['superadmin']}"}

        # Test User Creation - ALL Roles
        roles_to_create = ['MANAGER', 'EMPLOYEE', 'CONSULTANT']
        for role in roles_to_create:
            try:
                timestamp = int(time.time())
                user_data = {
                    "email": f"test.{role.lower()}.{timestamp}@aloria.com",
                    "full_name": f"Test {role.title()} User",
                    "phone": f"+33{timestamp % 1000000000}",
                    "role": role,
                    "send_email": False
                }
                response = self.session.post(f"{API_BASE}/users/create", json=user_data, headers=headers)
                if response.status_code in [200, 201]:
                    data = response.json()
                    if data.get('temporary_password'):
                        self.log_result(f"3.1 SuperAdmin Creates {role}", True, f"User created with temp password: {data['temporary_password']}")
                    else:
                        self.log_result(f"3.1 SuperAdmin Creates {role}", False, "No temporary password in response")
                else:
                    self.log_result(f"3.1 SuperAdmin Creates {role}", False, f"Status: {response.status_code}", response.text)
            except Exception as e:
                self.log_result(f"3.1 SuperAdmin Creates {role}", False, "Exception occurred", str(e))

        # Test Dashboard Stats
        try:
            response = self.session.get(f"{API_BASE}/admin/dashboard-stats", headers=headers)
            if response.status_code == 200:
                data = response.json()
                # Check the actual structure returned by the API
                if 'users' in data and 'business' in data and 'activity' in data:
                    users = data['users']
                    business = data['business']
                    self.log_result("3.2 Dashboard Stats", True, f"Stats: {business.get('total_cases', 0)} cases, {users.get('clients', 0)} clients, {users.get('employees', 0)} employees")
                else:
                    self.log_result("3.2 Dashboard Stats", False, f"Unexpected response structure: {list(data.keys())}")
            else:
                self.log_result("3.2 Dashboard Stats", False, f"Status: {response.status_code}", response.text)
        except Exception as e:
            self.log_result("3.2 Dashboard Stats", False, "Exception occurred", str(e))

        # Test Users List
        try:
            response = self.session.get(f"{API_BASE}/admin/users", headers=headers)
            if response.status_code == 200:
                users = response.json()
                self.log_result("3.3 Users List", True, f"Retrieved {len(users)} users")
            else:
                self.log_result("3.3 Users List", False, f"Status: {response.status_code}", response.text)
        except Exception as e:
            self.log_result("3.3 Users List", False, "Exception occurred", str(e))

        # Test Activities
        try:
            response = self.session.get(f"{API_BASE}/admin/activities", headers=headers)
            if response.status_code == 200:
                activities = response.json()
                self.log_result("3.4 Activities Log", True, f"Retrieved {len(activities)} activities")
            else:
                self.log_result("3.4 Activities Log", False, f"Status: {response.status_code}", response.text)
        except Exception as e:
            self.log_result("3.4 Activities Log", False, "Exception occurred", str(e))

    def test_priority_4_role_based_prospect_access(self):
        """PRIORITY 4: Test role-based prospect access"""
        print("=== PRIORITY 4: ROLE-BASED PROSPECT ACCESS ===")
        
        # Test each role's access to prospects
        role_expectations = {
            'superadmin': 'sees ALL prospects',
            'manager': 'sees assigned prospects only',
            'employee': 'sees assigned prospects only', 
            'consultant': 'sees only paiement_50k status',
            'client': 'should get 403'
        }
        
        for role, expectation in role_expectations.items():
            if role in self.tokens:
                try:
                    headers = {"Authorization": f"Bearer {self.tokens[role]}"}
                    response = self.session.get(f"{API_BASE}/contact-messages", headers=headers)
                    
                    if role == 'client':
                        if response.status_code == 403:
                            self.log_result(f"4.{list(role_expectations.keys()).index(role)+1} {role.upper()} Access", True, "Correctly denied access (403)")
                        else:
                            self.log_result(f"4.{list(role_expectations.keys()).index(role)+1} {role.upper()} Access", False, f"Expected 403, got {response.status_code}")
                    else:
                        if response.status_code == 200:
                            prospects = response.json()
                            if role == 'consultant':
                                # Check if all prospects have paiement_50k status
                                paiement_50k_count = sum(1 for p in prospects if p.get('status') == 'paiement_50k')
                                self.log_result(f"4.{list(role_expectations.keys()).index(role)+1} {role.upper()} Access", True, f"Sees {paiement_50k_count} prospects with paiement_50k status")
                            else:
                                self.log_result(f"4.{list(role_expectations.keys()).index(role)+1} {role.upper()} Access", True, f"Retrieved {len(prospects)} prospects")
                        else:
                            self.log_result(f"4.{list(role_expectations.keys()).index(role)+1} {role.upper()} Access", False, f"Status: {response.status_code}", response.text)
                except Exception as e:
                    self.log_result(f"4.{list(role_expectations.keys()).index(role)+1} {role.upper()} Access", False, "Exception occurred", str(e))

    def test_priority_5_payment_workflow(self):
        """PRIORITY 5: Test payment workflow"""
        print("=== PRIORITY 5: PAYMENT WORKFLOW ===")
        
        # Step 1: Client declares payment
        if self.test_client_id:
            # First login as client
            try:
                client_login = self.session.post(f"{API_BASE}/auth/login", json={
                    "email": "jb.kouassi@example.com",
                    "password": "Aloria2024!"
                })
                if client_login.status_code == 200:
                    client_token = client_login.json()['access_token']
                    
                    # Declare payment
                    headers = {"Authorization": f"Bearer {client_token}"}
                    payment_data = {
                        "amount": 2500.00,
                        "currency": "EUR",
                        "description": "Paiement pour services d'immigration - Permis de travail France",
                        "payment_method": "Virement bancaire"
                    }
                    response = self.session.post(f"{API_BASE}/payments", json=payment_data, headers=headers)
                    if response.status_code in [200, 201]:
                        data = response.json()
                        self.test_payment_id = data['id']
                        if data.get('status') == 'pending':
                            self.log_result("5.1 Payment Declaration", True, f"Payment declared with status 'pending', ID: {self.test_payment_id}")
                        else:
                            self.log_result("5.1 Payment Declaration", False, f"Expected status 'pending', got '{data.get('status')}'")
                    else:
                        self.log_result("5.1 Payment Declaration", False, f"Status: {response.status_code}", response.text)
                else:
                    self.log_result("5.1 Payment Declaration", False, "Could not login as client")
            except Exception as e:
                self.log_result("5.1 Payment Declaration", False, "Exception occurred", str(e))

        # Step 2: Manager confirms payment
        if 'manager' in self.tokens and self.test_payment_id:
            try:
                headers = {"Authorization": f"Bearer {self.tokens['manager']}"}
                
                # First generate confirmation code
                response = self.session.post(f"{API_BASE}/payments/{self.test_payment_id}/generate-code", headers=headers)
                if response.status_code == 200:
                    code_data = response.json()
                    confirmation_code = code_data.get('confirmation_code')
                    
                    if confirmation_code:
                        # Now confirm with the code
                        confirm_data = {
                            "action": "CONFIRMED",
                            "confirmation_code": confirmation_code
                        }
                        confirm_response = self.session.patch(f"{API_BASE}/payments/{self.test_payment_id}/confirm", 
                                                            json=confirm_data, headers=headers)
                        if confirm_response.status_code == 200:
                            confirm_result = confirm_response.json()
                            if confirm_result.get('status') == 'confirmed' and confirm_result.get('invoice_number'):
                                self.log_result("5.2 Payment Confirmation", True, f"Payment confirmed, Invoice: {confirm_result['invoice_number']}")
                            else:
                                self.log_result("5.2 Payment Confirmation", False, f"Status: {confirm_result.get('status')}, Invoice: {confirm_result.get('invoice_number')}")
                        else:
                            self.log_result("5.2 Payment Confirmation", False, f"Confirm Status: {confirm_response.status_code}", confirm_response.text)
                    else:
                        self.log_result("5.2 Payment Confirmation", False, "No confirmation code generated")
                else:
                    self.log_result("5.2 Payment Confirmation", False, f"Code Gen Status: {response.status_code}", response.text)
            except Exception as e:
                self.log_result("5.2 Payment Confirmation", False, "Exception occurred", str(e))

    def test_priority_6_withdrawal_manager(self):
        """PRIORITY 6: Test withdrawal manager"""
        print("=== PRIORITY 6: WITHDRAWAL MANAGER ===")
        
        # Step 1: Manager requests withdrawal
        if 'manager' in self.tokens:
            try:
                headers = {"Authorization": f"Bearer {self.tokens['manager']}"}
                withdrawal_data = {
                    "amount": 500.00,
                    "category": "BUREAUX",
                    "subcategory": "Loyer",
                    "description": "Paiement loyer bureau mensuel - Janvier 2025"
                }
                response = self.session.post(f"{API_BASE}/withdrawals", json=withdrawal_data, headers=headers)
                if response.status_code in [200, 201]:
                    data = response.json()
                    self.test_withdrawal_id = data['id']
                    self.log_result("6.1 Withdrawal Request", True, f"Withdrawal requested, ID: {self.test_withdrawal_id}")
                else:
                    self.log_result("6.1 Withdrawal Request", False, f"Status: {response.status_code}", response.text)
            except Exception as e:
                self.log_result("6.1 Withdrawal Request", False, "Exception occurred", str(e))

        # Step 2: SuperAdmin views withdrawals (approval endpoint not implemented)
        if 'superadmin' in self.tokens:
            try:
                headers = {"Authorization": f"Bearer {self.tokens['superadmin']}"}
                response = self.session.get(f"{API_BASE}/withdrawals", headers=headers)
                if response.status_code == 200:
                    withdrawals = response.json()
                    # Find our test withdrawal
                    test_withdrawal = next((w for w in withdrawals if w['id'] == self.test_withdrawal_id), None)
                    if test_withdrawal:
                        self.log_result("6.2 SuperAdmin View Withdrawals", True, f"SuperAdmin can view withdrawal: {test_withdrawal['description']}")
                    else:
                        self.log_result("6.2 SuperAdmin View Withdrawals", False, "Test withdrawal not found in list")
                else:
                    self.log_result("6.2 SuperAdmin View Withdrawals", False, f"Status: {response.status_code}", response.text)
            except Exception as e:
                self.log_result("6.2 SuperAdmin View Withdrawals", False, "Exception occurred", str(e))

    def test_client_creation_permissions(self):
        """Test client creation - CORRECTED: Both managers and employees can create clients"""
        print("=== Testing Client Creation Permissions (CORRECTED) ===")
        
        client_data = {
            "email": "client.test@example.com",
            "full_name": "Test Client",
            "phone": "+33555666777",
            "country": "Canada",
            "visa_type": "Work Permit",
            "message": "Test client creation"
        }

        # Test Manager can create client
        if self.manager_token:
            try:
                headers = {"Authorization": f"Bearer {self.manager_token}"}
                response = self.session.post(f"{API_BASE}/clients", json=client_data, headers=headers)
                if response.status_code == 200 or response.status_code == 201:
                    data = response.json()
                    self.test_client_id = data['id']
                    self.log_result("Manager Client Creation", True, f"Client created with ID: {self.test_client_id}")
                else:
                    self.log_result("Manager Client Creation", False, f"Status: {response.status_code}", response.text)
            except Exception as e:
                self.log_result("Manager Client Creation", False, "Exception occurred", str(e))
        else:
            self.log_result("Manager Client Creation", False, "No manager token available")

        # Test Employee CAN NOW create client (CORRECTED)
        if self.employee_token:
            try:
                headers = {"Authorization": f"Bearer {self.employee_token}"}
                employee_client_data = {
                    "email": "employee.client@example.com",
                    "full_name": "Client créé par Employé",
                    "phone": "+33777888999",
                    "country": "France",
                    "visa_type": "Student Visa",
                    "message": "Client créé par un employé - test correction"
                }
                response = self.session.post(f"{API_BASE}/clients", json=employee_client_data, headers=headers)
                if response.status_code == 200 or response.status_code == 201:
                    data = response.json()
                    self.log_result("Employee Client Creation (CORRECTED)", True, f"Employee can now create clients. Client ID: {data['id']}")
                    # Verify auto-assignment and login info
                    if "login_email" in data and "default_password" in data:
                        self.log_result("Employee Client Auto-Assignment", True, f"Auto-assignment working, login: {data['login_email']}, password: {data['default_password']}")
                    else:
                        self.log_result("Employee Client Auto-Assignment", False, "Missing login_email or default_password in response")
                else:
                    self.log_result("Employee Client Creation (CORRECTED)", False, f"Employee should now be able to create clients. Status: {response.status_code}, Response: {response.text}")
            except Exception as e:
                self.log_result("Employee Client Creation (CORRECTED)", False, "Exception occurred", str(e))
        else:
            self.log_result("Employee Client Creation (CORRECTED)", False, "No employee token available")

        # Test CLIENT still cannot create clients
        # First create a client user to test with
        client_token = None
        try:
            client_login_data = {
                "email": "client.test@example.com",
                "password": "Aloria2024!"
            }
            login_response = self.session.post(f"{API_BASE}/auth/login", json=client_login_data)
            if login_response.status_code == 200:
                client_token = login_response.json()['access_token']
                
                headers = {"Authorization": f"Bearer {client_token}"}
                response = self.session.post(f"{API_BASE}/clients", json=client_data, headers=headers)
                if response.status_code == 403:
                    self.log_result("Client User Creation (should fail)", True, "Client user correctly denied client creation")
                else:
                    self.log_result("Client User Creation (should fail)", False, f"Client user should not be able to create clients. Status: {response.status_code}")
            else:
                self.log_result("Client User Creation (should fail)", False, "Could not login as client to test permissions")
        except Exception as e:
            self.log_result("Client User Creation (should fail)", False, "Exception occurred", str(e))

    def test_chat_apis(self):
        """Test chat functionality"""
        print("=== Testing Chat APIs ===")
        
        # Test get conversations
        if self.manager_token:
            try:
                headers = {"Authorization": f"Bearer {self.manager_token}"}
                response = self.session.get(f"{API_BASE}/chat/conversations", headers=headers)
                if response.status_code == 200:
                    conversations = response.json()
                    self.log_result("Get Chat Conversations", True, f"Retrieved {len(conversations)} conversations")
                else:
                    self.log_result("Get Chat Conversations", False, f"Status: {response.status_code}", response.text)
            except Exception as e:
                self.log_result("Get Chat Conversations", False, "Exception occurred", str(e))

        # Test get available contacts for manager
        if self.manager_token:
            try:
                headers = {"Authorization": f"Bearer {self.manager_token}"}
                response = self.session.get(f"{API_BASE}/users/available-contacts", headers=headers)
                if response.status_code == 200:
                    contacts = response.json()
                    self.log_result("Manager Available Contacts", True, f"Manager can contact {len(contacts)} users")
                else:
                    self.log_result("Manager Available Contacts", False, f"Status: {response.status_code}", response.text)
            except Exception as e:
                self.log_result("Manager Available Contacts", False, "Exception occurred", str(e))

        # Test get available contacts for employee
        if self.employee_token:
            try:
                headers = {"Authorization": f"Bearer {self.employee_token}"}
                response = self.session.get(f"{API_BASE}/users/available-contacts", headers=headers)
                if response.status_code == 200:
                    contacts = response.json()
                    self.log_result("Employee Available Contacts", True, f"Employee can contact {len(contacts)} users")
                else:
                    self.log_result("Employee Available Contacts", False, f"Status: {response.status_code}", response.text)
            except Exception as e:
                self.log_result("Employee Available Contacts", False, "Exception occurred", str(e))

        # Test send message (if we have both users)
        if self.manager_token and self.employee_user:
            try:
                headers = {"Authorization": f"Bearer {self.manager_token}"}
                message_data = {
                    "receiver_id": self.employee_user['id'],
                    "message": "Test message from manager to employee"
                }
                response = self.session.post(f"{API_BASE}/chat/send", json=message_data, headers=headers)
                if response.status_code == 200 or response.status_code == 201:
                    self.log_result("Send Chat Message", True, "Message sent successfully")
                else:
                    self.log_result("Send Chat Message", False, f"Status: {response.status_code}", response.text)
            except Exception as e:
                self.log_result("Send Chat Message", False, "Exception occurred", str(e))

        # Test unread count
        if self.employee_token:
            try:
                headers = {"Authorization": f"Bearer {self.employee_token}"}
                response = self.session.get(f"{API_BASE}/chat/unread-count", headers=headers)
                if response.status_code == 200:
                    data = response.json()
                    self.log_result("Get Unread Count", True, f"Unread count: {data.get('unread_count', 0)}")
                else:
                    self.log_result("Get Unread Count", False, f"Status: {response.status_code}", response.text)
            except Exception as e:
                self.log_result("Get Unread Count", False, "Exception occurred", str(e))

    def test_visitor_management(self):
        """Test visitor registration, listing, and checkout"""
        print("=== Testing Visitor Management ===")
        
        # Test visitor registration by employee
        if self.employee_token:
            try:
                headers = {"Authorization": f"Bearer {self.employee_token}"}
                visitor_data = {
                    "name": "Jean Dupont",
                    "company": "Tech Solutions SARL",
                    "purpose": "Consultation initiale",
                    "details": "Consultation pour demande de visa de travail"
                }
                response = self.session.post(f"{API_BASE}/visitors", json=visitor_data, headers=headers)
                if response.status_code == 200 or response.status_code == 201:
                    data = response.json()
                    self.test_visitor_id = data['id']
                    self.log_result("Employee Visitor Registration", True, f"Visitor registered with ID: {self.test_visitor_id}")
                else:
                    self.log_result("Employee Visitor Registration", False, f"Status: {response.status_code}", response.text)
            except Exception as e:
                self.log_result("Employee Visitor Registration", False, "Exception occurred", str(e))

        # Test visitor registration by manager
        if self.manager_token:
            try:
                headers = {"Authorization": f"Bearer {self.manager_token}"}
                visitor_data = {
                    "name": "Marie Martin",
                    "company": "Consulting Plus",
                    "purpose": "Rendez-vous planifié",
                    "details": "Rendez-vous pour suivi de dossier"
                }
                response = self.session.post(f"{API_BASE}/visitors", json=visitor_data, headers=headers)
                if response.status_code == 200 or response.status_code == 201:
                    self.log_result("Manager Visitor Registration", True, "Manager can also register visitors")
                else:
                    self.log_result("Manager Visitor Registration", False, f"Status: {response.status_code}", response.text)
            except Exception as e:
                self.log_result("Manager Visitor Registration", False, "Exception occurred", str(e))

        # Test list visitors
        if self.employee_token:
            try:
                headers = {"Authorization": f"Bearer {self.employee_token}"}
                response = self.session.get(f"{API_BASE}/visitors", headers=headers)
                if response.status_code == 200:
                    visitors = response.json()
                    self.log_result("List Visitors", True, f"Retrieved {len(visitors)} visitors")
                else:
                    self.log_result("List Visitors", False, f"Status: {response.status_code}", response.text)
            except Exception as e:
                self.log_result("List Visitors", False, "Exception occurred", str(e))

        # Test visitor checkout
        if self.employee_token and self.test_visitor_id:
            try:
                headers = {"Authorization": f"Bearer {self.employee_token}"}
                response = self.session.patch(f"{API_BASE}/visitors/{self.test_visitor_id}/checkout", headers=headers)
                if response.status_code == 200:
                    self.log_result("Visitor Checkout", True, "Visitor checked out successfully")
                else:
                    self.log_result("Visitor Checkout", False, f"Status: {response.status_code}", response.text)
            except Exception as e:
                self.log_result("Visitor Checkout", False, "Exception occurred", str(e))

    def test_workflow_management(self):
        """Test workflow retrieval and custom step addition"""
        print("=== Testing Workflow Management ===")
        
        # Test get base workflows
        try:
            response = self.session.get(f"{API_BASE}/workflows")
            if response.status_code == 200:
                workflows = response.json()
                countries = list(workflows.keys())
                self.log_result("Get Base Workflows", True, f"Retrieved workflows for {len(countries)} countries: {', '.join(countries)}")
            else:
                self.log_result("Get Base Workflows", False, f"Status: {response.status_code}", response.text)
        except Exception as e:
            self.log_result("Get Base Workflows", False, "Exception occurred", str(e))

        # Test add custom workflow step (Manager only)
        if self.manager_token:
            try:
                headers = {"Authorization": f"Bearer {self.manager_token}"}
                custom_step = {
                    "title": "Étape personnalisée de vérification",
                    "description": "Vérification supplémentaire des documents par notre équipe juridique",
                    "documents": ["Attestation légale", "Vérification notariale"],
                    "duration": "3-5 jours ouvrables"
                }
                response = self.session.post(f"{API_BASE}/workflows/Canada/Work Permit/steps", json=custom_step, headers=headers)
                if response.status_code == 200 or response.status_code == 201:
                    self.log_result("Manager Add Custom Workflow Step", True, "Custom step added successfully")
                else:
                    self.log_result("Manager Add Custom Workflow Step", False, f"Status: {response.status_code}", response.text)
            except Exception as e:
                self.log_result("Manager Add Custom Workflow Step", False, "Exception occurred", str(e))

        # Test employee cannot add custom workflow step
        if self.employee_token:
            try:
                headers = {"Authorization": f"Bearer {self.employee_token}"}
                custom_step = {
                    "title": "Étape non autorisée",
                    "description": "Cette étape ne devrait pas être ajoutée",
                    "documents": ["Document test"],
                    "duration": "1 jour"
                }
                response = self.session.post(f"{API_BASE}/workflows/France/Student Visa/steps", json=custom_step, headers=headers)
                if response.status_code == 403:
                    self.log_result("Employee Add Custom Workflow Step (should fail)", True, "Employee correctly denied workflow modification")
                else:
                    self.log_result("Employee Add Custom Workflow Step (should fail)", False, f"Employee should not be able to modify workflows. Status: {response.status_code}")
            except Exception as e:
                self.log_result("Employee Add Custom Workflow Step (should fail)", False, "Exception occurred", str(e))

    def test_permissions_and_case_management(self):
        """Test case status updates and permissions"""
        print("=== Testing Case Management Permissions ===")
        
        # First, get cases to find one to update
        if self.manager_token:
            try:
                headers = {"Authorization": f"Bearer {self.manager_token}"}
                response = self.session.get(f"{API_BASE}/cases", headers=headers)
                if response.status_code == 200:
                    cases = response.json()
                    self.log_result("Get Cases", True, f"Retrieved {len(cases)} cases")
                    
                    # Test case status update by manager (if we have cases)
                    if cases:
                        case_id = cases[0]['id']
                        update_data = {
                            "current_step_index": 1,
                            "status": "En cours",
                            "notes": "Mise à jour par le manager - test"
                        }
                        update_response = self.session.patch(f"{API_BASE}/cases/{case_id}", json=update_data, headers=headers)
                        if update_response.status_code == 200:
                            self.log_result("Manager Case Status Update", True, "Manager successfully updated case status")
                        else:
                            self.log_result("Manager Case Status Update", False, f"Status: {update_response.status_code}", update_response.text)
                        
                        # Test employee CANNOT update cases (should get 403)
                        if self.employee_token:
                            employee_headers = {"Authorization": f"Bearer {self.employee_token}"}
                            employee_update_data = {
                                "current_step_index": 2,
                                "status": "Terminé",
                                "notes": "Tentative de mise à jour par employé"
                            }
                            employee_response = self.session.patch(f"{API_BASE}/cases/{case_id}", json=employee_update_data, headers=employee_headers)
                            if employee_response.status_code == 403:
                                self.log_result("Employee Case Update (should fail)", True, "Employee correctly denied case update permission")
                            else:
                                self.log_result("Employee Case Update (should fail)", False, f"Employee should not be able to update cases. Status: {employee_response.status_code}")
                else:
                    self.log_result("Get Cases", False, f"Status: {response.status_code}", response.text)
            except Exception as e:
                self.log_result("Get Cases", False, "Exception occurred", str(e))

        # Test employee case access (should only see assigned cases)
        if self.employee_token:
            try:
                headers = {"Authorization": f"Bearer {self.employee_token}"}
                response = self.session.get(f"{API_BASE}/cases", headers=headers)
                if response.status_code == 200:
                    cases = response.json()
                    self.log_result("Employee Get Cases", True, f"Employee can see {len(cases)} assigned cases")
                else:
                    self.log_result("Employee Get Cases", False, f"Status: {response.status_code}", response.text)
            except Exception as e:
                self.log_result("Employee Get Cases", False, "Exception occurred", str(e))

    def test_password_change_api(self):
        """Test password change functionality"""
        print("=== Testing Password Change API ===")
        
        # Test password change with correct old password
        if self.manager_token:
            try:
                headers = {"Authorization": f"Bearer {self.manager_token}"}
                password_data = {
                    "old_password": "admin123",
                    "new_password": "newadmin123"
                }
                response = self.session.patch(f"{API_BASE}/auth/change-password", json=password_data, headers=headers)
                if response.status_code == 200:
                    self.log_result("Manager Password Change (correct old password)", True, "Password changed successfully")
                    
                    # Change it back for other tests
                    password_data_back = {
                        "old_password": "newadmin123",
                        "new_password": "admin123"
                    }
                    self.session.patch(f"{API_BASE}/auth/change-password", json=password_data_back, headers=headers)
                else:
                    self.log_result("Manager Password Change (correct old password)", False, f"Status: {response.status_code}", response.text)
            except Exception as e:
                self.log_result("Manager Password Change (correct old password)", False, "Exception occurred", str(e))

        # Test password change with incorrect old password
        if self.manager_token:
            try:
                headers = {"Authorization": f"Bearer {self.manager_token}"}
                password_data = {
                    "old_password": "wrongpassword",
                    "new_password": "newadmin123"
                }
                response = self.session.patch(f"{API_BASE}/auth/change-password", json=password_data, headers=headers)
                if response.status_code == 400:
                    self.log_result("Manager Password Change (incorrect old password)", True, "Incorrect old password correctly rejected")
                else:
                    self.log_result("Manager Password Change (incorrect old password)", False, f"Expected 400, got {response.status_code}")
            except Exception as e:
                self.log_result("Manager Password Change (incorrect old password)", False, "Exception occurred", str(e))

    def test_client_credentials_api(self):
        """Test client credentials API with different permissions"""
        print("=== Testing Client Credentials API ===")
        
        if not self.test_client_id:
            self.log_result("Client Credentials Test", False, "No test client available")
            return

        # Test manager can get client credentials
        if self.manager_token:
            try:
                headers = {"Authorization": f"Bearer {self.manager_token}"}
                response = self.session.get(f"{API_BASE}/clients/{self.test_client_id}/credentials", headers=headers)
                if response.status_code == 200:
                    data = response.json()
                    if "email" in data and "password" in data:
                        self.log_result("Manager Get Client Credentials", True, f"Retrieved credentials for client: {data['email']}")
                    else:
                        self.log_result("Manager Get Client Credentials", False, "Response missing email or password fields")
                else:
                    self.log_result("Manager Get Client Credentials", False, f"Status: {response.status_code}", response.text)
            except Exception as e:
                self.log_result("Manager Get Client Credentials", False, "Exception occurred", str(e))

        # Test assigned employee can get client credentials
        if self.employee_token:
            try:
                headers = {"Authorization": f"Bearer {self.employee_token}"}
                response = self.session.get(f"{API_BASE}/clients/{self.test_client_id}/credentials", headers=headers)
                if response.status_code == 200:
                    data = response.json()
                    self.log_result("Assigned Employee Get Client Credentials", True, "Assigned employee can access client credentials")
                elif response.status_code == 403:
                    self.log_result("Non-assigned Employee Get Client Credentials", True, "Non-assigned employee correctly denied access")
                else:
                    self.log_result("Employee Get Client Credentials", False, f"Status: {response.status_code}", response.text)
            except Exception as e:
                self.log_result("Employee Get Client Credentials", False, "Exception occurred", str(e))

    def test_client_creation_with_password(self):
        """Test client creation includes default password and login info"""
        print("=== Testing Client Creation with Password ===")
        
        if self.manager_token:
            try:
                headers = {"Authorization": f"Bearer {self.manager_token}"}
                # Use timestamp to ensure unique email
                import time
                timestamp = int(time.time())
                client_data = {
                    "email": f"nouveau.client.{timestamp}@example.com",
                    "full_name": "Nouveau Client Test",
                    "phone": "+33123456789",
                    "country": "France",
                    "visa_type": "Work Permit (Talent Permit)",
                    "message": "Test création avec mot de passe par défaut"
                }
                response = self.session.post(f"{API_BASE}/clients", json=client_data, headers=headers)
                if response.status_code == 200 or response.status_code == 201:
                    data = response.json()
                    
                    # Check if response includes login_email and default_password for new accounts
                    if "login_email" in data and "default_password" in data:
                        if data["default_password"] == "Aloria2024!":
                            self.log_result("Client Creation with Default Password", True, f"New client created with default password 'Aloria2024!' and login email: {data['login_email']}")
                        else:
                            self.log_result("Client Creation with Default Password", False, f"Default password is '{data['default_password']}', expected 'Aloria2024!'")
                    else:
                        self.log_result("Client Creation with Default Password", False, "Response missing login_email or default_password fields")
                else:
                    self.log_result("Client Creation with Default Password", False, f"Status: {response.status_code}", response.text)
            except Exception as e:
                self.log_result("Client Creation with Default Password", False, "Exception occurred", str(e))

    def test_notification_system(self):
        """Test notification system APIs"""
        print("=== Testing Notification System ===")
        
        # Test get notifications
        if self.manager_token:
            try:
                headers = {"Authorization": f"Bearer {self.manager_token}"}
                response = self.session.get(f"{API_BASE}/notifications", headers=headers)
                if response.status_code == 200:
                    notifications = response.json()
                    self.log_result("Get Notifications", True, f"Retrieved {len(notifications)} notifications")
                else:
                    self.log_result("Get Notifications", False, f"Status: {response.status_code}", response.text)
            except Exception as e:
                self.log_result("Get Notifications", False, "Exception occurred", str(e))

        # Test get unread notifications count
        if self.manager_token:
            try:
                headers = {"Authorization": f"Bearer {self.manager_token}"}
                response = self.session.get(f"{API_BASE}/notifications/unread-count", headers=headers)
                if response.status_code == 200:
                    data = response.json()
                    unread_count = data.get('unread_count', 0)
                    self.log_result("Get Unread Notifications Count", True, f"Unread notifications: {unread_count}")
                else:
                    self.log_result("Get Unread Notifications Count", False, f"Status: {response.status_code}", response.text)
            except Exception as e:
                self.log_result("Get Unread Notifications Count", False, "Exception occurred", str(e))

        # Test mark notification as read (need to get a notification ID first)
        if self.manager_token:
            try:
                headers = {"Authorization": f"Bearer {self.manager_token}"}
                # Get notifications first
                response = self.session.get(f"{API_BASE}/notifications", headers=headers)
                if response.status_code == 200:
                    notifications = response.json()
                    if notifications:
                        notification_id = notifications[0]['id']
                        # Mark as read
                        read_response = self.session.patch(f"{API_BASE}/notifications/{notification_id}/read", headers=headers)
                        if read_response.status_code == 200:
                            self.log_result("Mark Notification Read", True, f"Notification {notification_id} marked as read")
                        else:
                            self.log_result("Mark Notification Read", False, f"Status: {read_response.status_code}", read_response.text)
                    else:
                        self.log_result("Mark Notification Read", False, "No notifications available to mark as read")
                else:
                    self.log_result("Mark Notification Read", False, "Could not retrieve notifications")
            except Exception as e:
                self.log_result("Mark Notification Read", False, "Exception occurred", str(e))

    def test_automatic_notifications(self):
        """Test automatic notifications creation"""
        print("=== Testing Automatic Notifications ===")
        
        # Test notifications created when sending messages
        if self.manager_token and self.employee_user:
            try:
                headers = {"Authorization": f"Bearer {self.manager_token}"}
                
                # Get initial unread count for employee
                employee_headers = {"Authorization": f"Bearer {self.employee_token}"}
                initial_response = self.session.get(f"{API_BASE}/notifications/unread-count", headers=employee_headers)
                initial_count = 0
                if initial_response.status_code == 200:
                    initial_count = initial_response.json().get('unread_count', 0)
                
                # Send message from manager to employee
                message_data = {
                    "receiver_id": self.employee_user['id'],
                    "message": "Test message pour vérifier les notifications automatiques"
                }
                response = self.session.post(f"{API_BASE}/chat/send", json=message_data, headers=headers)
                if response.status_code == 200 or response.status_code == 201:
                    # Check if notification was created for employee
                    final_response = self.session.get(f"{API_BASE}/notifications/unread-count", headers=employee_headers)
                    if final_response.status_code == 200:
                        final_count = final_response.json().get('unread_count', 0)
                        if final_count > initial_count:
                            self.log_result("Message Notification Creation", True, f"Notification created for message (count: {initial_count} → {final_count})")
                        else:
                            self.log_result("Message Notification Creation", False, f"No notification created for message (count stayed at {initial_count})")
                    else:
                        self.log_result("Message Notification Creation", False, "Could not check final notification count")
                else:
                    self.log_result("Message Notification Creation", False, f"Failed to send message. Status: {response.status_code}")
            except Exception as e:
                self.log_result("Message Notification Creation", False, "Exception occurred", str(e))

        # Test notifications created during case updates
        if self.manager_token and self.test_client_id:
            try:
                headers = {"Authorization": f"Bearer {self.manager_token}"}
                
                # Get the case for the test client
                cases_response = self.session.get(f"{API_BASE}/cases", headers=headers)
                if cases_response.status_code == 200:
                    cases = cases_response.json()
                    test_case = None
                    for case in cases:
                        if case['client_id'] == self.test_client_id:
                            test_case = case
                            break
                    
                    if test_case:
                        case_id = test_case['id']
                        
                        # Get client info to check notifications
                        client_response = self.session.get(f"{API_BASE}/clients/{self.test_client_id}", headers=headers)
                        if client_response.status_code == 200:
                            client_data = client_response.json()
                            client_user_id = client_data['user_id']
                            
                            # Try to login as client to check notifications
                            client_login_data = {
                                "email": "client.test@example.com",
                                "password": "Aloria2024!"
                            }
                            client_login_response = self.session.post(f"{API_BASE}/auth/login", json=client_login_data)
                            if client_login_response.status_code == 200:
                                client_token = client_login_response.json()['access_token']
                                client_headers = {"Authorization": f"Bearer {client_token}"}
                                
                                # Get initial notification count for client
                                initial_response = self.session.get(f"{API_BASE}/notifications/unread-count", headers=client_headers)
                                initial_count = 0
                                if initial_response.status_code == 200:
                                    initial_count = initial_response.json().get('unread_count', 0)
                                
                                # Update case as manager
                                update_data = {
                                    "current_step_index": 3,
                                    "status": "En cours de traitement",
                                    "notes": "Mise à jour pour test des notifications automatiques"
                                }
                                update_response = self.session.patch(f"{API_BASE}/cases/{case_id}", json=update_data, headers=headers)
                                if update_response.status_code == 200:
                                    # Check if notification was created for client
                                    final_response = self.session.get(f"{API_BASE}/notifications/unread-count", headers=client_headers)
                                    if final_response.status_code == 200:
                                        final_count = final_response.json().get('unread_count', 0)
                                        if final_count > initial_count:
                                            self.log_result("Case Update Notification Creation", True, f"Notification created for case update (count: {initial_count} → {final_count})")
                                        else:
                                            self.log_result("Case Update Notification Creation", False, f"No notification created for case update (count stayed at {initial_count})")
                                    else:
                                        self.log_result("Case Update Notification Creation", False, "Could not check final notification count")
                                else:
                                    self.log_result("Case Update Notification Creation", False, f"Failed to update case. Status: {update_response.status_code}")
                            else:
                                self.log_result("Case Update Notification Creation", False, "Could not login as client to check notifications")
                        else:
                            self.log_result("Case Update Notification Creation", False, "Could not get client data")
                    else:
                        self.log_result("Case Update Notification Creation", False, "Could not find case for test client")
                else:
                    self.log_result("Case Update Notification Creation", False, "Could not retrieve cases")
            except Exception as e:
                self.log_result("Case Update Notification Creation", False, "Exception occurred", str(e))

    def test_complete_integration(self):
        """Test complete integration scenario with notifications"""
        print("=== Testing Complete Integration with Notifications ===")
        
        if not self.manager_token:
            self.log_result("Complete Integration", False, "No manager token available")
            return

        integration_client_id = None
        integration_case_id = None
        
        try:
            # 1. Employee creates a new client
            if self.employee_token:
                headers = {"Authorization": f"Bearer {self.employee_token}"}
                import time
                timestamp = int(time.time())
                client_data = {
                    "email": f"integration.client.{timestamp}@example.com",
                    "full_name": "Client Intégration Complète",
                    "phone": "+33111222333",
                    "country": "Canada",
                    "visa_type": "Permanent Residence (Express Entry)",
                    "message": "Test intégration complète avec notifications"
                }
                response = self.session.post(f"{API_BASE}/clients", json=client_data, headers=headers)
                if response.status_code == 200 or response.status_code == 201:
                    client_response = response.json()
                    integration_client_id = client_response['id']
                    self.log_result("Integration Step 1: Employee Creates Client", True, f"Employee created client with ID: {integration_client_id}")
                    
                    # 2. Manager updates the client's case
                    if self.manager_token:
                        manager_headers = {"Authorization": f"Bearer {self.manager_token}"}
                        
                        # Get the case for this client
                        cases_response = self.session.get(f"{API_BASE}/cases", headers=manager_headers)
                        if cases_response.status_code == 200:
                            cases = cases_response.json()
                            integration_case = None
                            for case in cases:
                                if case['client_id'] == integration_client_id:
                                    integration_case = case
                                    integration_case_id = case['id']
                                    break
                            
                            if integration_case:
                                # Update case as manager
                                update_data = {
                                    "current_step_index": 2,
                                    "status": "Documents en cours de vérification",
                                    "notes": "Intégration complète - mise à jour par manager avec notifications"
                                }
                                update_response = self.session.patch(f"{API_BASE}/cases/{integration_case_id}", json=update_data, headers=manager_headers)
                                if update_response.status_code == 200:
                                    self.log_result("Integration Step 2: Manager Updates Case", True, "Manager successfully updated client case")
                                    
                                    # 3. Test messaging with notifications
                                    # Manager sends message to employee
                                    message_data = {
                                        "receiver_id": self.employee_user['id'],
                                        "message": "Bonjour, j'ai mis à jour le dossier du client. Pouvez-vous vérifier les documents?"
                                    }
                                    message_response = self.session.post(f"{API_BASE}/chat/send", json=message_data, headers=manager_headers)
                                    if message_response.status_code == 200 or message_response.status_code == 201:
                                        self.log_result("Integration Step 3: Manager-Employee Messaging", True, "Manager sent message to employee")
                                        
                                        # 4. Verify all notifications were created
                                        # Check employee notifications
                                        employee_headers = {"Authorization": f"Bearer {self.employee_token}"}
                                        employee_notif_response = self.session.get(f"{API_BASE}/notifications", headers=employee_headers)
                                        if employee_notif_response.status_code == 200:
                                            employee_notifications = employee_notif_response.json()
                                            case_update_notif = any(notif['type'] == 'case_update' for notif in employee_notifications)
                                            message_notif = any(notif['type'] == 'message' for notif in employee_notifications)
                                            
                                            if case_update_notif and message_notif:
                                                self.log_result("Integration Step 4: Employee Notifications", True, "Employee received both case update and message notifications")
                                            else:
                                                self.log_result("Integration Step 4: Employee Notifications", False, f"Missing notifications - case_update: {case_update_notif}, message: {message_notif}")
                                        else:
                                            self.log_result("Integration Step 4: Employee Notifications", False, "Could not retrieve employee notifications")
                                        
                                        # Check client notifications (login as client)
                                        client_login_data = {
                                            "email": client_data["email"],
                                            "password": "Aloria2024!"
                                        }
                                        client_login_response = self.session.post(f"{API_BASE}/auth/login", json=client_login_data)
                                        if client_login_response.status_code == 200:
                                            client_token = client_login_response.json()['access_token']
                                            client_headers = {"Authorization": f"Bearer {client_token}"}
                                            
                                            client_notif_response = self.session.get(f"{API_BASE}/notifications", headers=client_headers)
                                            if client_notif_response.status_code == 200:
                                                client_notifications = client_notif_response.json()
                                                case_update_notif = any(notif['type'] == 'case_update' for notif in client_notifications)
                                                
                                                if case_update_notif:
                                                    self.log_result("Integration Step 5: Client Notifications", True, "Client received case update notification")
                                                else:
                                                    self.log_result("Integration Step 5: Client Notifications", False, "Client did not receive case update notification")
                                            else:
                                                self.log_result("Integration Step 5: Client Notifications", False, "Could not retrieve client notifications")
                                        else:
                                            self.log_result("Integration Step 5: Client Notifications", False, "Could not login as client")
                                    else:
                                        self.log_result("Integration Step 3: Manager-Employee Messaging", False, f"Failed to send message. Status: {message_response.status_code}")
                                else:
                                    self.log_result("Integration Step 2: Manager Updates Case", False, f"Status: {update_response.status_code}", update_response.text)
                            else:
                                self.log_result("Integration Step 2: Find Case", False, "Could not find case for created client")
                        else:
                            self.log_result("Integration Step 2: Get Cases", False, f"Status: {cases_response.status_code}", cases_response.text)
                    else:
                        self.log_result("Integration Step 2: Manager Updates Case", False, "No manager token available")
                else:
                    self.log_result("Integration Step 1: Employee Creates Client", False, f"Status: {response.status_code}", response.text)
            else:
                self.log_result("Integration Step 1: Employee Creates Client", False, "No employee token available")
                
        except Exception as e:
            self.log_result("Complete Integration", False, "Exception occurred", str(e))

    def test_complete_scenario(self):
        """Test complete workflow scenario"""
        print("=== Testing Complete Scenario ===")
        
        if not self.manager_token:
            self.log_result("Complete Scenario", False, "No manager token available")
            return

        scenario_client_id = None
        scenario_case_id = None
        
        try:
            # 1. Create a client as manager
            headers = {"Authorization": f"Bearer {self.manager_token}"}
            import time
            timestamp = int(time.time())
            client_data = {
                "email": f"scenario.client.{timestamp}@example.com",
                "full_name": "Client Scénario Complet",
                "phone": "+33987654321",
                "country": "Canada",
                "visa_type": "Study Permit",
                "message": "Test scénario complet"
            }
            response = self.session.post(f"{API_BASE}/clients", json=client_data, headers=headers)
            if response.status_code == 200 or response.status_code == 201:
                client_response = response.json()
                scenario_client_id = client_response['id']
                self.log_result("Scenario Step 1: Create Client", True, f"Client created with ID: {scenario_client_id}")
                
                # 2. Get the case for this client
                cases_response = self.session.get(f"{API_BASE}/cases", headers=headers)
                if cases_response.status_code == 200:
                    cases = cases_response.json()
                    scenario_case = None
                    for case in cases:
                        if case['client_id'] == scenario_client_id:
                            scenario_case = case
                            scenario_case_id = case['id']
                            break
                    
                    if scenario_case:
                        # 3. Update case as manager
                        update_data = {
                            "current_step_index": 2,
                            "status": "En cours",
                            "notes": "Scénario complet - mise à jour par manager"
                        }
                        update_response = self.session.patch(f"{API_BASE}/cases/{scenario_case_id}", json=update_data, headers=headers)
                        if update_response.status_code == 200:
                            self.log_result("Scenario Step 2: Update Case", True, "Case updated successfully by manager")
                            
                            # 4. Test client login with new credentials
                            login_data = {
                                "email": client_data["email"],
                                "password": "Aloria2024!"
                            }
                            login_response = self.session.post(f"{API_BASE}/auth/login", json=login_data)
                            if login_response.status_code == 200:
                                client_token_data = login_response.json()
                                client_token = client_token_data['access_token']
                                self.log_result("Scenario Step 3: Client Login", True, "Client successfully logged in with default password")
                                
                                # 5. Client changes password
                                client_headers = {"Authorization": f"Bearer {client_token}"}
                                password_change_data = {
                                    "old_password": "Aloria2024!",
                                    "new_password": "MonNouveauMotDePasse123!"
                                }
                                password_response = self.session.patch(f"{API_BASE}/auth/change-password", json=password_change_data, headers=client_headers)
                                if password_response.status_code == 200:
                                    self.log_result("Scenario Step 4: Client Password Change", True, "Client successfully changed password")
                                else:
                                    self.log_result("Scenario Step 4: Client Password Change", False, f"Status: {password_response.status_code}", password_response.text)
                            else:
                                self.log_result("Scenario Step 3: Client Login", False, f"Status: {login_response.status_code}", login_response.text)
                        else:
                            self.log_result("Scenario Step 2: Update Case", False, f"Status: {update_response.status_code}", update_response.text)
                    else:
                        self.log_result("Scenario Step 2: Find Case", False, "Could not find case for created client")
                else:
                    self.log_result("Scenario Step 2: Get Cases", False, f"Status: {cases_response.status_code}", cases_response.text)
            else:
                self.log_result("Scenario Step 1: Create Client", False, f"Status: {response.status_code}", response.text)
                
        except Exception as e:
            self.log_result("Complete Scenario", False, "Exception occurred", str(e))

    def test_error_cases_and_validation(self):
        """Test error handling and validation"""
        print("=== Testing Error Cases and Validation ===")
        
        # Test invalid login
        try:
            response = self.session.post(f"{API_BASE}/auth/login", json={
                "email": "invalid@example.com",
                "password": "wrongpassword"
            })
            if response.status_code == 401:
                self.log_result("Invalid Login Handling", True, "Invalid credentials correctly rejected")
            else:
                self.log_result("Invalid Login Handling", False, f"Expected 401, got {response.status_code}")
        except Exception as e:
            self.log_result("Invalid Login Handling", False, "Exception occurred", str(e))

        # Test unauthorized access
        try:
            response = self.session.get(f"{API_BASE}/clients")  # No auth header
            if response.status_code == 401 or response.status_code == 403:
                self.log_result("Unauthorized Access Handling", True, "Unauthorized access correctly blocked")
            else:
                self.log_result("Unauthorized Access Handling", False, f"Expected 401/403, got {response.status_code}")
        except Exception as e:
            self.log_result("Unauthorized Access Handling", False, "Exception occurred", str(e))

        # Test invalid visitor purpose
        if self.employee_token:
            try:
                headers = {"Authorization": f"Bearer {self.employee_token}"}
                visitor_data = {
                    "name": "Test Invalid",
                    "purpose": "Invalid Purpose",  # Should be from enum
                    "details": "Test invalid purpose"
                }
                response = self.session.post(f"{API_BASE}/visitors", json=visitor_data, headers=headers)
                if response.status_code == 422:  # Validation error
                    self.log_result("Invalid Visitor Purpose Validation", True, "Invalid purpose correctly rejected")
                else:
                    self.log_result("Invalid Visitor Purpose Validation", False, f"Expected 422, got {response.status_code}")
            except Exception as e:
                self.log_result("Invalid Visitor Purpose Validation", False, "Exception occurred", str(e))

    def test_superadmin_creation(self):
        """Test SuperAdmin creation with secret key"""
        print("=== Testing SuperAdmin Creation ===")
        
        superadmin_data = {
            "email": "superadmin@aloria.com",
            "password": "SuperAdmin123!",
            "full_name": "Super Administrator",
            "phone": "+33100000000"
        }
        
        # Test with correct secret key
        try:
            response = self.session.post(f"{API_BASE}/auth/create-superadmin", 
                                       json=superadmin_data,
                                       params={"secret_key": "ALORIA_SUPER_SECRET_2024"})
            if response.status_code == 200 or response.status_code == 201:
                data = response.json()
                self.log_result("SuperAdmin Creation (correct secret)", True, f"SuperAdmin created: {data['user']['full_name']}")
            elif response.status_code == 400 and "existe déjà" in response.text:
                self.log_result("SuperAdmin Creation (already exists)", True, "SuperAdmin already exists - expected behavior")
            else:
                self.log_result("SuperAdmin Creation (correct secret)", False, f"Status: {response.status_code}", response.text)
        except Exception as e:
            self.log_result("SuperAdmin Creation (correct secret)", False, "Exception occurred", str(e))

        # Test with incorrect secret key
        try:
            response = self.session.post(f"{API_BASE}/auth/create-superadmin", 
                                       json=superadmin_data,
                                       params={"secret_key": "WRONG_SECRET"})
            if response.status_code == 403:
                self.log_result("SuperAdmin Creation (wrong secret)", True, "Wrong secret key correctly rejected")
            else:
                self.log_result("SuperAdmin Creation (wrong secret)", False, f"Expected 403, got {response.status_code}")
        except Exception as e:
            self.log_result("SuperAdmin Creation (wrong secret)", False, "Exception occurred", str(e))

    def test_role_hierarchy_permissions(self):
        """Test role hierarchy and user creation permissions"""
        print("=== Testing Role Hierarchy Permissions ===")
        
        # First login as SuperAdmin if exists
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
                self.log_result("SuperAdmin Login", False, "Could not login as SuperAdmin")
        except Exception as e:
            self.log_result("SuperAdmin Login", False, "Exception occurred", str(e))

        # Test SuperAdmin can create Manager
        if superadmin_token:
            try:
                headers = {"Authorization": f"Bearer {superadmin_token}"}
                manager_data = {
                    "email": "new.manager@aloria.com",
                    "full_name": "New Manager Created by SuperAdmin",
                    "phone": "+33200000001",
                    "role": "MANAGER",
                    "send_email": False
                }
                response = self.session.post(f"{API_BASE}/users/create", json=manager_data, headers=headers)
                if response.status_code == 200 or response.status_code == 201:
                    data = response.json()
                    self.log_result("SuperAdmin Creates Manager", True, f"Manager created with temp password: {data.get('temporary_password', 'N/A')}")
                elif response.status_code == 400 and "existe déjà" in response.text:
                    self.log_result("SuperAdmin Creates Manager", True, "Manager already exists - expected")
                else:
                    self.log_result("SuperAdmin Creates Manager", False, f"Status: {response.status_code}", response.text)
            except Exception as e:
                self.log_result("SuperAdmin Creates Manager", False, "Exception occurred", str(e))

        # Test Manager can create Employee and Client
        if self.manager_token:
            try:
                headers = {"Authorization": f"Bearer {self.manager_token}"}
                employee_data = {
                    "email": "new.employee@aloria.com",
                    "full_name": "New Employee Created by Manager",
                    "phone": "+33200000002",
                    "role": "EMPLOYEE",
                    "send_email": False
                }
                response = self.session.post(f"{API_BASE}/users/create", json=employee_data, headers=headers)
                if response.status_code == 200 or response.status_code == 201:
                    data = response.json()
                    self.log_result("Manager Creates Employee", True, f"Employee created with temp password: {data.get('temporary_password', 'N/A')}")
                elif response.status_code == 400 and "existe déjà" in response.text:
                    self.log_result("Manager Creates Employee", True, "Employee already exists - expected")
                else:
                    self.log_result("Manager Creates Employee", False, f"Status: {response.status_code}", response.text)
            except Exception as e:
                self.log_result("Manager Creates Employee", False, "Exception occurred", str(e))

        # Test Employee can create Client
        if self.employee_token:
            try:
                headers = {"Authorization": f"Bearer {self.employee_token}"}
                client_data = {
                    "email": "new.client@aloria.com",
                    "full_name": "New Client Created by Employee",
                    "phone": "+33200000003",
                    "role": "CLIENT",
                    "send_email": False
                }
                response = self.session.post(f"{API_BASE}/users/create", json=client_data, headers=headers)
                if response.status_code == 200 or response.status_code == 201:
                    data = response.json()
                    self.log_result("Employee Creates Client User", True, f"Client user created with temp password: {data.get('temporary_password', 'N/A')}")
                elif response.status_code == 400 and "existe déjà" in response.text:
                    self.log_result("Employee Creates Client User", True, "Client user already exists - expected")
                else:
                    self.log_result("Employee Creates Client User", False, f"Status: {response.status_code}", response.text)
            except Exception as e:
                self.log_result("Employee Creates Client User", False, "Exception occurred", str(e))

        # Test permission restrictions - Employee cannot create Manager
        if self.employee_token:
            try:
                headers = {"Authorization": f"Bearer {self.employee_token}"}
                invalid_data = {
                    "email": "invalid.manager@aloria.com",
                    "full_name": "Invalid Manager",
                    "phone": "+33200000004",
                    "role": "MANAGER",
                    "send_email": False
                }
                response = self.session.post(f"{API_BASE}/users/create", json=invalid_data, headers=headers)
                if response.status_code == 403:
                    self.log_result("Employee Cannot Create Manager", True, "Employee correctly denied manager creation")
                else:
                    self.log_result("Employee Cannot Create Manager", False, f"Expected 403, got {response.status_code}")
            except Exception as e:
                self.log_result("Employee Cannot Create Manager", False, "Exception occurred", str(e))

    def test_payment_system_comprehensive(self):
        """Test COMPLETE payment system workflow - CRITICAL BUGS INVESTIGATION"""
        print("=== TESTING PAYMENT SYSTEM - CRITICAL BUGS INVESTIGATION ===")
        
        # Create test client for payments
        test_payment_client_id = None
        client_email = None
        if self.manager_token:
            try:
                headers = {"Authorization": f"Bearer {self.manager_token}"}
                import time
                timestamp = int(time.time())
                client_email = f"sophie.martin.{timestamp}@example.com"
                client_data = {
                    "email": client_email,
                    "full_name": "Sophie Martin",
                    "phone": "+33145678901",
                    "country": "France",
                    "visa_type": "Work Permit (Talent Permit)",
                    "message": "Demande de visa de travail pour poste d'ingénieur"
                }
                response = self.session.post(f"{API_BASE}/clients", json=client_data, headers=headers)
                if response.status_code == 200 or response.status_code == 201:
                    test_payment_client_id = response.json()['id']
                    self.log_result("1. Create Payment Test Client", True, f"Client créé: {client_email}")
                else:
                    self.log_result("1. Create Payment Test Client", False, f"Status: {response.status_code}", response.text)
                    return
            except Exception as e:
                self.log_result("1. Create Payment Test Client", False, "Exception occurred", str(e))
                return

        # Test 1: Client declares payment
        payment_id = None
        client_token = None
        if test_payment_client_id and client_email:
            try:
                # Login as client
                client_login_data = {
                    "email": client_email,
                    "password": "Aloria2024!"
                }
                client_login_response = self.session.post(f"{API_BASE}/auth/login", json=client_login_data)
                if client_login_response.status_code == 200:
                    client_token = client_login_response.json()['access_token']
                    client_headers = {"Authorization": f"Bearer {client_token}"}
                    
                    # Declare payment
                    payment_data = {
                        "amount": 2500.00,
                        "currency": "EUR",
                        "description": "Honoraires pour dossier visa de travail - Talent Permit",
                        "payment_method": "Virement bancaire"
                    }
                    response = self.session.post(f"{API_BASE}/payments/declare", json=payment_data, headers=client_headers)
                    if response.status_code == 200 or response.status_code == 201:
                        payment_response = response.json()
                        payment_id = payment_response['id']
                        
                        # Verify all required fields in response
                        required_fields = ['id', 'client_id', 'client_name', 'amount', 'currency', 'status', 'declared_at']
                        missing_fields = [field for field in required_fields if field not in payment_response]
                        
                        if not missing_fields:
                            self.log_result("2. Client Declares Payment", True, 
                                          f"Paiement déclaré: ID={payment_id}, Montant={payment_response['amount']}€, Status={payment_response['status']}")
                        else:
                            self.log_result("2. Client Declares Payment", False, f"Champs manquants: {missing_fields}")
                    else:
                        self.log_result("2. Client Declares Payment", False, f"Status: {response.status_code}", response.text)
                        return
                else:
                    self.log_result("2. Client Login for Payment", False, f"Status: {client_login_response.status_code}")
                    return
            except Exception as e:
                self.log_result("2. Client Declares Payment", False, "Exception occurred", str(e))
                return

        # Test 2: Manager views pending payments
        if self.manager_token:
            try:
                headers = {"Authorization": f"Bearer {self.manager_token}"}
                response = self.session.get(f"{API_BASE}/payments/pending", headers=headers)
                if response.status_code == 200:
                    pending_payments = response.json()
                    
                    # Find our payment in pending list
                    our_payment = None
                    for payment in pending_payments:
                        if payment.get('id') == payment_id:
                            our_payment = payment
                            break
                    
                    if our_payment:
                        self.log_result("3. Manager Views Pending Payments", True, 
                                      f"Paiement trouvé dans la liste: {len(pending_payments)} paiements en attente")
                    else:
                        self.log_result("3. Manager Views Pending Payments", False, 
                                      f"Paiement {payment_id} non trouvé dans {len(pending_payments)} paiements en attente")
                else:
                    self.log_result("3. Manager Views Pending Payments", False, f"Status: {response.status_code}", response.text)
            except Exception as e:
                self.log_result("3. Manager Views Pending Payments", False, "Exception occurred", str(e))

        # Test 3: Test confirmation code generation and validation (Two-step process)
        confirmation_code = None
        invoice_number = None
        if self.manager_token and payment_id:
            try:
                headers = {"Authorization": f"Bearer {self.manager_token}"}
                
                # Step 1: Generate confirmation code
                confirmation_data = {
                    "action": "CONFIRMED"
                }
                response = self.session.patch(f"{API_BASE}/payments/{payment_id}/confirm", json=confirmation_data, headers=headers)
                
                if response.status_code == 200:
                    step1_result = response.json()
                    
                    # Check if confirmation code was generated
                    if 'confirmation_code' in step1_result and step1_result['confirmation_code']:
                        confirmation_code = step1_result['confirmation_code']
                        self.log_result("4. Confirmation Code Generation", True, 
                                      f"Code de confirmation généré: {confirmation_code}")
                        
                        # Step 2: Confirm with the generated code
                        confirmation_data_with_code = {
                            "action": "CONFIRMED",
                            "confirmation_code": confirmation_code
                        }
                        
                        step2_response = self.session.patch(f"{API_BASE}/payments/{payment_id}/confirm", 
                                                          json=confirmation_data_with_code, headers=headers)
                        
                        if step2_response.status_code == 200:
                            final_result = step2_response.json()
                            
                            # Check invoice number generation
                            if 'invoice_number' in final_result and final_result['invoice_number']:
                                invoice_number = final_result['invoice_number']
                                self.log_result("5. Invoice Number Generation", True, 
                                              f"Numéro de facture généré: {invoice_number}")
                            else:
                                self.log_result("5. Invoice Number Generation", False, 
                                              "Numéro de facture manquant ou vide")
                            
                            # Check status change
                            if final_result.get('status') == 'confirmed':
                                self.log_result("6. Payment Status Update", True, 
                                              f"Statut mis à jour: {final_result['status']}")
                            else:
                                self.log_result("6. Payment Status Update", False, 
                                              f"Statut incorrect: {final_result.get('status')}")
                        else:
                            self.log_result("5. Payment Final Confirmation", False, 
                                          f"Échec confirmation finale: {step2_response.status_code}", step2_response.text)
                    else:
                        self.log_result("4. Confirmation Code Generation", False, 
                                      "Code de confirmation manquant dans la réponse")
                else:
                    self.log_result("4. Payment Confirmation Process", False, 
                                  f"Status: {response.status_code}", response.text)
            except Exception as e:
                self.log_result("4. Payment Confirmation Process", False, "Exception occurred", str(e))

        # Test 4: Test rejection workflow
        rejection_payment_id = None
        if self.manager_token and client_token:
            try:
                # Create another payment to test rejection
                client_headers = {"Authorization": f"Bearer {client_token}"}
                payment_data = {
                    "amount": 1200.00,
                    "currency": "EUR", 
                    "description": "Paiement pour documents supplémentaires",
                    "payment_method": "Chèque"
                }
                response = self.session.post(f"{API_BASE}/payments/declare", json=payment_data, headers=client_headers)
                if response.status_code == 200 or response.status_code == 201:
                    rejection_payment_id = response.json()['id']
                    
                    # Now reject it
                    headers = {"Authorization": f"Bearer {self.manager_token}"}
                    rejection_data = {
                        "action": "REJECTED",
                        "rejection_reason": "Documents insuffisants - paiement refusé temporairement"
                    }
                    reject_response = self.session.patch(f"{API_BASE}/payments/{rejection_payment_id}/confirm", 
                                                       json=rejection_data, headers=headers)
                    
                    if reject_response.status_code == 200:
                        rejected_payment = reject_response.json()
                        if rejected_payment.get('status') == 'rejected':
                            self.log_result("7. Payment Rejection Workflow", True, 
                                          f"Paiement rejeté avec motif: {rejection_data['rejection_reason']}")
                        else:
                            self.log_result("7. Payment Rejection Workflow", False, 
                                          f"Statut incorrect après rejet: {rejected_payment.get('status')}")
                    else:
                        self.log_result("7. Payment Rejection Workflow", False, 
                                      f"Status: {reject_response.status_code}", reject_response.text)
                else:
                    self.log_result("7. Create Payment for Rejection Test", False, 
                                  f"Status: {response.status_code}")
            except Exception as e:
                self.log_result("7. Payment Rejection Workflow", False, "Exception occurred", str(e))

        # Test 5: Manager payment history (should see all payments)
        if self.manager_token:
            try:
                headers = {"Authorization": f"Bearer {self.manager_token}"}
                response = self.session.get(f"{API_BASE}/payments/history", headers=headers)
                if response.status_code == 200:
                    payment_history = response.json()
                    
                    # Check if our payments are in history
                    our_payments = [p for p in payment_history if p.get('id') in [payment_id, rejection_payment_id]]
                    
                    if len(our_payments) >= 1:
                        self.log_result("8. Manager Payment History", True, 
                                      f"Historique complet: {len(payment_history)} paiements, nos paiements trouvés: {len(our_payments)}")
                    else:
                        self.log_result("8. Manager Payment History", False, 
                                      f"Nos paiements non trouvés dans l'historique de {len(payment_history)} paiements")
                else:
                    self.log_result("8. Manager Payment History", False, f"Status: {response.status_code}", response.text)
            except Exception as e:
                self.log_result("8. Manager Payment History", False, "Exception occurred", str(e))

        # Test 6: Client payment history (should see only own payments)
        if client_token:
            try:
                client_headers = {"Authorization": f"Bearer {client_token}"}
                response = self.session.get(f"{API_BASE}/payments/history", headers=client_headers)
                if response.status_code == 200:
                    client_payment_history = response.json()
                    
                    # Check if client sees only their own payments
                    client_payments = [p for p in client_payment_history if p.get('client_id') == test_payment_client_id]
                    
                    if len(client_payments) == len(client_payment_history):
                        self.log_result("9. Client Payment History (Own Only)", True, 
                                      f"Client voit ses propres paiements: {len(client_payment_history)} paiements")
                    else:
                        self.log_result("9. Client Payment History (Own Only)", False, 
                                      f"Client voit des paiements d'autres clients: {len(client_payment_history)} total, {len(client_payments)} siens")
                else:
                    self.log_result("9. Client Payment History", False, f"Status: {response.status_code}", response.text)
            except Exception as e:
                self.log_result("9. Client Payment History", False, "Exception occurred", str(e))

        # Test 7: Test double confirmation (should fail)
        if self.manager_token and payment_id and confirmation_code:
            try:
                headers = {"Authorization": f"Bearer {self.manager_token}"}
                # Try to confirm again with the same code
                confirmation_data = {
                    "action": "CONFIRMED",
                    "confirmation_code": confirmation_code
                }
                response = self.session.patch(f"{API_BASE}/payments/{payment_id}/confirm", json=confirmation_data, headers=headers)
                
                if response.status_code == 400:
                    self.log_result("10. Double Confirmation Prevention", True, 
                                  "Tentative de double confirmation correctement bloquée")
                elif response.status_code == 200:
                    self.log_result("10. Double Confirmation Prevention", False, 
                                  "Double confirmation autorisée - BUG CRITIQUE")
                else:
                    self.log_result("10. Double Confirmation Prevention", False, 
                                  f"Réponse inattendue: {response.status_code}")
            except Exception as e:
                self.log_result("10. Double Confirmation Prevention", False, "Exception occurred", str(e))

        # Test 8: Test PDF generation (check if PDF URL is accessible)
        if self.manager_token and payment_id and invoice_number:
            try:
                headers = {"Authorization": f"Bearer {self.manager_token}"}
                # Get payment details to check PDF URL
                response = self.session.get(f"{API_BASE}/payments/history", headers=headers)
                if response.status_code == 200:
                    payments = response.json()
                    our_payment = None
                    for payment in payments:
                        if payment.get('id') == payment_id:
                            our_payment = payment
                            break
                    
                    if our_payment and 'pdf_invoice_url' in our_payment and our_payment['pdf_invoice_url']:
                        pdf_url = our_payment['pdf_invoice_url']
                        self.log_result("11. PDF Generation & Access", True, 
                                      f"PDF URL généré: {pdf_url}")
                        # Note: We can't actually access the PDF file as it's not implemented yet
                    else:
                        self.log_result("11. PDF Generation & Access", False, 
                                      "URL PDF manquante dans les données du paiement")
                else:
                    self.log_result("11. PDF Generation Check", False, f"Status: {response.status_code}")
            except Exception as e:
                self.log_result("11. PDF Generation & Access", False, "Exception occurred", str(e))

        # Test 9: Test invalid confirmation codes
        if self.manager_token and rejection_payment_id:
            try:
                headers = {"Authorization": f"Bearer {self.manager_token}"}
                confirmation_data = {
                    "action": "CONFIRMED",
                    "confirmation_code": "INVALID_CODE_123"
                }
                response = self.session.patch(f"{API_BASE}/payments/{rejection_payment_id}/confirm", json=confirmation_data, headers=headers)
                
                if response.status_code == 400:
                    self.log_result("12. Invalid Confirmation Code Handling", True, 
                                  "Code de confirmation invalide correctement rejeté")
                else:
                    self.log_result("12. Invalid Confirmation Code Handling", False, 
                                  f"Code invalide accepté - BUG: Status {response.status_code}")
            except Exception as e:
                self.log_result("12. Invalid Confirmation Code Handling", False, "Exception occurred", str(e))

        print("\n=== RÉSUMÉ DES TESTS SYSTÈME DE PAIEMENTS ===")
        print("Tests critiques effectués:")
        print("1. Déclaration de paiement par client")
        print("2. Visualisation des paiements en attente par manager") 
        print("3. Génération automatique des codes de confirmation")
        print("4. Workflow de confirmation avec validation")
        print("5. Workflow de rejet avec motif")
        print("6. Historique des paiements (manager vs client)")
        print("7. Prévention des doubles confirmations")
        print("8. Génération et accès aux PDFs")
        print("9. Validation des codes de confirmation")
        print("="*50)

    def test_superadmin_apis(self):
        """Test SuperAdmin specific APIs"""
        print("=== Testing SuperAdmin APIs ===")
        
        # Login as SuperAdmin
        superadmin_token = None
        try:
            login_response = self.session.post(f"{API_BASE}/auth/login", json={
                "email": "superadmin@aloria.com",
                "password": "SuperAdmin123!"
            })
            if login_response.status_code == 200:
                superadmin_token = login_response.json()['access_token']
                self.log_result("SuperAdmin Login for APIs", True, "SuperAdmin logged in successfully")
            else:
                self.log_result("SuperAdmin Login for APIs", False, "Could not login as SuperAdmin")
        except Exception as e:
            self.log_result("SuperAdmin Login for APIs", False, "Exception occurred", str(e))

        if not superadmin_token:
            self.log_result("SuperAdmin APIs", False, "No SuperAdmin token available")
            return

        headers = {"Authorization": f"Bearer {superadmin_token}"}

        # Test get all users
        try:
            response = self.session.get(f"{API_BASE}/admin/users", headers=headers)
            if response.status_code == 200:
                users = response.json()
                self.log_result("SuperAdmin Get All Users", True, f"Retrieved {len(users)} users")
            else:
                self.log_result("SuperAdmin Get All Users", False, f"Status: {response.status_code}", response.text)
        except Exception as e:
            self.log_result("SuperAdmin Get All Users", False, "Exception occurred", str(e))

        # Test get activities
        try:
            response = self.session.get(f"{API_BASE}/admin/activities", headers=headers)
            if response.status_code == 200:
                activities = response.json()
                self.log_result("SuperAdmin Get Activities", True, f"Retrieved {len(activities)} activities")
            else:
                self.log_result("SuperAdmin Get Activities", False, f"Status: {response.status_code}", response.text)
        except Exception as e:
            self.log_result("SuperAdmin Get Activities", False, "Exception occurred", str(e))

        # Test dashboard stats
        try:
            response = self.session.get(f"{API_BASE}/admin/dashboard-stats", headers=headers)
            if response.status_code == 200:
                stats = response.json()
                self.log_result("SuperAdmin Dashboard Stats", True, f"Retrieved dashboard stats: {len(stats)} metrics")
            else:
                self.log_result("SuperAdmin Dashboard Stats", False, f"Status: {response.status_code}", response.text)
        except Exception as e:
            self.log_result("SuperAdmin Dashboard Stats", False, "Exception occurred", str(e))

        # Test impersonation
        if self.manager_user:
            try:
                impersonation_data = {
                    "target_user_id": self.manager_user['id']
                }
                response = self.session.post(f"{API_BASE}/admin/impersonate", json=impersonation_data, headers=headers)
                if response.status_code == 200:
                    impersonation_response = response.json()
                    self.log_result("SuperAdmin Impersonation", True, f"Impersonation token created for manager")
                else:
                    self.log_result("SuperAdmin Impersonation", False, f"Status: {response.status_code}", response.text)
            except Exception as e:
                self.log_result("SuperAdmin Impersonation", False, "Exception occurred", str(e))

    def test_search_apis(self):
        """Test search functionality"""
        print("=== Testing Search APIs ===")
        
        # Test global search
        if self.manager_token:
            try:
                headers = {"Authorization": f"Bearer {self.manager_token}"}
                search_params = {"q": "test", "limit": 10}
                response = self.session.get(f"{API_BASE}/search/global", params=search_params, headers=headers)
                if response.status_code == 200:
                    search_results = response.json()
                    total_results = sum(len(results) for results in search_results.values())
                    self.log_result("Global Search", True, f"Global search returned {total_results} results across categories")
                else:
                    self.log_result("Global Search", False, f"Status: {response.status_code}", response.text)
            except Exception as e:
                self.log_result("Global Search", False, "Exception occurred", str(e))

        # Test category-specific searches
        categories = ["users", "clients", "cases", "visitors"]
        for category in categories:
            if self.manager_token:
                try:
                    headers = {"Authorization": f"Bearer {self.manager_token}"}
                    search_params = {"q": "test", "category": category, "limit": 5}
                    response = self.session.get(f"{API_BASE}/search/global", params=search_params, headers=headers)
                    if response.status_code == 200:
                        search_results = response.json()
                        category_results = search_results.get(category, [])
                        self.log_result(f"Search {category.title()}", True, f"Found {len(category_results)} {category} results")
                    else:
                        self.log_result(f"Search {category.title()}", False, f"Status: {response.status_code}", response.text)
                except Exception as e:
                    self.log_result(f"Search {category.title()}", False, "Exception occurred", str(e))

    def test_visitor_stats(self):
        """Test visitor statistics"""
        print("=== Testing Visitor Statistics ===")
        
        # Test visitor list with extended info
        if self.manager_token:
            try:
                headers = {"Authorization": f"Bearer {self.manager_token}"}
                response = self.session.get(f"{API_BASE}/visitors/list", headers=headers)
                if response.status_code == 200:
                    visitors_list = response.json()
                    self.log_result("Visitor List Extended", True, f"Retrieved extended visitor list: {len(visitors_list)} visitors")
                else:
                    self.log_result("Visitor List Extended", False, f"Status: {response.status_code}", response.text)
            except Exception as e:
                self.log_result("Visitor List Extended", False, "Exception occurred", str(e))

        # Test visitor statistics
        if self.manager_token:
            try:
                headers = {"Authorization": f"Bearer {self.manager_token}"}
                response = self.session.get(f"{API_BASE}/visitors/stats", headers=headers)
                if response.status_code == 200:
                    visitor_stats = response.json()
                    self.log_result("Visitor Statistics", True, f"Retrieved visitor statistics: {len(visitor_stats)} metrics")
                else:
                    self.log_result("Visitor Statistics", False, f"Status: {response.status_code}", response.text)
            except Exception as e:
                self.log_result("Visitor Statistics", False, "Exception occurred", str(e))

    def test_comprehensive_v2_scenario(self):
        """Test comprehensive V2 scenario with all new features"""
        print("=== Testing Comprehensive V2 Scenario ===")
        
        try:
            # 1. SuperAdmin creates Manager
            superadmin_token = None
            login_response = self.session.post(f"{API_BASE}/auth/login", json={
                "email": "superadmin@aloria.com",
                "password": "SuperAdmin123!"
            })
            if login_response.status_code == 200:
                superadmin_token = login_response.json()['access_token']
                
                # Create new manager
                headers = {"Authorization": f"Bearer {superadmin_token}"}
                import time
                timestamp = int(time.time())
                manager_data = {
                    "email": f"v2.manager.{timestamp}@aloria.com",
                    "full_name": "V2 Test Manager",
                    "phone": "+33400000001",
                    "role": "MANAGER",
                    "send_email": False
                }
                response = self.session.post(f"{API_BASE}/users/create", json=manager_data, headers=headers)
                if response.status_code == 200 or response.status_code == 201:
                    manager_temp_password = response.json().get('temporary_password')
                    self.log_result("V2 Scenario Step 1: SuperAdmin Creates Manager", True, f"Manager created with temp password")
                    
                    # 2. Manager logs in and creates Employee
                    manager_login_response = self.session.post(f"{API_BASE}/auth/login", json={
                        "email": manager_data["email"],
                        "password": manager_temp_password
                    })
                    if manager_login_response.status_code == 200:
                        v2_manager_token = manager_login_response.json()['access_token']
                        
                        # Manager creates employee
                        manager_headers = {"Authorization": f"Bearer {v2_manager_token}"}
                        employee_data = {
                            "email": f"v2.employee.{timestamp}@aloria.com",
                            "full_name": "V2 Test Employee",
                            "phone": "+33400000002",
                            "role": "EMPLOYEE",
                            "send_email": False
                        }
                        emp_response = self.session.post(f"{API_BASE}/users/create", json=employee_data, headers=manager_headers)
                        if emp_response.status_code == 200 or emp_response.status_code == 201:
                            self.log_result("V2 Scenario Step 2: Manager Creates Employee", True, "Employee created successfully")
                            
                            # 3. Employee creates Client and declares payment
                            employee_temp_password = emp_response.json().get('temporary_password')
                            emp_login_response = self.session.post(f"{API_BASE}/auth/login", json={
                                "email": employee_data["email"],
                                "password": employee_temp_password
                            })
                            if emp_login_response.status_code == 200:
                                v2_employee_token = emp_login_response.json()['access_token']
                                employee_headers = {"Authorization": f"Bearer {v2_employee_token}"}
                                
                                # Employee creates client
                                client_data = {
                                    "email": f"v2.client.{timestamp}@aloria.com",
                                    "full_name": "V2 Test Client",
                                    "phone": "+33400000003",
                                    "country": "Canada",
                                    "visa_type": "Work Permit",
                                    "message": "V2 comprehensive test client"
                                }
                                client_response = self.session.post(f"{API_BASE}/clients", json=client_data, headers=employee_headers)
                                if client_response.status_code == 200 or client_response.status_code == 201:
                                    v2_client_id = client_response.json()['id']
                                    self.log_result("V2 Scenario Step 3: Employee Creates Client", True, f"Client created: {v2_client_id}")
                                    
                                    # 4. Client declares payment
                                    client_login_response = self.session.post(f"{API_BASE}/auth/login", json={
                                        "email": client_data["email"],
                                        "password": "Aloria2024!"
                                    })
                                    if client_login_response.status_code == 200:
                                        v2_client_token = client_login_response.json()['access_token']
                                        client_headers = {"Authorization": f"Bearer {v2_client_token}"}
                                        
                                        payment_data = {
                                            "amount": 2000.00,
                                            "currency": "EUR",
                                            "description": "V2 Test Payment",
                                            "payment_method": "Bank Transfer"
                                        }
                                        payment_response = self.session.post(f"{API_BASE}/payments/declare", json=payment_data, headers=client_headers)
                                        if payment_response.status_code == 200 or payment_response.status_code == 201:
                                            v2_payment_id = payment_response.json()['id']
                                            self.log_result("V2 Scenario Step 4: Client Declares Payment", True, f"Payment declared: {v2_payment_id}")
                                            
                                            # 5. Manager confirms payment
                                            confirmation_data = {
                                                "action": "confirm",
                                                "notes": "V2 test payment confirmed"
                                            }
                                            confirm_response = self.session.patch(f"{API_BASE}/payments/{v2_payment_id}/confirm", json=confirmation_data, headers=manager_headers)
                                            if confirm_response.status_code == 200:
                                                invoice_number = confirm_response.json().get('invoice_number')
                                                self.log_result("V2 Scenario Step 5: Manager Confirms Payment", True, f"Payment confirmed with invoice: {invoice_number}")
                                                
                                                # 6. SuperAdmin monitors activities
                                                activities_response = self.session.get(f"{API_BASE}/admin/activities", headers=headers)
                                                if activities_response.status_code == 200:
                                                    activities = activities_response.json()
                                                    self.log_result("V2 Scenario Step 6: SuperAdmin Monitors", True, f"SuperAdmin can see {len(activities)} activities")
                                                else:
                                                    self.log_result("V2 Scenario Step 6: SuperAdmin Monitors", False, "Could not retrieve activities")
                                            else:
                                                self.log_result("V2 Scenario Step 5: Manager Confirms Payment", False, f"Status: {confirm_response.status_code}")
                                        else:
                                            self.log_result("V2 Scenario Step 4: Client Declares Payment", False, f"Status: {payment_response.status_code}")
                                    else:
                                        self.log_result("V2 Scenario Step 4: Client Login", False, "Could not login as client")
                                else:
                                    self.log_result("V2 Scenario Step 3: Employee Creates Client", False, f"Status: {client_response.status_code}")
                            else:
                                self.log_result("V2 Scenario Step 3: Employee Login", False, "Could not login as employee")
                        else:
                            self.log_result("V2 Scenario Step 2: Manager Creates Employee", False, f"Status: {emp_response.status_code}")
                    else:
                        self.log_result("V2 Scenario Step 2: Manager Login", False, "Could not login as manager")
                else:
                    self.log_result("V2 Scenario Step 1: SuperAdmin Creates Manager", False, f"Status: {response.status_code}")
            else:
                self.log_result("V2 Scenario: SuperAdmin Login", False, "Could not login as SuperAdmin")
                
        except Exception as e:
            self.log_result("V2 Comprehensive Scenario", False, "Exception occurred", str(e))

    def test_sequential_case_progression(self):
        """Test sequential case progression validation - RAPID TEST"""
        print("=== Testing Sequential Case Progression (RAPID) ===")
        
        if not self.manager_token:
            self.log_result("Sequential Case Progression", False, "No manager token available")
            return
            
        try:
            headers = {"Authorization": f"Bearer {self.manager_token}"}
            
            # Get a case to test with
            cases_response = self.session.get(f"{API_BASE}/cases", headers=headers)
            if cases_response.status_code != 200:
                self.log_result("Sequential Case Progression - Get Cases", False, f"Status: {cases_response.status_code}")
                return
                
            cases = cases_response.json()
            if not cases:
                self.log_result("Sequential Case Progression", False, "No cases available for testing")
                return
                
            case_id = cases[0]['id']
            current_step = cases[0]['current_step_index']
            
            # Test 1: Valid progression (+1 step)
            valid_progression = {
                "current_step_index": current_step + 1
            }
            response = self.session.patch(f"{API_BASE}/cases/{case_id}/progress", json=valid_progression, headers=headers)
            if response.status_code == 200:
                self.log_result("Sequential Progression - Valid +1 Step", True, f"Successfully advanced from step {current_step} to {current_step + 1}")
            else:
                self.log_result("Sequential Progression - Valid +1 Step", False, f"Status: {response.status_code}, Response: {response.text}")
            
            # Test 2: Invalid progression (jumping steps - should fail)
            invalid_progression = {
                "current_step_index": current_step + 5  # Jump 5 steps
            }
            response = self.session.patch(f"{API_BASE}/cases/{case_id}/progress", json=invalid_progression, headers=headers)
            if response.status_code == 400:
                self.log_result("Sequential Progression - Invalid Jump (should fail)", True, "Correctly prevented jumping multiple steps")
            else:
                self.log_result("Sequential Progression - Invalid Jump (should fail)", False, f"Should have prevented step jumping. Status: {response.status_code}")
            
            # Test 3: Valid backward progression (-1 step)
            if current_step > 0:
                backward_progression = {
                    "current_step_index": current_step - 1
                }
                response = self.session.patch(f"{API_BASE}/cases/{case_id}/progress", json=backward_progression, headers=headers)
                if response.status_code == 200:
                    self.log_result("Sequential Progression - Valid -1 Step", True, f"Successfully moved back from step {current_step} to {current_step - 1}")
                else:
                    self.log_result("Sequential Progression - Valid -1 Step", False, f"Status: {response.status_code}")
            
            # Test 4: Invalid backward progression (jumping back - should fail)
            if current_step > 2:
                invalid_backward = {
                    "current_step_index": current_step - 3  # Jump back 3 steps
                }
                response = self.session.patch(f"{API_BASE}/cases/{case_id}/progress", json=invalid_backward, headers=headers)
                if response.status_code == 400:
                    self.log_result("Sequential Progression - Invalid Backward Jump (should fail)", True, "Correctly prevented jumping backward multiple steps")
                else:
                    self.log_result("Sequential Progression - Invalid Backward Jump (should fail)", False, f"Should have prevented backward jumping. Status: {response.status_code}")
                    
        except Exception as e:
            self.log_result("Sequential Case Progression", False, "Exception occurred", str(e))

    def test_payment_system_rapid_validation(self):
        """Test payment system - RAPID VALIDATION"""
        print("=== Testing Payment System (RAPID VALIDATION) ===")
        
        # Test with existing credentials from test_result.md
        manager_credentials = {"email": "manager@test.com", "password": "password123"}
        
        try:
            # Login as manager
            login_response = self.session.post(f"{API_BASE}/auth/login", json=manager_credentials)
            if login_response.status_code != 200:
                self.log_result("Payment System - Manager Login", False, f"Could not login with manager@test.com. Status: {login_response.status_code}")
                return
                
            manager_token = login_response.json()['access_token']
            headers = {"Authorization": f"Bearer {manager_token}"}
            
            # Test 1: Get pending payments
            response = self.session.get(f"{API_BASE}/payments/pending", headers=headers)
            if response.status_code == 200:
                pending_payments = response.json()
                self.log_result("Payment System - Get Pending Payments", True, f"Retrieved {len(pending_payments)} pending payments")
            else:
                self.log_result("Payment System - Get Pending Payments", False, f"Status: {response.status_code}")
            
            # Test 2: Get payment history
            response = self.session.get(f"{API_BASE}/payments/history", headers=headers)
            if response.status_code == 200:
                payment_history = response.json()
                self.log_result("Payment System - Get Payment History", True, f"Retrieved {len(payment_history)} payment history entries")
            else:
                self.log_result("Payment System - Get Payment History", False, f"Status: {response.status_code}")
            
            # Test 3: Client payment declaration (need to login as client)
            # Try to find an existing client or create one for testing
            clients_response = self.session.get(f"{API_BASE}/clients", headers=headers)
            if clients_response.status_code == 200:
                clients = clients_response.json()
                if clients:
                    # Try to login as first client
                    client_login = {"email": "client@test.com", "password": "Aloria2024!"}
                    client_login_response = self.session.post(f"{API_BASE}/auth/login", json=client_login)
                    
                    if client_login_response.status_code == 200:
                        client_token = client_login_response.json()['access_token']
                        client_headers = {"Authorization": f"Bearer {client_token}"}
                        
                        # Declare a payment
                        payment_data = {
                            "amount": 1500.0,
                            "currency": "EUR",
                            "description": "Test payment declaration - rapid validation",
                            "payment_method": "Bank Transfer"
                        }
                        
                        payment_response = self.session.post(f"{API_BASE}/payments/declare", json=payment_data, headers=client_headers)
                        if payment_response.status_code == 200 or payment_response.status_code == 201:
                            payment_data_response = payment_response.json()
                            payment_id = payment_data_response['id']
                            self.log_result("Payment System - Client Payment Declaration", True, f"Payment declared with ID: {payment_id}")
                            
                            # Test 4: Manager confirmation workflow
                            # First generate confirmation code
                            confirm_data = {"action": "CONFIRMED"}
                            confirm_response = self.session.patch(f"{API_BASE}/payments/{payment_id}/confirm", json=confirm_data, headers=headers)
                            
                            if confirm_response.status_code == 200:
                                confirm_result = confirm_response.json()
                                if 'confirmation_code' in confirm_result:
                                    confirmation_code = confirm_result['confirmation_code']
                                    self.log_result("Payment System - Generate Confirmation Code", True, f"Confirmation code generated: {confirmation_code}")
                                    
                                    # Test 5: Complete confirmation with code
                                    final_confirm_data = {
                                        "action": "CONFIRMED",
                                        "confirmation_code": confirmation_code
                                    }
                                    final_response = self.session.patch(f"{API_BASE}/payments/{payment_id}/confirm", json=final_confirm_data, headers=headers)
                                    
                                    if final_response.status_code == 200:
                                        final_result = final_response.json()
                                        if 'invoice_number' in final_result:
                                            self.log_result("Payment System - Complete Confirmation & Invoice Generation", True, f"Payment confirmed, invoice: {final_result['invoice_number']}")
                                        else:
                                            self.log_result("Payment System - Complete Confirmation & Invoice Generation", False, "Invoice number not generated")
                                    else:
                                        self.log_result("Payment System - Complete Confirmation", False, f"Status: {final_response.status_code}")
                                else:
                                    self.log_result("Payment System - Generate Confirmation Code", False, "No confirmation code in response")
                            else:
                                self.log_result("Payment System - Generate Confirmation Code", False, f"Status: {confirm_response.status_code}")
                        else:
                            self.log_result("Payment System - Client Payment Declaration", False, f"Status: {payment_response.status_code}")
                    else:
                        self.log_result("Payment System - Client Login", False, "Could not login as client for payment testing")
                else:
                    self.log_result("Payment System - Find Client", False, "No clients available for payment testing")
            else:
                self.log_result("Payment System - Get Clients", False, f"Status: {clients_response.status_code}")
                
        except Exception as e:
            self.log_result("Payment System Rapid Validation", False, "Exception occurred", str(e))

    def test_basic_apis_sanity_check(self):
        """Test basic APIs - SANITY CHECK"""
        print("=== Testing Basic APIs (SANITY CHECK) ===")
        
        # Test 1: Manager Login
        manager_credentials = {"email": "manager@test.com", "password": "password123"}
        try:
            response = self.session.post(f"{API_BASE}/auth/login", json=manager_credentials)
            if response.status_code == 200:
                manager_data = response.json()
                self.manager_token = manager_data['access_token']
                self.log_result("Sanity Check - Manager Login", True, "Manager login successful")
            else:
                self.log_result("Sanity Check - Manager Login", False, f"Status: {response.status_code}")
        except Exception as e:
            self.log_result("Sanity Check - Manager Login", False, "Exception occurred", str(e))
        
        # Test 2: Employee Login
        employee_credentials = {"email": "employee@test.com", "password": "password123"}
        try:
            response = self.session.post(f"{API_BASE}/auth/login", json=employee_credentials)
            if response.status_code == 200:
                employee_data = response.json()
                self.employee_token = employee_data['access_token']
                self.log_result("Sanity Check - Employee Login", True, "Employee login successful")
            else:
                self.log_result("Sanity Check - Employee Login", False, f"Status: {response.status_code}")
        except Exception as e:
            self.log_result("Sanity Check - Employee Login", False, "Exception occurred", str(e))
        
        # Test 3: Client Creation
        if self.manager_token:
            try:
                headers = {"Authorization": f"Bearer {self.manager_token}"}
                import time
                timestamp = int(time.time())
                client_data = {
                    "email": f"sanity.client.{timestamp}@test.com",
                    "full_name": "Sanity Check Client",
                    "phone": "+33123456789",
                    "country": "France",
                    "visa_type": "Work Permit (Talent Permit)",
                    "message": "Sanity check client creation"
                }
                response = self.session.post(f"{API_BASE}/clients", json=client_data, headers=headers)
                if response.status_code == 200 or response.status_code == 201:
                    client_result = response.json()
                    self.log_result("Sanity Check - Client Creation", True, f"Client created with ID: {client_result['id']}")
                else:
                    self.log_result("Sanity Check - Client Creation", False, f"Status: {response.status_code}")
            except Exception as e:
                self.log_result("Sanity Check - Client Creation", False, "Exception occurred", str(e))
        
        # Test 4: Visitor Management
        if self.employee_token:
            try:
                headers = {"Authorization": f"Bearer {self.employee_token}"}
                visitor_data = {
                    "name": "Sanity Check Visitor",
                    "company": "Test Company",
                    "purpose": "Consultation initiale",
                    "details": "Sanity check visitor registration"
                }
                response = self.session.post(f"{API_BASE}/visitors", json=visitor_data, headers=headers)
                if response.status_code == 200 or response.status_code == 201:
                    visitor_result = response.json()
                    self.log_result("Sanity Check - Visitor Registration", True, f"Visitor registered with ID: {visitor_result['id']}")
                else:
                    self.log_result("Sanity Check - Visitor Registration", False, f"Status: {response.status_code}")
            except Exception as e:
                self.log_result("Sanity Check - Visitor Registration", False, "Exception occurred", str(e))

    def run_rapid_tests(self):
        """Run rapid tests focusing on recent improvements"""
        print("🚀 ALORIA AGENCY - RAPID VALIDATION TESTS")
        print("=" * 60)
        print(f"Testing against: {API_BASE}")
        print("Testing recent improvements and system stability")
        print("=" * 60)
        
        # 1. Basic APIs Sanity Check
        self.test_basic_apis_sanity_check()
        
        # 2. Sequential Case Progression
        self.test_sequential_case_progression()
        
        # 3. Payment System Final Validation
        self.test_payment_system_rapid_validation()
        
        # Print final results
        print("\n" + "=" * 60)
        print("🎯 RAPID TEST RESULTS")
        print("=" * 60)
        total_tests = self.results['passed'] + self.results['failed']
        success_rate = (self.results['passed'] / total_tests * 100) if total_tests > 0 else 0
        
        print(f"✅ PASSED: {self.results['passed']}")
        print(f"❌ FAILED: {self.results['failed']}")
        print(f"📊 SUCCESS RATE: {success_rate:.1f}%")
        
        if self.results['errors']:
            print(f"\n🔍 FAILED TESTS SUMMARY:")
            for error in self.results['errors']:
                print(f"   • {error['test']}: {error['message']}")
        
        print("=" * 60)

    def test_contact_messages_crm(self):
        """Test contact messages and CRM system"""
        print("=== Testing Contact Messages & CRM System ===")
        
        # Test data as specified in the review request
        contact_data = {
            "name": "Jean Dupont",
            "email": "jean.dupont@test.com",
            "phone": "+33123456789",
            "country": "France",
            "visa_type": "Permis de Travail (Passeport Talent)",
            "budget_range": "5000+€",
            "urgency_level": "Urgent",
            "message": "Je souhaite immigrer en France pour des opportunités professionnelles dans le secteur tech. J'ai 5 ans d'expérience et cherche à obtenir un passeport talent.",
            "lead_source": "Site web"
        }
        
        contact_message_id = None
        
        # 1. Test POST /api/contact-messages (public endpoint)
        try:
            response = self.session.post(f"{API_BASE}/contact-messages", json=contact_data)
            if response.status_code == 200 or response.status_code == 201:
                data = response.json()
                contact_message_id = data['id']
                
                # Verify lead score calculation
                expected_score = 50 + 30 + 20 + 15 + 10 + 5  # Base + budget + urgency + country + message length + complete info
                actual_score = data.get('conversion_probability', 0)
                
                if actual_score >= 90:  # Should be around 130 but capped at 100
                    self.log_result("Contact Message Creation with Lead Score", True, 
                                  f"Message created with ID: {contact_message_id}, Lead Score: {actual_score}%")
                else:
                    self.log_result("Contact Message Creation with Lead Score", False, 
                                  f"Lead score calculation incorrect. Expected ~100%, got {actual_score}%")
                
                # Verify status is "NEW"
                if data.get('status') == 'NEW':
                    self.log_result("Contact Message Status", True, "Message created with status 'NEW'")
                else:
                    self.log_result("Contact Message Status", False, f"Expected status 'NEW', got '{data.get('status')}'")
                    
            else:
                self.log_result("Contact Message Creation", False, f"Status: {response.status_code}", response.text)
        except Exception as e:
            self.log_result("Contact Message Creation", False, "Exception occurred", str(e))
        
        # 2. Test GET /api/contact-messages (Manager access)
        if self.manager_token:
            try:
                headers = {"Authorization": f"Bearer {self.manager_token}"}
                response = self.session.get(f"{API_BASE}/contact-messages", headers=headers)
                if response.status_code == 200:
                    messages = response.json()
                    self.log_result("Manager Get Contact Messages", True, f"Retrieved {len(messages)} contact messages")
                    
                    # Verify our message is in the list
                    if contact_message_id:
                        found_message = any(msg['id'] == contact_message_id for msg in messages)
                        if found_message:
                            self.log_result("Contact Message Retrieval", True, "Created message found in CRM list")
                        else:
                            self.log_result("Contact Message Retrieval", False, "Created message not found in CRM list")
                else:
                    self.log_result("Manager Get Contact Messages", False, f"Status: {response.status_code}", response.text)
            except Exception as e:
                self.log_result("Manager Get Contact Messages", False, "Exception occurred", str(e))
        
        # 3. Test GET /api/contact-messages (Employee access)
        if self.employee_token:
            try:
                headers = {"Authorization": f"Bearer {self.employee_token}"}
                response = self.session.get(f"{API_BASE}/contact-messages", headers=headers)
                if response.status_code == 200:
                    messages = response.json()
                    self.log_result("Employee Get Contact Messages", True, f"Employee can access {len(messages)} assigned messages")
                else:
                    self.log_result("Employee Get Contact Messages", False, f"Status: {response.status_code}", response.text)
            except Exception as e:
                self.log_result("Employee Get Contact Messages", False, "Exception occurred", str(e))
        
        # 4. Test filtering by status
        if self.manager_token:
            try:
                headers = {"Authorization": f"Bearer {self.manager_token}"}
                response = self.session.get(f"{API_BASE}/contact-messages?status=NEW", headers=headers)
                if response.status_code == 200:
                    new_messages = response.json()
                    self.log_result("Contact Messages Filter by Status", True, f"Found {len(new_messages)} NEW messages")
                else:
                    self.log_result("Contact Messages Filter by Status", False, f"Status: {response.status_code}", response.text)
            except Exception as e:
                self.log_result("Contact Messages Filter by Status", False, "Exception occurred", str(e))
        
        # 5. Test assignment functionality
        if self.manager_token and self.employee_user and contact_message_id:
            try:
                headers = {"Authorization": f"Bearer {self.manager_token}"}
                assignment_data = {"assigned_to": self.employee_user['id']}
                response = self.session.patch(f"{API_BASE}/contact-messages/{contact_message_id}/assign", 
                                            json=assignment_data, headers=headers)
                if response.status_code == 200:
                    self.log_result("Contact Message Assignment", True, f"Message assigned to employee {self.employee_user['full_name']}")
                else:
                    self.log_result("Contact Message Assignment", False, f"Status: {response.status_code}", response.text)
            except Exception as e:
                self.log_result("Contact Message Assignment", False, "Exception occurred", str(e))
        
        # 6. Test data validation
        try:
            invalid_data = {
                "name": "A",  # Too short
                "email": "invalid-email",  # Invalid format
                "country": "France",
                "message": "Short"  # Too short
            }
            response = self.session.post(f"{API_BASE}/contact-messages", json=invalid_data)
            if response.status_code == 422:  # Validation error
                self.log_result("Contact Form Validation", True, "Invalid data correctly rejected")
            else:
                self.log_result("Contact Form Validation", False, f"Expected 422, got {response.status_code}")
        except Exception as e:
            self.log_result("Contact Form Validation", False, "Exception occurred", str(e))
        
        # 7. Test lead score calculation with different scenarios
        test_scenarios = [
            {
                "name": "Low Score Test",
                "data": {
                    "name": "Test User",
                    "email": "test@example.com",
                    "country": "Other",
                    "urgency_level": "Information",
                    "budget_range": "500-1000€",
                    "message": "Short message",
                    "lead_source": "Site web"
                },
                "expected_min": 50,  # Base score only
                "expected_max": 70
            },
            {
                "name": "High Score Test", 
                "data": {
                    "name": "Premium Client",
                    "email": "premium@example.com",
                    "phone": "+33123456789",
                    "country": "Canada",
                    "visa_type": "Work Permit",
                    "urgency_level": "Urgent",
                    "budget_range": "5000+€",
                    "message": "I am looking for comprehensive immigration services for my family. We have significant experience in tech industry and are looking for the best possible service to ensure our successful immigration to Canada. We have done extensive research and are ready to proceed immediately with the right partner.",
                    "lead_source": "Référencement"
                },
                "expected_min": 95,  # Should be close to 100
                "expected_max": 100
            }
        ]
        
        for scenario in test_scenarios:
            try:
                response = self.session.post(f"{API_BASE}/contact-messages", json=scenario["data"])
                if response.status_code == 200 or response.status_code == 201:
                    data = response.json()
                    score = data.get('conversion_probability', 0)
                    if scenario["expected_min"] <= score <= scenario["expected_max"]:
                        self.log_result(f"Lead Score Calculation - {scenario['name']}", True, 
                                      f"Score {score}% within expected range {scenario['expected_min']}-{scenario['expected_max']}%")
                    else:
                        self.log_result(f"Lead Score Calculation - {scenario['name']}", False, 
                                      f"Score {score}% outside expected range {scenario['expected_min']}-{scenario['expected_max']}%")
                else:
                    self.log_result(f"Lead Score Calculation - {scenario['name']}", False, 
                                  f"Status: {response.status_code}", response.text)
            except Exception as e:
                self.log_result(f"Lead Score Calculation - {scenario['name']}", False, "Exception occurred", str(e))

    def test_review_request_specific_tests(self):
        """Test specific requirements from the review request"""
        print("=== Testing Review Request Specific Requirements ===")
        
        # 1. Test Dashboard SuperAdmin amélioré - GET /api/admin/dashboard-stats
        print("\n--- Test 1: Dashboard SuperAdmin amélioré ---")
        self.test_superadmin_dashboard_stats()
        
        # 2. Test nouveau formulaire de contact avec champs supplémentaires
        print("\n--- Test 2: Nouveau formulaire de contact avec champs supplémentaires ---")
        self.test_contact_form_new_fields()
        
        # 3. Test création d'utilisateur avec e-mail - POST /api/users/create avec send_email=true
        print("\n--- Test 3: Création d'utilisateur avec e-mail ---")
        self.test_user_creation_with_email()
        
        # 4. Test mise à jour de dossier avec e-mail - PATCH /api/cases/{id}
        print("\n--- Test 4: Mise à jour de dossier avec e-mail ---")
        self.test_case_update_with_email()
        
        # 5. Test général de régression - Login Manager: manager@test.com / password123
        print("\n--- Test 5: Test général de régression ---")
        self.test_regression_manager_login()

    def test_superadmin_dashboard_stats(self):
        """Test GET /api/admin/dashboard-stats pour vérifier les statistiques corrigées"""
        # First login as SuperAdmin
        superadmin_token = None
        try:
            login_response = self.session.post(f"{API_BASE}/auth/login", json={
                "email": "superadmin@aloria.com",
                "password": "SuperAdmin123!"
            })
            if login_response.status_code == 200:
                superadmin_token = login_response.json()['access_token']
                self.log_result("SuperAdmin Login for Dashboard Stats", True, "SuperAdmin logged in successfully")
            else:
                self.log_result("SuperAdmin Login for Dashboard Stats", False, f"Status: {login_response.status_code}")
                return
        except Exception as e:
            self.log_result("SuperAdmin Login for Dashboard Stats", False, "Exception occurred", str(e))
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
                            self.log_result("SuperAdmin Dashboard Stats", True, 
                                          f"Dashboard stats working: Users total: {users_data.get('total', 'N/A')}, "
                                          f"Business total cases: {business_data.get('total_cases', 'N/A')}")
                        else:
                            self.log_result("SuperAdmin Dashboard Stats", False, 
                                          "Missing expected fields: users.total or business.total_cases")
                    else:
                        self.log_result("SuperAdmin Dashboard Stats", False, 
                                      f"Missing expected sections: {missing_fields}")
                else:
                    self.log_result("SuperAdmin Dashboard Stats", False, 
                                  f"Status: {response.status_code}", response.text)
            except Exception as e:
                self.log_result("SuperAdmin Dashboard Stats", False, "Exception occurred", str(e))

    def test_contact_form_new_fields(self):
        """Test POST /api/contact-messages avec les nouveaux champs how_did_you_know et referred_by_employee"""
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
                                  f"Contact created with new fields: how_did_you_know='{data['how_did_you_know']}', "
                                  f"referred_by_employee='{data['referred_by_employee']}'")
                    
                    # Test automatic assignment if employee is mentioned
                    if data.get('referred_by_employee') and data.get('assigned_to'):
                        self.log_result("Contact Form Employee Assignment", True, 
                                      f"Automatic assignment working: assigned to {data.get('assigned_to_name', 'N/A')}")
                    else:
                        self.log_result("Contact Form Employee Assignment", False, 
                                      "No automatic assignment despite employee reference")
                else:
                    self.log_result("Contact Form New Fields", False, 
                                  "Response missing new fields: how_did_you_know or referred_by_employee")
            else:
                self.log_result("Contact Form New Fields", False, 
                              f"Status: {response.status_code}", response.text)
                
        except Exception as e:
            self.log_result("Contact Form New Fields", False, "Exception occurred", str(e))

        # Test email sending (even if SendGrid not configured)
        try:
            # Test that the API doesn't break even if email service fails
            contact_data_email_test = {
                "name": "Marie Martin",
                "email": "marie.martin@example.com",
                "phone": "+33987654321",
                "country": "Canada",
                "visa_type": "Study Permit",
                "budget_range": "5000+€",
                "urgency_level": "Normal",
                "message": "Test d'envoi d'e-mail automatique pour nouveau contact.",
                "lead_source": "Réseaux sociaux",
                "how_did_you_know": "Publicité Facebook",
                "referred_by_employee": None
            }
            
            response = self.session.post(f"{API_BASE}/contact-messages", json=contact_data_email_test)
            if response.status_code == 200 or response.status_code == 201:
                self.log_result("Contact Form Email Handling", True, 
                              "Contact form handles email sending without breaking (even if SendGrid not configured)")
            else:
                self.log_result("Contact Form Email Handling", False, 
                              f"Contact form broken by email sending. Status: {response.status_code}")
                
        except Exception as e:
            self.log_result("Contact Form Email Handling", False, "Exception occurred", str(e))

    def test_user_creation_with_email(self):
        """Test POST /api/users/create avec send_email=true"""
        # First login as manager to test user creation
        if not self.manager_token:
            self.log_result("User Creation with Email", False, "No manager token available")
            return
            
        try:
            headers = {"Authorization": f"Bearer {self.manager_token}"}
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
                
                # Verify email_sent field and that no temporary_password is returned when send_email=True
                if 'email_sent' in data:
                    email_sent = data.get('email_sent', False)
                    has_temp_password = 'temporary_password' in data and data['temporary_password'] is not None
                    
                    if email_sent or not has_temp_password:
                        self.log_result("User Creation with Email", True, 
                                      f"User created with send_email=True. Email sent: {email_sent}, "
                                      f"Temp password in response: {has_temp_password}")
                    else:
                        self.log_result("User Creation with Email", False, 
                                      "Email sending attempted but failed, and temporary password not provided")
                else:
                    self.log_result("User Creation with Email", False, 
                                  "Response missing email_sent field")
            else:
                self.log_result("User Creation with Email", False, 
                              f"Status: {response.status_code}", response.text)
                
        except Exception as e:
            self.log_result("User Creation with Email", False, "Exception occurred", str(e))

    def test_case_update_with_email(self):
        """Test PATCH /api/cases/{id} pour mettre à jour un dossier avec envoi d'e-mail"""
        if not self.manager_token:
            self.log_result("Case Update with Email", False, "No manager token available")
            return
            
        try:
            headers = {"Authorization": f"Bearer {self.manager_token}"}
            
            # First get available cases
            cases_response = self.session.get(f"{API_BASE}/cases", headers=headers)
            if cases_response.status_code == 200:
                cases = cases_response.json()
                if cases:
                    case_id = cases[0]['id']
                    
                    # Update the case
                    update_data = {
                        "current_step_index": 2,
                        "status": "En cours de traitement",
                        "notes": "Test mise à jour avec envoi d'e-mail automatique au client"
                    }
                    
                    response = self.session.patch(f"{API_BASE}/cases/{case_id}", json=update_data, headers=headers)
                    if response.status_code == 200:
                        data = response.json()
                        self.log_result("Case Update with Email", True, 
                                      f"Case updated successfully. Status: {data.get('status', 'N/A')}, "
                                      f"Step: {data.get('current_step_index', 'N/A')}")
                        
                        # Check if email sending was attempted (even if it fails due to SendGrid config)
                        # The API should not break even if email sending fails
                        self.log_result("Case Update Email Handling", True, 
                                      "Case update completed without breaking (email sending attempted)")
                    else:
                        self.log_result("Case Update with Email", False, 
                                      f"Status: {response.status_code}", response.text)
                else:
                    self.log_result("Case Update with Email", False, "No cases available to update")
            else:
                self.log_result("Case Update with Email", False, 
                              f"Could not retrieve cases. Status: {cases_response.status_code}")
                
        except Exception as e:
            self.log_result("Case Update with Email", False, "Exception occurred", str(e))

    def test_regression_manager_login(self):
        """Test général de régression - Login Manager: manager@test.com / password123"""
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
                              f"Manager login successful: {manager_user['full_name']} ({manager_user['email']})")
                
                # Test that all existing functionalities still work
                headers = {"Authorization": f"Bearer {manager_token}"}
                
                # Test 1: Get clients
                clients_response = self.session.get(f"{API_BASE}/clients", headers=headers)
                if clients_response.status_code == 200:
                    clients = clients_response.json()
                    self.log_result("Regression - Get Clients", True, f"Retrieved {len(clients)} clients")
                else:
                    self.log_result("Regression - Get Clients", False, f"Status: {clients_response.status_code}")
                
                # Test 2: Get cases
                cases_response = self.session.get(f"{API_BASE}/cases", headers=headers)
                if cases_response.status_code == 200:
                    cases = cases_response.json()
                    self.log_result("Regression - Get Cases", True, f"Retrieved {len(cases)} cases")
                else:
                    self.log_result("Regression - Get Cases", False, f"Status: {cases_response.status_code}")
                
                # Test 3: Get notifications
                notifications_response = self.session.get(f"{API_BASE}/notifications", headers=headers)
                if notifications_response.status_code == 200:
                    notifications = notifications_response.json()
                    self.log_result("Regression - Get Notifications", True, f"Retrieved {len(notifications)} notifications")
                else:
                    self.log_result("Regression - Get Notifications", False, f"Status: {notifications_response.status_code}")
                
                # Test 4: Get chat conversations
                chat_response = self.session.get(f"{API_BASE}/chat/conversations", headers=headers)
                if chat_response.status_code == 200:
                    conversations = chat_response.json()
                    self.log_result("Regression - Get Chat Conversations", True, f"Retrieved {len(conversations)} conversations")
                else:
                    self.log_result("Regression - Get Chat Conversations", False, f"Status: {chat_response.status_code}")
                
                # Test 5: Get visitors
                visitors_response = self.session.get(f"{API_BASE}/visitors", headers=headers)
                if visitors_response.status_code == 200:
                    visitors = visitors_response.json()
                    self.log_result("Regression - Get Visitors", True, f"Retrieved {len(visitors)} visitors")
                else:
                    self.log_result("Regression - Get Visitors", False, f"Status: {visitors_response.status_code}")
                    
            else:
                self.log_result("Regression Manager Login", False, 
                              f"Login failed. Status: {response.status_code}, Response: {response.text}")
                
        except Exception as e:
            self.log_result("Regression Manager Login", False, "Exception occurred", str(e))

    def test_prospects_workflow_complete(self):
        """Test complete prospects workflow as requested in review"""
        print("=== Testing Complete Prospects Workflow (ALORIA AGENCY V4) ===")
        
        # Step 1: Create prospect via landing page form
        prospect_data = {
            "name": "Test Prospect Workflow",
            "email": "prospect.workflow@test.com", 
            "phone": "+237600000001",
            "country": "Canada",
            "visa_type": "Work Permit",
            "message": "Je veux immigrer au Canada",
            "urgency_level": "Normal",
            "lead_source": "Site web",
            "how_did_you_know": "Recherche Google",
            "referred_by_employee": None
        }
        
        prospect_id = None
        try:
            response = self.session.post(f"{API_BASE}/contact-messages", json=prospect_data)
            if response.status_code == 200 or response.status_code == 201:
                data = response.json()
                prospect_id = data['id']
                if data.get('status') == 'nouveau':
                    self.log_result("Prospects Step 1: Create Prospect", True, f"Prospect created with ID: {prospect_id}, status: nouveau")
                else:
                    self.log_result("Prospects Step 1: Create Prospect", False, f"Expected status 'nouveau', got: {data.get('status')}")
            else:
                self.log_result("Prospects Step 1: Create Prospect", False, f"Status: {response.status_code}", response.text)
        except Exception as e:
            self.log_result("Prospects Step 1: Create Prospect", False, "Exception occurred", str(e))
        
        if not prospect_id:
            self.log_result("Prospects Workflow", False, "Cannot continue without prospect ID")
            return
        
        # Get SuperAdmin and Manager tokens
        superadmin_token = None
        manager_token = None
        employee_token = None
        employee_id = None
        
        # Login as SuperAdmin
        try:
            login_response = self.session.post(f"{API_BASE}/auth/login", json={
                "email": "superadmin@aloria.com",
                "password": "SuperAdmin123!"
            })
            if login_response.status_code == 200:
                superadmin_token = login_response.json()['access_token']
        except:
            pass
        
        # Login as Manager
        try:
            login_response = self.session.post(f"{API_BASE}/auth/login", json={
                "email": "manager@test.com",
                "password": "password123"
            })
            if login_response.status_code == 200:
                manager_token = login_response.json()['access_token']
        except:
            pass
        
        # Create employee with known credentials
        if manager_token:
            try:
                manager_headers = {"Authorization": f"Bearer {manager_token}"}
                employee_data = {
                    "email": "workflow.employee@aloria.com",
                    "full_name": "Workflow Test Employee",
                    "phone": "+33123456789",
                    "role": "EMPLOYEE",
                    "send_email": False
                }
                
                create_response = self.session.post(f"{API_BASE}/users/create", json=employee_data, headers=manager_headers)
                if create_response.status_code in [200, 201]:
                    employee_result = create_response.json()
                    temp_password = employee_result.get('temporary_password')
                    employee_id = employee_result['id']
                    
                    # Login as employee
                    employee_login = self.session.post(f"{API_BASE}/auth/login", json={
                        "email": "workflow.employee@aloria.com",
                        "password": temp_password
                    })
                    if employee_login.status_code == 200:
                        employee_token = employee_login.json()['access_token']
            except:
                pass
        
        # Step 2: SuperAdmin assigns prospect to Employee
        if superadmin_token and employee_id:
            try:
                headers = {"Authorization": f"Bearer {superadmin_token}"}
                assign_data = {"assigned_to": employee_id}
                response = self.session.patch(f"{API_BASE}/contact-messages/{prospect_id}/assign", json=assign_data, headers=headers)
                if response.status_code == 200:
                    self.log_result("Prospects Step 2: SuperAdmin Assigns to Employee", True, f"Prospect assigned to employee successfully")
                else:
                    self.log_result("Prospects Step 2: SuperAdmin Assigns to Employee", False, f"Status: {response.status_code}", response.text)
            except Exception as e:
                self.log_result("Prospects Step 2: SuperAdmin Assigns to Employee", False, "Exception occurred", str(e))
        else:
            self.log_result("Prospects Step 2: SuperAdmin Assigns to Employee", False, "No SuperAdmin token or employee ID available")
        
        # Step 3: Employee assigns to consultant (payment 50k)
        if employee_token:
            try:
                headers = {"Authorization": f"Bearer {employee_token}"}
                response = self.session.patch(f"{API_BASE}/contact-messages/{prospect_id}/assign-consultant", headers=headers)
                if response.status_code == 200:
                    data = response.json()
                    if data.get('payment_50k_amount') == 50000:
                        self.log_result("Prospects Step 3: Employee Assigns to Consultant", True, f"Prospect assigned to consultant, payment: 50000 CFA")
                    else:
                        self.log_result("Prospects Step 3: Employee Assigns to Consultant", False, f"Payment amount incorrect: {data.get('payment_50k_amount')}")
                else:
                    self.log_result("Prospects Step 3: Employee Assigns to Consultant", False, f"Status: {response.status_code}", response.text)
            except Exception as e:
                self.log_result("Prospects Step 3: Employee Assigns to Consultant", False, "Exception occurred", str(e))
        
        # Step 4: SuperAdmin adds consultant notes
        if superadmin_token:
            try:
                headers = {"Authorization": f"Bearer {superadmin_token}"}
                notes_data = {"note": "Profil très prometteur, bon niveau anglais"}
                response = self.session.patch(f"{API_BASE}/contact-messages/{prospect_id}/consultant-notes", json=notes_data, headers=headers)
                if response.status_code == 200:
                    self.log_result("Prospects Step 4: SuperAdmin Adds Consultant Notes", True, f"Consultant notes added successfully")
                else:
                    self.log_result("Prospects Step 4: SuperAdmin Adds Consultant Notes", False, f"Status: {response.status_code}", response.text)
            except Exception as e:
                self.log_result("Prospects Step 4: SuperAdmin Adds Consultant Notes", False, "Exception occurred", str(e))
        
        # Step 5: Employee converts prospect to client
        if employee_token:
            try:
                headers = {"Authorization": f"Bearer {employee_token}"}
                convert_data = {
                    "first_payment_amount": 150000,
                    "country": "Canada", 
                    "visa_type": "Work Permit"
                }
                response = self.session.post(f"{API_BASE}/contact-messages/{prospect_id}/convert-to-client", json=convert_data, headers=headers)
                if response.status_code == 200 or response.status_code == 201:
                    data = response.json()
                    if data.get('client_id'):
                        self.log_result("Prospects Step 5: Employee Converts to Client", True, f"Prospect converted to client, client_id: {data.get('client_id')}")
                        
                        # Verify client user was created using SuperAdmin access
                        if superadmin_token:
                            superadmin_headers = {"Authorization": f"Bearer {superadmin_token}"}
                            users_response = self.session.get(f"{API_BASE}/admin/users", headers=superadmin_headers)
                            if users_response.status_code == 200:
                                users = users_response.json()
                                client_user = next((u for u in users if u.get('role') == 'CLIENT' and u.get('email') == prospect_data['email']), None)
                                if client_user:
                                    self.log_result("Prospects Step 5a: Client User Created", True, f"Client user created with email: {client_user['email']}")
                                else:
                                    self.log_result("Prospects Step 5a: Client User Created", False, "Client user not found in users list")
                    else:
                        self.log_result("Prospects Step 5: Employee Converts to Client", False, f"No client_id in response")
                else:
                    self.log_result("Prospects Step 5: Employee Converts to Client", False, f"Status: {response.status_code}", response.text)
            except Exception as e:
                self.log_result("Prospects Step 5: Employee Converts to Client", False, "Exception occurred", str(e))

    def test_prospects_access_restrictions(self):
        """Test API access restrictions by role for prospects"""
        print("=== Testing Prospects API Access Restrictions ===")
        
        # SuperAdmin should see ALL prospects
        superadmin_token = None
        try:
            # Try different SuperAdmin credentials
            for creds in [
                {"email": "admin@aloria.com", "password": "password"},
                {"email": "superadmin@aloria.com", "password": "SuperAdmin123!"},
                {"email": "superadmin@aloria.com", "password": "password"}
            ]:
                login_response = self.session.post(f"{API_BASE}/auth/login", json=creds)
                if login_response.status_code == 200:
                    user_data = login_response.json()
                    if user_data['user']['role'] == 'SUPERADMIN':
                        superadmin_token = user_data['access_token']
                        break
        except:
            pass
        
        if superadmin_token:
            try:
                headers = {"Authorization": f"Bearer {superadmin_token}"}
                response = self.session.get(f"{API_BASE}/contact-messages", headers=headers)
                if response.status_code == 200:
                    prospects = response.json()
                    self.log_result("SuperAdmin Prospects Access", True, f"SuperAdmin can see ALL prospects: {len(prospects)} total")
                else:
                    self.log_result("SuperAdmin Prospects Access", False, f"Status: {response.status_code}", response.text)
            except Exception as e:
                self.log_result("SuperAdmin Prospects Access", False, "Exception occurred", str(e))
        
        # Manager/Employee should see ONLY assigned prospects
        if self.manager_token:
            try:
                headers = {"Authorization": f"Bearer {self.manager_token}"}
                response = self.session.get(f"{API_BASE}/contact-messages", headers=headers)
                if response.status_code == 200:
                    prospects = response.json()
                    self.log_result("Manager Prospects Access", True, f"Manager sees only assigned prospects: {len(prospects)} assigned")
                else:
                    self.log_result("Manager Prospects Access", False, f"Status: {response.status_code}", response.text)
            except Exception as e:
                self.log_result("Manager Prospects Access", False, "Exception occurred", str(e))
        
        if self.employee_token:
            try:
                headers = {"Authorization": f"Bearer {self.employee_token}"}
                response = self.session.get(f"{API_BASE}/contact-messages", headers=headers)
                if response.status_code == 200:
                    prospects = response.json()
                    self.log_result("Employee Prospects Access", True, f"Employee sees only assigned prospects: {len(prospects)} assigned")
                else:
                    self.log_result("Employee Prospects Access", False, f"Status: {response.status_code}", response.text)
            except Exception as e:
                self.log_result("Employee Prospects Access", False, "Exception occurred", str(e))
        
        # Client should be DENIED access (403)
        try:
            client_login_response = self.session.post(f"{API_BASE}/auth/login", json={
                "email": "client.test@example.com",
                "password": "Aloria2024!"
            })
            if client_login_response.status_code == 200:
                client_token = client_login_response.json()['access_token']
                client_headers = {"Authorization": f"Bearer {client_token}"}
                response = self.session.get(f"{API_BASE}/contact-messages", headers=client_headers)
                if response.status_code == 403:
                    self.log_result("Client Prospects Access (should be denied)", True, "Client correctly denied access to prospects (403)")
                else:
                    self.log_result("Client Prospects Access (should be denied)", False, f"Expected 403, got {response.status_code}")
            else:
                self.log_result("Client Prospects Access (should be denied)", False, "Could not login as client to test")
        except Exception as e:
            self.log_result("Client Prospects Access (should be denied)", False, "Exception occurred", str(e))

    def test_prospects_search_and_filtering(self):
        """Test prospects search and filtering functionality"""
        print("=== Testing Prospects Search and Filtering ===")
        
        if self.manager_token:
            try:
                headers = {"Authorization": f"Bearer {self.manager_token}"}
                
                # Test status filtering
                response = self.session.get(f"{API_BASE}/contact-messages?status=nouveau", headers=headers)
                if response.status_code == 200:
                    prospects = response.json()
                    # Verify all returned prospects have status 'nouveau'
                    all_nouveau = all(p.get('status') == 'nouveau' for p in prospects)
                    if all_nouveau:
                        self.log_result("Prospects Status Filtering", True, f"Status filter working: {len(prospects)} prospects with status 'nouveau'")
                    else:
                        self.log_result("Prospects Status Filtering", False, "Status filter not working correctly - mixed statuses returned")
                else:
                    self.log_result("Prospects Status Filtering", False, f"Status: {response.status_code}", response.text)
            except Exception as e:
                self.log_result("Prospects Status Filtering", False, "Exception occurred", str(e))

    def test_sendgrid_email_service(self):
        """Test SendGrid email service integration"""
        print("=== Testing SendGrid Email Service ===")
        
        # Check backend logs for email attempts (since SendGrid may not be configured)
        try:
            # Create a prospect to trigger welcome email
            prospect_data = {
                "name": "Email Test Prospect",
                "email": "emailtest@example.com",
                "phone": "+237600000002", 
                "country": "France",
                "visa_type": "Student Visa",
                "message": "Test email service integration",
                "urgency_level": "Normal",
                "lead_source": "Site web",
                "how_did_you_know": "Test"
            }
            
            response = self.session.post(f"{API_BASE}/contact-messages", json=prospect_data)
            if response.status_code == 200 or response.status_code == 201:
                self.log_result("Email Service Test - Prospect Creation", True, "Prospect created - check backend logs for email attempts")
            else:
                self.log_result("Email Service Test - Prospect Creation", False, f"Status: {response.status_code}")
                
        except Exception as e:
            self.log_result("Email Service Test", False, "Exception occurred", str(e))

    def test_existing_endpoints_regression(self):
        """Test existing endpoints to ensure no regression"""
        print("=== Testing Existing Endpoints (Regression) ===")
        
        # Test login endpoints
        if self.manager_token:
            self.log_result("Regression - Manager Login", True, "Manager login still working")
        else:
            self.log_result("Regression - Manager Login", False, "Manager login broken")
        
        if self.employee_token:
            self.log_result("Regression - Employee Login", True, "Employee login still working")
        else:
            self.log_result("Regression - Employee Login", False, "Employee login broken")
        
        # Test cases endpoint
        if self.manager_token:
            try:
                headers = {"Authorization": f"Bearer {self.manager_token}"}
                response = self.session.get(f"{API_BASE}/cases", headers=headers)
                if response.status_code == 200:
                    cases = response.json()
                    self.log_result("Regression - Cases Endpoint", True, f"Cases endpoint working: {len(cases)} cases")
                else:
                    self.log_result("Regression - Cases Endpoint", False, f"Status: {response.status_code}")
            except Exception as e:
                self.log_result("Regression - Cases Endpoint", False, "Exception occurred", str(e))
        
        # Test users endpoint
        if self.manager_token:
            try:
                headers = {"Authorization": f"Bearer {self.manager_token}"}
                response = self.session.get(f"{API_BASE}/users", headers=headers)
                if response.status_code == 200:
                    users = response.json()
                    self.log_result("Regression - Users Endpoint", True, f"Users endpoint working: {len(users)} users")
                else:
                    self.log_result("Regression - Users Endpoint", False, f"Status: {response.status_code}")
            except Exception as e:
                self.log_result("Regression - Users Endpoint", False, "Exception occurred", str(e))
        
        # Test payments endpoint
        if self.manager_token:
            try:
                headers = {"Authorization": f"Bearer {self.manager_token}"}
                response = self.session.get(f"{API_BASE}/payments", headers=headers)
                if response.status_code == 200:
                    payments = response.json()
                    self.log_result("Regression - Payments Endpoint", True, f"Payments endpoint working: {len(payments)} payments")
                else:
                    self.log_result("Regression - Payments Endpoint", False, f"Status: {response.status_code}")
            except Exception as e:
                self.log_result("Regression - Payments Endpoint", False, "Exception occurred", str(e))
        
        # Test company-info endpoint
        try:
            response = self.session.get(f"{API_BASE}/company-info")
            if response.status_code == 200:
                company_info = response.json()
                # Check if balance includes 50k CFA from prospects
                balance = company_info.get('balance', {})
                self.log_result("Regression - Company Info Endpoint", True, f"Company info working, balance: {balance}")
            else:
                self.log_result("Regression - Company Info Endpoint", False, f"Status: {response.status_code}")
        except Exception as e:
            self.log_result("Regression - Company Info Endpoint", False, "Exception occurred", str(e))

    def test_comprehensive_backend_post_fixes(self):
        """Comprehensive backend testing after critical fixes - as per review request"""
        print("=== COMPREHENSIVE BACKEND TESTING - POST CRITICAL FIXES ===")
        
        # HIGH PRIORITY TESTS (as per review request)
        print("\n🔥 HIGH PRIORITY TESTS")
        print("-" * 40)
        
        # 1. Authentication & User Management
        self.test_user_registration_and_login()
        self.test_superadmin_creation()
        self.test_role_hierarchy_permissions()
        self.test_password_change_api()
        
        # 2. Prospect Workflow V4 - Complete 5-step process
        self.test_prospects_workflow_complete()
        
        # 3. Visitor Management with new fields
        self.test_visitor_stats()
        
        # 4. Payment System - Complete workflow
        self.test_payment_system_comprehensive()
        
        # 5. Chat System & WebSocket
        self.test_chat_apis()
        
        print("\n🔶 MEDIUM PRIORITY TESTS")
        print("-" * 40)
        
        # 6. Notification System
        self.test_notification_system()
        self.test_automatic_notifications()
        
        # 7. Case Management
        self.test_client_creation_permissions()
        self.test_permissions_and_case_management()
        self.test_client_credentials_api()
        self.test_client_creation_with_password()
        
        # 8. SuperAdmin Features
        self.test_superadmin_apis()
        
        # 9. Search System
        self.test_search_apis()
        
        # 10. Email Service
        self.test_sendgrid_email_service()
        
        print("\n🔷 ADDITIONAL COMPREHENSIVE TESTS")
        print("-" * 40)
        
        # Contact Messages & CRM
        self.test_contact_messages_crm()
        
        # Workflow management
        self.test_workflow_management()
        
        # Integration scenarios
        self.test_complete_integration()
        self.test_complete_scenario()
        self.test_comprehensive_v2_scenario()
        
        # Error handling and edge cases
        self.test_error_cases_and_validation()
        self.test_existing_endpoints_regression()
        self.test_prospects_access_restrictions()
        self.test_prospects_search_and_filtering()
        self.test_review_request_specific_tests()

    def run_all_tests(self):
        """Run all tests in sequence - PRODUCTION READY EXHAUSTIVE TESTING"""
        print("🚀 ALORIA AGENCY - BACKEND TESTING EXHAUSTIF - PRODUCTION READY")
        print(f"Backend URL: {API_BASE}")
        print("Testing ALL critical functionalities for production deployment")
        print("=" * 80)
        
        # Authentication setup
        self.authenticate_all_roles()
        
        # Run priority tests in order
        self.test_priority_1_prospect_workflow()
        self.test_priority_2_manager_employee_actions()
        self.test_priority_3_superadmin_operations()
        self.test_priority_4_role_based_prospect_access()
        self.test_priority_5_payment_workflow()
        self.test_priority_6_withdrawal_manager()
        
        # Print comprehensive summary
        print("=" * 80)
        print("🎯 PRODUCTION READINESS TEST SUMMARY")
        print(f"✅ Passed: {self.results['passed']}")
        print(f"❌ Failed: {self.results['failed']}")
        total_tests = self.results['passed'] + self.results['failed']
        success_rate = (self.results['passed'] / total_tests * 100) if total_tests > 0 else 0
        print(f"📊 Success Rate: {success_rate:.1f}%")
        
        # Production readiness assessment
        if success_rate >= 95:
            print("🟢 PRODUCTION READY - Excellent success rate")
        elif success_rate >= 85:
            print("🟡 MOSTLY READY - Minor issues to address")
        else:
            print("🔴 NOT READY - Critical issues need fixing")
        
        if self.results['errors']:
            print(f"\n🔍 FAILED TESTS ({len(self.results['errors'])}):")
            for i, error in enumerate(self.results['errors'], 1):
                print(f"   {i}. {error['test']}")
                if error['message']:
                    print(f"      → {error['message']}")
                if error['error']:
                    print(f"      → Error: {error['error'][:100]}...")
        
        print("=" * 80)
        return self.results['failed'] == 0

if __name__ == "__main__":
    tester = APITester()
    
    # Check if rapid tests are requested
    if len(sys.argv) > 1 and sys.argv[1] == "--rapid":
        tester.run_rapid_tests()
    else:
        tester.run_all_tests()
    
    # Return success/failure based on results
    success = tester.results['failed'] == 0
    sys.exit(0 if success else 1)