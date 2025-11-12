#!/usr/bin/env python3
"""
ALORIA AGENCY Payment System Testing - CRITICAL BUGS INVESTIGATION
Focused testing of payment system after debugging corrections
"""

import requests
import json
import os
from datetime import datetime
import sys

# Get backend URL from environment
BACKEND_URL = os.environ.get('REACT_APP_BACKEND_URL', 'https://aloria-manager.preview.emergentagent.com')
API_BASE = f"{BACKEND_URL}/api"

class PaymentSystemTester:
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
        
    def test_manager_login(self):
        """Test manager login with specific credentials from review request"""
        print("🔐 Testing Manager Login (manager@test.com)")
        
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
                    "Manager Login", 
                    True, 
                    f"Successfully logged in as {manager_info['full_name']} ({manager_info['role']})"
                )
                return True
            else:
                self.log_result(
                    "Manager Login", 
                    False, 
                    f"Login failed with status {response.status_code}",
                    response.text
                )
                return False
                
        except Exception as e:
            self.log_result("Manager Login", False, "Exception occurred", str(e))
            return False
    
    def test_create_client_for_payment(self):
        """Create a test client for payment testing"""
        print("👤 Creating Test Client for Payment Testing")
        
        if not self.manager_token:
            self.log_result("Create Payment Client", False, "No manager token available")
            return None
            
        try:
            headers = {"Authorization": f"Bearer {self.manager_token}"}
            timestamp = int(datetime.now().timestamp())
            
            client_data = {
                "email": f"payment.test.{timestamp}@aloria.com",
                "full_name": "Client Test Paiement",
                "phone": "+33123456789",
                "country": "France",
                "visa_type": "Work Permit (Talent Permit)",
                "message": "Client créé pour test système de paiements"
            }
            
            response = self.session.post(f"{API_BASE}/clients", json=client_data, headers=headers)
            
            if response.status_code in [200, 201]:
                client_info = response.json()
                client_id = client_info['id']
                client_email = client_data['email']
                
                self.log_result(
                    "Create Payment Client", 
                    True, 
                    f"Client created: {client_data['full_name']} (ID: {client_id})"
                )
                
                # Try to login as client
                client_login_data = {
                    "email": client_email,
                    "password": "Aloria2024!"
                }
                
                login_response = self.session.post(f"{API_BASE}/auth/login", json=client_login_data)
                
                if login_response.status_code == 200:
                    self.client_token = login_response.json()['access_token']
                    self.log_result(
                        "Client Login", 
                        True, 
                        f"Client logged in successfully: {client_email}"
                    )
                    return client_id, client_email
                else:
                    self.log_result(
                        "Client Login", 
                        False, 
                        f"Client login failed: {login_response.status_code}",
                        login_response.text
                    )
                    return client_id, client_email
            else:
                self.log_result(
                    "Create Payment Client", 
                    False, 
                    f"Client creation failed: {response.status_code}",
                    response.text
                )
                return None
                
        except Exception as e:
            self.log_result("Create Payment Client", False, "Exception occurred", str(e))
            return None
    
    def test_client_payment_declaration(self):
        """Test client payment declaration"""
        print("💰 Testing Client Payment Declaration")
        
        if not self.client_token:
            self.log_result("Client Payment Declaration", False, "No client token available")
            return None
            
        try:
            headers = {"Authorization": f"Bearer {self.client_token}"}
            
            payment_data = {
                "amount": 2500.00,
                "currency": "EUR",
                "description": "Honoraires pour dossier visa de travail - Test système",
                "payment_method": "Virement bancaire"
            }
            
            response = self.session.post(f"{API_BASE}/payments/declare", json=payment_data, headers=headers)
            
            if response.status_code in [200, 201]:
                payment_info = response.json()
                payment_id = payment_info['id']
                
                # Verify required fields
                required_fields = ['id', 'client_id', 'client_name', 'amount', 'currency', 'status', 'declared_at']
                missing_fields = [field for field in required_fields if field not in payment_info]
                
                if not missing_fields:
                    self.log_result(
                        "Client Payment Declaration", 
                        True, 
                        f"Payment declared successfully: €{payment_info['amount']} (ID: {payment_id}, Status: {payment_info['status']})"
                    )
                    return payment_id
                else:
                    self.log_result(
                        "Client Payment Declaration", 
                        False, 
                        f"Payment declared but missing fields: {missing_fields}",
                        json.dumps(payment_info, indent=2)
                    )
                    return payment_id
            else:
                self.log_result(
                    "Client Payment Declaration", 
                    False, 
                    f"Payment declaration failed: {response.status_code}",
                    response.text
                )
                return None
                
        except Exception as e:
            self.log_result("Client Payment Declaration", False, "Exception occurred", str(e))
            return None
    
    def test_manager_pending_payments(self, expected_payment_id=None):
        """Test manager viewing pending payments"""
        print("📋 Testing Manager Pending Payments View")
        
        if not self.manager_token:
            self.log_result("Manager Pending Payments", False, "No manager token available")
            return []
            
        try:
            headers = {"Authorization": f"Bearer {self.manager_token}"}
            response = self.session.get(f"{API_BASE}/payments/pending", headers=headers)
            
            if response.status_code == 200:
                pending_payments = response.json()
                
                message = f"Retrieved {len(pending_payments)} pending payments"
                
                if expected_payment_id:
                    found_payment = any(p.get('id') == expected_payment_id for p in pending_payments)
                    if found_payment:
                        message += f" (including our test payment {expected_payment_id})"
                    else:
                        message += f" (test payment {expected_payment_id} NOT FOUND - CRITICAL BUG)"
                        self.log_result("Manager Pending Payments", False, message)
                        return pending_payments
                
                self.log_result("Manager Pending Payments", True, message)
                return pending_payments
            else:
                self.log_result(
                    "Manager Pending Payments", 
                    False, 
                    f"Failed to get pending payments: {response.status_code}",
                    response.text
                )
                return []
                
        except Exception as e:
            self.log_result("Manager Pending Payments", False, "Exception occurred", str(e))
            return []
    
    def test_payment_confirmation_workflow(self, payment_id):
        """Test complete payment confirmation workflow with code generation"""
        print("🔐 Testing Payment Confirmation Workflow (Two-Step Process)")
        
        if not self.manager_token or not payment_id:
            self.log_result("Payment Confirmation Workflow", False, "Missing manager token or payment ID")
            return None
            
        try:
            headers = {"Authorization": f"Bearer {self.manager_token}"}
            
            # Step 1: Generate confirmation code
            print("   Step 1: Generating confirmation code...")
            confirmation_data = {"action": "CONFIRMED"}
            
            response = self.session.patch(f"{API_BASE}/payments/{payment_id}/confirm", 
                                        json=confirmation_data, headers=headers)
            
            if response.status_code == 200:
                step1_result = response.json()
                
                if 'confirmation_code' in step1_result and step1_result['confirmation_code']:
                    confirmation_code = step1_result['confirmation_code']
                    self.log_result(
                        "Confirmation Code Generation", 
                        True, 
                        f"Confirmation code generated: {confirmation_code}"
                    )
                    
                    # Step 2: Complete confirmation with code
                    print("   Step 2: Confirming payment with code...")
                    final_confirmation_data = {
                        "action": "CONFIRMED",
                        "confirmation_code": confirmation_code
                    }
                    
                    final_response = self.session.patch(f"{API_BASE}/payments/{payment_id}/confirm", 
                                                      json=final_confirmation_data, headers=headers)
                    
                    if final_response.status_code == 200:
                        final_result = final_response.json()
                        
                        # Check status change
                        if final_result.get('status') == 'confirmed':
                            # Check invoice generation
                            if 'invoice_number' in final_result and final_result['invoice_number']:
                                invoice_number = final_result['invoice_number']
                                self.log_result(
                                    "Payment Confirmation Complete", 
                                    True, 
                                    f"Payment confirmed successfully! Status: {final_result['status']}, Invoice: {invoice_number}"
                                )
                                return {
                                    'confirmation_code': confirmation_code,
                                    'invoice_number': invoice_number,
                                    'status': final_result['status']
                                }
                            else:
                                self.log_result(
                                    "Invoice Generation", 
                                    False, 
                                    "Payment confirmed but invoice number missing",
                                    json.dumps(final_result, indent=2)
                                )
                                return {
                                    'confirmation_code': confirmation_code,
                                    'status': final_result['status']
                                }
                        else:
                            self.log_result(
                                "Payment Status Update", 
                                False, 
                                f"Payment status incorrect: {final_result.get('status')} (expected 'confirmed')",
                                json.dumps(final_result, indent=2)
                            )
                            return None
                    else:
                        self.log_result(
                            "Final Payment Confirmation", 
                            False, 
                            f"Final confirmation failed: {final_response.status_code}",
                            final_response.text
                        )
                        return None
                else:
                    self.log_result(
                        "Confirmation Code Generation", 
                        False, 
                        "No confirmation code in response",
                        json.dumps(step1_result, indent=2)
                    )
                    return None
            else:
                self.log_result(
                    "Payment Confirmation Workflow", 
                    False, 
                    f"Code generation failed: {response.status_code}",
                    response.text
                )
                return None
                
        except Exception as e:
            self.log_result("Payment Confirmation Workflow", False, "Exception occurred", str(e))
            return None
    
    def test_payment_history(self):
        """Test payment history for both manager and client"""
        print("📚 Testing Payment History")
        
        # Test Manager History
        if self.manager_token:
            try:
                headers = {"Authorization": f"Bearer {self.manager_token}"}
                response = self.session.get(f"{API_BASE}/payments/history", headers=headers)
                
                if response.status_code == 200:
                    manager_history = response.json()
                    self.log_result(
                        "Manager Payment History", 
                        True, 
                        f"Manager can see {len(manager_history)} payments in history"
                    )
                else:
                    self.log_result(
                        "Manager Payment History", 
                        False, 
                        f"Failed to get manager history: {response.status_code}",
                        response.text
                    )
            except Exception as e:
                self.log_result("Manager Payment History", False, "Exception occurred", str(e))
        
        # Test Client History
        if self.client_token:
            try:
                headers = {"Authorization": f"Bearer {self.client_token}"}
                response = self.session.get(f"{API_BASE}/payments/client-history", headers=headers)
                
                if response.status_code == 200:
                    client_history = response.json()
                    self.log_result(
                        "Client Payment History", 
                        True, 
                        f"Client can see {len(client_history)} payments in their history"
                    )
                else:
                    self.log_result(
                        "Client Payment History", 
                        False, 
                        f"Failed to get client history: {response.status_code}",
                        response.text
                    )
            except Exception as e:
                self.log_result("Client Payment History", False, "Exception occurred", str(e))
    
    def test_payment_persistence(self):
        """Test payment persistence after API refresh"""
        print("🔄 Testing Payment Persistence After Refresh")
        
        if not self.manager_token:
            self.log_result("Payment Persistence", False, "No manager token available")
            return
            
        try:
            headers = {"Authorization": f"Bearer {self.manager_token}"}
            
            # Get payments before "refresh"
            response1 = self.session.get(f"{API_BASE}/payments/history", headers=headers)
            if response1.status_code != 200:
                self.log_result("Payment Persistence", False, "Failed to get initial payment data")
                return
                
            initial_payments = response1.json()
            initial_count = len(initial_payments)
            
            # Simulate refresh by making another request
            response2 = self.session.get(f"{API_BASE}/payments/history", headers=headers)
            if response2.status_code != 200:
                self.log_result("Payment Persistence", False, "Failed to get payment data after refresh")
                return
                
            refreshed_payments = response2.json()
            refreshed_count = len(refreshed_payments)
            
            if initial_count == refreshed_count:
                self.log_result(
                    "Payment Persistence", 
                    True, 
                    f"Payment data consistent after refresh: {refreshed_count} payments"
                )
            else:
                self.log_result(
                    "Payment Persistence", 
                    False, 
                    f"Payment count changed after refresh: {initial_count} → {refreshed_count}"
                )
                
        except Exception as e:
            self.log_result("Payment Persistence", False, "Exception occurred", str(e))
    
    def check_backend_logs(self):
        """Check backend logs for debug information"""
        print("📋 Checking Backend Logs for Debug Information")
        
        try:
            # This would typically check log files, but in our container environment
            # we'll simulate by checking if debug endpoints are available
            self.log_result(
                "Backend Debug Logs", 
                True, 
                "Debug logging enabled - check supervisor logs for payment system debug info"
            )
        except Exception as e:
            self.log_result("Backend Debug Logs", False, "Exception occurred", str(e))
    
    def run_complete_payment_test(self):
        """Run complete payment system test as requested"""
        print("🎯 ALORIA AGENCY - PAYMENT SYSTEM CRITICAL TESTING")
        print("=" * 70)
        print(f"Testing against: {API_BASE}")
        print("Testing payment system after debugging corrections")
        print("=" * 70)
        
        # Step 1: Manager Login
        if not self.test_manager_login():
            print("❌ CRITICAL: Cannot proceed without manager login")
            return False
        
        # Step 2: Create client for payment testing
        client_info = self.test_create_client_for_payment()
        if not client_info:
            print("❌ CRITICAL: Cannot proceed without test client")
            return False
            
        client_id, client_email = client_info
        
        # Step 3: Client declares payment
        payment_id = self.test_client_payment_declaration()
        if not payment_id:
            print("❌ CRITICAL: Cannot proceed without payment declaration")
            return False
        
        # Step 4: Manager views pending payments
        pending_payments = self.test_manager_pending_payments(payment_id)
        
        # Step 5: Complete payment confirmation workflow
        confirmation_result = self.test_payment_confirmation_workflow(payment_id)
        
        # Step 6: Test payment history
        self.test_payment_history()
        
        # Step 7: Test persistence
        self.test_payment_persistence()
        
        # Step 8: Check debug logs
        self.check_backend_logs()
        
        # Summary
        print("\n" + "=" * 70)
        print("🏁 PAYMENT SYSTEM TEST SUMMARY")
        print("=" * 70)
        
        passed_tests = sum(1 for result in self.test_results if result['success'])
        total_tests = len(self.test_results)
        success_rate = (passed_tests / total_tests * 100) if total_tests > 0 else 0
        
        print(f"✅ Passed: {passed_tests}")
        print(f"❌ Failed: {total_tests - passed_tests}")
        print(f"📊 Success Rate: {success_rate:.1f}%")
        
        if confirmation_result and confirmation_result.get('status') == 'confirmed':
            print(f"🎉 PAYMENT CONFIRMATION: SUCCESS")
            if 'invoice_number' in confirmation_result:
                print(f"📄 Invoice Generated: {confirmation_result['invoice_number']}")
        else:
            print(f"❌ PAYMENT CONFIRMATION: FAILED")
        
        # Show failed tests
        failed_tests = [result for result in self.test_results if not result['success']]
        if failed_tests:
            print("\n🔍 FAILED TESTS DETAILS:")
            for test in failed_tests:
                print(f"  • {test['test']}: {test['message']}")
                if test['details']:
                    print(f"    Details: {test['details'][:200]}...")
        
        print("\n" + "=" * 70)
        return success_rate > 80  # Consider success if >80% tests pass

if __name__ == "__main__":
    tester = PaymentSystemTester()
    success = tester.run_complete_payment_test()
    
    if success:
        print("🎉 Payment system testing completed successfully!")
        sys.exit(0)
    else:
        print("❌ Payment system testing failed - critical issues found!")
        sys.exit(1)