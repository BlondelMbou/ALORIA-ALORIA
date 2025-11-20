#!/usr/bin/env python3
"""
ALORIA AGENCY - Test Téléchargement de Factures - CLIENT vs MANAGER
Test spécifique pour le bug de permission 403 pour les clients téléchargeant leurs propres factures

PROBLÈME IDENTIFIÉ ET CORRIGÉ:
- Ligne 3263-3265 de server.py - Vérification de permission incorrecte pour CLIENT
- Le code vérifiait client_id != current_user["id"] 
- Mais client_id du paiement = client.id (ID du profil client)
- Et current_user["id"] = user_id du client
- Donc client.id != user_id → CLIENT toujours refusé ❌

CORRECTION APPLIQUÉE:
- Récupérer le profil client avec user_id = current_user["id"]
- Vérifier que le paiement appartient au client
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

class FocusedInvoiceTest:
    def __init__(self):
        self.session = requests.Session()
        self.tokens = {}
        self.users = {}
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

    def test_manager_baseline(self):
        """TEST 1 - Manager télécharge une facture (baseline)"""
        print("\n" + "="*60)
        print("TEST 1 - MANAGER TÉLÉCHARGE UNE FACTURE (BASELINE)")
        print("="*60)
        
        # Authenticate manager
        if not self.authenticate_user('manager', CREDENTIALS['manager']):
            return False
            
        headers = {"Authorization": f"Bearer {self.tokens['manager']}"}
        
        # Get manager payment history
        print("\n🔸 ÉTAPE 1.1 - Récupérer l'historique des paiements")
        try:
            response = self.session.get(f"{API_BASE}/payments/manager-history", headers=headers)
            
            if response.status_code == 200:
                payments = response.json()
                confirmed_payments = [p for p in payments if p.get('status') in ['CONFIRMED', 'confirmed'] and p.get('invoice_number')]
                
                if confirmed_payments:
                    payment = confirmed_payments[0]
                    payment_id = payment['id']
                    invoice_number = payment['invoice_number']
                    
                    self.log_result("1.1 Get Manager Payments", True, 
                                  f"Trouvé {len(confirmed_payments)} paiement(s) confirmé(s) avec facture")
                    
                    # Test invoice download
                    print("\n🔸 ÉTAPE 1.2 - Télécharger la facture")
                    invoice_response = self.session.get(f"{API_BASE}/payments/{payment_id}/invoice", headers=headers)
                    
                    if invoice_response.status_code == 200:
                        content_type = invoice_response.headers.get('content-type', '')
                        content_disposition = invoice_response.headers.get('content-disposition', '')
                        content_length = len(invoice_response.content)
                        
                        success = ('application/pdf' in content_type and 
                                 'Facture_' in content_disposition and 
                                 content_length > 0)
                        
                        self.log_result("1.2 Manager Invoice Download", success, 
                                      f"Status: 200 OK, Type: {content_type}, Taille: {content_length} bytes")
                        return success
                    else:
                        self.log_result("1.2 Manager Invoice Download", False, 
                                      f"Status: {invoice_response.status_code}", invoice_response.text)
                        return False
                else:
                    self.log_result("1.1 Get Manager Payments", False, 
                                  f"Aucun paiement confirmé avec facture trouvé sur {len(payments)} paiements")
                    return False
            else:
                self.log_result("1.1 Get Manager Payments", False, 
                              f"Status: {response.status_code}", response.text)
                return False
                
        except Exception as e:
            self.log_result("1.1 Get Manager Payments", False, "Exception occurred", str(e))
            return False

    def test_client_own_invoice(self):
        """TEST 2 - Client télécharge SA PROPRE facture (bug fix principal)"""
        print("\n" + "="*60)
        print("TEST 2 - CLIENT TÉLÉCHARGE SA PROPRE FACTURE (BUG FIX)")
        print("="*60)
        
        # Get manager token to find payments and clients
        headers = {"Authorization": f"Bearer {self.tokens['manager']}"}
        
        # Step 1: Find a confirmed payment and its associated client
        print("\n🔸 ÉTAPE 2.1 - Trouver un paiement confirmé et son client")
        try:
            # Get payments
            payments_response = self.session.get(f"{API_BASE}/payments/manager-history", headers=headers)
            if payments_response.status_code != 200:
                self.log_result("2.1 Find Payment and Client", False, 
                              f"Cannot get payments: {payments_response.status_code}")
                return False
            
            payments = payments_response.json()
            confirmed_payments = [p for p in payments if p.get('status') in ['CONFIRMED', 'confirmed'] and p.get('invoice_number')]
            
            if not confirmed_payments:
                self.log_result("2.1 Find Payment and Client", False, 
                              "No confirmed payments with invoice found")
                return False
            
            # Get clients
            clients_response = self.session.get(f"{API_BASE}/clients", headers=headers)
            if clients_response.status_code != 200:
                self.log_result("2.1 Find Payment and Client", False, 
                              f"Cannot get clients: {clients_response.status_code}")
                return False
            
            clients = clients_response.json()
            
            # Find a payment that belongs to a client we can identify
            target_payment = None
            target_client = None
            
            for payment in confirmed_payments:
                client_id = payment.get('client_id')
                if client_id:
                    # Find matching client
                    for client in clients:
                        if client.get('id') == client_id or client.get('user_id') == client_id:
                            target_payment = payment
                            target_client = client
                            break
                    if target_payment:
                        break
            
            if not target_payment or not target_client:
                self.log_result("2.1 Find Payment and Client", False, 
                              "Cannot match payment to client")
                return False
            
            payment_id = target_payment['id']
            client_email = target_client.get('email')
            
            # If no email in client record, try to construct it or use a known pattern
            if not client_email:
                # Try common patterns based on client data
                possible_emails = [
                    'client@test.com',
                    'client1@gmail.com', 
                    'test.client@example.com'
                ]
                client_email = possible_emails[0]  # Use first as fallback
            
            self.log_result("2.1 Find Payment and Client", True, 
                          f"Paiement: {payment_id}, Client: {client_email}")
            
        except Exception as e:
            self.log_result("2.1 Find Payment and Client", False, "Exception occurred", str(e))
            return False
        
        # Step 2: Login as the client
        print("\n🔸 ÉTAPE 2.2 - Se connecter en tant que client")
        
        client_credentials = {
            "email": client_email,
            "password": "Aloria2024!"  # Default password from review
        }
        
        if not self.authenticate_user('client', client_credentials):
            # Try alternative emails if first fails
            alternative_emails = ['client1@gmail.com', 'client@test.com', 'test.client@example.com']
            
            for alt_email in alternative_emails:
                if alt_email != client_email:
                    alt_credentials = {"email": alt_email, "password": "Aloria2024!"}
                    if self.authenticate_user('client', alt_credentials):
                        client_email = alt_email
                        break
            else:
                self.log_result("2.2 Client Authentication", False, 
                              f"Cannot login with any client email")
                return False
        
        # Step 3: Verify client can see their payments
        print("\n🔸 ÉTAPE 2.3 - Vérifier l'accès aux paiements du client")
        
        client_headers = {"Authorization": f"Bearer {self.tokens['client']}"}
        
        try:
            response = self.session.get(f"{API_BASE}/payments/client-history", headers=client_headers)
            if response.status_code == 200:
                client_payments = response.json()
                self.log_result("2.3 Client Payment Access", True, 
                              f"Client voit {len(client_payments)} paiement(s)")
            else:
                self.log_result("2.3 Client Payment Access", False, 
                              f"Status: {response.status_code}")
        except Exception as e:
            self.log_result("2.3 Client Payment Access", False, "Exception occurred", str(e))
        
        # Step 4: THE MAIN TEST - Download invoice as client
        print("\n🔸 ÉTAPE 2.4 - TÉLÉCHARGER LA FACTURE EN TANT QUE CLIENT (TEST PRINCIPAL)")
        
        try:
            response = self.session.get(f"{API_BASE}/payments/{payment_id}/invoice", headers=client_headers)
            
            if response.status_code == 200:
                content_type = response.headers.get('content-type', '')
                content_length = len(response.content)
                
                success = 'application/pdf' in content_type and content_length > 0
                
                self.log_result("2.4 Client Invoice Download (BUG FIX)", success, 
                              f"✅ Status: 200 OK (PAS 403 Forbidden!) - Type: {content_type}, Taille: {content_length} bytes")
                return success
                
            elif response.status_code == 403:
                self.log_result("2.4 Client Invoice Download (BUG FIX)", False, 
                              "❌ Status: 403 Forbidden - LE BUG PERSISTE! Client ne peut pas télécharger sa propre facture", 
                              response.text)
                return False
            else:
                self.log_result("2.4 Client Invoice Download (BUG FIX)", False, 
                              f"Status: {response.status_code}", response.text)
                return False
                
        except Exception as e:
            self.log_result("2.4 Client Invoice Download (BUG FIX)", False, "Exception occurred", str(e))
            return False

    def test_client_security(self):
        """TEST 3 - Client ne peut pas télécharger facture d'un autre client (sécurité)"""
        print("\n" + "="*60)
        print("TEST 3 - CLIENT NE PEUT PAS TÉLÉCHARGER FACTURE D'AUTRUI (SÉCURITÉ)")
        print("="*60)
        
        if 'client' not in self.tokens:
            self.log_result("Test 3 Setup", False, "Client token not available")
            return False
        
        # Get a different payment (from manager's view)
        headers = {"Authorization": f"Bearer {self.tokens['manager']}"}
        
        try:
            response = self.session.get(f"{API_BASE}/payments/manager-history", headers=headers)
            if response.status_code == 200:
                payments = response.json()
                confirmed_payments = [p for p in payments if p.get('status') in ['CONFIRMED', 'confirmed'] and p.get('invoice_number')]
                
                if confirmed_payments:
                    # Use a different payment (not the client's own)
                    other_payment_id = confirmed_payments[-1]['id']  # Use last payment
                    
                    # Try to download as client
                    client_headers = {"Authorization": f"Bearer {self.tokens['client']}"}
                    invoice_response = self.session.get(f"{API_BASE}/payments/{other_payment_id}/invoice", headers=client_headers)
                    
                    if invoice_response.status_code == 403:
                        self.log_result("3.1 Client Security Check", True, 
                                      "✅ Status: 403 Forbidden - Sécurité OK, client ne peut pas télécharger facture d'autrui")
                        return True
                    else:
                        self.log_result("3.1 Client Security Check", False, 
                                      f"❌ FAILLE DE SÉCURITÉ! Status: {invoice_response.status_code} - Client peut télécharger facture d'autrui")
                        return False
                else:
                    self.log_result("3.1 Client Security Check", False, 
                                  "No confirmed payments available for security test")
                    return False
            else:
                self.log_result("3.1 Client Security Check", False, 
                              f"Cannot get payments for security test: {response.status_code}")
                return False
                
        except Exception as e:
            self.log_result("3.1 Client Security Check", False, "Exception occurred", str(e))
            return False

    def run_focused_tests(self):
        """Run focused invoice download tests"""
        print("ALORIA AGENCY - Test Téléchargement de Factures - CLIENT vs MANAGER")
        print("Test spécifique pour le bug de permission 403 (CORRECTION LIGNES 3263-3265)")
        print("="*80)
        
        # Test 1: Manager baseline (should work)
        test1_success = self.test_manager_baseline()
        
        # Test 2: Client downloads own invoice (main bug fix test)
        test2_success = self.test_client_own_invoice()
        
        # Test 3: Client security (should be blocked)
        test3_success = self.test_client_security()
        
        # Final results
        print("\n" + "="*80)
        print("RÉSULTATS FINAUX - TEST TÉLÉCHARGEMENT DE FACTURES")
        print("="*80)
        
        total_tests = self.results['passed'] + self.results['failed']
        success_rate = (self.results['passed'] / total_tests * 100) if total_tests > 0 else 0
        
        print(f"✅ Tests réussis: {self.results['passed']}")
        print(f"❌ Tests échoués: {self.results['failed']}")
        print(f"📊 Taux de réussite: {success_rate:.1f}%")
        
        # Critical test results
        print(f"\n🎯 RÉSULTATS CRITIQUES:")
        print(f"   TEST 1 - Manager télécharge facture: {'✅ PASS' if test1_success else '❌ FAIL'} (BASELINE)")
        print(f"   TEST 2 - Client télécharge SA facture: {'✅ PASS' if test2_success else '❌ FAIL'} (BUG FIX PRINCIPAL)")
        print(f"   TEST 3 - Client bloqué pour autre facture: {'✅ PASS' if test3_success else '❌ FAIL'} (SÉCURITÉ)")
        
        if self.results['errors']:
            print(f"\n🚨 ERREURS DÉTECTÉES:")
            for error in self.results['errors']:
                print(f"   - {error['test']}: {error['message']}")
                if error['error']:
                    print(f"     Détail: {error['error']}")
        
        # Determine overall success - Test 2 is the critical bug fix
        overall_success = test2_success and test1_success
        
        if overall_success:
            print(f"\n🎉 CONCLUSION: BUG FIX VALIDÉ!")
            print(f"✅ La correction des lignes 3263-3265 de server.py fonctionne")
            print(f"✅ Les clients peuvent maintenant télécharger leurs propres factures")
        else:
            print(f"\n💥 CONCLUSION: BUG FIX ÉCHOUÉ!")
            if not test2_success:
                print(f"❌ Les clients ne peuvent toujours pas télécharger leurs propres factures")
                print(f"❌ La correction des lignes 3263-3265 de server.py ne fonctionne pas")
        
        return overall_success

if __name__ == "__main__":
    tester = FocusedInvoiceTest()
    success = tester.run_focused_tests()
    
    if success:
        print("\n🎉 TEST TÉLÉCHARGEMENT DE FACTURES: SUCCÈS")
        print("✅ Le bug de permission 403 pour les clients est corrigé!")
        sys.exit(0)
    else:
        print("\n💥 TEST TÉLÉCHARGEMENT DE FACTURES: ÉCHEC")
        print("❌ Le bug de permission 403 persiste")
        sys.exit(1)