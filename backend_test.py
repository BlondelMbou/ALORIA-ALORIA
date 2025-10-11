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
BACKEND_URL = os.environ.get('REACT_APP_BACKEND_URL', 'https://immigra-portal.preview.emergentagent.com')
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

        # Test 3: Test confirmation code generation and validation
        confirmation_code = None
        if self.manager_token and payment_id:
            try:
                headers = {"Authorization": f"Bearer {self.manager_token}"}
                
                # First, try to confirm with CONFIRMED action (should generate confirmation code)
                confirmation_data = {
                    "action": "CONFIRMED",
                    "confirmation_code": None  # Should be auto-generated
                }
                response = self.session.patch(f"{API_BASE}/payments/{payment_id}/confirm", json=confirmation_data, headers=headers)
                
                if response.status_code == 200:
                    confirmed_payment = response.json()
                    
                    # Check if confirmation code was generated
                    if 'confirmation_code' in confirmed_payment:
                        confirmation_code = confirmed_payment['confirmation_code']
                        self.log_result("4. Confirmation Code Generation", True, 
                                      f"Code de confirmation généré: {confirmation_code}")
                    else:
                        self.log_result("4. Confirmation Code Generation", False, 
                                      "Code de confirmation manquant dans la réponse")
                    
                    # Check invoice number generation
                    if 'invoice_number' in confirmed_payment and confirmed_payment['invoice_number']:
                        invoice_number = confirmed_payment['invoice_number']
                        self.log_result("5. Invoice Number Generation", True, 
                                      f"Numéro de facture généré: {invoice_number}")
                    else:
                        self.log_result("5. Invoice Number Generation", False, 
                                      "Numéro de facture manquant ou vide")
                    
                    # Check status change
                    if confirmed_payment.get('status') == 'confirmed':
                        self.log_result("6. Payment Status Update", True, 
                                      f"Statut mis à jour: {confirmed_payment['status']}")
                    else:
                        self.log_result("6. Payment Status Update", False, 
                                      f"Statut incorrect: {confirmed_payment.get('status')}")
                        
                elif response.status_code == 400:
                    # Check if it's asking for confirmation code
                    error_msg = response.text
                    if "confirmation" in error_msg.lower() or "code" in error_msg.lower():
                        self.log_result("4. Confirmation Code Validation", True, 
                                      "Système demande code de confirmation - workflow correct")
                    else:
                        self.log_result("4. Confirmation Code Validation", False, 
                                      f"Erreur inattendue: {error_msg}")
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
        if self.manager_token and payment_id:
            try:
                headers = {"Authorization": f"Bearer {self.manager_token}"}
                confirmation_data = {
                    "action": "CONFIRMED",
                    "confirmation_code": confirmation_code if confirmation_code else "TEST"
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
        if self.manager_token and payment_id:
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
                    
                    if our_payment and 'pdf_url' in our_payment and our_payment['pdf_url']:
                        # Try to access PDF URL
                        pdf_response = self.session.get(our_payment['pdf_url'])
                        if pdf_response.status_code == 200 and 'pdf' in pdf_response.headers.get('content-type', '').lower():
                            self.log_result("11. PDF Generation & Access", True, 
                                          f"PDF généré et accessible: {our_payment['pdf_url']}")
                        else:
                            self.log_result("11. PDF Generation & Access", False, 
                                          f"PDF non accessible ou format incorrect: {pdf_response.status_code}")
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

    def run_all_tests(self):
        """Run all test suites including V2 features"""
        print("🚀 Starting ALORIA AGENCY V2 Backend API Tests - COMPREHENSIVE TESTING")
        print(f"Testing against: {API_BASE}")
        print("=" * 60)
        
        # V2 New Features Tests
        self.test_superadmin_creation()
        self.test_role_hierarchy_permissions()
        self.test_payment_system()
        self.test_superadmin_apis()
        self.test_search_apis()
        self.test_visitor_stats()
        self.test_comprehensive_v2_scenario()
        
        # Existing Features Tests
        self.test_user_registration_and_login()
        self.test_client_creation_permissions()
        self.test_notification_system()
        self.test_automatic_notifications()
        self.test_complete_integration()
        self.test_client_creation_with_password()
        self.test_password_change_api()
        self.test_client_credentials_api()
        self.test_chat_apis()
        self.test_visitor_management()
        self.test_workflow_management()
        self.test_permissions_and_case_management()
        self.test_complete_scenario()
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