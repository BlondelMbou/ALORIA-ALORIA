#!/usr/bin/env python3
"""
ALORIA AGENCY - Test Téléchargement de Factures - CLIENT vs MANAGER
Test spécifique pour le bug de permission 403 pour les clients téléchargeant leurs propres factures

TESTS REQUIS:
1. Manager télécharge une facture (baseline)
2. Client télécharge SA PROPRE facture (bug fix)
3. Client essaie de télécharger une facture d'un autre client (sécurité)
4. Employee télécharge une facture de son client assigné
5. Client télécharge une facture de paiement initial (création)
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
    'employee': {'email': 'employee@aloria.com', 'password': 'emp123'}
}

class InvoiceDownloadTester:
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

    def authenticate_user(self, role, credentials):
        """Authenticate a single user"""
        try:
            response = self.session.post(f"{API_BASE}/auth/login", json=credentials)
            if response.status_code == 200:
                data = response.json()
                self.tokens[role] = data['access_token']
                self.users[role] = data['user']
                self.log_result(f"{role.upper()} Login", True, 
                              f"Logged in as {credentials['email']} - Role: {data['user']['role']}")
                return True
            else:
                self.log_result(f"{role.upper()} Login", False, 
                              f"Status: {response.status_code}", response.text)
                return False
        except Exception as e:
            self.log_result(f"{role.upper()} Login", False, "Exception occurred", str(e))
            return False

    def authenticate_users(self):
        """Authenticate all required users"""
        print("=== AUTHENTICATION SETUP ===")
        
        for role, credentials in CREDENTIALS.items():
            if not self.authenticate_user(role, credentials):
                return False
        return True

    def find_confirmed_payment_with_invoice(self, headers):
        """Find a confirmed payment with invoice number"""
        try:
            # Try different payment endpoints
            endpoints = ["/payments/manager-history", "/payments/history"]
            
            for endpoint in endpoints:
                response = self.session.get(f"{API_BASE}{endpoint}", headers=headers)
                if response.status_code == 200:
                    payments = response.json()
                    
                    # Look for confirmed payments with invoice numbers
                    for payment in payments:
                        status = payment.get('status', '').upper()
                        invoice_number = payment.get('invoice_number')
                        
                        if status == 'CONFIRMED' and invoice_number:
                            return payment
                        
                        # Also check for 'confirmed' (lowercase)
                        if payment.get('status') == 'confirmed' and invoice_number:
                            return payment
            
            return None
        except Exception as e:
            print(f"   Error finding confirmed payment: {e}")
            return None

    def test_1_manager_downloads_invoice(self):
        """TEST 1 - Manager télécharge une facture (baseline)"""
        print("\n" + "="*60)
        print("TEST 1 - MANAGER TÉLÉCHARGE UNE FACTURE (BASELINE)")
        print("="*60)
        
        if 'manager' not in self.tokens:
            self.log_result("Test 1 Setup", False, "Manager token not available")
            return False
            
        headers = {"Authorization": f"Bearer {self.tokens['manager']}"}
        
        # 1. Find a confirmed payment with invoice
        print("\n🔸 ÉTAPE 1.1 - Trouver un paiement confirmé avec facture")
        payment = self.find_confirmed_payment_with_invoice(headers)
        
        if not payment:
            self.log_result("1.1 Find Confirmed Payment", False, "Aucun paiement confirmé avec facture trouvé")
            return False
        
        payment_id = payment['id']
        invoice_number = payment['invoice_number']
        self.test_data['manager_payment_id'] = payment_id
        self.test_data['manager_invoice_number'] = invoice_number
        
        self.log_result("1.1 Find Confirmed Payment", True, 
                      f"Paiement trouvé: {payment_id} - Facture: {invoice_number}")
        
        # 2. Download the invoice
        print("\n🔸 ÉTAPE 1.2 - Télécharger la facture")
        try:
            response = self.session.get(f"{API_BASE}/payments/{payment_id}/invoice", headers=headers)
            
            if response.status_code == 200:
                content_type = response.headers.get('content-type', '')
                content_disposition = response.headers.get('content-disposition', '')
                content_length = len(response.content)
                
                verifications = []
                
                # Verify Content-Type
                if 'application/pdf' in content_type:
                    verifications.append("✅ Content-Type: application/pdf")
                else:
                    verifications.append(f"❌ Content-Type: {content_type}")
                
                # Verify Content-Disposition
                if 'Facture_' in content_disposition:
                    verifications.append("✅ Content-Disposition contient 'Facture_'")
                else:
                    verifications.append(f"❌ Content-Disposition: {content_disposition}")
                
                # Verify file size
                if content_length > 0:
                    verifications.append(f"✅ Taille du fichier: {content_length} bytes")
                else:
                    verifications.append("❌ Fichier vide")
                
                all_verified = all("✅" in v for v in verifications)
                self.log_result("1.2 Manager Invoice Download", all_verified, 
                              f"Vérifications: {'; '.join(verifications)}")
                
                return all_verified
            else:
                self.log_result("1.2 Manager Invoice Download", False, 
                              f"Status: {response.status_code}", response.text)
                return False
                
        except Exception as e:
            self.log_result("1.2 Manager Invoice Download", False, "Exception occurred", str(e))
            return False

    def find_client_with_confirmed_payment(self):
        """Find a client with a confirmed payment"""
        try:
            headers = {"Authorization": f"Bearer {self.tokens['manager']}"}
            
            # Get all payments
            response = self.session.get(f"{API_BASE}/payments", headers=headers)
            if response.status_code != 200:
                return None, None
            
            payments = response.json()
            
            # Find a confirmed payment
            for payment in payments:
                status = payment.get('status', '').upper()
                invoice_number = payment.get('invoice_number')
                client_id = payment.get('client_id')
                
                if (status == 'CONFIRMED' or payment.get('status') == 'confirmed') and invoice_number and client_id:
                    # Get client info
                    client = self.get_client_info(client_id)
                    if client:
                        return payment, client
            
            return None, None
        except Exception as e:
            print(f"   Error finding client with confirmed payment: {e}")
            return None, None

    def get_client_info(self, client_id):
        """Get client information"""
        try:
            headers = {"Authorization": f"Bearer {self.tokens['manager']}"}
            
            # Try to get client by ID
            response = self.session.get(f"{API_BASE}/clients/{client_id}", headers=headers)
            if response.status_code == 200:
                return response.json()
            
            # Try to get from clients list
            response = self.session.get(f"{API_BASE}/clients", headers=headers)
            if response.status_code == 200:
                clients = response.json()
                for client in clients:
                    if client.get('id') == client_id or client.get('user_id') == client_id:
                        return client
            
            return None
        except Exception as e:
            print(f"   Error getting client info: {e}")
            return None

    def test_2_client_downloads_own_invoice(self):
        """TEST 2 - Client télécharge SA PROPRE facture (bug fix)"""
        print("\n" + "="*60)
        print("TEST 2 - CLIENT TÉLÉCHARGE SA PROPRE FACTURE (BUG FIX)")
        print("="*60)
        
        # 1. Find a confirmed payment and its client
        print("\n🔸 ÉTAPE 2.1 - Trouver un paiement confirmé et son client")
        
        headers = {"Authorization": f"Bearer {self.tokens['manager']}"}
        
        try:
            # Get payments
            response = self.session.get(f"{API_BASE}/payments", headers=headers)
            if response.status_code != 200:
                self.log_result("2.1 Find Payment and Client", False, 
                              f"Cannot get payments: {response.status_code}")
                return False
            
            payments = response.json()
            target_payment = None
            target_client = None
            
            # Find a confirmed payment with client
            for payment in payments:
                status = payment.get('status', '').upper()
                invoice_number = payment.get('invoice_number')
                client_id = payment.get('client_id')
                
                if (status == 'CONFIRMED' or payment.get('status') == 'confirmed') and invoice_number and client_id:
                    # Get client info
                    client_response = self.session.get(f"{API_BASE}/clients", headers=headers)
                    if client_response.status_code == 200:
                        clients = client_response.json()
                        for client in clients:
                            if client.get('id') == client_id or client.get('user_id') == client_id:
                                target_payment = payment
                                target_client = client
                                break
                    
                    if target_payment and target_client:
                        break
            
            if not target_payment or not target_client:
                self.log_result("2.1 Find Payment and Client", False, 
                              "Aucun paiement confirmé avec client trouvé")
                return False
            
            payment_id = target_payment['id']
            client_email = target_client.get('email')
            
            if not client_email:
                # Try to get email from user record
                user_id = target_client.get('user_id')
                if user_id:
                    # We can't directly access users endpoint, so we'll try a common pattern
                    # Most clients use default password
                    client_email = target_client.get('full_name', '').lower().replace(' ', '.') + '@test.com'
                    if not client_email or '@test.com' not in client_email:
                        # Try some common patterns
                        possible_emails = [
                            'client@test.com',
                            'client1@gmail.com',
                            'test.client@example.com'
                        ]
                        client_email = possible_emails[0]  # Use first as fallback
            
            self.test_data['client_payment_id'] = payment_id
            self.test_data['client_email'] = client_email
            
            self.log_result("2.1 Find Payment and Client", True, 
                          f"Paiement: {payment_id}, Client: {client_email}")
            
        except Exception as e:
            self.log_result("2.1 Find Payment and Client", False, "Exception occurred", str(e))
            return False
        
        # 2. Login as the client
        print("\n🔸 ÉTAPE 2.2 - Se connecter en tant que client")
        
        client_credentials = {
            "email": client_email,
            "password": "Aloria2024!"  # Default password
        }
        
        if not self.authenticate_user('client', client_credentials):
            self.log_result("2.2 Client Authentication", False, 
                          f"Cannot login as client: {client_email}")
            return False
        
        # 3. Verify client can see their payment
        print("\n🔸 ÉTAPE 2.3 - Vérifier que le client voit son paiement")
        
        client_headers = {"Authorization": f"Bearer {self.tokens['client']}"}
        
        try:
            response = self.session.get(f"{API_BASE}/payments/client-history", headers=client_headers)
            if response.status_code == 200:
                client_payments = response.json()
                client_payment = next((p for p in client_payments if p.get('id') == payment_id), None)
                
                if client_payment:
                    self.log_result("2.3 Client Payment Visibility", True, 
                                  f"Client voit son paiement: {payment_id}")
                else:
                    self.log_result("2.3 Client Payment Visibility", False, 
                                  f"Client ne voit pas son paiement dans {len(client_payments)} paiements")
            else:
                self.log_result("2.3 Client Payment Visibility", False, 
                              f"Status: {response.status_code}")
        except Exception as e:
            self.log_result("2.3 Client Payment Visibility", False, "Exception occurred", str(e))
        
        # 4. Download the invoice as client (THE MAIN TEST)
        print("\n🔸 ÉTAPE 2.4 - Télécharger la facture en tant que client")
        
        try:
            response = self.session.get(f"{API_BASE}/payments/{payment_id}/invoice", headers=client_headers)
            
            if response.status_code == 200:
                content_type = response.headers.get('content-type', '')
                content_length = len(response.content)
                
                verifications = []
                
                # Verify Content-Type
                if 'application/pdf' in content_type:
                    verifications.append("✅ Content-Type: application/pdf")
                else:
                    verifications.append(f"❌ Content-Type: {content_type}")
                
                # Verify file size
                if content_length > 0:
                    verifications.append(f"✅ Taille du fichier: {content_length} bytes")
                else:
                    verifications.append("❌ Fichier vide")
                
                all_verified = all("✅" in v for v in verifications)
                self.log_result("2.4 Client Invoice Download (BUG FIX)", all_verified, 
                              f"Status: 200 OK (PAS 403 Forbidden) - {'; '.join(verifications)}")
                
                return all_verified
            elif response.status_code == 403:
                self.log_result("2.4 Client Invoice Download (BUG FIX)", False, 
                              "Status: 403 Forbidden - LE BUG PERSISTE!", response.text)
                return False
            else:
                self.log_result("2.4 Client Invoice Download (BUG FIX)", False, 
                              f"Status: {response.status_code}", response.text)
                return False
                
        except Exception as e:
            self.log_result("2.4 Client Invoice Download (BUG FIX)", False, "Exception occurred", str(e))
            return False

    def test_3_client_cannot_download_other_client_invoice(self):
        """TEST 3 - Client essaie de télécharger une facture d'un autre client (sécurité)"""
        print("\n" + "="*60)
        print("TEST 3 - CLIENT ESSAIE DE TÉLÉCHARGER FACTURE D'AUTRE CLIENT (SÉCURITÉ)")
        print("="*60)
        
        if 'client' not in self.tokens:
            self.log_result("Test 3 Setup", False, "Client token not available")
            return False
        
        # Use the manager's payment ID (different client)
        if 'manager_payment_id' not in self.test_data:
            self.log_result("Test 3 Setup", False, "Manager payment ID not available")
            return False
        
        client_headers = {"Authorization": f"Bearer {self.tokens['client']}"}
        other_payment_id = self.test_data['manager_payment_id']
        
        print(f"\n🔸 ÉTAPE 3.1 - Essayer de télécharger facture d'un autre client")
        
        try:
            response = self.session.get(f"{API_BASE}/payments/{other_payment_id}/invoice", headers=client_headers)
            
            if response.status_code == 403:
                self.log_result("3.1 Client Security Check", True, 
                              "Status: 403 Forbidden - Sécurité OK, client ne peut pas télécharger facture d'autrui")
                return True
            else:
                self.log_result("3.1 Client Security Check", False, 
                              f"Status: {response.status_code} - FAILLE DE SÉCURITÉ! Client peut télécharger facture d'autrui", 
                              response.text)
                return False
                
        except Exception as e:
            self.log_result("3.1 Client Security Check", False, "Exception occurred", str(e))
            return False

    def test_4_employee_downloads_assigned_client_invoice(self):
        """TEST 4 - Employee télécharge une facture de son client assigné"""
        print("\n" + "="*60)
        print("TEST 4 - EMPLOYEE TÉLÉCHARGE FACTURE DE SON CLIENT ASSIGNÉ")
        print("="*60)
        
        if 'employee' not in self.tokens:
            self.log_result("Test 4 Setup", False, "Employee token not available")
            return False
        
        employee_headers = {"Authorization": f"Bearer {self.tokens['employee']}"}
        
        # 1. Find a payment from an assigned client
        print("\n🔸 ÉTAPE 4.1 - Trouver un paiement d'un client assigné")
        
        try:
            # Get employee's assigned clients
            response = self.session.get(f"{API_BASE}/clients", headers=employee_headers)
            if response.status_code != 200:
                self.log_result("4.1 Find Assigned Client Payment", False, 
                              f"Cannot get assigned clients: {response.status_code}")
                return False
            
            assigned_clients = response.json()
            if not assigned_clients:
                self.log_result("4.1 Find Assigned Client Payment", False, 
                              "Employee has no assigned clients")
                return False
            
            # Get payments and find one from assigned client
            manager_headers = {"Authorization": f"Bearer {self.tokens['manager']}"}
            payments_response = self.session.get(f"{API_BASE}/payments", headers=manager_headers)
            
            if payments_response.status_code != 200:
                self.log_result("4.1 Find Assigned Client Payment", False, 
                              f"Cannot get payments: {payments_response.status_code}")
                return False
            
            payments = payments_response.json()
            assigned_payment = None
            
            for payment in payments:
                status = payment.get('status', '').upper()
                invoice_number = payment.get('invoice_number')
                client_id = payment.get('client_id')
                
                if (status == 'CONFIRMED' or payment.get('status') == 'confirmed') and invoice_number:
                    # Check if this payment belongs to an assigned client
                    for client in assigned_clients:
                        if client.get('id') == client_id or client.get('user_id') == client_id:
                            assigned_payment = payment
                            break
                    
                    if assigned_payment:
                        break
            
            if not assigned_payment:
                self.log_result("4.1 Find Assigned Client Payment", False, 
                              "No confirmed payment found from assigned clients")
                return False
            
            payment_id = assigned_payment['id']
            self.log_result("4.1 Find Assigned Client Payment", True, 
                          f"Paiement trouvé: {payment_id}")
            
        except Exception as e:
            self.log_result("4.1 Find Assigned Client Payment", False, "Exception occurred", str(e))
            return False
        
        # 2. Download the invoice as employee
        print("\n🔸 ÉTAPE 4.2 - Télécharger la facture en tant qu'employé")
        
        try:
            response = self.session.get(f"{API_BASE}/payments/{payment_id}/invoice", headers=employee_headers)
            
            if response.status_code == 200:
                content_type = response.headers.get('content-type', '')
                content_length = len(response.content)
                
                verifications = []
                
                if 'application/pdf' in content_type:
                    verifications.append("✅ Content-Type: application/pdf")
                else:
                    verifications.append(f"❌ Content-Type: {content_type}")
                
                if content_length > 0:
                    verifications.append(f"✅ Taille du fichier: {content_length} bytes")
                else:
                    verifications.append("❌ Fichier vide")
                
                all_verified = all("✅" in v for v in verifications)
                self.log_result("4.2 Employee Invoice Download", all_verified, 
                              f"Status: 200 OK - {'; '.join(verifications)}")
                
                return all_verified
            else:
                self.log_result("4.2 Employee Invoice Download", False, 
                              f"Status: {response.status_code}", response.text)
                return False
                
        except Exception as e:
            self.log_result("4.2 Employee Invoice Download", False, "Exception occurred", str(e))
            return False

    def test_5_client_downloads_initial_payment_invoice(self):
        """TEST 5 - Client télécharge une facture de paiement initial (création)"""
        print("\n" + "="*60)
        print("TEST 5 - CLIENT TÉLÉCHARGE FACTURE DE PAIEMENT INITIAL (CRÉATION)")
        print("="*60)
        
        # 1. Find a client with first_payment_amount > 0
        print("\n🔸 ÉTAPE 5.1 - Trouver un client avec paiement initial")
        
        try:
            headers = {"Authorization": f"Bearer {self.tokens['manager']}"}
            
            # Get all clients
            response = self.session.get(f"{API_BASE}/clients", headers=headers)
            if response.status_code != 200:
                self.log_result("5.1 Find Client with Initial Payment", False, 
                              f"Cannot get clients: {response.status_code}")
                return False
            
            clients = response.json()
            target_client = None
            
            # Look for client with first_payment_amount or recent creation
            for client in clients:
                if client.get('first_payment_amount', 0) > 0:
                    target_client = client
                    break
            
            if not target_client:
                # If no client with first_payment_amount, use any recent client
                if clients:
                    target_client = clients[0]  # Use first client as fallback
                else:
                    self.log_result("5.1 Find Client with Initial Payment", False, 
                                  "No clients found")
                    return False
            
            client_email = target_client.get('email')
            if not client_email:
                # Try common patterns
                client_email = 'client@test.com'
            
            self.log_result("5.1 Find Client with Initial Payment", True, 
                          f"Client trouvé: {target_client.get('full_name', 'N/A')} - {client_email}")
            
        except Exception as e:
            self.log_result("5.1 Find Client with Initial Payment", False, "Exception occurred", str(e))
            return False
        
        # 2. Login as this client
        print("\n🔸 ÉTAPE 5.2 - Se connecter en tant que client")
        
        client_credentials = {
            "email": client_email,
            "password": "Aloria2024!"
        }
        
        if not self.authenticate_user('initial_client', client_credentials):
            self.log_result("5.2 Initial Client Authentication", False, 
                          f"Cannot login as client: {client_email}")
            return False
        
        # 3. Get client's payments and find initial payment
        print("\n🔸 ÉTAPE 5.3 - Récupérer le paiement initial")
        
        client_headers = {"Authorization": f"Bearer {self.tokens['initial_client']}"}
        
        try:
            response = self.session.get(f"{API_BASE}/payments", headers=client_headers)
            if response.status_code != 200:
                self.log_result("5.3 Get Initial Payment", False, 
                              f"Status: {response.status_code}")
                return False
            
            payments = response.json()
            initial_payment = None
            
            # Look for payment with "Premier versement" description
            for payment in payments:
                description = payment.get('description', '').lower()
                if 'premier' in description or 'initial' in description:
                    initial_payment = payment
                    break
            
            if not initial_payment and payments:
                # Use first payment as fallback
                initial_payment = payments[0]
            
            if not initial_payment:
                self.log_result("5.3 Get Initial Payment", False, 
                              "No initial payment found")
                return False
            
            payment_id = initial_payment['id']
            self.log_result("5.3 Get Initial Payment", True, 
                          f"Paiement initial trouvé: {payment_id}")
            
        except Exception as e:
            self.log_result("5.3 Get Initial Payment", False, "Exception occurred", str(e))
            return False
        
        # 4. Download the invoice
        print("\n🔸 ÉTAPE 5.4 - Télécharger la facture du paiement initial")
        
        try:
            response = self.session.get(f"{API_BASE}/payments/{payment_id}/invoice", headers=client_headers)
            
            if response.status_code == 200:
                content_type = response.headers.get('content-type', '')
                content_length = len(response.content)
                
                verifications = []
                
                if 'application/pdf' in content_type:
                    verifications.append("✅ Content-Type: application/pdf")
                else:
                    verifications.append(f"❌ Content-Type: {content_type}")
                
                if content_length > 0:
                    verifications.append(f"✅ Taille du fichier: {content_length} bytes")
                else:
                    verifications.append("❌ Fichier vide")
                
                all_verified = all("✅" in v for v in verifications)
                self.log_result("5.4 Initial Payment Invoice Download", all_verified, 
                              f"Status: 200 OK - {'; '.join(verifications)}")
                
                return all_verified
            else:
                self.log_result("5.4 Initial Payment Invoice Download", False, 
                              f"Status: {response.status_code}", response.text)
                return False
                
        except Exception as e:
            self.log_result("5.4 Initial Payment Invoice Download", False, "Exception occurred", str(e))
            return False

    def run_invoice_download_tests(self):
        """Run all invoice download tests"""
        print("ALORIA AGENCY - Test Téléchargement de Factures - CLIENT vs MANAGER")
        print("Test spécifique pour le bug de permission 403")
        print("="*80)
        
        # Authentication
        if not self.authenticate_users():
            print("❌ ÉCHEC: Impossible d'authentifier les utilisateurs")
            return False
        
        # Test 1: Manager downloads invoice (baseline)
        print("\n" + "🔹" * 20 + " TESTS PRINCIPAUX " + "🔹" * 20)
        test1_success = self.test_1_manager_downloads_invoice()
        
        # Test 2: Client downloads own invoice (bug fix)
        test2_success = self.test_2_client_downloads_own_invoice()
        
        # Test 3: Client cannot download other client's invoice (security)
        test3_success = self.test_3_client_cannot_download_other_client_invoice()
        
        # Test 4: Employee downloads assigned client invoice
        test4_success = self.test_4_employee_downloads_assigned_client_invoice()
        
        # Test 5: Client downloads initial payment invoice
        test5_success = self.test_5_client_downloads_initial_payment_invoice()
        
        # Final results
        print("\n" + "="*80)
        print("RÉSULTATS FINAUX - TÉLÉCHARGEMENT DE FACTURES")
        print("="*80)
        
        total_tests = self.results['passed'] + self.results['failed']
        success_rate = (self.results['passed'] / total_tests * 100) if total_tests > 0 else 0
        
        print(f"✅ Tests réussis: {self.results['passed']}")
        print(f"❌ Tests échoués: {self.results['failed']}")
        print(f"📊 Taux de réussite: {success_rate:.1f}%")
        
        # Critical test results
        print(f"\n🎯 RÉSULTATS CRITIQUES:")
        print(f"   TEST 1 - Manager télécharge facture: {'✅ PASS' if test1_success else '❌ FAIL'}")
        print(f"   TEST 2 - Client télécharge SA facture: {'✅ PASS' if test2_success else '❌ FAIL'} (BUG FIX)")
        print(f"   TEST 3 - Client bloqué pour autre facture: {'✅ PASS' if test3_success else '❌ FAIL'} (SÉCURITÉ)")
        print(f"   TEST 4 - Employee télécharge facture assignée: {'✅ PASS' if test4_success else '❌ FAIL'}")
        print(f"   TEST 5 - Client télécharge facture initiale: {'✅ PASS' if test5_success else '❌ FAIL'}")
        
        if self.results['errors']:
            print(f"\n🚨 ERREURS DÉTECTÉES:")
            for error in self.results['errors']:
                print(f"   - {error['test']}: {error['message']}")
                if error['error']:
                    print(f"     Détail: {error['error']}")
        
        # Determine overall success
        critical_tests_passed = sum([test1_success, test2_success, test3_success])
        overall_success = critical_tests_passed >= 2 and test2_success  # Test 2 is the main bug fix
        
        return overall_success

if __name__ == "__main__":
    tester = InvoiceDownloadTester()
    success = tester.run_invoice_download_tests()
    
    if success:
        print("\n🎉 TEST TÉLÉCHARGEMENT DE FACTURES: SUCCÈS")
        print("✅ Le bug de permission 403 pour les clients est corrigé!")
        sys.exit(0)
    else:
        print("\n💥 TEST TÉLÉCHARGEMENT DE FACTURES: ÉCHEC")
        print("❌ Le bug de permission 403 persiste ou autres problèmes détectés")
        sys.exit(1)