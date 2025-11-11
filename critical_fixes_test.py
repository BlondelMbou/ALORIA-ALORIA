#!/usr/bin/env python3
"""
ALORIA AGENCY - Critical Fixes Verification Test Suite
Tests specific critical fixes mentioned in the review request:
1. Prospect Conversion to Client
2. Client Reassignment 
3. SuperAdmin APIs
4. User Creation - CONSULTANT Role
5. Visitor Creation
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

class CriticalFixesTester:
    def __init__(self):
        self.session = requests.Session()
        self.superadmin_token = None
        self.manager_token = None
        self.employee_token = None
        self.consultant_token = None
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

    def authenticate_users(self):
        """Authenticate with review credentials"""
        print("=== Authenticating with Review Credentials ===")
        
        # SuperAdmin: superadmin@aloria.com / SuperAdmin123!
        try:
            response = self.session.post(f"{API_BASE}/auth/login", json={
                "email": "superadmin@aloria.com",
                "password": "SuperAdmin123!"
            })
            if response.status_code == 200:
                self.superadmin_token = response.json()['access_token']
                self.log_result("SuperAdmin Authentication", True, "SuperAdmin logged in successfully")
            else:
                self.log_result("SuperAdmin Authentication", False, f"Status: {response.status_code}", response.text)
        except Exception as e:
            self.log_result("SuperAdmin Authentication", False, "Exception occurred", str(e))

        # Manager: manager@test.com / password123
        try:
            response = self.session.post(f"{API_BASE}/auth/login", json={
                "email": "manager@test.com",
                "password": "password123"
            })
            if response.status_code == 200:
                self.manager_token = response.json()['access_token']
                self.log_result("Manager Authentication", True, "Manager logged in successfully")
            else:
                self.log_result("Manager Authentication", False, f"Status: {response.status_code}", response.text)
        except Exception as e:
            self.log_result("Manager Authentication", False, "Exception occurred", str(e))

        # Employee: employee@aloria.com / emp123
        try:
            response = self.session.post(f"{API_BASE}/auth/login", json={
                "email": "employee@aloria.com",
                "password": "emp123"
            })
            if response.status_code == 200:
                self.employee_token = response.json()['access_token']
                self.log_result("Employee Authentication", True, "Employee logged in successfully")
            else:
                self.log_result("Employee Authentication", False, f"Status: {response.status_code}", response.text)
        except Exception as e:
            self.log_result("Employee Authentication", False, "Exception occurred", str(e))

    def test_superadmin_apis(self):
        """Test SuperAdmin APIs that feed SuperAdminDashboard"""
        print("=== Testing SuperAdmin APIs (HIGH PRIORITY) ===")
        
        if not self.superadmin_token:
            self.log_result("SuperAdmin APIs", False, "No SuperAdmin token available")
            return

        headers = {"Authorization": f"Bearer {self.superadmin_token}"}

        # Test GET /api/admin/users (should return ALL users list)
        try:
            response = self.session.get(f"{API_BASE}/admin/users", headers=headers)
            if response.status_code == 200:
                users = response.json()
                self.log_result("GET /api/admin/users", True, f"Retrieved {len(users)} users from system")
            else:
                self.log_result("GET /api/admin/users", False, f"Status: {response.status_code}", response.text)
        except Exception as e:
            self.log_result("GET /api/admin/users", False, "Exception occurred", str(e))

        # Test GET /api/admin/activities (should return activities history)
        try:
            response = self.session.get(f"{API_BASE}/admin/activities", headers=headers)
            if response.status_code == 200:
                activities = response.json()
                self.log_result("GET /api/admin/activities", True, f"Retrieved {len(activities)} activity entries")
            else:
                self.log_result("GET /api/admin/activities", False, f"Status: {response.status_code}", response.text)
        except Exception as e:
            self.log_result("GET /api/admin/activities", False, "Exception occurred", str(e))

        # Test GET /api/admin/dashboard-stats (should return stats)
        try:
            response = self.session.get(f"{API_BASE}/admin/dashboard-stats", headers=headers)
            if response.status_code == 200:
                stats = response.json()
                # Check the actual structure returned by the API
                if 'users' in stats and 'business' in stats:
                    users = stats['users']
                    business = stats['business']
                    total_cases = business.get('total_cases', 0)
                    active_cases = business.get('active_cases', 0)
                    total_clients = users.get('clients', 0)
                    total_employees = users.get('employees', 0)
                    self.log_result("GET /api/admin/dashboard-stats", True, f"Dashboard stats complete: {total_cases} cases, {total_clients} clients, {total_employees} employees")
                else:
                    self.log_result("GET /api/admin/dashboard-stats", False, f"Unexpected response structure: {list(stats.keys())}")
            else:
                self.log_result("GET /api/admin/dashboard-stats", False, f"Status: {response.status_code}", response.text)
        except Exception as e:
            self.log_result("GET /api/admin/dashboard-stats", False, "Exception occurred", str(e))

    def test_consultant_user_creation(self):
        """Test User Creation - CONSULTANT Role (HIGH PRIORITY)"""
        print("=== Testing CONSULTANT User Creation (HIGH PRIORITY) ===")
        
        if not self.superadmin_token:
            self.log_result("CONSULTANT User Creation", False, "No SuperAdmin token available")
            return

        headers = {"Authorization": f"Bearer {self.superadmin_token}"}
        
        # Test POST /api/users with role='CONSULTANT'
        try:
            timestamp = int(time.time())
            consultant_data = {
                "email": f"consultant.test.{timestamp}@aloria.com",
                "full_name": "Test Consultant User",
                "phone": "+33123456789",
                "role": "CONSULTANT",
                "send_email": False
            }
            response = self.session.post(f"{API_BASE}/users/create", json=consultant_data, headers=headers)
            if response.status_code == 200 or response.status_code == 201:
                data = response.json()
                self.log_result("CONSULTANT User Creation", True, f"CONSULTANT user created successfully with ID: {data.get('id', 'N/A')}")
                
                # Try to login as consultant to verify creation
                if 'temporary_password' in data:
                    login_response = self.session.post(f"{API_BASE}/auth/login", json={
                        "email": consultant_data["email"],
                        "password": data['temporary_password']
                    })
                    if login_response.status_code == 200:
                        self.consultant_token = login_response.json()['access_token']
                        self.log_result("CONSULTANT Login Verification", True, "CONSULTANT can login with temporary password")
                    else:
                        self.log_result("CONSULTANT Login Verification", False, f"Login failed: {login_response.status_code}")
            else:
                self.log_result("CONSULTANT User Creation", False, f"Status: {response.status_code}", response.text)
        except Exception as e:
            self.log_result("CONSULTANT User Creation", False, "Exception occurred", str(e))

    def test_visitor_creation(self):
        """Test Visitor Creation (MEDIUM PRIORITY)"""
        print("=== Testing Visitor Creation (MEDIUM PRIORITY) ===")
        
        # Test with MANAGER role
        if self.manager_token:
            try:
                headers = {"Authorization": f"Bearer {self.manager_token}"}
                visitor_data = {
                    "full_name": "Jean-Pierre Dubois",
                    "phone_number": "+33123456789",
                    "purpose": "Consultation initiale",
                    "cni_number": "123456789012"
                }
                response = self.session.post(f"{API_BASE}/visitors", json=visitor_data, headers=headers)
                if response.status_code == 200 or response.status_code == 201:
                    data = response.json()
                    self.log_result("Manager Visitor Creation", True, f"Visitor created by Manager with ID: {data.get('id', 'N/A')}")
                else:
                    self.log_result("Manager Visitor Creation", False, f"Status: {response.status_code}", response.text)
            except Exception as e:
                self.log_result("Manager Visitor Creation", False, "Exception occurred", str(e))

        # Test with EMPLOYEE role
        if self.employee_token:
            try:
                headers = {"Authorization": f"Bearer {self.employee_token}"}
                visitor_data = {
                    "full_name": "Marie-Claire Martin",
                    "phone_number": "+33987654321",
                    "purpose": "Remise de documents",
                    "cni_number": "987654321098"
                }
                response = self.session.post(f"{API_BASE}/visitors", json=visitor_data, headers=headers)
                if response.status_code == 200 or response.status_code == 201:
                    data = response.json()
                    self.log_result("Employee Visitor Creation", True, f"Visitor created by Employee with ID: {data.get('id', 'N/A')}")
                else:
                    self.log_result("Employee Visitor Creation", False, f"Status: {response.status_code}", response.text)
            except Exception as e:
                self.log_result("Employee Visitor Creation", False, "Exception occurred", str(e))

    def create_test_prospect(self):
        """Create a test prospect for conversion testing"""
        try:
            # Create a contact message (prospect)
            timestamp = int(time.time())
            prospect_data = {
                "name": f"Test Prospect {timestamp}",
                "email": f"prospect.{timestamp}@example.com",
                "phone": "+33123456789",
                "country": "France",
                "visa_type": "Work Permit",
                "budget_range": "5000+€",
                "urgency_level": "Urgent",
                "message": "Je souhaite obtenir un permis de travail en France. J'ai un budget conséquent et c'est urgent.",
                "lead_source": "Site web",
                "how_did_you_know": "Recherche Google"
            }
            
            response = self.session.post(f"{API_BASE}/contact-messages", json=prospect_data)
            if response.status_code == 200 or response.status_code == 201:
                prospect = response.json()
                prospect_id = prospect['id']
                
                # Assign to employee and set status to 'paiement_50k'
                if self.superadmin_token:
                    headers = {"Authorization": f"Bearer {self.superadmin_token}"}
                    
                    # First assign to employee
                    assign_response = self.session.patch(
                        f"{API_BASE}/contact-messages/{prospect_id}/assign",
                        json={"employee_id": "some-employee-id"},
                        headers=headers
                    )
                    
                    # Then set to consultant payment status
                    consultant_response = self.session.patch(
                        f"{API_BASE}/contact-messages/{prospect_id}/assign-consultant",
                        json={"consultant_id": "some-consultant-id", "payment_amount": 50000},
                        headers=headers
                    )
                    
                    return prospect_id
            return None
        except Exception as e:
            print(f"Error creating test prospect: {e}")
            return None

    def test_prospect_conversion_to_client(self):
        """Test Prospect Conversion to Client (HIGH PRIORITY)"""
        print("=== Testing Prospect Conversion to Client (HIGH PRIORITY) ===")
        
        # First, get existing prospects with correct status
        if self.manager_token:
            try:
                headers = {"Authorization": f"Bearer {self.manager_token}"}
                
                # Get all contact messages to find one with correct status
                response = self.session.get(f"{API_BASE}/contact-messages", headers=headers)
                if response.status_code == 200:
                    prospects = response.json()
                    
                    # Find a prospect with status 'paiement_50k' or 'en_consultation'
                    suitable_prospect = None
                    for prospect in prospects:
                        if prospect.get('status') in ['paiement_50k', 'en_consultation']:
                            suitable_prospect = prospect
                            break
                    
                    if suitable_prospect:
                        prospect_id = suitable_prospect['id']
                        
                        # Test conversion with MANAGER role - need to provide client_data
                        client_data = {
                            "country": suitable_prospect.get('country', 'France'),
                            "visa_type": suitable_prospect.get('visa_type', 'Work Permit'),
                            "first_payment_amount": 0
                        }
                        convert_response = self.session.post(
                            f"{API_BASE}/contact-messages/{prospect_id}/convert-to-client",
                            json=client_data,
                            headers=headers
                        )
                        
                        if convert_response.status_code == 200 or convert_response.status_code == 201:
                            data = convert_response.json()
                            self.log_result("Manager Prospect Conversion", True, f"Prospect converted to client successfully. Client ID: {data.get('client_id', 'N/A')}")
                            
                            # Verify prospect status changed to 'converti_client'
                            check_response = self.session.get(f"{API_BASE}/contact-messages", headers=headers)
                            if check_response.status_code == 200:
                                updated_prospects = check_response.json()
                                updated_prospect = next((p for p in updated_prospects if p['id'] == prospect_id), None)
                                if updated_prospect and updated_prospect.get('status') == 'converti_client':
                                    self.log_result("Prospect Status Update", True, "Prospect status correctly changed to 'converti_client'")
                                else:
                                    self.log_result("Prospect Status Update", False, f"Status not updated correctly: {updated_prospect.get('status') if updated_prospect else 'Not found'}")
                        else:
                            self.log_result("Manager Prospect Conversion", False, f"Status: {convert_response.status_code}", convert_response.text)
                    else:
                        self.log_result("Prospect Conversion Setup", False, "No suitable prospect found with status 'paiement_50k' or 'en_consultation'")
                else:
                    self.log_result("Get Prospects for Conversion", False, f"Status: {response.status_code}", response.text)
            except Exception as e:
                self.log_result("Prospect Conversion to Client", False, "Exception occurred", str(e))

        # Test with EMPLOYEE role
        if self.employee_token:
            try:
                headers = {"Authorization": f"Bearer {self.employee_token}"}
                
                # Get prospects assigned to this employee
                response = self.session.get(f"{API_BASE}/contact-messages", headers=headers)
                if response.status_code == 200:
                    prospects = response.json()
                    
                    # Find a suitable prospect
                    suitable_prospect = None
                    for prospect in prospects:
                        if prospect.get('status') in ['paiement_50k', 'en_consultation']:
                            suitable_prospect = prospect
                            break
                    
                    if suitable_prospect:
                        prospect_id = suitable_prospect['id']
                        
                        client_data = {
                            "country": suitable_prospect.get('country', 'France'),
                            "visa_type": suitable_prospect.get('visa_type', 'Work Permit'),
                            "first_payment_amount": 0
                        }
                        convert_response = self.session.post(
                            f"{API_BASE}/contact-messages/{prospect_id}/convert-to-client",
                            json=client_data,
                            headers=headers
                        )
                        
                        if convert_response.status_code == 200 or convert_response.status_code == 201:
                            data = convert_response.json()
                            self.log_result("Employee Prospect Conversion", True, f"Employee can convert prospects. Client ID: {data.get('client_id', 'N/A')}")
                        else:
                            self.log_result("Employee Prospect Conversion", False, f"Status: {convert_response.status_code}", convert_response.text)
                    else:
                        self.log_result("Employee Prospect Conversion", False, "No suitable prospect assigned to employee")
            except Exception as e:
                self.log_result("Employee Prospect Conversion", False, "Exception occurred", str(e))

    def test_client_reassignment(self):
        """Test Client Reassignment (HIGH PRIORITY)"""
        print("=== Testing Client Reassignment (HIGH PRIORITY) ===")
        
        if not self.manager_token:
            self.log_result("Client Reassignment", False, "No Manager token available")
            return

        headers = {"Authorization": f"Bearer {self.manager_token}"}
        
        try:
            # First, get list of clients
            clients_response = self.session.get(f"{API_BASE}/clients", headers=headers)
            if clients_response.status_code == 200:
                clients = clients_response.json()
                
                if clients:
                    client_id = clients[0]['id']
                    
                    # Get list of employees to reassign to
                    users_response = self.session.get(f"{API_BASE}/admin/users", headers=headers)
                    if users_response.status_code == 200:
                        users = users_response.json()
                        employees = [user for user in users if user.get('role') == 'EMPLOYEE']
                        
                        if employees:
                            new_employee_id = employees[0]['id']
                            
                            # Test PATCH /api/clients/{client_id}/reassign - new_employee_id is path parameter
                            reassign_response = self.session.patch(
                                f"{API_BASE}/clients/{client_id}/reassign",
                                params={"new_employee_id": new_employee_id},
                                headers=headers
                            )
                            
                            if reassign_response.status_code == 200:
                                data = reassign_response.json()
                                self.log_result("Client Reassignment", True, f"Client successfully reassigned to employee {new_employee_id}")
                                
                                # Verify the reassignment
                                verify_response = self.session.get(f"{API_BASE}/clients/{client_id}", headers=headers)
                                if verify_response.status_code == 200:
                                    updated_client = verify_response.json()
                                    if updated_client.get('assigned_employee_id') == new_employee_id:
                                        self.log_result("Client Reassignment Verification", True, "Client assignment updated correctly")
                                    else:
                                        self.log_result("Client Reassignment Verification", False, f"Assignment not updated: {updated_client.get('assigned_employee_id')} != {new_employee_id}")
                            else:
                                self.log_result("Client Reassignment", False, f"Status: {reassign_response.status_code}", reassign_response.text)
                        else:
                            self.log_result("Client Reassignment", False, "No employees found for reassignment")
                    else:
                        self.log_result("Client Reassignment", False, f"Could not get users list: {users_response.status_code}")
                else:
                    self.log_result("Client Reassignment", False, "No clients found for reassignment test")
            else:
                self.log_result("Client Reassignment", False, f"Could not get clients list: {clients_response.status_code}")
        except Exception as e:
            self.log_result("Client Reassignment", False, "Exception occurred", str(e))

    def run_all_tests(self):
        """Run all critical fixes tests"""
        print("🚀 ALORIA AGENCY - Critical Fixes Verification Test Suite")
        print("=" * 60)
        
        # Authenticate first
        self.authenticate_users()
        
        # Run high priority tests
        self.test_superadmin_apis()
        self.test_consultant_user_creation()
        self.test_prospect_conversion_to_client()
        self.test_client_reassignment()
        
        # Run medium priority tests
        self.test_visitor_creation()
        
        # Print summary
        print("\n" + "=" * 60)
        print("🎯 CRITICAL FIXES TEST SUMMARY")
        print("=" * 60)
        print(f"✅ PASSED: {self.results['passed']}")
        print(f"❌ FAILED: {self.results['failed']}")
        print(f"📊 SUCCESS RATE: {(self.results['passed'] / (self.results['passed'] + self.results['failed']) * 100):.1f}%")
        
        if self.results['errors']:
            print("\n🔍 FAILED TESTS DETAILS:")
            for error in self.results['errors']:
                print(f"   ❌ {error['test']}")
                if error['message']:
                    print(f"      Message: {error['message']}")
                if error['error']:
                    print(f"      Error: {error['error']}")
        
        return self.results['failed'] == 0

if __name__ == "__main__":
    tester = CriticalFixesTester()
    success = tester.run_all_tests()
    sys.exit(0 if success else 1)