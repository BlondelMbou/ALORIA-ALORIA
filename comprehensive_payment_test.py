#!/usr/bin/env python3
"""
ALORIA AGENCY Payment System - COMPREHENSIVE VALIDATION
Testing all requirements from the review request
"""

import requests
import json
import os
from datetime import datetime
import sys

# Get backend URL from environment
BACKEND_URL = os.environ.get('REACT_APP_BACKEND_URL', 'https://agence-debug.preview.emergentagent.com')
API_BASE = f"{BACKEND_URL}/api"

class ComprehensivePaymentTester:
    def __init__(self):
        self.session = requests.Session()
        self.manager_token = None
        self.client_token = None
        self.test_results = []
        
    def log_result(self, test_name, success, message="", details=""):
        """Log test result with detailed information"""
        status = "✅ PASS" if success else "❌ FAIL"
        timestamp = datetime.now().strftime("%H:%M:%S")
        
        result = {
            'test': test_name,
            'success': success,
            'message': message,
            'details': details,
            'timestamp': timestamp
        }
        self.test_results.append(result)
        
        print(f"[{timestamp}] {status}: {test_name}")
        if message:
            print(f"   📝 {message}")
        if details and not success:
            print(f"   🔍 Details: {details}")
        print()
        
    def test_manager_login_specific_credentials(self):
        """Test manager login with EXACT credentials from review request"""
        print("🔐 Testing Manager Login (manager@test.com / password123)")
        
        try:
            login_data = {
                "email": "manager@test.com",
                "password": "password123"
            }
            
            response = self.session.post(f"{API_BASE}/auth/login", json=login_data)
            
            if response.status_code == 200:
                data = response.json()
                self.manager_token = data['access_token']
                manager_info = data['user']
                
                self.log_result(
                    "Manager Login (Specific Credentials)", 
                    True, 
                    f"✅ Successfully logged in as {manager_info['full_name']} ({manager_info['role']})"
                )
                return True
            else:
                self.log_result(
                    "Manager Login (Specific Credentials)", 
                    False, 
                    f"❌ Login failed with status {response.status_code}",
                    response.text
                )
                return False
                
        except Exception as e:
            self.log_result("Manager Login (Specific Credentials)", False, "Exception occurred", str(e))
            return False
    
    def test_complete_payment_workflow(self):
        """Test complete payment workflow: pending → code generation → confirmation → confirmed status"""
        print("💰 Testing Complete Payment Workflow")
        
        if not self.manager_token:
            self.log_result("Complete Payment Workflow", False, "No manager token available")
            return False
            
        # Step 1: Create client and payment
        try:
            headers = {"Authorization": f"Bearer {self.manager_token}"}
            timestamp = int(datetime.now().timestamp())
            
            # Create client
            client_data = {
                "email": f"workflow.test.{timestamp}@aloria.com",
                "full_name": "Client Workflow Test",
                "phone": "+33123456789",
                "country": "France",
                "visa_type": "Work Permit (Talent Permit)",
                "message": "Client pour test workflow complet"
            }
            
            client_response = self.session.post(f"{API_BASE}/clients", json=client_data, headers=headers)
            if client_response.status_code not in [200, 201]:
                self.log_result("Complete Payment Workflow - Client Creation", False, f"Status: {client_response.status_code}")
                return False
                
            # Login as client
            client_login_data = {
                "email": client_data['email'],
                "password": "Aloria2024!"
            }
            
            client_login_response = self.session.post(f"{API_BASE}/auth/login", json=client_login_data)
            if client_login_response.status_code != 200:
                self.log_result("Complete Payment Workflow - Client Login", False, f"Status: {client_login_response.status_code}")
                return False
                
            client_token = client_login_response.json()['access_token']
            client_headers = {"Authorization": f"Bearer {client_token}"}
            
            # Declare payment
            payment_data = {
                "amount": 3500.00,
                "currency": "EUR",
                "description": "Test workflow complet - Honoraires visa de travail",
                "payment_method": "Virement bancaire"
            }
            
            payment_response = self.session.post(f"{API_BASE}/payments/declare", json=payment_data, headers=client_headers)
            if payment_response.status_code not in [200, 201]:
                self.log_result("Complete Payment Workflow - Payment Declaration", False, f"Status: {payment_response.status_code}")
                return False
                
            payment_info = payment_response.json()
            payment_id = payment_info['id']
            
            # Verify payment is pending
            if payment_info['status'] != 'pending':
                self.log_result("Complete Payment Workflow - Pending Status", False, f"Expected 'pending', got '{payment_info['status']}'")
                return False
                
            self.log_result("Complete Payment Workflow - Step 1 (Pending)", True, f"Payment created in pending status: {payment_id}")
            
            # Step 2: Generate confirmation code
            confirmation_data = {"action": "CONFIRMED"}
            code_response = self.session.patch(f"{API_BASE}/payments/{payment_id}/confirm", json=confirmation_data, headers=headers)
            
            if code_response.status_code != 200:
                self.log_result("Complete Payment Workflow - Code Generation", False, f"Status: {code_response.status_code}")
                return False
                
            code_result = code_response.json()
            if 'confirmation_code' not in code_result or not code_result['confirmation_code']:
                self.log_result("Complete Payment Workflow - Code Generation", False, "No confirmation code generated")
                return False
                
            confirmation_code = code_result['confirmation_code']
            self.log_result("Complete Payment Workflow - Step 2 (Code Generation)", True, f"Confirmation code generated: {confirmation_code}")
            
            # Step 3: Confirm with code
            final_confirmation_data = {
                "action": "CONFIRMED",
                "confirmation_code": confirmation_code
            }
            
            final_response = self.session.patch(f"{API_BASE}/payments/{payment_id}/confirm", json=final_confirmation_data, headers=headers)
            
            if final_response.status_code != 200:
                self.log_result("Complete Payment Workflow - Final Confirmation", False, f"Status: {final_response.status_code}")
                return False
                
            final_result = final_response.json()
            
            # Step 4: Verify status is "confirmed" (NOT "rejected")
            if final_result.get('status') != 'confirmed':
                self.log_result("Complete Payment Workflow - Confirmed Status", False, f"Expected 'confirmed', got '{final_result.get('status')}'")
                return False
                
            # Step 5: Verify invoice generation
            if 'invoice_number' not in final_result or not final_result['invoice_number']:
                self.log_result("Complete Payment Workflow - Invoice Generation", False, "No invoice number generated")
                return False
                
            invoice_number = final_result['invoice_number']
            self.log_result("Complete Payment Workflow - Step 3 (Confirmation)", True, f"✅ Payment confirmed with status 'confirmed' (NOT rejected)")
            self.log_result("Complete Payment Workflow - Step 4 (Invoice)", True, f"📄 Invoice generated: {invoice_number}")
            
            return True
            
        except Exception as e:
            self.log_result("Complete Payment Workflow", False, "Exception occurred", str(e))
            return False
    
    def test_confirmation_codes_functionality(self):
        """Test that confirmation codes work correctly"""
        print("🔐 Testing Confirmation Codes Functionality")
        
        if not self.manager_token:
            self.log_result("Confirmation Codes Test", False, "No manager token available")
            return False
            
        try:
            # Create a test payment first
            headers = {"Authorization": f"Bearer {self.manager_token}"}
            timestamp = int(datetime.now().timestamp())
            
            # Create client and payment (simplified)
            client_data = {
                "email": f"code.test.{timestamp}@aloria.com",
                "full_name": "Client Code Test",
                "phone": "+33123456789",
                "country": "Canada",
                "visa_type": "Work Permit",
                "message": "Test codes de confirmation"
            }
            
            client_response = self.session.post(f"{API_BASE}/clients", json=client_data, headers=headers)
            if client_response.status_code not in [200, 201]:
                return False
                
            # Login as client and create payment
            client_login_response = self.session.post(f"{API_BASE}/auth/login", json={
                "email": client_data['email'],
                "password": "Aloria2024!"
            })
            
            if client_login_response.status_code != 200:
                return False
                
            client_token = client_login_response.json()['access_token']
            client_headers = {"Authorization": f"Bearer {client_token}"}
            
            payment_response = self.session.post(f"{API_BASE}/payments/declare", json={
                "amount": 2000.00,
                "currency": "EUR",
                "description": "Test codes de confirmation",
                "payment_method": "Chèque"
            }, headers=client_headers)
            
            if payment_response.status_code not in [200, 201]:
                return False
                
            payment_id = payment_response.json()['id']
            
            # Test 1: Generate code
            code_response = self.session.patch(f"{API_BASE}/payments/{payment_id}/confirm", 
                                             json={"action": "CONFIRMED"}, headers=headers)
            
            if code_response.status_code != 200:
                self.log_result("Confirmation Codes - Generation", False, f"Status: {code_response.status_code}")
                return False
                
            code_result = code_response.json()
            confirmation_code = code_result.get('confirmation_code')
            
            if not confirmation_code:
                self.log_result("Confirmation Codes - Generation", False, "No code generated")
                return False
                
            self.log_result("Confirmation Codes - Generation", True, f"Code generated successfully: {confirmation_code}")
            
            # Test 2: Try with wrong code
            wrong_code_response = self.session.patch(f"{API_BASE}/payments/{payment_id}/confirm", 
                                                   json={"action": "CONFIRMED", "confirmation_code": "WRONG"}, 
                                                   headers=headers)
            
            if wrong_code_response.status_code == 400:
                self.log_result("Confirmation Codes - Wrong Code Rejection", True, "Wrong code correctly rejected")
            else:
                self.log_result("Confirmation Codes - Wrong Code Rejection", False, f"Wrong code not rejected: {wrong_code_response.status_code}")
                
            # Test 3: Use correct code
            correct_code_response = self.session.patch(f"{API_BASE}/payments/{payment_id}/confirm", 
                                                     json={"action": "CONFIRMED", "confirmation_code": confirmation_code}, 
                                                     headers=headers)
            
            if correct_code_response.status_code == 200:
                result = correct_code_response.json()
                if result.get('status') == 'confirmed':
                    self.log_result("Confirmation Codes - Correct Code Acceptance", True, "Correct code accepted and payment confirmed")
                    return True
                else:
                    self.log_result("Confirmation Codes - Correct Code Acceptance", False, f"Code accepted but status wrong: {result.get('status')}")
                    return False
            else:
                self.log_result("Confirmation Codes - Correct Code Acceptance", False, f"Status: {correct_code_response.status_code}")
                return False
                
        except Exception as e:
            self.log_result("Confirmation Codes Test", False, "Exception occurred", str(e))
            return False
    
    def test_payment_history_both_sides(self):
        """Test payment history for both Manager and Client"""
        print("📚 Testing Payment History (Manager & Client)")
        
        if not self.manager_token:
            self.log_result("Payment History Test", False, "No manager token available")
            return False
            
        try:
            headers = {"Authorization": f"Bearer {self.manager_token}"}
            
            # Test Manager History
            manager_history_response = self.session.get(f"{API_BASE}/payments/history", headers=headers)
            
            if manager_history_response.status_code == 200:
                manager_history = manager_history_response.json()
                self.log_result("Payment History - Manager", True, f"Manager can see {len(manager_history)} payments in history")
                
                # Check if confirmed payments appear
                confirmed_payments = [p for p in manager_history if p.get('status') == 'confirmed']
                self.log_result("Payment History - Confirmed Payments", True, f"Found {len(confirmed_payments)} confirmed payments in manager history")
            else:
                self.log_result("Payment History - Manager", False, f"Status: {manager_history_response.status_code}")
                return False
            
            # Test Client History (need a client token)
            # Create a client and test their history
            timestamp = int(datetime.now().timestamp())
            client_data = {
                "email": f"history.test.{timestamp}@aloria.com",
                "full_name": "Client History Test",
                "phone": "+33123456789",
                "country": "France",
                "visa_type": "Student Visa",
                "message": "Test historique client"
            }
            
            client_response = self.session.post(f"{API_BASE}/clients", json=client_data, headers=headers)
            if client_response.status_code in [200, 201]:
                # Login as client
                client_login_response = self.session.post(f"{API_BASE}/auth/login", json={
                    "email": client_data['email'],
                    "password": "Aloria2024!"
                })
                
                if client_login_response.status_code == 200:
                    client_token = client_login_response.json()['access_token']
                    client_headers = {"Authorization": f"Bearer {client_token}"}
                    
                    # Test client history endpoint
                    client_history_response = self.session.get(f"{API_BASE}/payments/client-history", headers=client_headers)
                    
                    if client_history_response.status_code == 200:
                        client_history = client_history_response.json()
                        self.log_result("Payment History - Client", True, f"Client can see {len(client_history)} payments in their history")
                        return True
                    else:
                        self.log_result("Payment History - Client", False, f"Status: {client_history_response.status_code}")
                        return False
                else:
                    self.log_result("Payment History - Client Login", False, "Could not login as client")
                    return False
            else:
                self.log_result("Payment History - Client Creation", False, "Could not create test client")
                return False
                
        except Exception as e:
            self.log_result("Payment History Test", False, "Exception occurred", str(e))
            return False
    
    def test_persistence_after_refresh(self):
        """Test that payments remain visible after API refresh"""
        print("🔄 Testing Payment Persistence After Refresh")
        
        if not self.manager_token:
            self.log_result("Payment Persistence", False, "No manager token available")
            return False
            
        try:
            headers = {"Authorization": f"Bearer {self.manager_token}"}
            
            # Get initial payment count
            response1 = self.session.get(f"{API_BASE}/payments/history", headers=headers)
            if response1.status_code != 200:
                self.log_result("Payment Persistence - Initial Check", False, f"Status: {response1.status_code}")
                return False
                
            initial_payments = response1.json()
            initial_count = len(initial_payments)
            initial_confirmed = len([p for p in initial_payments if p.get('status') == 'confirmed'])
            
            # Wait a moment and check again (simulate refresh)
            import time
            time.sleep(1)
            
            response2 = self.session.get(f"{API_BASE}/payments/history", headers=headers)
            if response2.status_code != 200:
                self.log_result("Payment Persistence - After Refresh", False, f"Status: {response2.status_code}")
                return False
                
            refreshed_payments = response2.json()
            refreshed_count = len(refreshed_payments)
            refreshed_confirmed = len([p for p in refreshed_payments if p.get('status') == 'confirmed'])
            
            if initial_count == refreshed_count and initial_confirmed == refreshed_confirmed:
                self.log_result("Payment Persistence", True, f"✅ Data consistent after refresh: {refreshed_count} total, {refreshed_confirmed} confirmed")
                return True
            else:
                self.log_result("Payment Persistence", False, f"❌ Data changed: {initial_count}→{refreshed_count} total, {initial_confirmed}→{refreshed_confirmed} confirmed")
                return False
                
        except Exception as e:
            self.log_result("Payment Persistence", False, "Exception occurred", str(e))
            return False
    
    def test_pdf_invoice_generation(self):
        """Test that PDF invoices are generated"""
        print("📄 Testing PDF Invoice Generation")
        
        if not self.manager_token:
            self.log_result("PDF Invoice Generation", False, "No manager token available")
            return False
            
        try:
            headers = {"Authorization": f"Bearer {self.manager_token}"}
            
            # Get payment history and check for PDF URLs
            response = self.session.get(f"{API_BASE}/payments/history", headers=headers)
            if response.status_code != 200:
                self.log_result("PDF Invoice Generation", False, f"Status: {response.status_code}")
                return False
                
            payments = response.json()
            confirmed_payments = [p for p in payments if p.get('status') == 'confirmed']
            
            if not confirmed_payments:
                self.log_result("PDF Invoice Generation", False, "No confirmed payments found to check PDF generation")
                return False
                
            # Check if confirmed payments have PDF URLs
            payments_with_pdf = [p for p in confirmed_payments if p.get('pdf_invoice_url')]
            
            if payments_with_pdf:
                sample_payment = payments_with_pdf[0]
                self.log_result("PDF Invoice Generation", True, f"✅ PDF URLs generated for confirmed payments. Sample: {sample_payment.get('pdf_invoice_url')}")
                return True
            else:
                self.log_result("PDF Invoice Generation", False, f"❌ No PDF URLs found in {len(confirmed_payments)} confirmed payments")
                return False
                
        except Exception as e:
            self.log_result("PDF Invoice Generation", False, "Exception occurred", str(e))
            return False
    
    def run_comprehensive_test(self):
        """Run all comprehensive payment system tests"""
        print("🎯 ALORIA AGENCY - COMPREHENSIVE PAYMENT SYSTEM VALIDATION")
        print("=" * 80)
        print(f"Testing against: {API_BASE}")
        print("Validating all requirements from review request")
        print("=" * 80)
        
        # Test 1: Manager Login with specific credentials
        if not self.test_manager_login_specific_credentials():
            print("❌ CRITICAL: Cannot proceed without manager login")
            return False
        
        # Test 2: Complete payment workflow
        print("\n" + "="*50)
        print("🔄 TESTING COMPLETE PAYMENT WORKFLOW")
        print("="*50)
        workflow_success = self.test_complete_payment_workflow()
        
        # Test 3: Confirmation codes functionality
        print("\n" + "="*50)
        print("🔐 TESTING CONFIRMATION CODES")
        print("="*50)
        codes_success = self.test_confirmation_codes_functionality()
        
        # Test 4: Payment history both sides
        print("\n" + "="*50)
        print("📚 TESTING PAYMENT HISTORY")
        print("="*50)
        history_success = self.test_payment_history_both_sides()
        
        # Test 5: Persistence after refresh
        print("\n" + "="*50)
        print("🔄 TESTING PERSISTENCE")
        print("="*50)
        persistence_success = self.test_persistence_after_refresh()
        
        # Test 6: PDF invoice generation
        print("\n" + "="*50)
        print("📄 TESTING PDF GENERATION")
        print("="*50)
        pdf_success = self.test_pdf_invoice_generation()
        
        # Summary
        print("\n" + "=" * 80)
        print("🏁 COMPREHENSIVE PAYMENT SYSTEM TEST SUMMARY")
        print("=" * 80)
        
        passed_tests = sum(1 for result in self.test_results if result['success'])
        total_tests = len(self.test_results)
        success_rate = (passed_tests / total_tests * 100) if total_tests > 0 else 0
        
        print(f"✅ Passed: {passed_tests}")
        print(f"❌ Failed: {total_tests - passed_tests}")
        print(f"📊 Success Rate: {success_rate:.1f}%")
        
        # Critical requirements check
        critical_tests = {
            "Manager Login": any(r['test'].startswith('Manager Login') and r['success'] for r in self.test_results),
            "Payment Workflow": workflow_success,
            "Confirmation Codes": codes_success,
            "Payment History": history_success,
            "Data Persistence": persistence_success,
            "PDF Generation": pdf_success
        }
        
        print("\n🎯 CRITICAL REQUIREMENTS STATUS:")
        for requirement, status in critical_tests.items():
            status_icon = "✅" if status else "❌"
            print(f"  {status_icon} {requirement}")
        
        all_critical_passed = all(critical_tests.values())
        
        if all_critical_passed:
            print("\n🎉 ALL CRITICAL REQUIREMENTS PASSED!")
            print("✅ Manager login with manager@test.com / password123 works")
            print("✅ Complete payment workflow: pending → code → confirmed (NOT rejected)")
            print("✅ Confirmation codes generate and validate correctly")
            print("✅ Payment history works for both Manager and Client")
            print("✅ Payments persist after API refresh")
            print("✅ PDF invoices are generated for confirmed payments")
        else:
            print("\n❌ SOME CRITICAL REQUIREMENTS FAILED!")
            
        # Show failed tests
        failed_tests = [result for result in self.test_results if not result['success']]
        if failed_tests:
            print("\n🔍 FAILED TESTS DETAILS:")
            for test in failed_tests:
                print(f"  • {test['test']}: {test['message']}")
                if test['details']:
                    print(f"    Details: {test['details'][:200]}...")
        
        print("\n" + "=" * 80)
        return all_critical_passed and success_rate >= 90

if __name__ == "__main__":
    tester = ComprehensivePaymentTester()
    success = tester.run_comprehensive_test()
    
    if success:
        print("🎉 Comprehensive payment system testing PASSED!")
        sys.exit(0)
    else:
        print("❌ Comprehensive payment system testing FAILED!")
        sys.exit(1)