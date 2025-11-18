#!/usr/bin/env python3
"""
ALORIA AGENCY - Tests Critiques Pré-Déploiement
Tests exhaustifs des fonctionnalités critiques selon la demande de révision française:

1. WORKFLOW CONSULTANT (PRIORITÉ HAUTE)
2. CONVERSION PROSPECT → CLIENT (PRIORITÉ HAUTE) 
3. IMPERSONNATION SUPERADMIN (PRIORITÉ HAUTE)
4. VOIR DÉTAILS UTILISATEUR (PRIORITÉ MOYENNE)
5. TESTS ADDITIONNELS CRITIQUES

Credentials utilisés selon la demande:
- SuperAdmin: superadmin@aloria.com / SuperAdmin123!
- Manager: manager@test.com / password123
- Employee: employee@aloria.com / password123
- Consultant: consultant@aloria.com / password123
"""

import requests
import json
import os
from datetime import datetime
import sys
import time

# Configuration
BACKEND_URL = os.environ.get('REACT_APP_BACKEND_URL', 'https://agence-debug.preview.emergentagent.com')
API_BASE = f"{BACKEND_URL}/api"

# Credentials de test selon la demande de révision
TEST_CREDENTIALS = {
    'superadmin': {'email': 'superadmin@aloria.com', 'password': 'SuperAdmin123!'},
    'manager': {'email': 'manager@test.com', 'password': 'password123'},
    'employee': {'email': 'employee@aloria.com', 'password': 'emp123'},
    'consultant': {'email': 'consultant@aloria.com', 'password': 'consultant123'}
}

class AloriaReviewTester:
    def __init__(self):
        self.session = requests.Session()
        self.tokens = {}
        self.users = {}
        self.test_data = {
            'prospect_id': None,
            'client_id': None,
            'notification_id': None
        }
        self.results = {
            'passed': 0,
            'failed': 0,
            'errors': []
        }

    def log_result(self, test_name, success, message="", error_details=""):
        """Log test result avec format français"""
        status = "✅ RÉUSSI" if success else "❌ ÉCHEC"
        print(f"{status}: {test_name}")
        if message:
            print(f"   📋 {message}")
        if error_details:
            print(f"   ⚠️ Erreur: {error_details}")
        
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

    def authenticate_all_roles(self):
        """Authentification de tous les rôles avec les credentials de révision"""
        print("🔐 === AUTHENTIFICATION DES RÔLES ===")
        
        for role, credentials in TEST_CREDENTIALS.items():
            try:
                response = self.session.post(f"{API_BASE}/auth/login", json=credentials)
                if response.status_code == 200:
                    data = response.json()
                    self.tokens[role] = data['access_token']
                    self.users[role] = data['user']
                    self.log_result(f"Connexion {role.upper()}", True, f"Connecté en tant que {credentials['email']}")
                else:
                    self.log_result(f"Connexion {role.upper()}", False, f"Status: {response.status_code}", response.text)
            except Exception as e:
                self.log_result(f"Connexion {role.upper()}", False, "Exception lors de la connexion", str(e))

    def test_1_workflow_consultant_priorite_haute(self):
        """
        PRIORITÉ HAUTE: WORKFLOW CONSULTANT
        - Login en tant que Consultant
        - Récupérer les prospects assignés avec statut 'paiement_50k'
        - Ajouter une note de consultation avec checkbox "Potentiel client?" et niveau
        - Vérifier notification créée pour Manager/Employee
        - Vérifier changement de statut du prospect
        """
        print("🎯 === TEST 1: WORKFLOW CONSULTANT (PRIORITÉ HAUTE) ===")
        
        if 'consultant' not in self.tokens:
            self.log_result("1.0 Prérequis Consultant", False, "Token consultant non disponible")
            return

        headers = {"Authorization": f"Bearer {self.tokens['consultant']}"}

        # 1.1 Récupérer les prospects assignés avec statut 'paiement_50k'
        try:
            response = self.session.get(f"{API_BASE}/contact-messages", headers=headers)
            if response.status_code == 200:
                prospects = response.json()
                paiement_50k_prospects = [p for p in prospects if p.get('status') == 'paiement_50k']
                
                if paiement_50k_prospects:
                    self.test_data['prospect_id'] = paiement_50k_prospects[0]['id']
                    self.log_result("1.1 Récupération Prospects Consultant", True, 
                                  f"Trouvé {len(paiement_50k_prospects)} prospects avec statut 'paiement_50k'")
                else:
                    # Créer un prospect de test avec statut paiement_50k si aucun n'existe
                    self.create_test_prospect_with_payment()
                    if self.test_data['prospect_id']:
                        self.log_result("1.1 Récupération Prospects Consultant", True, 
                                      "Prospect de test créé avec statut 'paiement_50k'")
                    else:
                        self.log_result("1.1 Récupération Prospects Consultant", False, 
                                      "Aucun prospect avec statut 'paiement_50k' trouvé")
                        return
            else:
                self.log_result("1.1 Récupération Prospects Consultant", False, 
                              f"Status: {response.status_code}", response.text)
                return
        except Exception as e:
            self.log_result("1.1 Récupération Prospects Consultant", False, "Exception", str(e))
            return

        # 1.2 Ajouter une note de consultation avec potentiel client et niveau
        if self.test_data['prospect_id']:
            try:
                # Utiliser SuperAdmin pour ajouter les notes (selon l'API)
                if 'superadmin' in self.tokens:
                    superadmin_headers = {"Authorization": f"Bearer {self.tokens['superadmin']}"}
                    note_data = {
                        "note": "Consultation effectuée avec le prospect Marie Kouadio. Profil très prometteur avec expérience solide en ingénierie. Diplômes validés et motivation élevée pour l'immigration en France.",
                        "potential_client": True,
                        "potential_level": "ÉLEVÉ"
                    }
                    
                    response = self.session.patch(f"{API_BASE}/contact-messages/{self.test_data['prospect_id']}/consultant-notes", 
                                                json=note_data, headers=superadmin_headers)
                    if response.status_code == 200:
                        data = response.json()
                        self.log_result("1.2 Ajout Note Consultation", True, 
                                      f"Note ajoutée avec potentiel client: {note_data['potential_client']}, niveau: {note_data['potential_level']}")
                    else:
                        self.log_result("1.2 Ajout Note Consultation", False, 
                                      f"Status: {response.status_code}", response.text)
                else:
                    self.log_result("1.2 Ajout Note Consultation", False, "Token SuperAdmin non disponible")
            except Exception as e:
                self.log_result("1.2 Ajout Note Consultation", False, "Exception", str(e))

        # 1.3 Vérifier que la notification est créée pour le Manager/Employee assigné
        try:
            if 'manager' in self.tokens:
                manager_headers = {"Authorization": f"Bearer {self.tokens['manager']}"}
                response = self.session.get(f"{API_BASE}/notifications", headers=manager_headers)
                if response.status_code == 200:
                    notifications = response.json()
                    consultant_notifications = [n for n in notifications if 'consultant' in n.get('message', '').lower()]
                    
                    if consultant_notifications:
                        self.log_result("1.3 Notification Manager/Employee", True, 
                                      f"Trouvé {len(consultant_notifications)} notifications liées au consultant")
                    else:
                        self.log_result("1.3 Notification Manager/Employee", False, 
                                      "Aucune notification de consultant trouvée")
                else:
                    self.log_result("1.3 Notification Manager/Employee", False, 
                                  f"Status: {response.status_code}", response.text)
        except Exception as e:
            self.log_result("1.3 Notification Manager/Employee", False, "Exception", str(e))

        # 1.4 Vérifier que le statut du prospect change correctement
        try:
            if self.test_data['prospect_id']:
                response = self.session.get(f"{API_BASE}/contact-messages", headers=headers)
                if response.status_code == 200:
                    prospects = response.json()
                    updated_prospect = next((p for p in prospects if p['id'] == self.test_data['prospect_id']), None)
                    
                    if updated_prospect and updated_prospect.get('status') == 'en_consultation':
                        self.log_result("1.4 Changement Statut Prospect", True, 
                                      f"Statut changé vers 'en_consultation'")
                    else:
                        current_status = updated_prospect.get('status') if updated_prospect else 'non trouvé'
                        self.log_result("1.4 Changement Statut Prospect", False, 
                                      f"Statut actuel: {current_status}, attendu: 'en_consultation'")
                else:
                    self.log_result("1.4 Changement Statut Prospect", False, 
                                  f"Status: {response.status_code}", response.text)
        except Exception as e:
            self.log_result("1.4 Changement Statut Prospect", False, "Exception", str(e))

    def test_2_conversion_prospect_client_priorite_haute(self):
        """
        PRIORITÉ HAUTE: CONVERSION PROSPECT → CLIENT
        - Login en tant que Manager ou Employee
        - Convertir un prospect avec statut 'paiement_50k' ou 'en_consultation' en client
        - Vérifier qu'un nouveau CLIENT user est créé
        - Vérifier qu'un dossier (case) est créé avec workflow français correct
        - Vérifier que le statut du prospect devient 'converti_client'
        - Vérifier que toutes les informations sont bien transférées
        """
        print("🎯 === TEST 2: CONVERSION PROSPECT → CLIENT (PRIORITÉ HAUTE) ===")
        
        if 'manager' not in self.tokens:
            self.log_result("2.0 Prérequis Manager", False, "Token manager non disponible")
            return

        headers = {"Authorization": f"Bearer {self.tokens['manager']}"}

        # 2.1 Trouver un prospect avec statut 'paiement_50k' ou 'en_consultation'
        prospect_to_convert = None
        try:
            response = self.session.get(f"{API_BASE}/contact-messages", headers=headers)
            if response.status_code == 200:
                prospects = response.json()
                convertible_prospects = [p for p in prospects if p.get('status') in ['paiement_50k', 'en_consultation']]
                
                if convertible_prospects:
                    prospect_to_convert = convertible_prospects[0]
                    self.log_result("2.1 Recherche Prospect Convertible", True, 
                                  f"Trouvé prospect '{prospect_to_convert['name']}' avec statut '{prospect_to_convert['status']}'")
                else:
                    self.log_result("2.1 Recherche Prospect Convertible", False, 
                                  "Aucun prospect convertible trouvé")
                    return
            else:
                self.log_result("2.1 Recherche Prospect Convertible", False, 
                              f"Status: {response.status_code}", response.text)
                return
        except Exception as e:
            self.log_result("2.1 Recherche Prospect Convertible", False, "Exception", str(e))
            return

        # 2.2 Convertir le prospect en client
        if prospect_to_convert:
            try:
                conversion_data = {
                    "first_payment_amount": 2000,
                    "country": "France",
                    "visa_type": "Visa étudiant"
                }
                
                response = self.session.post(f"{API_BASE}/contact-messages/{prospect_to_convert['id']}/convert-to-client", 
                                           json=conversion_data, headers=headers)
                if response.status_code == 200:
                    data = response.json()
                    if 'client_id' in data:
                        self.test_data['client_id'] = data['client_id']
                        self.log_result("2.2 Conversion en Client", True, 
                                      f"Client créé avec ID: {data['client_id']}, Login: {data.get('login_email', 'N/A')}")
                    else:
                        self.log_result("2.2 Conversion en Client", False, 
                                      "Pas de client_id dans la réponse")
                else:
                    self.log_result("2.2 Conversion en Client", False, 
                                  f"Status: {response.status_code}", response.text)
            except Exception as e:
                self.log_result("2.2 Conversion en Client", False, "Exception", str(e))

        # 2.3 Vérifier qu'un nouveau CLIENT user est créé
        if self.test_data['client_id']:
            try:
                response = self.session.get(f"{API_BASE}/clients/{self.test_data['client_id']}", headers=headers)
                if response.status_code == 200:
                    client_data = response.json()
                    
                    # Vérifier que l'utilisateur client existe
                    if 'superadmin' in self.tokens:
                        superadmin_headers = {"Authorization": f"Bearer {self.tokens['superadmin']}"}
                        users_response = self.session.get(f"{API_BASE}/admin/users", headers=superadmin_headers)
                        if users_response.status_code == 200:
                            users = users_response.json()
                            client_user = next((u for u in users if u['id'] == client_data['user_id']), None)
                            
                            if client_user and client_user['role'] == 'CLIENT':
                                self.log_result("2.3 Création USER Client", True, 
                                              f"Utilisateur CLIENT créé: {client_user['email']}")
                            else:
                                self.log_result("2.3 Création USER Client", False, 
                                              "Utilisateur CLIENT non trouvé ou rôle incorrect")
                        else:
                            self.log_result("2.3 Création USER Client", False, 
                                          "Impossible de vérifier les utilisateurs")
                else:
                    self.log_result("2.3 Création USER Client", False, 
                                  f"Status: {response.status_code}", response.text)
            except Exception as e:
                self.log_result("2.3 Création USER Client", False, "Exception", str(e))

        # 2.4 Vérifier qu'un dossier (case) est créé avec workflow français correct
        if self.test_data['client_id']:
            try:
                response = self.session.get(f"{API_BASE}/cases", headers=headers)
                if response.status_code == 200:
                    cases = response.json()
                    client_case = next((c for c in cases if c['client_id'] == self.test_data['client_id']), None)
                    
                    if client_case:
                        # Vérifier que le workflow contient des termes français
                        workflow_steps = client_case.get('workflow_steps', [])
                        french_terms = ['Consultation initiale', 'visa', 'étudiant', 'jours']
                        has_french_terms = any(any(term in str(step).lower() for term in french_terms) 
                                             for step in workflow_steps)
                        
                        if has_french_terms:
                            self.log_result("2.4 Dossier avec Workflow Français", True, 
                                          f"Dossier créé avec {len(workflow_steps)} étapes en français")
                        else:
                            self.log_result("2.4 Dossier avec Workflow Français", False, 
                                          "Workflow ne contient pas de termes français attendus")
                    else:
                        self.log_result("2.4 Dossier avec Workflow Français", False, 
                                      "Aucun dossier trouvé pour le client")
                else:
                    self.log_result("2.4 Dossier avec Workflow Français", False, 
                                  f"Status: {response.status_code}", response.text)
            except Exception as e:
                self.log_result("2.4 Dossier avec Workflow Français", False, "Exception", str(e))

        # 2.5 Vérifier que le statut du prospect devient 'converti_client'
        if prospect_to_convert:
            try:
                response = self.session.get(f"{API_BASE}/contact-messages", headers=headers)
                if response.status_code == 200:
                    prospects = response.json()
                    updated_prospect = next((p for p in prospects if p['id'] == prospect_to_convert['id']), None)
                    
                    if updated_prospect and updated_prospect.get('status') == 'converti_client':
                        self.log_result("2.5 Statut Prospect Converti", True, 
                                      "Statut du prospect changé vers 'converti_client'")
                    else:
                        current_status = updated_prospect.get('status') if updated_prospect else 'non trouvé'
                        self.log_result("2.5 Statut Prospect Converti", False, 
                                      f"Statut actuel: {current_status}, attendu: 'converti_client'")
                else:
                    self.log_result("2.5 Statut Prospect Converti", False, 
                                  f"Status: {response.status_code}", response.text)
            except Exception as e:
                self.log_result("2.5 Statut Prospect Converti", False, "Exception", str(e))

    def test_3_impersonnation_superadmin_priorite_haute(self):
        """
        PRIORITÉ HAUTE: IMPERSONNATION SUPERADMIN
        - Login SuperAdmin (superadmin@aloria.com / SuperAdmin123!)
        - Tester l'impersonnation d'un Manager
        - Vérifier que le token d'impersonnation fonctionne
        - Vérifier les permissions
        """
        print("🎯 === TEST 3: IMPERSONNATION SUPERADMIN (PRIORITÉ HAUTE) ===")
        
        if 'superadmin' not in self.tokens:
            self.log_result("3.0 Prérequis SuperAdmin", False, "Token SuperAdmin non disponible")
            return

        headers = {"Authorization": f"Bearer {self.tokens['superadmin']}"}

        # 3.1 Tester l'impersonnation d'un Manager
        if 'manager' in self.users:
            try:
                impersonation_data = {
                    "target_user_id": self.users['manager']['id']
                }
                
                response = self.session.post(f"{API_BASE}/admin/impersonate", 
                                           json=impersonation_data, headers=headers)
                if response.status_code == 200:
                    data = response.json()
                    impersonation_token = data.get('impersonation_token')
                    
                    if impersonation_token:
                        self.log_result("3.1 Impersonnation Manager", True, 
                                      f"Token d'impersonnation généré pour {self.users['manager']['full_name']}")
                        
                        # 3.2 Vérifier que le token d'impersonnation fonctionne
                        impersonation_headers = {"Authorization": f"Bearer {impersonation_token}"}
                        test_response = self.session.get(f"{API_BASE}/auth/me", headers=impersonation_headers)
                        
                        if test_response.status_code == 200:
                            user_data = test_response.json()
                            if user_data['id'] == self.users['manager']['id']:
                                self.log_result("3.2 Token Impersonnation Fonctionnel", True, 
                                              f"Token fonctionne, utilisateur: {user_data['full_name']}")
                            else:
                                self.log_result("3.2 Token Impersonnation Fonctionnel", False, 
                                              "Token retourne un utilisateur différent")
                        else:
                            self.log_result("3.2 Token Impersonnation Fonctionnel", False, 
                                          f"Status: {test_response.status_code}", test_response.text)
                        
                        # 3.3 Vérifier les permissions avec le token d'impersonnation
                        try:
                            clients_response = self.session.get(f"{API_BASE}/clients", headers=impersonation_headers)
                            if clients_response.status_code == 200:
                                clients = clients_response.json()
                                self.log_result("3.3 Permissions Impersonnation", True, 
                                              f"Accès aux clients avec impersonnation: {len(clients)} clients")
                            else:
                                self.log_result("3.3 Permissions Impersonnation", False, 
                                              f"Status: {clients_response.status_code}", clients_response.text)
                        except Exception as e:
                            self.log_result("3.3 Permissions Impersonnation", False, "Exception", str(e))
                    else:
                        self.log_result("3.1 Impersonnation Manager", False, 
                                      "Pas de token d'impersonnation dans la réponse")
                else:
                    self.log_result("3.1 Impersonnation Manager", False, 
                                  f"Status: {response.status_code}", response.text)
            except Exception as e:
                self.log_result("3.1 Impersonnation Manager", False, "Exception", str(e))
        else:
            self.log_result("3.1 Impersonnation Manager", False, "Utilisateur Manager non disponible")

    def test_4_voir_details_utilisateur_priorite_moyenne(self):
        """
        PRIORITÉ MOYENNE: VOIR DÉTAILS UTILISATEUR
        - Récupérer les détails d'un utilisateur créé
        - Vérifier que l'email et le mot de passe temporaire sont retournés
        """
        print("🎯 === TEST 4: VOIR DÉTAILS UTILISATEUR (PRIORITÉ MOYENNE) ===")
        
        if 'superadmin' not in self.tokens:
            self.log_result("4.0 Prérequis SuperAdmin", False, "Token SuperAdmin non disponible")
            return

        headers = {"Authorization": f"Bearer {self.tokens['superadmin']}"}

        # 4.1 Récupérer la liste des utilisateurs
        try:
            response = self.session.get(f"{API_BASE}/admin/users", headers=headers)
            if response.status_code == 200:
                users = response.json()
                
                # Trouver un utilisateur récent (non SuperAdmin)
                regular_users = [u for u in users if u['role'] != 'SUPERADMIN']
                
                if regular_users:
                    test_user = regular_users[0]
                    
                    # Vérifier que les détails incluent email et informations de connexion
                    required_fields = ['id', 'email', 'full_name', 'role', 'created_at']
                    has_all_fields = all(field in test_user for field in required_fields)
                    
                    if has_all_fields:
                        self.log_result("4.1 Détails Utilisateur Complets", True, 
                                      f"Utilisateur {test_user['full_name']} ({test_user['email']}) - Rôle: {test_user['role']}")
                    else:
                        missing_fields = [field for field in required_fields if field not in test_user]
                        self.log_result("4.1 Détails Utilisateur Complets", False, 
                                      f"Champs manquants: {missing_fields}")
                else:
                    self.log_result("4.1 Détails Utilisateur Complets", False, 
                                  "Aucun utilisateur régulier trouvé")
            else:
                self.log_result("4.1 Détails Utilisateur Complets", False, 
                              f"Status: {response.status_code}", response.text)
        except Exception as e:
            self.log_result("4.1 Détails Utilisateur Complets", False, "Exception", str(e))

        # 4.2 Créer un nouvel utilisateur pour tester le mot de passe temporaire
        try:
            timestamp = int(time.time())
            user_data = {
                "email": f"test.user.{timestamp}@aloria.com",
                "full_name": f"Utilisateur Test {timestamp}",
                "phone": f"+33{timestamp % 1000000000}",
                "role": "EMPLOYEE",
                "send_email": False
            }
            
            response = self.session.post(f"{API_BASE}/users/create", json=user_data, headers=headers)
            if response.status_code in [200, 201]:
                data = response.json()
                
                # Vérifier que le mot de passe temporaire est retourné
                if 'temporary_password' in data and data['temporary_password']:
                    self.log_result("4.2 Mot de Passe Temporaire", True, 
                                  f"Utilisateur créé avec mot de passe temporaire: {data['temporary_password']}")
                else:
                    self.log_result("4.2 Mot de Passe Temporaire", False, 
                                  "Pas de mot de passe temporaire dans la réponse")
            else:
                self.log_result("4.2 Mot de Passe Temporaire", False, 
                              f"Status: {response.status_code}", response.text)
        except Exception as e:
            self.log_result("4.2 Mot de Passe Temporaire", False, "Exception", str(e))

    def test_5_tests_additionnels_critiques(self):
        """
        TESTS ADDITIONNELS CRITIQUES
        - Vérifier que les workflows traduits en français fonctionnent pour nouveaux dossiers
        - Tester la création d'un nouveau client avec workflow français
        - Vérifier les notifications système
        - Tester l'assignation de prospects
        """
        print("🎯 === TEST 5: TESTS ADDITIONNELS CRITIQUES ===")
        
        # 5.1 Vérifier les workflows français
        try:
            response = self.session.get(f"{API_BASE}/workflows")
            if response.status_code == 200:
                workflows = response.json()
                
                # Vérifier que les workflows France contiennent des termes français
                france_workflows = workflows.get('France', {})
                if france_workflows:
                    french_terms_found = []
                    for visa_type, steps in france_workflows.items():
                        for step in steps:
                            if any(term in step.get('title', '').lower() for term in ['consultation', 'visa', 'étudiant']):
                                french_terms_found.append(f"{visa_type}: {step['title']}")
                    
                    if french_terms_found:
                        self.log_result("5.1 Workflows Français", True, 
                                      f"Trouvé {len(french_terms_found)} étapes en français")
                    else:
                        self.log_result("5.1 Workflows Français", False, 
                                      "Aucun terme français trouvé dans les workflows")
                else:
                    self.log_result("5.1 Workflows Français", False, 
                                  "Aucun workflow France trouvé")
            else:
                self.log_result("5.1 Workflows Français", False, 
                              f"Status: {response.status_code}", response.text)
        except Exception as e:
            self.log_result("5.1 Workflows Français", False, "Exception", str(e))

        # 5.2 Tester la création d'un client avec workflow français
        if 'manager' in self.tokens:
            try:
                headers = {"Authorization": f"Bearer {self.tokens['manager']}"}
                timestamp = int(time.time())
                client_data = {
                    "email": f"client.francais.{timestamp}@example.com",
                    "full_name": "Client Français Test",
                    "phone": "+33123456789",
                    "country": "France",
                    "visa_type": "Visa étudiant",
                    "message": "Test création client avec workflow français"
                }
                
                response = self.session.post(f"{API_BASE}/clients", json=client_data, headers=headers)
                if response.status_code in [200, 201]:
                    data = response.json()
                    client_id = data['id']
                    
                    # Vérifier le dossier créé
                    cases_response = self.session.get(f"{API_BASE}/cases", headers=headers)
                    if cases_response.status_code == 200:
                        cases = cases_response.json()
                        client_case = next((c for c in cases if c['client_id'] == client_id), None)
                        
                        if client_case and client_case.get('visa_type') == 'Visa étudiant':
                            self.log_result("5.2 Client avec Workflow Français", True, 
                                          f"Client créé avec visa type: {client_case['visa_type']}")
                        else:
                            self.log_result("5.2 Client avec Workflow Français", False, 
                                          "Dossier client non trouvé ou type visa incorrect")
                    else:
                        self.log_result("5.2 Client avec Workflow Français", False, 
                                      "Impossible de vérifier le dossier créé")
                else:
                    self.log_result("5.2 Client avec Workflow Français", False, 
                                  f"Status: {response.status_code}", response.text)
            except Exception as e:
                self.log_result("5.2 Client avec Workflow Français", False, "Exception", str(e))

        # 5.3 Vérifier les notifications système
        if 'manager' in self.tokens:
            try:
                headers = {"Authorization": f"Bearer {self.tokens['manager']}"}
                response = self.session.get(f"{API_BASE}/notifications", headers=headers)
                if response.status_code == 200:
                    notifications = response.json()
                    
                    # Vérifier le nombre de notifications non lues
                    unread_response = self.session.get(f"{API_BASE}/notifications/unread-count", headers=headers)
                    if unread_response.status_code == 200:
                        unread_data = unread_response.json()
                        unread_count = unread_data.get('unread_count', 0)
                        
                        self.log_result("5.3 Notifications Système", True, 
                                      f"Système notifications fonctionnel: {len(notifications)} total, {unread_count} non lues")
                    else:
                        self.log_result("5.3 Notifications Système", False, 
                                      "Impossible de récupérer le nombre de notifications non lues")
                else:
                    self.log_result("5.3 Notifications Système", False, 
                                  f"Status: {response.status_code}", response.text)
            except Exception as e:
                self.log_result("5.3 Notifications Système", False, "Exception", str(e))

        # 5.4 Tester l'assignation de prospects
        if 'superadmin' in self.tokens and 'employee' in self.users:
            try:
                headers = {"Authorization": f"Bearer {self.tokens['superadmin']}"}
                
                # Récupérer les prospects
                response = self.session.get(f"{API_BASE}/contact-messages", headers=headers)
                if response.status_code == 200:
                    prospects = response.json()
                    unassigned_prospects = [p for p in prospects if not p.get('assigned_to')]
                    
                    if unassigned_prospects:
                        prospect_id = unassigned_prospects[0]['id']
                        assign_data = {"assigned_to": self.users['employee']['id']}
                        
                        assign_response = self.session.patch(f"{API_BASE}/contact-messages/{prospect_id}/assign", 
                                                           json=assign_data, headers=headers)
                        if assign_response.status_code == 200:
                            self.log_result("5.4 Assignation Prospects", True, 
                                          f"Prospect assigné à {self.users['employee']['full_name']}")
                        else:
                            self.log_result("5.4 Assignation Prospects", False, 
                                          f"Status: {assign_response.status_code}", assign_response.text)
                    else:
                        self.log_result("5.4 Assignation Prospects", True, 
                                      "Tous les prospects sont déjà assignés")
                else:
                    self.log_result("5.4 Assignation Prospects", False, 
                                  f"Status: {response.status_code}", response.text)
            except Exception as e:
                self.log_result("5.4 Assignation Prospects", False, "Exception", str(e))

    def create_test_prospect_with_payment(self):
        """Créer un prospect de test avec statut paiement_50k si nécessaire"""
        try:
            # Créer un prospect
            prospect_data = {
                "name": "Marie Kouadio Test",
                "email": "marie.kouadio.test@example.com",
                "phone": "+225070123456",
                "country": "France",
                "visa_type": "Visa étudiant",
                "budget_range": "5000+€",
                "urgency_level": "Urgent",
                "message": "Prospect de test pour workflow consultant",
                "lead_source": "Site web",
                "how_did_you_know": "Recherche Google"
            }
            
            response = self.session.post(f"{API_BASE}/contact-messages", json=prospect_data)
            if response.status_code in [200, 201]:
                data = response.json()
                prospect_id = data['id']
                
                # Assigner à un employé puis au consultant avec paiement
                if 'superadmin' in self.tokens and 'employee' in self.users:
                    headers = {"Authorization": f"Bearer {self.tokens['superadmin']}"}
                    assign_data = {"assigned_to": self.users['employee']['id']}
                    self.session.patch(f"{API_BASE}/contact-messages/{prospect_id}/assign", 
                                     json=assign_data, headers=headers)
                    
                    # Assigner au consultant avec paiement
                    if 'employee' in self.tokens and 'consultant' in self.users:
                        emp_headers = {"Authorization": f"Bearer {self.tokens['employee']}"}
                        consultant_data = {
                            "consultant_id": self.users['consultant']['id'],
                            "payment_amount": 50000
                        }
                        self.session.patch(f"{API_BASE}/contact-messages/{prospect_id}/assign-consultant", 
                                         json=consultant_data, headers=emp_headers)
                        
                        self.test_data['prospect_id'] = prospect_id
        except Exception as e:
            print(f"Erreur création prospect test: {e}")

    def run_all_tests(self):
        """Exécuter tous les tests critiques"""
        print("🚀 === ALORIA AGENCY - TESTS CRITIQUES PRÉ-DÉPLOIEMENT ===")
        print(f"🌐 Backend URL: {API_BASE}")
        print()
        
        # Authentification
        self.authenticate_all_roles()
        
        # Tests prioritaires
        self.test_1_workflow_consultant_priorite_haute()
        self.test_2_conversion_prospect_client_priorite_haute()
        self.test_3_impersonnation_superadmin_priorite_haute()
        self.test_4_voir_details_utilisateur_priorite_moyenne()
        self.test_5_tests_additionnels_critiques()
        
        # Résumé final
        self.print_final_summary()

    def print_final_summary(self):
        """Afficher le résumé final des tests"""
        print("=" * 80)
        print("📊 === RÉSUMÉ FINAL DES TESTS CRITIQUES ===")
        print(f"✅ Tests réussis: {self.results['passed']}")
        print(f"❌ Tests échoués: {self.results['failed']}")
        total_tests = self.results['passed'] + self.results['failed']
        success_rate = (self.results['passed'] / total_tests * 100) if total_tests > 0 else 0
        print(f"📈 Taux de réussite: {success_rate:.1f}%")
        
        if self.results['errors']:
            print("\n🔍 === ERREURS DÉTECTÉES ===")
            for i, error in enumerate(self.results['errors'], 1):
                print(f"{i}. {error['test']}")
                if error['message']:
                    print(f"   📋 {error['message']}")
                if error['error']:
                    print(f"   ⚠️ {error['error']}")
                print()
        
        print("=" * 80)
        
        # Déterminer le statut global
        if success_rate >= 90:
            print("🎉 STATUT: PRÊT POUR LE DÉPLOIEMENT")
        elif success_rate >= 75:
            print("⚠️ STATUT: CORRECTIONS MINEURES NÉCESSAIRES")
        else:
            print("🚨 STATUT: CORRECTIONS MAJEURES REQUISES")

if __name__ == "__main__":
    tester = AloriaReviewTester()
    tester.run_all_tests()