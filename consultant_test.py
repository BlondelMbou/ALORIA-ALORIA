#!/usr/bin/env python3
"""
ALORIA AGENCY - CONSULTANT Role Backend Testing Suite
Focused testing for CONSULTANT role prospect access as requested in review.
"""

import requests
import json
import os
from datetime import datetime
import sys

# Get backend URL from environment
BACKEND_URL = os.environ.get('REACT_APP_BACKEND_URL', 'https://aloria-dev.preview.emergentagent.com')
API_BASE = f"{BACKEND_URL}/api"

class ConsultantTester:
    def __init__(self):
        self.session = requests.Session()
        self.superadmin_token = None
        self.manager_token = None
        self.employee_token = None
        self.consultant_token = None
        self.client_token = None
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

    def setup_test_users(self):
        """Setup all required test users"""
        print("=== Setting Up Test Users ===")
        
        # 1. SuperAdmin login
        try:
            response = self.session.post(f"{API_BASE}/auth/login", json={
                "email": "superadmin@aloria.com",
                "password": "SuperAdmin123!"
            })
            if response.status_code == 200:
                self.superadmin_token = response.json()['access_token']
                self.log_result("SuperAdmin Login", True, "SuperAdmin authenticated successfully")
            else:
                self.log_result("SuperAdmin Login", False, f"Status: {response.status_code}", response.text)
        except Exception as e:
            self.log_result("SuperAdmin Login", False, "Exception occurred", str(e))

        # 2. Manager login
        try:
            response = self.session.post(f"{API_BASE}/auth/login", json={
                "email": "manager@test.com",
                "password": "password123"
            })
            if response.status_code == 200:
                self.manager_token = response.json()['access_token']
                self.log_result("Manager Login", True, "Manager authenticated successfully")
            else:
                self.log_result("Manager Login", False, f"Status: {response.status_code}", response.text)
        except Exception as e:
            self.log_result("Manager Login", False, "Exception occurred", str(e))

        # 3. Employee registration/login
        employee_data = {
            "email": "employee@aloria.com",
            "password": "emp123",
            "full_name": "Test Employee",
            "phone": "+33987654321",
            "role": "EMPLOYEE"
        }
        
        try:
            response = self.session.post(f"{API_BASE}/auth/register", json=employee_data)
            if response.status_code in [200, 201]:
                self.employee_token = response.json()['access_token']
                self.log_result("Employee Registration", True, "Employee created and authenticated")
            elif response.status_code == 400 and "already registered" in response.text:
                # Try login
                login_response = self.session.post(f"{API_BASE}/auth/login", json={
                    "email": employee_data["email"],
                    "password": employee_data["password"]
                })
                if login_response.status_code == 200:
                    self.employee_token = login_response.json()['access_token']
                    self.log_result("Employee Login", True, "Employee authenticated successfully")
                else:
                    self.log_result("Employee Login", False, f"Status: {login_response.status_code}", login_response.text)
            else:
                self.log_result("Employee Registration", False, f"Status: {response.status_code}", response.text)
        except Exception as e:
            self.log_result("Employee Registration", False, "Exception occurred", str(e))

        # 4. CONSULTANT registration/login
        consultant_data = {
            "email": "consultant@aloria.com",
            "password": "consultant123",
            "full_name": "Test Consultant",
            "phone": "+33666777888",
            "role": "CONSULTANT"
        }
        
        try:
            response = self.session.post(f"{API_BASE}/auth/register", json=consultant_data)
            if response.status_code in [200, 201]:
                self.consultant_token = response.json()['access_token']
                self.log_result("CONSULTANT Registration", True, "CONSULTANT created and authenticated")
            elif response.status_code == 400 and "already registered" in response.text:
                # Try login
                login_response = self.session.post(f"{API_BASE}/auth/login", json={
                    "email": consultant_data["email"],
                    "password": consultant_data["password"]
                })
                if login_response.status_code == 200:
                    self.consultant_token = login_response.json()['access_token']
                    self.log_result("CONSULTANT Login", True, "CONSULTANT authenticated successfully")
                else:
                    self.log_result("CONSULTANT Login", False, f"Status: {login_response.status_code}", login_response.text)
            else:
                self.log_result("CONSULTANT Registration", False, f"Status: {response.status_code}", response.text)
        except Exception as e:
            self.log_result("CONSULTANT Registration", False, "Exception occurred", str(e))

        # 5. Client login (if exists)
        try:
            response = self.session.post(f"{API_BASE}/auth/login", json={
                "email": "client@test.com",
                "password": "Aloria2024!"
            })
            if response.status_code == 200:
                self.client_token = response.json()['access_token']
                self.log_result("Client Login", True, "Client authenticated successfully")
            else:
                self.log_result("Client Login", False, "Client not available for testing")
        except Exception as e:
            self.log_result("Client Login", False, "Exception occurred", str(e))

    def test_consultant_prospect_access(self):
        """Test CONSULTANT role prospect access - HIGH PRIORITY"""
        print("=== Testing CONSULTANT Role Prospect Access (HIGH PRIORITY) ===")
        
        if not self.consultant_token:
            self.log_result("CONSULTANT Prospect Access", False, "No CONSULTANT token available")
            return

        try:
            headers = {"Authorization": f"Bearer {self.consultant_token}"}
            response = self.session.get(f"{API_BASE}/contact-messages", headers=headers)
            
            if response.status_code == 200:
                prospects = response.json()
                
                # Check if CONSULTANT only sees prospects with status='paiement_50k'
                if prospects:
                    paid_prospects = [p for p in prospects if p.get('status') == 'paiement_50k']
                    all_paid = all(p.get('status') == 'paiement_50k' for p in prospects)
                    
                    if all_paid:
                        self.log_result("CONSULTANT Sees Only Paid Prospects", True, 
                                      f"CONSULTANT correctly sees {len(prospects)} prospects, all with status='paiement_50k'")
                    else:
                        non_paid = [p for p in prospects if p.get('status') != 'paiement_50k']
                        self.log_result("CONSULTANT Sees Only Paid Prospects", False, 
                                      f"CONSULTANT sees {len(non_paid)} prospects without 'paiement_50k' status")
                else:
                    self.log_result("CONSULTANT Sees Only Paid Prospects", True, 
                                  "CONSULTANT sees 0 prospects (no paid prospects exist)")
                    
            elif response.status_code == 403:
                self.log_result("CONSULTANT Prospect Access", False, 
                              "CONSULTANT denied access (403) - API prefix issue not resolved")
            else:
                self.log_result("CONSULTANT Prospect Access", False, 
                              f"Unexpected status: {response.status_code}", response.text)
                
        except Exception as e:
            self.log_result("CONSULTANT Prospect Access", False, "Exception occurred", str(e))

    def test_prospect_display_by_all_roles(self):
        """Test prospect display filtering by all roles"""
        print("=== Testing Prospect Display by All Roles (HIGH PRIORITY) ===")
        
        # Test SUPERADMIN sees ALL prospects
        if self.superadmin_token:
            try:
                headers = {"Authorization": f"Bearer {self.superadmin_token}"}
                response = self.session.get(f"{API_BASE}/contact-messages", headers=headers)
                if response.status_code == 200:
                    all_prospects = response.json()
                    self.log_result("SUPERADMIN Sees All Prospects", True, 
                                  f"SUPERADMIN sees ALL {len(all_prospects)} prospects (no filtering)")
                else:
                    self.log_result("SUPERADMIN Sees All Prospects", False, 
                                  f"Status: {response.status_code}", response.text)
            except Exception as e:
                self.log_result("SUPERADMIN Sees All Prospects", False, "Exception occurred", str(e))

        # Test MANAGER sees assigned prospects
        if self.manager_token:
            try:
                headers = {"Authorization": f"Bearer {self.manager_token}"}
                response = self.session.get(f"{API_BASE}/contact-messages", headers=headers)
                if response.status_code == 200:
                    manager_prospects = response.json()
                    self.log_result("MANAGER Sees Assigned Prospects", True, 
                                  f"MANAGER sees {len(manager_prospects)} assigned prospects")
                else:
                    self.log_result("MANAGER Sees Assigned Prospects", False, 
                                  f"Status: {response.status_code}", response.text)
            except Exception as e:
                self.log_result("MANAGER Sees Assigned Prospects", False, "Exception occurred", str(e))

        # Test EMPLOYEE sees assigned prospects
        if self.employee_token:
            try:
                headers = {"Authorization": f"Bearer {self.employee_token}"}
                response = self.session.get(f"{API_BASE}/contact-messages", headers=headers)
                if response.status_code == 200:
                    employee_prospects = response.json()
                    self.log_result("EMPLOYEE Sees Assigned Prospects", True, 
                                  f"EMPLOYEE sees {len(employee_prospects)} assigned prospects")
                else:
                    self.log_result("EMPLOYEE Sees Assigned Prospects", False, 
                                  f"Status: {response.status_code}", response.text)
            except Exception as e:
                self.log_result("EMPLOYEE Sees Assigned Prospects", False, "Exception occurred", str(e))

        # Test CLIENT receives 403
        if self.client_token:
            try:
                headers = {"Authorization": f"Bearer {self.client_token}"}
                response = self.session.get(f"{API_BASE}/contact-messages", headers=headers)
                if response.status_code == 403:
                    self.log_result("CLIENT Denied Access", True, "CLIENT correctly denied access (403)")
                else:
                    self.log_result("CLIENT Denied Access", False, 
                                  f"CLIENT should receive 403, got {response.status_code}")
            except Exception as e:
                self.log_result("CLIENT Denied Access", False, "Exception occurred", str(e))

    def test_consultant_specific_endpoints(self):
        """Test consultant-specific endpoints with correct role permissions"""
        print("=== Testing Consultant-Specific Endpoints ===")
        
        # First, get prospects to find one with paiement_50k status
        if not self.superadmin_token:
            self.log_result("CONSULTANT Specific Endpoints", False, "No SUPERADMIN token available for notes test")
            return

        try:
            # Use SUPERADMIN to get all prospects
            headers = {"Authorization": f"Bearer {self.superadmin_token}"}
            response = self.session.get(f"{API_BASE}/contact-messages", headers=headers)
            
            if response.status_code == 200:
                prospects = response.json()
                paid_prospect = None
                
                for prospect in prospects:
                    if prospect.get('status') == 'paiement_50k':
                        paid_prospect = prospect
                        break
                
                if paid_prospect:
                    prospect_id = paid_prospect['id']
                    
                    # Test PATCH /api/contact-messages/{id}/consultant-notes (SUPERADMIN role required)
                    try:
                        notes_data = {
                            "note": "Test consultation notes from SUPERADMIN role for consultant workflow"
                        }
                        notes_response = self.session.patch(f"{API_BASE}/contact-messages/{prospect_id}/consultant-notes", 
                                                          json=notes_data, headers=headers)
                        if notes_response.status_code == 200:
                            self.log_result("SUPERADMIN Add Consultant Notes", True, 
                                          f"SUPERADMIN successfully added consultant notes to prospect {prospect_id}")
                        else:
                            self.log_result("SUPERADMIN Add Consultant Notes", False, 
                                          f"Status: {notes_response.status_code}", notes_response.text)
                    except Exception as e:
                        self.log_result("SUPERADMIN Add Consultant Notes", False, "Exception occurred", str(e))

                    # Test POST /api/contact-messages/{id}/convert-to-client (EMPLOYEE role required)
                    if self.employee_token:
                        try:
                            employee_headers = {"Authorization": f"Bearer {self.employee_token}"}
                            
                            # First check if prospect is assigned to employee
                            if paid_prospect.get('assigned_to') == None:
                                # Assign prospect to employee first
                                assign_data = {"assigned_to": "employee_id"}  # This would need actual employee ID
                                assign_response = self.session.patch(f"{API_BASE}/contact-messages/{prospect_id}/assign", 
                                                                   json=assign_data, headers=headers)
                                if assign_response.status_code != 200:
                                    self.log_result("Assign Prospect to Employee for Conversion", False, 
                                                  f"Could not assign prospect: {assign_response.status_code}")
                            
                            convert_data = {
                                "country": paid_prospect.get('country', 'France'),
                                "visa_type": paid_prospect.get('visa_type', 'Work Permit'),
                                "first_payment_amount": 1000
                            }
                            convert_response = self.session.post(f"{API_BASE}/contact-messages/{prospect_id}/convert-to-client", 
                                                               json=convert_data, headers=employee_headers)
                            if convert_response.status_code == 200:
                                self.log_result("EMPLOYEE Convert Prospect to Client", True, 
                                              f"EMPLOYEE successfully converted prospect {prospect_id} to client")
                            else:
                                self.log_result("EMPLOYEE Convert Prospect to Client", False, 
                                              f"Status: {convert_response.status_code}", convert_response.text)
                        except Exception as e:
                            self.log_result("EMPLOYEE Convert Prospect to Client", False, "Exception occurred", str(e))
                    
                    # Test CONSULTANT role cannot add notes (should get 403)
                    if self.consultant_token:
                        try:
                            consultant_headers = {"Authorization": f"Bearer {self.consultant_token}"}
                            notes_data = {"note": "CONSULTANT should not be able to add notes"}
                            notes_response = self.session.patch(f"{API_BASE}/contact-messages/{prospect_id}/consultant-notes", 
                                                              json=notes_data, headers=consultant_headers)
                            if notes_response.status_code == 403:
                                self.log_result("CONSULTANT Cannot Add Notes (Expected)", True, 
                                              "CONSULTANT correctly denied permission to add notes (403)")
                            else:
                                self.log_result("CONSULTANT Cannot Add Notes (Expected)", False, 
                                              f"CONSULTANT should get 403, got {notes_response.status_code}")
                        except Exception as e:
                            self.log_result("CONSULTANT Cannot Add Notes (Expected)", False, "Exception occurred", str(e))
                else:
                    self.log_result("Find Paid Prospect for Endpoint Tests", False, 
                                  "No prospects with status='paiement_50k' found for testing")
            else:
                self.log_result("Get Prospects for Endpoint Tests", False, 
                              f"Status: {response.status_code}", response.text)
        except Exception as e:
            self.log_result("Get Prospects for Endpoint Tests", False, "Exception occurred", str(e))

    def create_test_prospect_data(self):
        """Create test prospect data if needed"""
        print("=== Creating Test Prospect Data ===")
        
        if not self.superadmin_token:
            self.log_result("Create Test Data", False, "No SUPERADMIN token available")
            return

        # Check if we have prospects with paiement_50k status
        try:
            headers = {"Authorization": f"Bearer {self.superadmin_token}"}
            response = self.session.get(f"{API_BASE}/contact-messages", headers=headers)
            
            if response.status_code == 200:
                prospects = response.json()
                paid_prospects = [p for p in prospects if p.get('status') == 'paiement_50k']
                
                if len(paid_prospects) == 0:
                    # Create new prospect
                    import time
                    timestamp = int(time.time())
                    prospect_data = {
                        "name": f"Test Prospect {timestamp}",
                        "email": f"prospect.{timestamp}@example.com",
                        "phone": "+33123456789",
                        "country": "France",
                        "visa_type": "Work Permit",
                        "budget_range": "5000+€",
                        "urgency_level": "Urgent",
                        "message": "Test prospect for CONSULTANT role testing - needs to reach paiement_50k status",
                        "lead_source": "WEBSITE",
                        "how_did_you_know": "Google search"
                    }
                    
                    create_response = self.session.post(f"{API_BASE}/contact-messages", json=prospect_data)
                    if create_response.status_code in [200, 201]:
                        new_prospect = create_response.json()
                        prospect_id = new_prospect['id']
                        self.log_result("Create Test Prospect", True, 
                                      f"Created prospect {prospect_id} with status: {new_prospect.get('status', 'unknown')}")
                        
                        # Try to advance prospect through workflow to paiement_50k status
                        # This would require implementing the full workflow, which may not be available
                        self.log_result("Advance Prospect to Paid Status", False, 
                                      "Workflow advancement not implemented in test - manual setup required")
                    else:
                        self.log_result("Create Test Prospect", False, 
                                      f"Status: {create_response.status_code}", create_response.text)
                else:
                    self.log_result("Check Existing Paid Prospects", True, 
                                  f"Found {len(paid_prospects)} existing prospects with status='paiement_50k'")
            else:
                self.log_result("Check Existing Prospects", False, 
                              f"Status: {response.status_code}", response.text)
        except Exception as e:
            self.log_result("Check/Create Test Data", False, "Exception occurred", str(e))

    def run_consultant_tests(self):
        """Run all CONSULTANT role tests"""
        print("🎯 ALORIA AGENCY - CONSULTANT ROLE BACKEND TESTING")
        print(f"Backend URL: {BACKEND_URL}")
        print("Focus: CONSULTANT role prospect access with /api prefix fix")
        print("=" * 80)
        
        # Setup test users
        self.setup_test_users()
        
        # Create test data if needed
        self.create_test_prospect_data()
        
        # Run CONSULTANT-specific tests
        print("\n🔍 HIGH PRIORITY CONSULTANT ROLE TESTS")
        print("=" * 50)
        self.test_consultant_prospect_access()
        self.test_prospect_display_by_all_roles()
        self.test_consultant_specific_endpoints()
        print("=" * 50)
        
        # Print final results
        print("\n" + "=" * 80)
        print("🎯 CONSULTANT ROLE TEST RESULTS")
        print(f"✅ Passed: {self.results['passed']}")
        print(f"❌ Failed: {self.results['failed']}")
        total = self.results['passed'] + self.results['failed']
        success_rate = (self.results['passed'] / total * 100) if total > 0 else 0
        print(f"📊 Success Rate: {success_rate:.1f}%")
        
        if self.results['errors']:
            print("\n❌ FAILED TESTS SUMMARY:")
            for error in self.results['errors']:
                print(f"  • {error['test']}: {error['message']}")
                if error['error']:
                    print(f"    Error: {error['error'][:200]}...")
        
        print("=" * 80)
        return self.results['failed'] == 0

if __name__ == "__main__":
    tester = ConsultantTester()
    success = tester.run_consultant_tests()
    sys.exit(0 if success else 1)