#!/usr/bin/env python3
"""
ALORIA AGENCY - Tests des nouvelles modifications
Tests spécifiques pour les nouvelles fonctionnalités demandées:
1. Test création client avec assignation employé
2. Test restrictions dashboard employé (PATCH /api/cases/{id} -> 403)
3. Test notifications système complet
4. Test workflow complet (manager -> employé -> client)
5. Test pays limités (Canada et France uniquement)
"""

import requests
import json
import os
import sys
from datetime import datetime
import time

# Configuration
BACKEND_URL = os.environ.get('REACT_APP_BACKEND_URL', 'https://aloria-refactor.preview.emergentagent.com')
API_BASE = f"{BACKEND_URL}/api"

class AloriaAgencyTester:
    def __init__(self):
        self.session = requests.Session()
        self.manager_token = None
        self.employee_token = None
        self.client_token = None
        self.manager_user = None
        self.employee_user = None
        self.client_user = None
        self.test_client_id = None
        self.test_case_id = None
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

    def setup_users(self):
        """Setup manager and employee users for testing"""
        print("=== Configuration des utilisateurs de test ===")
        
        # Setup Manager
        manager_data = {
            "email": "manager.aloria@test.com",
            "password": "manager123",
            "full_name": "Manager Aloria Test",
            "phone": "+33123456789",
            "role": "MANAGER"
        }
        
        try:
            response = self.session.post(f"{API_BASE}/auth/register", json=manager_data)
            if response.status_code in [200, 201]:
                data = response.json()
                self.manager_token = data['access_token']
                self.manager_user = data['user']
                self.log_result("Setup Manager", True, f"Manager créé: {self.manager_user['id']}")
            elif response.status_code == 400 and "already registered" in response.text:
                # Login existing user
                login_response = self.session.post(f"{API_BASE}/auth/login", json={
                    "email": manager_data["email"],
                    "password": manager_data["password"]
                })
                if login_response.status_code == 200:
                    data = login_response.json()
                    self.manager_token = data['access_token']
                    self.manager_user = data['user']
                    self.log_result("Setup Manager (existing)", True, f"Manager connecté: {self.manager_user['id']}")
                else:
                    self.log_result("Setup Manager", False, "Échec connexion manager existant", login_response.text)
            else:
                self.log_result("Setup Manager", False, f"Status: {response.status_code}", response.text)
        except Exception as e:
            self.log_result("Setup Manager", False, "Exception", str(e))

        # Setup Employee
        employee_data = {
            "email": "employee.aloria@test.com",
            "password": "employee123",
            "full_name": "Employé Aloria Test",
            "phone": "+33987654321",
            "role": "EMPLOYEE"
        }
        
        try:
            response = self.session.post(f"{API_BASE}/auth/register", json=employee_data)
            if response.status_code in [200, 201]:
                data = response.json()
                self.employee_token = data['access_token']
                self.employee_user = data['user']
                self.log_result("Setup Employee", True, f"Employé créé: {self.employee_user['id']}")
            elif response.status_code == 400 and "already registered" in response.text:
                # Login existing user
                login_response = self.session.post(f"{API_BASE}/auth/login", json={
                    "email": employee_data["email"],
                    "password": employee_data["password"]
                })
                if login_response.status_code == 200:
                    data = login_response.json()
                    self.employee_token = data['access_token']
                    self.employee_user = data['user']
                    self.log_result("Setup Employee (existing)", True, f"Employé connecté: {self.employee_user['id']}")
                else:
                    self.log_result("Setup Employee", False, "Échec connexion employé existant", login_response.text)
            else:
                self.log_result("Setup Employee", False, f"Status: {response.status_code}", response.text)
        except Exception as e:
            self.log_result("Setup Employee", False, "Exception", str(e))

    def test_client_creation_with_employee_assignment(self):
        """Test 1: Création client avec assignation employé"""
        print("=== Test 1: Création client avec assignation employé ===")
        
        if not self.manager_token or not self.employee_user:
            self.log_result("Test 1 - Prérequis", False, "Manager ou employé non disponible")
            return

        try:
            headers = {"Authorization": f"Bearer {self.manager_token}"}
            timestamp = int(time.time())
            
            # Test avec assigned_employee_id spécifié
            client_data = {
                "email": f"client.assigne.{timestamp}@test.com",
                "full_name": "Client Assigné Test",
                "phone": "+33111222333",
                "country": "Canada",
                "visa_type": "Work Permit",
                "message": "Test assignation employé spécifique",
                "assigned_employee_id": self.employee_user['id']  # Assignation spécifique
            }
            
            response = self.session.post(f"{API_BASE}/clients", json=client_data, headers=headers)
            if response.status_code in [200, 201]:
                data = response.json()
                self.test_client_id = data['id']
                
                # Vérifier l'assignation
                if data.get('assigned_employee_id') == self.employee_user['id']:
                    self.log_result("Test 1A - Assignation spécifique", True, 
                                  f"Client assigné à l'employé spécifié: {data['assigned_employee_name']}")
                else:
                    self.log_result("Test 1A - Assignation spécifique", False, 
                                  f"Assignation incorrecte. Attendu: {self.employee_user['id']}, Reçu: {data.get('assigned_employee_id')}")
                
                # Vérifier les informations de connexion
                if data.get('login_email') and data.get('default_password'):
                    self.log_result("Test 1B - Informations connexion", True, 
                                  f"Email: {data['login_email']}, Mot de passe: {data['default_password']}")
                else:
                    self.log_result("Test 1B - Informations connexion", False, 
                                  "Informations de connexion manquantes")
                
            else:
                self.log_result("Test 1 - Création client", False, f"Status: {response.status_code}", response.text)
                
        except Exception as e:
            self.log_result("Test 1 - Exception", False, "Exception", str(e))

        # Test création par employé (doit fonctionner)
        if self.employee_token:
            try:
                headers = {"Authorization": f"Bearer {self.employee_token}"}
                client_data = {
                    "email": f"client.par.employe.{timestamp}@test.com",
                    "full_name": "Client Créé par Employé",
                    "phone": "+33444555666",
                    "country": "France",
                    "visa_type": "Student Visa",
                    "message": "Test création par employé"
                }
                
                response = self.session.post(f"{API_BASE}/clients", json=client_data, headers=headers)
                if response.status_code in [200, 201]:
                    data = response.json()
                    self.log_result("Test 1C - Création par employé", True, 
                                  f"Employé peut créer des clients. ID: {data['id']}")
                else:
                    self.log_result("Test 1C - Création par employé", False, 
                                  f"Status: {response.status_code}", response.text)
                    
            except Exception as e:
                self.log_result("Test 1C - Exception", False, "Exception", str(e))

    def test_employee_dashboard_restrictions(self):
        """Test 2: Restrictions dashboard employé"""
        print("=== Test 2: Restrictions dashboard employé ===")
        
        if not self.employee_token or not self.test_client_id:
            self.log_result("Test 2 - Prérequis", False, "Employé ou client test non disponible")
            return

        try:
            # D'abord, obtenir un cas à tester
            headers = {"Authorization": f"Bearer {self.employee_token}"}
            cases_response = self.session.get(f"{API_BASE}/cases", headers=headers)
            
            if cases_response.status_code == 200:
                cases = cases_response.json()
                if cases:
                    case_id = cases[0]['id']
                    self.test_case_id = case_id
                    
                    # Test: Employé peut voir les cas (GET)
                    self.log_result("Test 2A - Employé peut voir les cas", True, 
                                  f"Employé peut voir {len(cases)} cas")
                    
                    # Test: Employé NE PEUT PAS mettre à jour les cas (PATCH -> 403)
                    update_data = {
                        "current_step_index": 2,
                        "status": "Tentative mise à jour par employé",
                        "notes": "Ceci ne devrait pas fonctionner"
                    }
                    
                    patch_response = self.session.patch(f"{API_BASE}/cases/{case_id}", 
                                                      json=update_data, headers=headers)
                    
                    if patch_response.status_code == 403:
                        self.log_result("Test 2B - Restriction PATCH employé", True, 
                                      "Employé correctement bloqué pour mise à jour cas (403)")
                    else:
                        self.log_result("Test 2B - Restriction PATCH employé", False, 
                                      f"Employé devrait recevoir 403. Status: {patch_response.status_code}")
                        
                else:
                    self.log_result("Test 2 - Aucun cas", False, "Aucun cas disponible pour test")
            else:
                self.log_result("Test 2 - Récupération cas", False, 
                              f"Status: {cases_response.status_code}", cases_response.text)
                
        except Exception as e:
            self.log_result("Test 2 - Exception", False, "Exception", str(e))

        # Test: Seuls les managers peuvent mettre à jour
        if self.manager_token and self.test_case_id:
            try:
                headers = {"Authorization": f"Bearer {self.manager_token}"}
                update_data = {
                    "current_step_index": 1,
                    "status": "Mise à jour par manager",
                    "notes": "Test restriction - seul manager peut modifier"
                }
                
                response = self.session.patch(f"{API_BASE}/cases/{self.test_case_id}", 
                                            json=update_data, headers=headers)
                
                if response.status_code == 200:
                    self.log_result("Test 2C - Manager peut modifier", True, 
                                  "Manager peut mettre à jour les cas")
                else:
                    self.log_result("Test 2C - Manager peut modifier", False, 
                                  f"Status: {response.status_code}", response.text)
                    
            except Exception as e:
                self.log_result("Test 2C - Exception", False, "Exception", str(e))

    def test_complete_notification_system(self):
        """Test 3: Système de notifications complet"""
        print("=== Test 3: Système de notifications complet ===")
        
        if not self.manager_token:
            self.log_result("Test 3 - Prérequis", False, "Manager non disponible")
            return

        try:
            headers = {"Authorization": f"Bearer {self.manager_token}"}
            
            # Test 3A: GET /api/notifications
            notifications_response = self.session.get(f"{API_BASE}/notifications", headers=headers)
            if notifications_response.status_code == 200:
                notifications = notifications_response.json()
                self.log_result("Test 3A - GET notifications", True, 
                              f"Récupéré {len(notifications)} notifications")
            else:
                self.log_result("Test 3A - GET notifications", False, 
                              f"Status: {notifications_response.status_code}", notifications_response.text)
            
            # Test 3B: GET /api/notifications/unread-count
            unread_response = self.session.get(f"{API_BASE}/notifications/unread-count", headers=headers)
            if unread_response.status_code == 200:
                unread_data = unread_response.json()
                unread_count = unread_data.get('unread_count', 0)
                self.log_result("Test 3B - GET unread count", True, 
                              f"Notifications non lues: {unread_count}")
            else:
                self.log_result("Test 3B - GET unread count", False, 
                              f"Status: {unread_response.status_code}", unread_response.text)
            
            # Test 3C: PATCH /api/notifications/{id}/read
            if notifications_response.status_code == 200:
                notifications = notifications_response.json()
                if notifications:
                    notification_id = notifications[0]['id']
                    read_response = self.session.patch(f"{API_BASE}/notifications/{notification_id}/read", 
                                                     headers=headers)
                    if read_response.status_code == 200:
                        self.log_result("Test 3C - PATCH mark read", True, 
                                      f"Notification {notification_id} marquée comme lue")
                    else:
                        self.log_result("Test 3C - PATCH mark read", False, 
                                      f"Status: {read_response.status_code}", read_response.text)
                else:
                    self.log_result("Test 3C - PATCH mark read", False, 
                                  "Aucune notification disponible pour test")
                    
        except Exception as e:
            self.log_result("Test 3 - Exception", False, "Exception", str(e))

    def test_complete_workflow(self):
        """Test 4: Workflow complet avec notifications"""
        print("=== Test 4: Workflow complet avec notifications ===")
        
        if not all([self.manager_token, self.employee_token]):
            self.log_result("Test 4 - Prérequis", False, "Manager ou employé non disponible")
            return

        workflow_client_id = None
        workflow_case_id = None
        
        try:
            # Étape 1: Manager crée un client et l'assigne à un employé
            manager_headers = {"Authorization": f"Bearer {self.manager_token}"}
            timestamp = int(time.time())
            
            client_data = {
                "email": f"workflow.client.{timestamp}@test.com",
                "full_name": "Client Workflow Complet",
                "phone": "+33777888999",
                "country": "Canada",
                "visa_type": "Permanent Residence (Express Entry)",
                "message": "Test workflow complet avec notifications",
                "assigned_employee_id": self.employee_user['id']
            }
            
            client_response = self.session.post(f"{API_BASE}/clients", json=client_data, headers=manager_headers)
            if client_response.status_code in [200, 201]:
                client_data_response = client_response.json()
                workflow_client_id = client_data_response['id']
                self.log_result("Test 4A - Manager crée client", True, 
                              f"Client créé et assigné à employé: {workflow_client_id}")
                
                # Étape 2: Trouver le cas associé
                cases_response = self.session.get(f"{API_BASE}/cases", headers=manager_headers)
                if cases_response.status_code == 200:
                    cases = cases_response.json()
                    workflow_case = None
                    for case in cases:
                        if case['client_id'] == workflow_client_id:
                            workflow_case = case
                            workflow_case_id = case['id']
                            break
                    
                    if workflow_case:
                        # Étape 3: Manager met à jour le cas
                        update_data = {
                            "current_step_index": 2,
                            "status": "Documents en cours de vérification",
                            "notes": "Workflow complet - mise à jour par manager avec notifications"
                        }
                        
                        update_response = self.session.patch(f"{API_BASE}/cases/{workflow_case_id}", 
                                                           json=update_data, headers=manager_headers)
                        if update_response.status_code == 200:
                            self.log_result("Test 4B - Manager met à jour cas", True, 
                                          "Cas mis à jour avec succès par manager")
                            
                            # Étape 4: Vérifier que l'employé reçoit les notifications
                            employee_headers = {"Authorization": f"Bearer {self.employee_token}"}
                            time.sleep(1)  # Attendre que les notifications soient créées
                            
                            employee_notif_response = self.session.get(f"{API_BASE}/notifications", 
                                                                     headers=employee_headers)
                            if employee_notif_response.status_code == 200:
                                employee_notifications = employee_notif_response.json()
                                case_update_notif = any(notif['type'] == 'case_update' 
                                                      for notif in employee_notifications)
                                
                                if case_update_notif:
                                    self.log_result("Test 4C - Employé reçoit notification", True, 
                                                  "Employé a reçu notification de mise à jour cas")
                                else:
                                    self.log_result("Test 4C - Employé reçoit notification", False, 
                                                  "Employé n'a pas reçu notification de mise à jour cas")
                            else:
                                self.log_result("Test 4C - Vérification notifications employé", False, 
                                              f"Status: {employee_notif_response.status_code}")
                            
                            # Étape 5: Connecter le client et vérifier ses notifications
                            client_login_data = {
                                "email": client_data["email"],
                                "password": "Aloria2024!"
                            }
                            
                            client_login_response = self.session.post(f"{API_BASE}/auth/login", 
                                                                    json=client_login_data)
                            if client_login_response.status_code == 200:
                                client_token_data = client_login_response.json()
                                client_token = client_token_data['access_token']
                                client_headers = {"Authorization": f"Bearer {client_token}"}
                                
                                client_notif_response = self.session.get(f"{API_BASE}/notifications", 
                                                                        headers=client_headers)
                                if client_notif_response.status_code == 200:
                                    client_notifications = client_notif_response.json()
                                    case_update_notif = any(notif['type'] == 'case_update' 
                                                          for notif in client_notifications)
                                    
                                    if case_update_notif:
                                        self.log_result("Test 4D - Client reçoit notification", True, 
                                                      "Client a reçu notification de mise à jour cas")
                                    else:
                                        self.log_result("Test 4D - Client reçoit notification", False, 
                                                      "Client n'a pas reçu notification de mise à jour cas")
                                else:
                                    self.log_result("Test 4D - Vérification notifications client", False, 
                                                  f"Status: {client_notif_response.status_code}")
                                
                                # Étape 6: Tester que l'employé NE PEUT PAS modifier le cas
                                employee_update_data = {
                                    "current_step_index": 3,
                                    "status": "Tentative employé",
                                    "notes": "L'employé ne devrait pas pouvoir modifier"
                                }
                                
                                employee_update_response = self.session.patch(f"{API_BASE}/cases/{workflow_case_id}", 
                                                                             json=employee_update_data, 
                                                                             headers=employee_headers)
                                if employee_update_response.status_code == 403:
                                    self.log_result("Test 4E - Employé ne peut PAS modifier", True, 
                                                  "Employé correctement bloqué pour modification cas")
                                else:
                                    self.log_result("Test 4E - Employé ne peut PAS modifier", False, 
                                                  f"Employé devrait être bloqué. Status: {employee_update_response.status_code}")
                            else:
                                self.log_result("Test 4D - Connexion client", False, 
                                              f"Status: {client_login_response.status_code}")
                        else:
                            self.log_result("Test 4B - Manager met à jour cas", False, 
                                          f"Status: {update_response.status_code}", update_response.text)
                    else:
                        self.log_result("Test 4 - Trouver cas", False, "Cas non trouvé pour client créé")
                else:
                    self.log_result("Test 4 - Récupération cas", False, 
                                  f"Status: {cases_response.status_code}")
            else:
                self.log_result("Test 4A - Manager crée client", False, 
                              f"Status: {client_response.status_code}", client_response.text)
                
        except Exception as e:
            self.log_result("Test 4 - Exception", False, "Exception", str(e))

    def test_limited_countries(self):
        """Test 5: Pays limités (Canada et France uniquement)"""
        print("=== Test 5: Pays limités dans workflows ===")
        
        try:
            # Test récupération des workflows
            workflows_response = self.session.get(f"{API_BASE}/workflows")
            if workflows_response.status_code == 200:
                workflows = workflows_response.json()
                countries = list(workflows.keys())
                
                # Vérifier que seuls Canada et France sont présents
                expected_countries = {"Canada", "France"}
                actual_countries = set(countries)
                
                if actual_countries == expected_countries:
                    self.log_result("Test 5A - Pays limités", True, 
                                  f"Workflows limités aux pays attendus: {', '.join(countries)}")
                else:
                    self.log_result("Test 5A - Pays limités", False, 
                                  f"Pays inattendus. Attendu: {expected_countries}, Reçu: {actual_countries}")
                
                # Vérifier le contenu des workflows pour chaque pays
                for country in countries:
                    if country in workflows:
                        visa_types = list(workflows[country].keys())
                        self.log_result(f"Test 5B - Workflows {country}", True, 
                                      f"{country}: {len(visa_types)} types de visa disponibles")
                        
                        # Vérifier qu'il y a des étapes pour chaque type de visa
                        for visa_type in visa_types:
                            steps = workflows[country][visa_type]
                            if len(steps) > 0:
                                self.log_result(f"Test 5C - Étapes {country} {visa_type}", True, 
                                              f"{visa_type}: {len(steps)} étapes définies")
                            else:
                                self.log_result(f"Test 5C - Étapes {country} {visa_type}", False, 
                                              f"{visa_type}: Aucune étape définie")
            else:
                self.log_result("Test 5 - Récupération workflows", False, 
                              f"Status: {workflows_response.status_code}", workflows_response.text)
                
        except Exception as e:
            self.log_result("Test 5 - Exception", False, "Exception", str(e))

        # Test création client avec pays non supporté (devrait échouer ou utiliser workflow par défaut)
        if self.manager_token:
            try:
                headers = {"Authorization": f"Bearer {self.manager_token}"}
                timestamp = int(time.time())
                
                # Tenter de créer un client avec un pays non supporté
                client_data = {
                    "email": f"client.pays.invalide.{timestamp}@test.com",
                    "full_name": "Client Pays Non Supporté",
                    "phone": "+33999888777",
                    "country": "Allemagne",  # Pays non supporté
                    "visa_type": "Work Permit",
                    "message": "Test pays non supporté"
                }
                
                response = self.session.post(f"{API_BASE}/clients", json=client_data, headers=headers)
                if response.status_code in [200, 201]:
                    # Si la création réussit, vérifier que le workflow est vide ou par défaut
                    data = response.json()
                    client_id = data['id']
                    
                    # Récupérer le cas associé
                    cases_response = self.session.get(f"{API_BASE}/cases", headers=headers)
                    if cases_response.status_code == 200:
                        cases = cases_response.json()
                        test_case = None
                        for case in cases:
                            if case['client_id'] == client_id:
                                test_case = case
                                break
                        
                        if test_case:
                            workflow_steps = test_case.get('workflow_steps', [])
                            if len(workflow_steps) == 0:
                                self.log_result("Test 5D - Pays non supporté", True, 
                                              "Pays non supporté: workflow vide comme attendu")
                            else:
                                self.log_result("Test 5D - Pays non supporté", False, 
                                              f"Pays non supporté mais workflow présent: {len(workflow_steps)} étapes")
                        else:
                            self.log_result("Test 5D - Cas pays non supporté", False, 
                                          "Cas non trouvé pour client pays non supporté")
                else:
                    self.log_result("Test 5D - Création pays non supporté", False, 
                                  f"Création client pays non supporté échouée. Status: {response.status_code}")
                    
            except Exception as e:
                self.log_result("Test 5D - Exception", False, "Exception", str(e))

    def run_all_tests(self):
        """Exécuter tous les tests"""
        print("🚀 ALORIA AGENCY - Tests des nouvelles modifications")
        print(f"URL de test: {API_BASE}")
        print("=" * 70)
        
        # Configuration initiale
        self.setup_users()
        
        # Tests spécifiques
        self.test_client_creation_with_employee_assignment()
        self.test_employee_dashboard_restrictions()
        self.test_complete_notification_system()
        self.test_complete_workflow()
        self.test_limited_countries()
        
        # Résumé
        print("=" * 70)
        print("🏁 Résumé des tests")
        print(f"✅ Réussis: {self.results['passed']}")
        print(f"❌ Échoués: {self.results['failed']}")
        total_tests = self.results['passed'] + self.results['failed']
        if total_tests > 0:
            success_rate = (self.results['passed'] / total_tests) * 100
            print(f"📊 Taux de réussite: {success_rate:.1f}%")
        
        if self.results['errors']:
            print("\n🔍 Détails des échecs:")
            for error in self.results['errors']:
                print(f"  • {error['test']}: {error['message']}")
                if error['error']:
                    print(f"    Erreur: {error['error'][:200]}...")
        
        return self.results['failed'] == 0

if __name__ == "__main__":
    tester = AloriaAgencyTester()
    success = tester.run_all_tests()
    sys.exit(0 if success else 1)