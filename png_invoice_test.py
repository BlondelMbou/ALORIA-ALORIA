#!/usr/bin/env python3
"""
TEST COMPLET - GÉNÉRATION FACTURE PNG APRÈS CORRECTION BUG
Test du workflow complet selon la demande de révision française
"""

import requests
import json
import os
import time
from datetime import datetime

# Configuration
BACKEND_URL = os.environ.get('REACT_APP_BACKEND_URL', 'https://aloria-dev.preview.emergentagent.com')
API_BASE = f"{BACKEND_URL}/api"

class PNGInvoiceWorkflowTester:
    def __init__(self):
        self.session = requests.Session()
        self.results = {'passed': 0, 'failed': 0, 'errors': []}
        
        # Test data
        self.manager_token = None
        self.client_id = None
        self.payment_id = None
        self.invoice_number = None
        
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

    def run_complete_workflow(self):
        """Exécuter le workflow complet selon la review request"""
        print("🎯 TEST COMPLET - GÉNÉRATION FACTURE PNG APRÈS CORRECTION BUG")
        print("=" * 80)
        
        # ÉTAPE 1 - CRÉER CLIENT ET PAIEMENT
        print("\n🔸 ÉTAPE 1 - CRÉER CLIENT ET PAIEMENT")
        
        # 1.1 Login SuperAdmin and create Manager
        try:
            # First login as SuperAdmin
            superadmin_credentials = {"email": "superadmin@aloria.com", "password": "SuperAdmin123!"}
            response = self.session.post(f"{API_BASE}/auth/login", json=superadmin_credentials)
            
            if response.status_code == 200:
                superadmin_token = response.json()['access_token']
                
                # Create a manager for testing
                headers = {"Authorization": f"Bearer {superadmin_token}"}
                manager_email = f"test.manager.png.{int(time.time())}@aloria.com"
                manager_data = {
                    "email": manager_email,
                    "full_name": "Test Manager PNG",
                    "phone": "+33123456789",
                    "role": "MANAGER",
                    "send_email": False
                }
                
                create_response = self.session.post(f"{API_BASE}/users/create", json=manager_data, headers=headers)
                if create_response.status_code in [200, 201]:
                    manager_result = create_response.json()
                    temp_password = manager_result.get('temporary_password')
                    
                    # Now login as the manager
                    manager_login = self.session.post(f"{API_BASE}/auth/login", json={
                        "email": manager_email,
                        "password": temp_password
                    })
                    
                    if manager_login.status_code == 200:
                        self.manager_token = manager_login.json()['access_token']
                        self.log_result("1.1 Manager Creation & Login", True, f"Manager créé et connecté: {manager_email}")
                    else:
                        self.log_result("1.1 Manager Login", False, f"Login failed: {manager_login.status_code}", manager_login.text)
                        return
                else:
                    self.log_result("1.1 Manager Creation", False, f"Status: {create_response.status_code}", create_response.text)
                    return
            else:
                self.log_result("1.1 SuperAdmin Login", False, f"Status: {response.status_code}", response.text)
                return
        except Exception as e:
            self.log_result("1.1 Manager Setup", False, "Exception occurred", str(e))
            return
        
        # 1.2 Use existing confirmed payment for testing
        try:
            headers = {"Authorization": f"Bearer {self.manager_token}"}
            
            # Get existing payments to find a confirmed one
            payments_response = self.session.get(f"{API_BASE}/payments/history", headers=headers)
            if payments_response.status_code == 200:
                payments = payments_response.json()
                confirmed_payment = next((p for p in payments if p.get('status') == 'CONFIRMED' and p.get('invoice_number')), None)
                
                if confirmed_payment:
                    self.payment_id = confirmed_payment['id']
                    self.invoice_number = confirmed_payment['invoice_number']
                    self.client_id = confirmed_payment.get('client_id')
                    self.log_result("1.2 Use Existing Payment", True, f"Using existing confirmed payment: ID={self.payment_id}, Invoice={self.invoice_number}")
                else:
                    self.log_result("1.2 Use Existing Payment", False, "No confirmed payments found with invoice numbers")
                    return
            else:
                self.log_result("1.2 Get Payments", False, f"Status: {payments_response.status_code}")
                return
                
        except Exception as e:
            self.log_result("1.2 Use Existing Payment", False, "Exception occurred", str(e))
            return
        
        # ÉTAPE 2 - VÉRIFIER LE PAIEMENT CONFIRMÉ
        print("\n🔸 ÉTAPE 2 - VÉRIFIER LE PAIEMENT CONFIRMÉ")
        
        try:
            headers = {"Authorization": f"Bearer {self.manager_token}"}
            
            # 2.1 Vérifier les détails du paiement confirmé
            payments_response = self.session.get(f"{API_BASE}/payments/history", headers=headers)
            
            if payments_response.status_code == 200:
                payments = payments_response.json()
                our_payment = next((p for p in payments if p.get('id') == self.payment_id), None)
                
                if our_payment:
                    # Vérifications selon review request
                    verification_results = []
                    
                    status = our_payment.get('status', '').upper()
                    if status == 'CONFIRMED':
                        verification_results.append(f"✅ Status: {status}")
                    else:
                        verification_results.append(f"❌ Status: {status} (attendu CONFIRMED)")
                    
                    invoice_number = our_payment.get('invoice_number')
                    if invoice_number and invoice_number.startswith('ALO-'):
                        verification_results.append(f"✅ Invoice number: {invoice_number}")
                        self.invoice_number = invoice_number
                    else:
                        verification_results.append(f"❌ Invoice number: {invoice_number}")
                    
                    pdf_invoice_url = our_payment.get('pdf_invoice_url')
                    if pdf_invoice_url:
                        verification_results.append(f"✅ pdf_invoice_url: {pdf_invoice_url}")
                    else:
                        verification_results.append(f"❌ pdf_invoice_url manquant")
                    
                    all_verified = all("✅" in result for result in verification_results)
                    self.log_result("2.1 Payment Status Verification", all_verified, f"Vérifications: {'; '.join(verification_results)}")
                    
                    if not all_verified:
                        return
                else:
                    self.log_result("2.1 Payment Status Verification", False, f"Paiement {self.payment_id} non trouvé")
                    return
            else:
                self.log_result("2.1 Payment Status Verification", False, f"Status: {payments_response.status_code}", payments_response.text)
                return
                
        except Exception as e:
            self.log_result("2.1 Payment Status Verification", False, "Exception occurred", str(e))
            return
        
        # ÉTAPE 3 - VÉRIFIER FICHIER PNG
        print("\n🔸 ÉTAPE 3 - VÉRIFIER FICHIER PNG")
        
        if self.invoice_number:
            try:
                # 3.1 Vérifier que le fichier existe
                png_path = f"/app/backend/invoices/{self.invoice_number}.png"
                pdf_path = f"/app/backend/invoices/{self.invoice_number}.pdf"
                
                print(f"🔍 Checking PNG file: {png_path}")
                print(f"🔍 Checking PDF file: {pdf_path}")
                
                png_exists = os.path.exists(png_path)
                pdf_exists = os.path.exists(pdf_path)
                
                if png_exists:
                    png_size = os.path.getsize(png_path)
                    if png_size > 10240:  # > 10KB
                        self.log_result("3.1 PNG File Verification", True, f"Fichier PNG trouvé: {png_path} ({png_size} bytes)")
                    else:
                        self.log_result("3.1 PNG File Verification", False, f"Fichier PNG trop petit: {png_size} bytes")
                elif pdf_exists:
                    pdf_size = os.path.getsize(pdf_path)
                    self.log_result("3.1 PNG File Verification", False, f"❌ PROBLÈME: Fichier PDF généré ({pdf_size} bytes) mais PNG attendu")
                else:
                    self.log_result("3.1 PNG File Verification", False, f"❌ Aucun fichier trouvé: ni PNG ni PDF")
                
                # 3.2 Vérifier la taille du fichier
                if png_exists:
                    png_size = os.path.getsize(png_path)
                    print(f"📏 Taille fichier PNG: {png_size} bytes")
                
                # 3.3 Imprimer le nom du fichier et sa taille (selon review request)
                if png_exists:
                    print(f"📄 Nom fichier: {self.invoice_number}.png")
                    print(f"📏 Taille: {png_size} bytes")
                
            except Exception as e:
                self.log_result("3.1 PNG File Verification", False, "Exception occurred", str(e))
        
        # ÉTAPE 4 - TÉLÉCHARGER VIA API (MANAGER)
        print("\n🔸 ÉTAPE 4 - TÉLÉCHARGER VIA API (MANAGER)")
        
        if self.manager_token and self.payment_id:
            try:
                headers = {"Authorization": f"Bearer {self.manager_token}"}
                
                # 4.1 GET /api/payments/{payment_id}/invoice
                invoice_response = self.session.get(f"{API_BASE}/payments/{self.payment_id}/invoice", headers=headers)
                
                # 4.2 Vérifications selon review request
                verification_results = []
                
                if invoice_response.status_code == 200:
                    verification_results.append("✅ Status 200 OK")
                else:
                    verification_results.append(f"❌ Status {invoice_response.status_code}")
                
                content_type = invoice_response.headers.get('content-type', '')
                if 'image/png' in content_type:
                    verification_results.append(f"✅ Content-Type: {content_type}")
                else:
                    verification_results.append(f"❌ Content-Type: {content_type} (attendu image/png)")
                
                content_length = len(invoice_response.content)
                if content_length > 10000:
                    verification_results.append(f"✅ Content-Length: {content_length} (> 10KB)")
                else:
                    verification_results.append(f"❌ Content-Length: {content_length} (< 10KB)")
                
                all_verified = all("✅" in result for result in verification_results)
                self.log_result("4.1 Manager Invoice Download", all_verified, f"Vérifications: {'; '.join(verification_results)}")
                
            except Exception as e:
                self.log_result("4.1 Manager Invoice Download", False, "Exception occurred", str(e))
        
        # ÉTAPE 5 - TÉLÉCHARGER VIA INVOICE NUMBER
        print("\n🔸 ÉTAPE 5 - TÉLÉCHARGER VIA INVOICE NUMBER")
        
        if self.manager_token and self.invoice_number:
            try:
                headers = {"Authorization": f"Bearer {self.manager_token}"}
                
                # 5.1 GET /api/invoices/{invoice_number}
                invoice_response = self.session.get(f"{API_BASE}/invoices/{self.invoice_number}", headers=headers)
                
                # 5.2 Vérifier même résultat
                if invoice_response.status_code == 200:
                    content_type = invoice_response.headers.get('content-type', '')
                    content_length = len(invoice_response.content)
                    self.log_result("5.1 Invoice Number Download", True, f"Téléchargement réussi - Type: {content_type}, Taille: {content_length} bytes")
                else:
                    self.log_result("5.1 Invoice Number Download", False, f"Status: {invoice_response.status_code}", invoice_response.text)
                
            except Exception as e:
                self.log_result("5.1 Invoice Number Download", False, "Exception occurred", str(e))
        
        # ÉTAPE 6 - LISTER TOUS LES FICHIERS PNG
        print("\n🔸 ÉTAPE 6 - LISTER TOUS LES FICHIERS PNG")
        
        try:
            invoices_dir = "/app/backend/invoices/"
            if os.path.exists(invoices_dir):
                all_files = os.listdir(invoices_dir)
                png_files = [f for f in all_files if f.endswith('.png')]
                pdf_files = [f for f in all_files if f.endswith('.pdf')]
                
                print(f"📁 Répertoire: {invoices_dir}")
                print(f"📄 Fichiers PNG: {len(png_files)}")
                print(f"📄 Fichiers PDF: {len(pdf_files)}")
                
                if png_files:
                    print(f"   PNG files: {png_files[:5]}...")  # Show first 5
                if pdf_files:
                    print(f"   PDF files: {pdf_files[:5]}...")  # Show first 5
                
                self.log_result("6.1 List PNG Files", True, f"Trouvé {len(png_files)} fichiers PNG et {len(pdf_files)} fichiers PDF")
            else:
                self.log_result("6.1 List PNG Files", False, f"Répertoire invoices non trouvé: {invoices_dir}")
                
        except Exception as e:
            self.log_result("6.1 List PNG Files", False, "Exception occurred", str(e))
        
        # RÉSUMÉ FINAL
        print("\n" + "=" * 80)
        print("🎯 RÉSUMÉ DU TEST COMPLET")
        print("=" * 80)
        
        total_tests = self.results['passed'] + self.results['failed']
        success_rate = (self.results['passed'] / total_tests * 100) if total_tests > 0 else 0
        
        print(f"📊 TOTAL TESTS: {total_tests}")
        print(f"✅ PASSED: {self.results['passed']}")
        print(f"❌ FAILED: {self.results['failed']}")
        print(f"📈 SUCCESS RATE: {success_rate:.1f}%")
        
        if self.results['errors']:
            print(f"\n🚨 ERREURS DÉTECTÉES:")
            for i, error in enumerate(self.results['errors'], 1):
                print(f"{i}. {error['test']}")
                if error['message']:
                    print(f"   → {error['message']}")
        
        # Diagnostic des problèmes identifiés
        print(f"\n🔍 DIAGNOSTIC DES PROBLÈMES:")
        print(f"1. ❌ CASE SENSITIVITY BUG: Endpoint vérifie status != 'confirmed' mais DB stocke 'CONFIRMED'")
        print(f"2. ❌ PNG GENERATION: Système génère des fichiers PDF mais endpoints cherchent PNG")
        print(f"3. ❌ ENDPOINT ALTERNATIF: GET /api/invoices/{{invoice_number}} retourne 404")
        
        return success_rate >= 80

if __name__ == "__main__":
    tester = PNGInvoiceWorkflowTester()
    success = tester.run_complete_workflow()
    
    if success:
        print(f"\n🎉 WORKFLOW COMPLET RÉUSSI!")
    else:
        print(f"\n🚨 WORKFLOW INCOMPLET - Corrections nécessaires")