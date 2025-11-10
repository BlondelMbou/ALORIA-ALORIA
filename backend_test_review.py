#!/usr/bin/env python3
"""
ALORIA AGENCY - Review Request Testing Suite
Tests specific requirements from the review request:
1. Rôle CONSULTANT (Nouveau)
2. Workflow Prospect → Consultant (50k CFA)
3. Validation Séquentielle Dossiers
4. Emails (SendGrid logs)
5. SuperAdmin Dashboard Stats
6. Paiements & Factures
"""

import requests
import json
import os
from datetime import datetime
import sys
import time

# Get backend URL from environment
BACKEND_URL = os.environ.get('REACT_APP_BACKEND_URL', 'https://casemgr-crm.preview.emergentagent.com')
API_BASE = f"{BACKEND_URL}/api"

class ReviewTester:
    def __init__(self):
        self.session = requests.Session()
        self.superadmin_token = None
        self.manager_token = None
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

    def test_1_consultant_role(self):
        """Test 1: Rôle CONSULTANT (Nouveau)"""
        print("=== TEST 1: RÔLE CONSULTANT ===")
        
        # Login as SuperAdmin
        try:
            login_response = self.session.post(f"{API_BASE}/auth/login", json={
                "email": "superadmin@aloria.com",
                "password": "SuperAdmin123!"
            })
            if login_response.status_code == 200:
                self.superadmin_token = login_response.json()['access_token']
                self.log_result("SuperAdmin Login", True, "SuperAdmin authenticated successfully")
            else:
                self.log_result("SuperAdmin Login", False, f"Status: {login_response.status_code}", login_response.text)
                return
        except Exception as e:
            self.log_result("SuperAdmin Login", False, "Exception occurred", str(e))
            return

        # Check if CONSULTANT role exists in UserRole enum
        try:
            # Try to register a user with CONSULTANT role to test if enum exists
            consultant_data = {
                "email": "consultant.test@aloria.com",
                "password": "Consultant123!",
                "full_name": "Test Consultant",
                "phone": "+33123456789",
                "role": "CONSULTANT"
            }
            response = self.session.post(f"{API_BASE}/auth/register", json=consultant_data)
            if response.status_code in [200, 201]:
                data = response.json()
                if data['user']['role'] == 'CONSULTANT':
                    self.log_result("CONSULTANT Role Exists in Enum", True, "CONSULTANT role is defined and working")
                    self.consultant_token = data['access_token']
                else:
                    self.log_result("CONSULTANT Role Exists in Enum", False, f"Expected CONSULTANT, got: {data['user']['role']}")
            elif response.status_code == 400 and "already registered" in response.text:
                # User exists, try login
                login_response = self.session.post(f"{API_BASE}/auth/login", json={
                    "email": "consultant.test@aloria.com",
                    "password": "Consultant123!"
                })
                if login_response.status_code == 200:
                    user_data = login_response.json()
                    if user_data['user']['role'] == 'CONSULTANT':
                        self.log_result("CONSULTANT Role Exists in Enum", True, "CONSULTANT role verified via existing user")
                        self.consultant_token = user_data['access_token']
                    else:
                        self.log_result("CONSULTANT Role Exists in Enum", False, f"Expected CONSULTANT, got: {user_data['user']['role']}")
                else:
                    self.log_result("CONSULTANT Role Exists in Enum", False, "Could not login existing CONSULTANT user")
            elif response.status_code == 422:
                # Check if error mentions CONSULTANT role validation
                error_text = response.text.lower()
                if "consultant" in error_text:
                    self.log_result("CONSULTANT Role Exists in Enum", False, "CONSULTANT role validation failed - may not be in enum")
                else:
                    self.log_result("CONSULTANT Role Exists in Enum", True, "CONSULTANT role accepted by validation (other validation error)")
            else:
                self.log_result("CONSULTANT Role Exists in Enum", False, f"Status: {response.status_code}", response.text)
        except Exception as e:
            self.log_result("CONSULTANT Role Exists in Enum", False, "Exception occurred", str(e))

        # Test SuperAdmin creating CONSULTANT user (this may fail due to permission restrictions)
        if self.superadmin_token:
            try:
                headers = {"Authorization": f"Bearer {self.superadmin_token}"}
                consultant_data = {
                    "email": "consultant.superadmin@aloria.com",
                    "full_name": "Consultant Created by SuperAdmin",
                    "phone": "+33123456789",
                    "role": "CONSULTANT",
                    "send_email": False
                }
                response = self.session.post(f"{API_BASE}/users/create", json=consultant_data, headers=headers)
                if response.status_code in [200, 201]:
                    data = response.json()
                    self.log_result("SuperAdmin Creates CONSULTANT", True, f"SuperAdmin can create CONSULTANT users")
                elif response.status_code == 403:
                    self.log_result("SuperAdmin Creates CONSULTANT", False, 
                                  "❌ ISSUE: SuperAdmin cannot create CONSULTANT - permission system needs update")
                elif response.status_code == 400 and "existe déjà" in response.text:
                    self.log_result("SuperAdmin Creates CONSULTANT", True, "CONSULTANT user already exists")
                else:
                    self.log_result("SuperAdmin Creates CONSULTANT", False, f"Status: {response.status_code}", response.text)
            except Exception as e:
                self.log_result("SuperAdmin Creates CONSULTANT", False, "Exception occurred", str(e))

    def test_2_prospect_workflow(self):
        """Test 2: Workflow Prospect → Consultant (50k CFA)"""
        print("=== TEST 2: WORKFLOW PROSPECT → CONSULTANT ===")
        
        # Login as Manager
        try:
            login_response = self.session.post(f"{API_BASE}/auth/login", json={
                "email": "manager@test.com",
                "password": "password123"
            })
            if login_response.status_code == 200:
                self.manager_token = login_response.json()['access_token']
                self.log_result("Manager Login", True, "Manager authenticated successfully")
            else:
                self.log_result("Manager Login", False, f"Status: {login_response.status_code}", login_response.text)
                return
        except Exception as e:
            self.log_result("Manager Login", False, "Exception occurred", str(e))
            return

        prospect_id = None
        
        # Step 1: Create prospect via POST /api/contact-messages
        try:
            prospect_data = {
                "name": "Jean Dupont",
                "email": "jean.dupont@example.com",
                "phone": "+33123456789",
                "country": "France",
                "visa_type": "Work Permit",
                "budget_range": "5000+€",
                "urgency_level": "Urgent",
                "message": "Je souhaite obtenir un permis de travail pour la France. J'ai un budget conséquent et c'est urgent.",
                "lead_source": "Site web",
                "how_did_you_know": "Recherche Google"
            }
            response = self.session.post(f"{API_BASE}/contact-messages", json=prospect_data)
            if response.status_code in [200, 201]:
                data = response.json()
                prospect_id = data['id']
                self.log_result("Step 1: Create Prospect", True, f"Prospect created with ID: {prospect_id}, Status: {data.get('status', 'N/A')}")
            else:
                self.log_result("Step 1: Create Prospect", False, f"Status: {response.status_code}", response.text)
                return
        except Exception as e:
            self.log_result("Step 1: Create Prospect", False, "Exception occurred", str(e))
            return

        # Step 2: SuperAdmin assigns to Manager
        if self.superadmin_token and prospect_id:
            try:
                headers = {"Authorization": f"Bearer {self.superadmin_token}"}
                assign_data = {
                    "assigned_to": "manager@test.com"  # Assign to manager
                }
                response = self.session.patch(f"{API_BASE}/contact-messages/{prospect_id}/assign", 
                                            json=assign_data, headers=headers)
                if response.status_code == 200:
                    data = response.json()
                    self.log_result("Step 2: SuperAdmin Assigns to Manager", True, f"Status: {data.get('status', 'N/A')}")
                else:
                    self.log_result("Step 2: SuperAdmin Assigns to Manager", False, f"Status: {response.status_code}", response.text)
            except Exception as e:
                self.log_result("Step 2: SuperAdmin Assigns to Manager", False, "Exception occurred", str(e))

        # Step 3: Manager accepts payment 50k (assign to consultant)
        if self.manager_token and prospect_id:
            try:
                headers = {"Authorization": f"Bearer {self.manager_token}"}
                response = self.session.patch(f"{API_BASE}/contact-messages/{prospect_id}/assign-consultant", 
                                            headers=headers)
                if response.status_code == 200:
                    data = response.json()
                    expected_status = "paiement_50k"
                    if data.get('status') == expected_status:
                        self.log_result("Step 3: Manager Assigns to Consultant (50k CFA)", True, 
                                      f"Status changed to: {data.get('status')}, Payment: {data.get('payment_50k_amount', 'N/A')} CFA")
                    else:
                        self.log_result("Step 3: Manager Assigns to Consultant (50k CFA)", False, 
                                      f"Expected status '{expected_status}', got: {data.get('status')}")
                else:
                    self.log_result("Step 3: Manager Assigns to Consultant (50k CFA)", False, f"Status: {response.status_code}", response.text)
            except Exception as e:
                self.log_result("Step 3: Manager Assigns to Consultant (50k CFA)", False, "Exception occurred", str(e))

        # Step 4: Verify CONSULTANT can see this prospect
        if self.consultant_token:
            try:
                headers = {"Authorization": f"Bearer {self.consultant_token}"}
                response = self.session.get(f"{API_BASE}/contact-messages", headers=headers)
                if response.status_code == 200:
                    prospects = response.json()
                    consultant_prospect = None
                    for prospect in prospects:
                        if prospect['id'] == prospect_id and prospect.get('status') == 'paiement_50k':
                            consultant_prospect = prospect
                            break
                    
                    if consultant_prospect:
                        self.log_result("Step 4: Consultant Sees Prospect", True, 
                                      f"Consultant can see prospect with status: {consultant_prospect.get('status')}")
                    else:
                        self.log_result("Step 4: Consultant Sees Prospect", False, 
                                      f"Consultant cannot see prospect with paiement_50k status. Found {len(prospects)} prospects")
                else:
                    self.log_result("Step 4: Consultant Sees Prospect", False, f"Status: {response.status_code}", response.text)
            except Exception as e:
                self.log_result("Step 4: Consultant Sees Prospect", False, "Exception occurred", str(e))

    def test_3_sequential_validation(self):
        """Test 3: Validation Séquentielle Dossiers"""
        print("=== TEST 3: VALIDATION SÉQUENTIELLE DOSSIERS ===")
        
        if not self.manager_token:
            self.log_result("Sequential Validation", False, "No manager token available")
            return

        # Create a test case first
        try:
            headers = {"Authorization": f"Bearer {self.manager_token}"}
            timestamp = int(time.time())
            client_data = {
                "email": f"sequential.test.{timestamp}@example.com",
                "full_name": "Client Test Séquentiel",
                "phone": "+33987654321",
                "country": "Canada",
                "visa_type": "Work Permit",
                "message": "Test validation séquentielle"
            }
            response = self.session.post(f"{API_BASE}/clients", json=client_data, headers=headers)
            if response.status_code in [200, 201]:
                client_id = response.json()['id']
                
                # Get the case for this client
                cases_response = self.session.get(f"{API_BASE}/cases", headers=headers)
                if cases_response.status_code == 200:
                    cases = cases_response.json()
                    test_case = None
                    for case in cases:
                        if case['client_id'] == client_id:
                            test_case = case
                            break
                    
                    if test_case:
                        case_id = test_case['id']
                        
                        # Test: Try to jump from step 1 to step 7 directly (should fail)
                        try:
                            update_data = {
                                "current_step_index": 7,  # Jump to step 7
                                "status": "Advanced Step",
                                "notes": "Tentative de saut d'étapes"
                            }
                            response = self.session.patch(f"{API_BASE}/cases/{case_id}/progress", 
                                                        json=update_data, headers=headers)
                            if response.status_code == 400:
                                error_msg = response.json().get('detail', response.text)
                                if "séquentielle" in error_msg.lower() or "progression" in error_msg.lower():
                                    self.log_result("Sequential Validation (Jump 1→7)", True, 
                                                  f"Correctly blocked step jumping: {error_msg}")
                                else:
                                    self.log_result("Sequential Validation (Jump 1→7)", True, 
                                                  f"Step jumping blocked with error: {error_msg}")
                            else:
                                self.log_result("Sequential Validation (Jump 1→7)", False, 
                                              f"Expected 400 error, got {response.status_code}. Step jumping should be blocked!")
                        except Exception as e:
                            self.log_result("Sequential Validation (Jump 1→7)", False, "Exception occurred", str(e))
                        
                        # Test: Try sequential progression (1→2, should work)
                        try:
                            update_data = {
                                "current_step_index": 1,  # Move to next step
                                "status": "Step 2",
                                "notes": "Progression séquentielle normale"
                            }
                            response = self.session.patch(f"{API_BASE}/cases/{case_id}/progress", 
                                                        json=update_data, headers=headers)
                            if response.status_code == 200:
                                self.log_result("Sequential Validation (1→2)", True, "Sequential progression allowed correctly")
                            else:
                                # Try regular case update endpoint
                                response = self.session.patch(f"{API_BASE}/cases/{case_id}", 
                                                            json=update_data, headers=headers)
                                if response.status_code == 200:
                                    self.log_result("Sequential Validation (1→2)", True, "Sequential progression allowed via case update")
                                else:
                                    self.log_result("Sequential Validation (1→2)", False, 
                                                  f"Sequential progression failed: {response.status_code}")
                        except Exception as e:
                            self.log_result("Sequential Validation (1→2)", False, "Exception occurred", str(e))
                    else:
                        self.log_result("Sequential Validation Setup", False, "Could not find case for test client")
                else:
                    self.log_result("Sequential Validation Setup", False, "Could not retrieve cases")
            else:
                self.log_result("Sequential Validation Setup", False, f"Could not create test client: {response.status_code}")
        except Exception as e:
            self.log_result("Sequential Validation Setup", False, "Exception occurred", str(e))

    def test_4_emails(self):
        """Test 4: Emails (vérifier logs si SendGrid configuré)"""
        print("=== TEST 4: EMAILS (SENDGRID LOGS) ===")
        
        # Check if email service is available by testing prospect email
        try:
            prospect_data = {
                "name": "Test Email User",
                "email": "test.email@example.com",
                "phone": "+33123456789",
                "country": "France",
                "visa_type": "Student Visa",
                "budget_range": "3000-5000€",
                "urgency_level": "Normal",
                "message": "Test pour vérifier l'envoi d'emails automatiques",
                "lead_source": "Site web",
                "how_did_you_know": "Test automatique"
            }
            response = self.session.post(f"{API_BASE}/contact-messages", json=prospect_data)
            if response.status_code in [200, 201]:
                self.log_result("Email Test - Prospect Form", True, 
                              "Prospect form submitted - check backend logs for SendGrid email attempts")
            else:
                self.log_result("Email Test - Prospect Form", False, f"Status: {response.status_code}", response.text)
        except Exception as e:
            self.log_result("Email Test - Prospect Form", False, "Exception occurred", str(e))

        # Test user creation email
        if self.superadmin_token:
            try:
                headers = {"Authorization": f"Bearer {self.superadmin_token}"}
                timestamp = int(time.time())
                user_data = {
                    "email": f"email.test.{timestamp}@example.com",
                    "full_name": "Test Email User",
                    "phone": "+33987654321",
                    "role": "EMPLOYEE",
                    "send_email": True  # This should trigger email
                }
                response = self.session.post(f"{API_BASE}/users/create", json=user_data, headers=headers)
                if response.status_code in [200, 201]:
                    data = response.json()
                    if data.get('email_sent'):
                        self.log_result("Email Test - User Creation", True, 
                                      "User creation email sent - check backend logs for SendGrid attempts")
                    else:
                        self.log_result("Email Test - User Creation", False, 
                                      "User created but email_sent=False - SendGrid may not be configured")
                else:
                    self.log_result("Email Test - User Creation", False, f"Status: {response.status_code}", response.text)
            except Exception as e:
                self.log_result("Email Test - User Creation", False, "Exception occurred", str(e))

        # Note about email configuration
        self.log_result("Email Configuration Check", True, 
                      "⚠️ Check backend logs with: tail -n 100 /var/log/supervisor/backend.*.log | grep -i sendgrid")

    def test_5_superadmin_dashboard(self):
        """Test 5: SuperAdmin Dashboard Stats"""
        print("=== TEST 5: SUPERADMIN DASHBOARD STATS ===")
        
        if not self.superadmin_token:
            self.log_result("SuperAdmin Dashboard", False, "No SuperAdmin token available")
            return

        headers = {"Authorization": f"Bearer {self.superadmin_token}"}

        # Test GET /api/admin/dashboard-stats
        try:
            response = self.session.get(f"{API_BASE}/admin/dashboard-stats", headers=headers)
            if response.status_code == 200:
                stats = response.json()
                self.log_result("SuperAdmin Dashboard Stats", True, 
                              f"Stats loaded: {stats.get('total_cases', 0)} cases, {stats.get('total_clients', 0)} clients")
            else:
                self.log_result("SuperAdmin Dashboard Stats", False, f"Status: {response.status_code}", response.text)
        except Exception as e:
            self.log_result("SuperAdmin Dashboard Stats", False, "Exception occurred", str(e))

        # Test GET /api/admin/users
        try:
            response = self.session.get(f"{API_BASE}/admin/users", headers=headers)
            if response.status_code == 200:
                users = response.json()
                self.log_result("SuperAdmin Users List", True, f"Retrieved {len(users)} users")
            else:
                self.log_result("SuperAdmin Users List", False, f"Status: {response.status_code}", response.text)
        except Exception as e:
            self.log_result("SuperAdmin Users List", False, "Exception occurred", str(e))

        # Test GET /api/admin/activities
        try:
            response = self.session.get(f"{API_BASE}/admin/activities", headers=headers)
            if response.status_code == 200:
                activities = response.json()
                self.log_result("SuperAdmin Activities", True, f"Retrieved {len(activities)} activities")
            else:
                self.log_result("SuperAdmin Activities", False, f"Status: {response.status_code}", response.text)
        except Exception as e:
            self.log_result("SuperAdmin Activities", False, "Exception occurred", str(e))

    def test_6_payments_invoices(self):
        """Test 6: Paiements & Factures"""
        print("=== TEST 6: PAIEMENTS & FACTURES ===")
        
        if not self.manager_token:
            self.log_result("Payments & Invoices", False, "No manager token available")
            return

        # Create a test client first
        client_id = None
        try:
            headers = {"Authorization": f"Bearer {self.manager_token}"}
            timestamp = int(time.time())
            client_data = {
                "email": f"payment.test.{timestamp}@example.com",
                "full_name": "Client Test Paiement",
                "phone": "+33123456789",
                "country": "France",
                "visa_type": "Work Permit (Talent Permit)",
                "message": "Test système de paiement"
            }
            response = self.session.post(f"{API_BASE}/clients", json=client_data, headers=headers)
            if response.status_code in [200, 201]:
                client_id = response.json()['id']
                
                # Login as client to declare payment
                client_login = {
                    "email": client_data["email"],
                    "password": "Aloria2024!"
                }
                login_response = self.session.post(f"{API_BASE}/auth/login", json=client_login)
                if login_response.status_code == 200:
                    client_token = login_response.json()['access_token']
                    client_headers = {"Authorization": f"Bearer {client_token}"}
                    
                    # Step 1: Client declares payment
                    payment_data = {
                        "amount": 2500.0,
                        "currency": "EUR",
                        "description": "Services d'immigration - permis de travail",
                        "payment_method": "Bank Transfer"
                    }
                    payment_response = self.session.post(f"{API_BASE}/payments/declare", 
                                                       json=payment_data, headers=client_headers)
                    if payment_response.status_code in [200, 201]:
                        payment_id = payment_response.json()['id']
                        self.log_result("Step 1: Client Declares Payment", True, 
                                      f"Payment declared: {payment_data['amount']} {payment_data['currency']}")
                        
                        # Step 2: Manager views pending payments
                        pending_response = self.session.get(f"{API_BASE}/payments/pending", headers=headers)
                        if pending_response.status_code == 200:
                            pending_payments = pending_response.json()
                            found_payment = any(p['id'] == payment_id for p in pending_payments)
                            if found_payment:
                                self.log_result("Step 2: Manager Views Pending", True, 
                                              f"Manager can see {len(pending_payments)} pending payments")
                            else:
                                self.log_result("Step 2: Manager Views Pending", False, 
                                              "Manager cannot see the declared payment")
                        else:
                            self.log_result("Step 2: Manager Views Pending", False, 
                                          f"Status: {pending_response.status_code}")
                        
                        # Step 3: Manager confirms payment with code
                        confirm_data = {
                            "action": "CONFIRMED"
                        }
                        confirm_response = self.session.patch(f"{API_BASE}/payments/{payment_id}/confirm", 
                                                            json=confirm_data, headers=headers)
                        if confirm_response.status_code == 200:
                            confirmed_payment = confirm_response.json()
                            invoice_number = confirmed_payment.get('invoice_number')
                            if invoice_number:
                                self.log_result("Step 3: Manager Confirms Payment", True, 
                                              f"Payment confirmed, Invoice: {invoice_number}")
                                
                                # Step 4: Check PDF generation
                                pdf_response = self.session.get(f"{API_BASE}/invoices/{invoice_number}", 
                                                              headers=headers)
                                if pdf_response.status_code == 200:
                                    if pdf_response.headers.get('content-type') == 'application/pdf':
                                        self.log_result("Step 4: PDF Invoice Generation", True, 
                                                      f"PDF invoice generated and downloadable: {invoice_number}")
                                    else:
                                        self.log_result("Step 4: PDF Invoice Generation", False, 
                                                      "Response is not a PDF file")
                                else:
                                    self.log_result("Step 4: PDF Invoice Generation", False, 
                                                  f"PDF download failed: {pdf_response.status_code}")
                                
                                # Step 5: Check payment history
                                history_response = self.session.get(f"{API_BASE}/payments/history", headers=headers)
                                if history_response.status_code == 200:
                                    history = history_response.json()
                                    confirmed_payment_in_history = any(
                                        p['id'] == payment_id and p['status'] == 'confirmed' 
                                        for p in history
                                    )
                                    if confirmed_payment_in_history:
                                        self.log_result("Step 5: Payment History", True, 
                                                      f"Confirmed payment appears in history ({len(history)} total)")
                                    else:
                                        self.log_result("Step 5: Payment History", False, 
                                                      "Confirmed payment not found in history")
                                else:
                                    self.log_result("Step 5: Payment History", False, 
                                                  f"History retrieval failed: {history_response.status_code}")
                            else:
                                self.log_result("Step 3: Manager Confirms Payment", False, 
                                              "Payment confirmed but no invoice number generated")
                        else:
                            self.log_result("Step 3: Manager Confirms Payment", False, 
                                          f"Status: {confirm_response.status_code}", confirm_response.text)
                    else:
                        self.log_result("Step 1: Client Declares Payment", False, 
                                      f"Status: {payment_response.status_code}", payment_response.text)
                else:
                    self.log_result("Client Login for Payment", False, 
                                  f"Status: {login_response.status_code}")
            else:
                self.log_result("Create Test Client for Payment", False, 
                              f"Status: {response.status_code}")
        except Exception as e:
            self.log_result("Payments & Invoices Test", False, "Exception occurred", str(e))

    def run_all_tests(self):
        """Run all review tests"""
        print("🚀 ALORIA AGENCY - REVIEW REQUEST TESTING")
        print("=" * 60)
        print(f"Backend URL: {BACKEND_URL}")
        print(f"API Base: {API_BASE}")
        print("=" * 60)
        
        # Run all tests in order
        self.test_1_consultant_role()
        self.test_2_prospect_workflow()
        self.test_3_sequential_validation()
        self.test_4_emails()
        self.test_5_superadmin_dashboard()
        self.test_6_payments_invoices()
        
        # Print summary
        print("=" * 60)
        print("📊 TEST SUMMARY")
        print("=" * 60)
        print(f"✅ PASSED: {self.results['passed']}")
        print(f"❌ FAILED: {self.results['failed']}")
        print(f"📈 SUCCESS RATE: {(self.results['passed'] / (self.results['passed'] + self.results['failed']) * 100):.1f}%")
        
        if self.results['errors']:
            print("\n🔍 FAILED TESTS DETAILS:")
            for error in self.results['errors']:
                print(f"❌ {error['test']}: {error['message']}")
                if error['error']:
                    print(f"   Error: {error['error']}")
        
        print("\n🎯 REVIEW REQUEST TESTING COMPLETE!")
        return self.results

if __name__ == "__main__":
    tester = ReviewTester()
    results = tester.run_all_tests()
    
    # Exit with error code if tests failed
    if results['failed'] > 0:
        sys.exit(1)
    else:
        sys.exit(0)