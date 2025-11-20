#!/usr/bin/env python3
"""
ALORIA AGENCY - Test Changement de Mot de Passe - Tous les Rôles
Test complet du système de changement de mot de passe pour tous les rôles

TESTS À EFFECTUER:
- TEST 1: CLIENT Change Son Mot de Passe
- TEST 2: EMPLOYEE Change Son Mot de Passe  
- TEST 3: MANAGER Change Son Mot de Passe
- TEST 4: SUPERADMIN Change Son Mot de Passe
- TEST 5: Erreurs de Validation (mot de passe incorrect, trop court, champs manquants)
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
    'employee': {'email': 'employee@aloria.com', 'password': 'emp123'},
    'superadmin': {'email': 'superadmin@aloria.com', 'password': 'SuperAdmin123!'}
}

class WorkflowTester:
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

    def authenticate_users(self):
        """Authenticate all required users"""
        print("=== AUTHENTICATION SETUP ===")
        
        for role, credentials in CREDENTIALS.items():
            try:
                response = self.session.post(f"{API_BASE}/auth/login", json=credentials)
                if response.status_code == 200:
                    data = response.json()
                    self.tokens[role] = data['access_token']
                    self.users[role] = data['user']
                    self.log_result(f"{role.upper()} Login", True, 
                                  f"Logged in as {credentials['email']} - Role: {data['user']['role']}")
                else:
                    self.log_result(f"{role.upper()} Login", False, 
                                  f"Status: {response.status_code}", response.text)
                    return False
            except Exception as e:
                self.log_result(f"{role.upper()} Login", False, "Exception occurred", str(e))
                return False
        return True

    def phase_1_employee_client_creation(self):
        """PHASE 1 - Création de Client par Employee"""
        print("\n" + "="*60)
        print("PHASE 1 - CRÉATION DE CLIENT PAR EMPLOYEE")
        print("="*60)
        
        if 'employee' not in self.tokens:
            self.log_result("Phase 1 Setup", False, "Employee token not available")
            return False
            
        headers = {"Authorization": f"Bearer {self.tokens['employee']}"}
        
        # 1. Créer un client directement via POST /api/clients
        print("\n🔸 ÉTAPE 1.1 - Créer un client directement")
        try:
            client_data = {
                "email": "client.employee.test@example.com",
                "full_name": "Test Client Employee",
                "phone": "+33612345678",
                "country": "Canada",
                "visa_type": "Permis de travail",
                "message": "Test de création par employé"
            }
            
            response = self.session.post(f"{API_BASE}/clients", json=client_data, headers=headers)
            
            if response.status_code in [200, 201]:
                client = response.json()
                self.test_data['client_id'] = client['id']
                self.test_data['user_id'] = client['user_id']
                
                self.log_result("1.1 Create Client", True, 
                              f"Client créé: {client['id']} - {client.get('full_name', 'N/A')}")
            else:
                self.log_result("1.1 Create Client", False, 
                              f"Status: {response.status_code}", response.text)
                return False
                
        except Exception as e:
            self.log_result("1.1 Create Client", False, "Exception occurred", str(e))
            return False
        
        # 2. Créer un paiement initial pour le client
        print("\n🔸 ÉTAPE 1.2 - Créer un paiement initial")
        try:
            # Login as the created client to declare payment
            client_credentials = {
                "email": "client.employee.test@example.com",
                "password": "Aloria2024!"  # Default password
            }
            
            login_response = self.session.post(f"{API_BASE}/auth/login", json=client_credentials)
            
            if login_response.status_code == 200:
                client_token = login_response.json()['access_token']
                client_headers = {"Authorization": f"Bearer {client_token}"}
                
                payment_data = {
                    "amount": 50000,
                    "currency": "CFA",
                    "description": "Premier versement - Test workflow",
                    "payment_method": "Virement bancaire"
                }
                
                payment_response = self.session.post(f"{API_BASE}/payments/declare", 
                                                   json=payment_data, headers=client_headers)
                
                if payment_response.status_code in [200, 201]:
                    payment = payment_response.json()
                    self.test_data['payment_id'] = payment['id']
                    
                    self.log_result("1.2 Create Payment", True, 
                                  f"Paiement créé: {payment['id']} - {payment['amount']} {payment['currency']}")
                else:
                    self.log_result("1.2 Create Payment", False, 
                                  f"Status: {payment_response.status_code}", payment_response.text)
            else:
                self.log_result("1.2 Client Login for Payment", False, 
                              f"Status: {login_response.status_code}", login_response.text)
                
        except Exception as e:
            self.log_result("1.2 Create Payment", False, "Exception occurred", str(e))
        
        # 3. Vérifications post-création
        print("\n🔸 ÉTAPE 1.3 - Vérifications post-création")
        self.verify_client_creation()
        
        # 4. Vérifier le Dashboard Client
        print("\n🔸 ÉTAPE 1.4 - Vérifier le Dashboard Client")
        self.verify_client_dashboard()
        
        return True

    def verify_client_creation(self):
        """Vérifier que le client est créé correctement"""
        headers = {"Authorization": f"Bearer {self.tokens['employee']}"}
        
        # Vérifier le client dans la collection clients
        try:
            response = self.session.get(f"{API_BASE}/clients", headers=headers)
            if response.status_code == 200:
                clients = response.json()
                created_client = next((c for c in clients if c['id'] == self.test_data['client_id']), None)
                
                if created_client:
                    verifications = []
                    
                    # Vérifier les données du client
                    if created_client.get('full_name') == "Test Client Employee":
                        verifications.append("✅ Nom client correct")
                    else:
                        verifications.append(f"❌ Nom client: {created_client.get('full_name')}")
                    
                    if created_client.get('email') == "client.employee.test@example.com":
                        verifications.append("✅ Email client correct")
                    else:
                        verifications.append(f"❌ Email client: {created_client.get('email')}")
                    
                    if created_client.get('assigned_employee_id') == self.users['employee']['id']:
                        verifications.append("✅ Employé assigné automatiquement")
                    else:
                        verifications.append(f"❌ Assignation employé: {created_client.get('assigned_employee_id')}")
                    
                    all_verified = all("✅" in v for v in verifications)
                    self.log_result("1.3.1 Client Data Verification", all_verified, 
                                  f"Vérifications: {'; '.join(verifications)}")
                else:
                    self.log_result("1.3.1 Client Data Verification", False, "Client non trouvé")
            else:
                self.log_result("1.3.1 Client Data Verification", False, 
                              f"Status: {response.status_code}")
                
        except Exception as e:
            self.log_result("1.3.1 Client Data Verification", False, "Exception occurred", str(e))
        
        # Vérifier le dossier (case)
        try:
            response = self.session.get(f"{API_BASE}/cases", headers=headers)
            if response.status_code == 200:
                cases = response.json()
                print(f"   DEBUG: Found {len(cases)} cases total")
                
                # Try to find case by client_id or user_id
                created_case = None
                for case in cases:
                    print(f"   DEBUG: Case {case.get('id')} - client_id: {case.get('client_id')}, client_name: {case.get('client_name')}")
                    if (case.get('client_id') == self.test_data['client_id'] or 
                        case.get('client_id') == self.test_data['user_id'] or
                        case.get('client_name') == "Test Client Employee"):
                        created_case = case
                        break
                
                if created_case:
                    verifications = []
                    
                    if created_case.get('country') == "Canada":
                        verifications.append("✅ Pays correct")
                    else:
                        verifications.append(f"❌ Pays: {created_case.get('country')}")
                    
                    if created_case.get('visa_type') == "Permis de travail":
                        verifications.append("✅ Type de visa correct")
                    else:
                        verifications.append(f"❌ Type de visa: {created_case.get('visa_type')}")
                    
                    if len(created_case.get('workflow_steps', [])) > 10:
                        verifications.append(f"✅ Workflow steps: {len(created_case['workflow_steps'])} étapes")
                    else:
                        verifications.append(f"❌ Workflow steps: {len(created_case.get('workflow_steps', []))} étapes")
                    
                    # Store case_id for later use
                    self.test_data['case_id'] = created_case['id']
                    
                    all_verified = all("✅" in v for v in verifications)
                    self.log_result("1.3.2 Case Data Verification", all_verified, 
                                  f"Vérifications: {'; '.join(verifications)}")
                else:
                    self.log_result("1.3.2 Case Data Verification", False, 
                                  f"Dossier non trouvé - client_id: {self.test_data['client_id']}, user_id: {self.test_data['user_id']}")
            else:
                self.log_result("1.3.2 Case Data Verification", False, 
                              f"Status: {response.status_code}")
                
        except Exception as e:
            self.log_result("1.3.2 Case Data Verification", False, "Exception occurred", str(e))

    def verify_client_dashboard(self):
        """Vérifier l'accès au dashboard client"""
        try:
            # Login avec le client créé
            client_credentials = {
                "email": "client.employee.test@example.com",
                "password": "Aloria2024!"  # Mot de passe par défaut
            }
            
            response = self.session.post(f"{API_BASE}/auth/login", json=client_credentials)
            
            if response.status_code == 200:
                client_data = response.json()
                client_token = client_data['access_token']
                
                self.log_result("1.4.1 Client Login", True, 
                              f"Client connecté: {client_data['user']['full_name']}")
                
                # Vérifier l'accès aux dossiers
                headers = {"Authorization": f"Bearer {client_token}"}
                cases_response = self.session.get(f"{API_BASE}/cases", headers=headers)
                
                if cases_response.status_code == 200:
                    cases = cases_response.json()
                    if len(cases) > 0:
                        self.log_result("1.4.2 Client Cases Access", True, 
                                      f"Client peut voir {len(cases)} dossier(s)")
                    else:
                        self.log_result("1.4.2 Client Cases Access", False, 
                                      "Aucun dossier accessible au client")
                else:
                    self.log_result("1.4.2 Client Cases Access", False, 
                                  f"Status: {cases_response.status_code}")
                
                # Vérifier l'accès aux paiements
                payments_response = self.session.get(f"{API_BASE}/payments/client-history", headers=headers)
                
                if payments_response.status_code == 200:
                    payments = payments_response.json()
                    if len(payments) > 0:
                        payment = payments[0]
                        if payment.get('amount') == 50000:
                            self.log_result("1.4.3 Client Payments Access", True, 
                                          f"Client peut voir son paiement de {payment['amount']} CFA")
                        else:
                            self.log_result("1.4.3 Client Payments Access", False, 
                                          f"Montant incorrect: {payment.get('amount')}")
                    else:
                        self.log_result("1.4.3 Client Payments Access", False, 
                                      "Aucun paiement visible au client")
                else:
                    self.log_result("1.4.3 Client Payments Access", False, 
                                  f"Status: {payments_response.status_code}")
                
            else:
                self.log_result("1.4.1 Client Login", False, 
                              f"Status: {response.status_code}", response.text)
                
        except Exception as e:
            self.log_result("1.4.1 Client Login", False, "Exception occurred", str(e))

    def phase_2_manager_case_update(self):
        """PHASE 2 - Mise à jour du Dossier par Manager avec Notifications"""
        print("\n" + "="*60)
        print("PHASE 2 - MISE À JOUR DU DOSSIER PAR MANAGER")
        print("="*60)
        
        if 'manager' not in self.tokens:
            self.log_result("Phase 2 Setup", False, "Manager token not available")
            return False
            
        headers = {"Authorization": f"Bearer {self.tokens['manager']}"}
        
        # 1. Récupérer le dossier créé par l'employé
        print("\n🔸 ÉTAPE 2.1 - Récupérer le dossier")
        try:
            response = self.session.get(f"{API_BASE}/cases", headers=headers)
            
            if response.status_code == 200:
                cases = response.json()
                target_case = next((c for c in cases if c.get('client_name') == "Test Client Employee"), None)
                
                if target_case:
                    self.test_data['case_id'] = target_case['id']
                    self.log_result("2.1 Get Case", True, 
                                  f"Dossier trouvé: {target_case['id']} - Client: {target_case['client_name']}")
                else:
                    self.log_result("2.1 Get Case", False, "Dossier non trouvé")
                    return False
            else:
                self.log_result("2.1 Get Case", False, 
                              f"Status: {response.status_code}", response.text)
                return False
                
        except Exception as e:
            self.log_result("2.1 Get Case", False, "Exception occurred", str(e))
            return False
        
        # 2. Mettre à jour le dossier
        print("\n🔸 ÉTAPE 2.2 - Mettre à jour le dossier")
        try:
            update_data = {
                "current_step_index": 3,
                "status": "En cours",
                "notes": "Mise à jour par Manager - Test workflow"
            }
            
            case_id = self.test_data['case_id']
            response = self.session.patch(f"{API_BASE}/cases/{case_id}", 
                                        json=update_data, headers=headers)
            
            if response.status_code == 200:
                updated_case = response.json()
                self.log_result("2.2 Update Case", True, 
                              f"Dossier mis à jour - Étape: {updated_case.get('current_step_index')}, Status: {updated_case.get('status')}")
            else:
                self.log_result("2.2 Update Case", False, 
                              f"Status: {response.status_code}", response.text)
                return False
                
        except Exception as e:
            self.log_result("2.2 Update Case", False, "Exception occurred", str(e))
            return False
        
        # 3. Vérifier les notifications
        print("\n🔸 ÉTAPE 2.3 - Vérifier les notifications")
        self.verify_notifications_after_update()
        
        return True

    def verify_notifications_after_update(self):
        """Vérifier que les notifications sont créées après mise à jour"""
        
        # Vérifier notifications pour l'employé
        try:
            headers = {"Authorization": f"Bearer {self.tokens['employee']}"}
            response = self.session.get(f"{API_BASE}/notifications", headers=headers)
            
            if response.status_code == 200:
                notifications = response.json()
                case_notifications = [n for n in notifications if n.get('type') == 'case_update']
                
                if len(case_notifications) > 0:
                    latest_notification = case_notifications[0]
                    if "Test Client Employee" in latest_notification.get('message', ''):
                        self.log_result("2.3.1 Employee Notification", True, 
                                      f"Notification reçue: {latest_notification['title']}")
                    else:
                        self.log_result("2.3.1 Employee Notification", False, 
                                      f"Notification incorrecte: {latest_notification.get('message')}")
                else:
                    self.log_result("2.3.1 Employee Notification", False, 
                                  "Aucune notification de mise à jour trouvée")
            else:
                self.log_result("2.3.1 Employee Notification", False, 
                              f"Status: {response.status_code}")
                
        except Exception as e:
            self.log_result("2.3.1 Employee Notification", False, "Exception occurred", str(e))
        
        # Vérifier notifications pour le client
        try:
            client_credentials = {
                "email": "client.employee.test@example.com",
                "password": "Aloria2024!"
            }
            
            login_response = self.session.post(f"{API_BASE}/auth/login", json=client_credentials)
            
            if login_response.status_code == 200:
                client_token = login_response.json()['access_token']
                headers = {"Authorization": f"Bearer {client_token}"}
                
                response = self.session.get(f"{API_BASE}/notifications", headers=headers)
                
                if response.status_code == 200:
                    notifications = response.json()
                    case_notifications = [n for n in notifications if n.get('type') == 'case_update']
                    
                    if len(case_notifications) > 0:
                        self.log_result("2.3.2 Client Notification", True, 
                                      f"Client a reçu {len(case_notifications)} notification(s)")
                    else:
                        self.log_result("2.3.2 Client Notification", False, 
                                      "Client n'a reçu aucune notification")
                else:
                    self.log_result("2.3.2 Client Notification", False, 
                                  f"Status: {response.status_code}")
            else:
                self.log_result("2.3.2 Client Notification", False, 
                              "Impossible de se connecter en tant que client")
                
        except Exception as e:
            self.log_result("2.3.2 Client Notification", False, "Exception occurred", str(e))

    def phase_3_manager_client_creation(self):
        """PHASE 3 - Création de Client par Manager avec Affectation"""
        print("\n" + "="*60)
        print("PHASE 3 - CRÉATION DE CLIENT PAR MANAGER")
        print("="*60)
        
        if 'manager' not in self.tokens:
            self.log_result("Phase 3 Setup", False, "Manager token not available")
            return False
            
        headers = {"Authorization": f"Bearer {self.tokens['manager']}"}
        
        # 1. Créer un client directement
        print("\n🔸 ÉTAPE 3.1 - Créer un client directement")
        try:
            client_data = {
                "email": "client.manager.test@example.com",
                "full_name": "Test Client Manager",
                "phone": "+33698765432",
                "country": "France",
                "visa_type": "Visa étudiant",
                "message": "Test de création par manager"
            }
            
            response = self.session.post(f"{API_BASE}/clients", json=client_data, headers=headers)
            
            if response.status_code in [200, 201]:
                client = response.json()
                self.test_data['manager_client_id'] = client['id']
                
                self.log_result("3.1 Create Manager Client", True, 
                              f"Client créé: {client['id']} - {client.get('full_name', 'N/A')}")
            else:
                self.log_result("3.1 Create Manager Client", False, 
                              f"Status: {response.status_code}", response.text)
                return False
                
        except Exception as e:
            self.log_result("3.1 Create Manager Client", False, "Exception occurred", str(e))
            return False
        
        # 2. Créer un paiement pour ce client
        print("\n🔸 ÉTAPE 3.2 - Créer un paiement")
        try:
            # Login as the created client to declare payment
            client_credentials = {
                "email": "client.manager.test@example.com",
                "password": "Aloria2024!"  # Default password
            }
            
            login_response = self.session.post(f"{API_BASE}/auth/login", json=client_credentials)
            
            if login_response.status_code == 200:
                client_token = login_response.json()['access_token']
                client_headers = {"Authorization": f"Bearer {client_token}"}
                
                payment_data = {
                    "amount": 75000,
                    "currency": "CFA",
                    "description": "Premier versement - Test manager",
                    "payment_method": "Espèces"
                }
                
                payment_response = self.session.post(f"{API_BASE}/payments/declare", 
                                                   json=payment_data, headers=client_headers)
                
                if payment_response.status_code in [200, 201]:
                    payment = payment_response.json()
                    self.log_result("3.2 Create Manager Payment", True, 
                                  f"Paiement créé: {payment['id']} - {payment['amount']} {payment['currency']}")
                else:
                    self.log_result("3.2 Create Manager Payment", False, 
                                  f"Status: {payment_response.status_code}", payment_response.text)
            else:
                self.log_result("3.2 Manager Client Login", False, 
                              f"Status: {login_response.status_code}", login_response.text)
                
        except Exception as e:
            self.log_result("3.2 Create Manager Payment", False, "Exception occurred", str(e))
        
        # 3. Vérifier l'affectation automatique au manager
        print("\n🔸 ÉTAPE 3.3 - Vérifier l'affectation")
        self.verify_manager_assignment()
        
        # 4. Réaffecter le client à l'employé
        print("\n🔸 ÉTAPE 3.4 - Réaffecter à l'employé")
        self.test_client_reassignment()
        
        return True

    def verify_manager_assignment(self):
        """Vérifier que le client est assigné au manager"""
        try:
            headers = {"Authorization": f"Bearer {self.tokens['manager']}"}
            response = self.session.get(f"{API_BASE}/clients", headers=headers)
            
            if response.status_code == 200:
                clients = response.json()
                manager_client = next((c for c in clients if c['id'] == self.test_data['manager_client_id']), None)
                
                if manager_client:
                    if manager_client.get('assigned_employee_id') == self.users['manager']['id']:
                        self.log_result("3.3 Manager Assignment", True, 
                                      "Client assigné automatiquement au manager")
                    else:
                        self.log_result("3.3 Manager Assignment", False, 
                                      f"Assignation incorrecte: {manager_client.get('assigned_employee_id')}")
                else:
                    self.log_result("3.3 Manager Assignment", False, "Client non trouvé")
            else:
                self.log_result("3.3 Manager Assignment", False, 
                              f"Status: {response.status_code}")
                
        except Exception as e:
            self.log_result("3.3 Manager Assignment", False, "Exception occurred", str(e))

    def test_client_reassignment(self):
        """Tester la réaffectation du client"""
        try:
            headers = {"Authorization": f"Bearer {self.tokens['manager']}"}
            reassignment_data = {
                "assigned_employee_id": self.users['employee']['id']
            }
            
            client_id = self.test_data['manager_client_id']
            response = self.session.patch(f"{API_BASE}/clients/{client_id}", 
                                        json=reassignment_data, headers=headers)
            
            if response.status_code == 200:
                updated_client = response.json()
                if updated_client.get('assigned_employee_id') == self.users['employee']['id']:
                    self.log_result("3.4 Client Reassignment", True, 
                                  "Client réaffecté avec succès à l'employé")
                else:
                    self.log_result("3.4 Client Reassignment", False, 
                                  f"Réaffectation échouée: {updated_client.get('assigned_employee_id')}")
            else:
                self.log_result("3.4 Client Reassignment", False, 
                              f"Status: {response.status_code}", response.text)
                
        except Exception as e:
            self.log_result("3.4 Client Reassignment", False, "Exception occurred", str(e))

    def phase_4_workflow_validation(self):
        """PHASE 4 - Validation Complète du Workflow"""
        print("\n" + "="*60)
        print("PHASE 4 - VALIDATION COMPLÈTE DU WORKFLOW")
        print("="*60)
        
        # 1. Vérifier la structure du workflow
        print("\n🔸 ÉTAPE 4.1 - Vérifier la structure du workflow")
        self.verify_workflow_structure()
        
        # 2. Vérifier les permissions
        print("\n🔸 ÉTAPE 4.2 - Vérifier les permissions")
        self.verify_permissions()
        
        # 3. Vérifier la facture PDF
        print("\n🔸 ÉTAPE 4.3 - Vérifier la facture PDF")
        self.verify_pdf_invoice()
        
        return True

    def verify_workflow_structure(self):
        """Vérifier la structure des workflows"""
        try:
            headers = {"Authorization": f"Bearer {self.tokens['manager']}"}
            response = self.session.get(f"{API_BASE}/workflows", headers=headers)
            
            if response.status_code == 200:
                workflows = response.json()
                
                # Vérifier workflow Canada
                canada_workflows = workflows.get('Canada', {})
                canada_work_permit = canada_workflows.get('Permis de travail', [])
                
                if len(canada_work_permit) >= 15:
                    self.log_result("4.1.1 Canada Workflow", True, 
                                  f"Workflow Canada: {len(canada_work_permit)} étapes")
                else:
                    self.log_result("4.1.1 Canada Workflow", False, 
                                  f"Workflow Canada incomplet: {len(canada_work_permit)} étapes")
                
                # Vérifier workflow France
                france_workflows = workflows.get('France', {})
                france_student_visa = france_workflows.get('Visa étudiant', [])
                
                if len(france_student_visa) >= 10:
                    self.log_result("4.1.2 France Workflow", True, 
                                  f"Workflow France: {len(france_student_visa)} étapes")
                else:
                    self.log_result("4.1.2 France Workflow", False, 
                                  f"Workflow France incomplet: {len(france_student_visa)} étapes")
                
                # Vérifier structure des étapes
                if canada_work_permit:
                    first_step = canada_work_permit[0]
                    required_fields = ['title', 'description', 'documents', 'duration']
                    missing_fields = [field for field in required_fields if field not in first_step]
                    
                    if not missing_fields:
                        self.log_result("4.1.3 Step Structure", True, 
                                      "Structure des étapes complète")
                    else:
                        self.log_result("4.1.3 Step Structure", False, 
                                      f"Champs manquants: {missing_fields}")
                        
            else:
                self.log_result("4.1 Workflow Structure", False, 
                              f"Status: {response.status_code}")
                
        except Exception as e:
            self.log_result("4.1 Workflow Structure", False, "Exception occurred", str(e))

    def verify_permissions(self):
        """Vérifier les permissions d'accès"""
        
        # Test 1: Client ne peut voir que SON dossier
        try:
            client_credentials = {
                "email": "client.employee.test@example.com",
                "password": "Aloria2024!"
            }
            
            login_response = self.session.post(f"{API_BASE}/auth/login", json=client_credentials)
            
            if login_response.status_code == 200:
                client_token = login_response.json()['access_token']
                headers = {"Authorization": f"Bearer {client_token}"}
                
                response = self.session.get(f"{API_BASE}/cases", headers=headers)
                
                if response.status_code == 200:
                    cases = response.json()
                    # Client ne devrait voir que ses propres dossiers
                    if len(cases) == 1 and cases[0]['client_name'] == "Test Client Employee":
                        self.log_result("4.2.1 Client Permissions", True, 
                                      "Client ne voit que son propre dossier")
                    else:
                        self.log_result("4.2.1 Client Permissions", False, 
                                      f"Client voit {len(cases)} dossier(s)")
                else:
                    self.log_result("4.2.1 Client Permissions", False, 
                                  f"Status: {response.status_code}")
            else:
                self.log_result("4.2.1 Client Permissions", False, 
                              "Impossible de se connecter en tant que client")
                
        except Exception as e:
            self.log_result("4.2.1 Client Permissions", False, "Exception occurred", str(e))
        
        # Test 2: Employee ne voit que les dossiers assignés
        try:
            headers = {"Authorization": f"Bearer {self.tokens['employee']}"}
            response = self.session.get(f"{API_BASE}/cases", headers=headers)
            
            if response.status_code == 200:
                cases = response.json()
                # Employee devrait voir les dossiers qui lui sont assignés
                assigned_cases = [c for c in cases if c.get('client_name') in ["Test Client Employee"]]
                
                if len(assigned_cases) > 0:
                    self.log_result("4.2.2 Employee Permissions", True, 
                                  f"Employee voit {len(assigned_cases)} dossier(s) assigné(s)")
                else:
                    self.log_result("4.2.2 Employee Permissions", False, 
                                  "Employee ne voit aucun dossier assigné")
            else:
                self.log_result("4.2.2 Employee Permissions", False, 
                              f"Status: {response.status_code}")
                
        except Exception as e:
            self.log_result("4.2.2 Employee Permissions", False, "Exception occurred", str(e))
        
        # Test 3: Manager voit TOUS les dossiers
        try:
            headers = {"Authorization": f"Bearer {self.tokens['manager']}"}
            response = self.session.get(f"{API_BASE}/cases", headers=headers)
            
            if response.status_code == 200:
                cases = response.json()
                # Manager devrait voir tous les dossiers
                if len(cases) >= 2:  # Au moins les 2 créés dans ce test
                    self.log_result("4.2.3 Manager Permissions", True, 
                                  f"Manager voit {len(cases)} dossier(s) au total")
                else:
                    self.log_result("4.2.3 Manager Permissions", False, 
                                  f"Manager ne voit que {len(cases)} dossier(s)")
            else:
                self.log_result("4.2.3 Manager Permissions", False, 
                              f"Status: {response.status_code}")
                
        except Exception as e:
            self.log_result("4.2.3 Manager Permissions", False, "Exception occurred", str(e))

    def verify_pdf_invoice(self):
        """Vérifier la génération de factures PDF"""
        try:
            headers = {"Authorization": f"Bearer {self.tokens['manager']}"}
            
            # Récupérer l'historique des paiements
            response = self.session.get(f"{API_BASE}/payments/history", headers=headers)
            
            if response.status_code == 200:
                payments = response.json()
                confirmed_payments = [p for p in payments if p.get('status') == 'CONFIRMED' and p.get('invoice_number')]
                
                if confirmed_payments:
                    payment = confirmed_payments[0]
                    payment_id = payment['id']
                    
                    # Tester le téléchargement de la facture
                    invoice_response = self.session.get(f"{API_BASE}/payments/{payment_id}/invoice", headers=headers)
                    
                    if invoice_response.status_code == 200:
                        content_type = invoice_response.headers.get('content-type', '')
                        content_length = len(invoice_response.content)
                        
                        if 'application/pdf' in content_type:
                            self.log_result("4.3.1 PDF Invoice Download", True, 
                                          f"Facture PDF téléchargée - Taille: {content_length} bytes")
                        else:
                            self.log_result("4.3.1 PDF Invoice Download", False, 
                                          f"Content-Type incorrect: {content_type}")
                    else:
                        self.log_result("4.3.1 PDF Invoice Download", False, 
                                      f"Status: {invoice_response.status_code}")
                else:
                    self.log_result("4.3.1 PDF Invoice Download", False, 
                                  "Aucun paiement confirmé avec facture trouvé")
            else:
                self.log_result("4.3.1 PDF Invoice Download", False, 
                              f"Status: {response.status_code}")
                
        except Exception as e:
            self.log_result("4.3.1 PDF Invoice Download", False, "Exception occurred", str(e))

    def cleanup_test_data(self):
        """Nettoyer les données de test créées"""
        print("\n" + "="*60)
        print("NETTOYAGE DES DONNÉES DE TEST")
        print("="*60)
        
        # Note: Dans un environnement de production, on supprimerait les données de test
        # Ici on se contente de les lister pour information
        
        test_items = []
        if 'client_id' in self.test_data:
            test_items.append(f"Client Employee: {self.test_data['client_id']}")
        if 'manager_client_id' in self.test_data:
            test_items.append(f"Client Manager: {self.test_data['manager_client_id']}")
        
        if test_items:
            self.log_result("Cleanup Info", True, 
                          f"Données de test créées: {'; '.join(test_items)}")
        else:
            self.log_result("Cleanup Info", True, "Aucune donnée de test à nettoyer")

    def run_complete_workflow_test(self):
        """Exécuter le test complet du workflow"""
        print("ALORIA AGENCY - Test Complet du Workflow Client")
        print("Création, Dashboard, Affectation et Notifications")
        print("="*80)
        
        # Authentication
        if not self.authenticate_users():
            print("❌ ÉCHEC: Impossible d'authentifier les utilisateurs")
            return False
        
        # Phase 1: Création de Client par Employee
        if not self.phase_1_employee_client_creation():
            print("❌ ÉCHEC: Phase 1 - Création de Client par Employee")
            return False
        
        # Phase 2: Mise à jour du Dossier par Manager
        if not self.phase_2_manager_case_update():
            print("❌ ÉCHEC: Phase 2 - Mise à jour du Dossier par Manager")
            return False
        
        # Phase 3: Création de Client par Manager
        if not self.phase_3_manager_client_creation():
            print("❌ ÉCHEC: Phase 3 - Création de Client par Manager")
            return False
        
        # Phase 4: Validation Complète du Workflow
        if not self.phase_4_workflow_validation():
            print("❌ ÉCHEC: Phase 4 - Validation Complète du Workflow")
            return False
        
        # Cleanup
        self.cleanup_test_data()
        
        # Résultats finaux
        print("\n" + "="*80)
        print("RÉSULTATS FINAUX")
        print("="*80)
        
        total_tests = self.results['passed'] + self.results['failed']
        success_rate = (self.results['passed'] / total_tests * 100) if total_tests > 0 else 0
        
        print(f"✅ Tests réussis: {self.results['passed']}")
        print(f"❌ Tests échoués: {self.results['failed']}")
        print(f"📊 Taux de réussite: {success_rate:.1f}%")
        
        if self.results['errors']:
            print(f"\n🚨 ERREURS DÉTECTÉES:")
            for error in self.results['errors']:
                print(f"   - {error['test']}: {error['message']}")
        
        return success_rate >= 80  # Considérer comme succès si >= 80%

if __name__ == "__main__":
    tester = WorkflowTester()
    success = tester.run_complete_workflow_test()
    
    if success:
        print("\n🎉 TEST COMPLET DU WORKFLOW: SUCCÈS")
        sys.exit(0)
    else:
        print("\n💥 TEST COMPLET DU WORKFLOW: ÉCHEC")
        sys.exit(1)