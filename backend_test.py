#!/usr/bin/env python3
"""
ALORIA AGENCY Backend API Testing Suite
Tests all backend functionalities including authentication, client management, 
chat system, visitor management, and workflow customization.
"""

import requests
import json
import os
from datetime import datetime
import sys

# Get backend URL from environment
BACKEND_URL = os.environ.get('REACT_APP_BACKEND_URL', 'https://dossier-track.preview.emergentagent.com')
API_BASE = f"{BACKEND_URL}/api"

class APITester:
    def __init__(self):
        self.session = requests.Session()
        self.manager_token = None
        self.employee_token = None
        self.manager_user = None
        self.employee_user = None
        self.test_client_id = None
        self.test_visitor_id = None
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

    def test_user_registration_and_login(self):
        """Test user registration and login for MANAGER and EMPLOYEE"""
        print("=== Testing Authentication ===")
        
        # Test Manager Registration
        manager_data = {
            "email": "manager@aloria.com",
            "password": "admin123",
            "full_name": "Test Manager",
            "phone": "+33123456789",
            "role": "MANAGER"
        }
        
        try:
            response = self.session.post(f"{API_BASE}/auth/register", json=manager_data)
            if response.status_code == 201 or response.status_code == 200:
                data = response.json()
                self.manager_token = data['access_token']
                self.manager_user = data['user']
                self.log_result("Manager Registration", True, f"Manager created with ID: {self.manager_user['id']}")
            elif response.status_code == 400 and "already registered" in response.text:
                # User already exists, try login
                login_response = self.session.post(f"{API_BASE}/auth/login", json={
                    "email": manager_data["email"],
                    "password": manager_data["password"]
                })
                if login_response.status_code == 200:
                    data = login_response.json()
                    self.manager_token = data['access_token']
                    self.manager_user = data['user']
                    self.log_result("Manager Login (existing user)", True, f"Manager logged in with ID: {self.manager_user['id']}")
                else:
                    self.log_result("Manager Login", False, "Failed to login existing manager", login_response.text)
            else:
                self.log_result("Manager Registration", False, f"Status: {response.status_code}", response.text)
        except Exception as e:
            self.log_result("Manager Registration", False, "Exception occurred", str(e))

        # Test Employee Registration
        employee_data = {
            "email": "employee@aloria.com",
            "password": "emp123",
            "full_name": "Test Employee",
            "phone": "+33987654321",
            "role": "EMPLOYEE"
        }
        
        try:
            response = self.session.post(f"{API_BASE}/auth/register", json=employee_data)
            if response.status_code == 201 or response.status_code == 200:
                data = response.json()
                self.employee_token = data['access_token']
                self.employee_user = data['user']
                self.log_result("Employee Registration", True, f"Employee created with ID: {self.employee_user['id']}")
            elif response.status_code == 400 and "already registered" in response.text:
                # User already exists, try login
                login_response = self.session.post(f"{API_BASE}/auth/login", json={
                    "email": employee_data["email"],
                    "password": employee_data["password"]
                })
                if login_response.status_code == 200:
                    data = login_response.json()
                    self.employee_token = data['access_token']
                    self.employee_user = data['user']
                    self.log_result("Employee Login (existing user)", True, f"Employee logged in with ID: {self.employee_user['id']}")
                else:
                    self.log_result("Employee Login", False, "Failed to login existing employee", login_response.text)
            else:
                self.log_result("Employee Registration", False, f"Status: {response.status_code}", response.text)
        except Exception as e:
            self.log_result("Employee Registration", False, "Exception occurred", str(e))

    def test_client_creation_permissions(self):
        """Test client creation - only managers should be able to create clients"""
        print("=== Testing Client Creation Permissions ===")
        
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

        # Test Employee cannot create client
        if self.employee_token:
            try:
                headers = {"Authorization": f"Bearer {self.employee_token}"}
                response = self.session.post(f"{API_BASE}/clients", json=client_data, headers=headers)
                if response.status_code == 403:
                    self.log_result("Employee Client Creation (should fail)", True, "Employee correctly denied client creation")
                else:
                    self.log_result("Employee Client Creation (should fail)", False, f"Employee should not be able to create clients. Status: {response.status_code}")
            except Exception as e:
                self.log_result("Employee Client Creation (should fail)", False, "Exception occurred", str(e))
        else:
            self.log_result("Employee Client Creation (should fail)", False, "No employee token available")

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

    def run_all_tests(self):
        """Run all test suites"""
        print("🚀 Starting ALORIA AGENCY Backend API Tests")
        print(f"Testing against: {API_BASE}")
        print("=" * 60)
        
        self.test_user_registration_and_login()
        self.test_client_creation_permissions()
        self.test_chat_apis()
        self.test_visitor_management()
        self.test_workflow_management()
        self.test_permissions_and_case_management()
        self.test_error_cases_and_validation()
        
        print("=" * 60)
        print("🏁 Test Summary")
        print(f"✅ Passed: {self.results['passed']}")
        print(f"❌ Failed: {self.results['failed']}")
        print(f"📊 Success Rate: {(self.results['passed'] / (self.results['passed'] + self.results['failed']) * 100):.1f}%")
        
        if self.results['errors']:
            print("\n🔍 Failed Tests Details:")
            for error in self.results['errors']:
                print(f"  • {error['test']}: {error['message']}")
                if error['error']:
                    print(f"    Error: {error['error'][:200]}...")
        
        return self.results['failed'] == 0

if __name__ == "__main__":
    tester = APITester()
    success = tester.run_all_tests()
    sys.exit(0 if success else 1)