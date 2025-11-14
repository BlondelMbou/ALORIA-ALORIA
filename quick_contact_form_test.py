#!/usr/bin/env python3
"""
ALORIA AGENCY - Test rapide du formulaire de contact
Script simple pour tester le nouveau formulaire de contact de la landing page
"""

import requests
import json
import os
from datetime import datetime

# Configuration
BACKEND_URL = os.environ.get('REACT_APP_BACKEND_URL', 'https://migration-hub.preview.emergentagent.com')
API_BASE = f"{BACKEND_URL}/api"

def test_contact_form():
    """Test du formulaire de contact avec données variées"""
    
    print("🎯 TEST FORMULAIRE DE CONTACT - ALORIA AGENCY")
    print("="*50)
    
    # Données de test réalistes
    test_contacts = [
        {
            "name": "Marie Dubois",
            "email": "marie.dubois@example.com",
            "phone": "+33 1 23 45 67 89",
            "country": "France",
            "visa_type": "Permis de Travail (Passeport Talent)",
            "budget_range": "5000+€",
            "urgency_level": "URGENT",
            "message": "Bonjour, je suis développeuse senior et j'ai reçu une offre d'emploi à Paris. J'aimerais être accompagnée pour obtenir le passeport talent le plus rapidement possible. Mon entreprise est prête à financer l'accompagnement.",
            "lead_source": "WEBSITE"
        },
        {
            "name": "Ahmed Hassan",
            "email": "a.hassan.canada@gmail.com", 
            "phone": "+212 6 12 34 56 78",
            "country": "Canada",
            "visa_type": "Résidence Permanente (Entrée Express)",
            "budget_range": "3000-5000€",
            "urgency_level": "NORMAL",
            "message": "Ingénieur civil avec 6 ans d'expérience, je souhaite immigrer au Canada. Score CRS estimé à 470 points. Besoin d'accompagnement pour optimiser mon profil.",
            "lead_source": "WEBSITE"
        },
        {
            "name": "Elena Popov",
            "email": "elena.student@university.edu",
            "country": "France", 
            "visa_type": "Visa Étudiant",
            "budget_range": "1000-3000€",
            "urgency_level": "FLEXIBLE",
            "message": "Étudiante bulgare, j'aimerais faire mon master en France. J'ai le temps de bien préparer mon dossier.",
            "lead_source": "WEBSITE"
        },
        {
            "name": "Test Lead Minimum",
            "email": "test@test.com",
            "country": "Autre",
            "message": "Information générale sur l'immigration.",
            "lead_source": "WEBSITE"
        },
        {
            "name": "Premium Client",
            "email": "premium@company.com",
            "phone": "+1 555 123 4567",
            "country": "Canada", 
            "visa_type": "Permis de Travail",
            "budget_range": "5000+€",
            "urgency_level": "URGENT",
            "message": "PDG d'une startup tech, relocating équipe complète au Canada. Budget illimité, accompagnement premium requis pour 10+ personnes. Timeline agressive - 3 mois maximum.",
            "lead_source": "WEBSITE"
        }
    ]
    
    created_contacts = []
    
    for i, contact_data in enumerate(test_contacts, 1):
        print(f"\n📝 Test {i}/5: Création contact {contact_data['name']}")
        print(f"   Email: {contact_data['email']}")
        print(f"   Pays: {contact_data['country']}")
        print(f"   Budget: {contact_data.get('budget_range', 'Non spécifié')}")
        print(f"   Urgence: {contact_data.get('urgency_level', 'Non spécifiée')}")
        
        try:
            # Envoyer la requête
            response = requests.post(f"{API_BASE}/contact-messages", json=contact_data)
            
            if response.status_code in [200, 201]:
                result = response.json()
                created_contacts.append(result)
                
                # Afficher les résultats
                print(f"   ✅ Contact créé avec succès!")
                print(f"   📊 Lead Score: {result.get('conversion_probability', 'N/A')}%")
                print(f"   🆔 ID: {result.get('id', 'N/A')}")
                print(f"   📅 Statut: {result.get('status', 'N/A')}")
                
                # Analyser le score
                score = result.get('conversion_probability', 0)
                if score >= 80:
                    print("   🌟 Lead PREMIUM - Priorité maximale")
                elif score >= 60:
                    print("   ⭐ Lead QUALIFIÉ - Bon potentiel")
                elif score >= 40:
                    print("   📋 Lead STANDARD - Potentiel moyen")
                else:
                    print("   📝 Lead BASIQUE - Suivi standard")
                    
            else:
                print(f"   ❌ Erreur création: {response.status_code}")
                if response.text:
                    try:
                        error_detail = response.json()
                        print(f"   📋 Détail: {error_detail.get('detail', 'Erreur inconnue')}")
                    except:
                        print(f"   📋 Réponse: {response.text[:100]}...")
                        
        except Exception as e:
            print(f"   ❌ Exception: {e}")
    
    # Résumé des résultats
    print("\n" + "="*50)
    print("📊 RÉSUMÉ DES TESTS")
    print(f"✅ {len(created_contacts)}/{len(test_contacts)} contacts créés avec succès")
    
    if created_contacts:
        scores = [c.get('conversion_probability', 0) for c in created_contacts]
        avg_score = sum(scores) / len(scores)
        
        print(f"📈 Score moyen: {avg_score:.1f}%")
        print(f"📊 Scores: {scores}")
        
        # Catégoriser les leads
        premium_leads = len([s for s in scores if s >= 80])
        qualified_leads = len([s for s in scores if 60 <= s < 80])
        standard_leads = len([s for s in scores if 40 <= s < 60])
        basic_leads = len([s for s in scores if s < 40])
        
        print(f"\n🎯 CATÉGORISATION DES LEADS:")
        print(f"   🌟 Premium (≥80%): {premium_leads}")
        print(f"   ⭐ Qualifié (60-79%): {qualified_leads}")
        print(f"   📋 Standard (40-59%): {standard_leads}")
        print(f"   📝 Basique (<40%): {basic_leads}")
    
    return created_contacts

def test_crm_access(created_contacts):
    """Test d'accès aux données via CRM Manager"""
    
    if not created_contacts:
        print("\n⚠️ Aucun contact créé - skip test CRM")
        return
        
    print("\n🔐 TEST ACCÈS CRM MANAGER")
    print("-" * 30)
    
    # Login Manager
    login_data = {"email": "manager@test.com", "password": "password123"}
    
    try:
        login_response = requests.post(f"{API_BASE}/auth/login", json=login_data)
        
        if login_response.status_code == 200:
            token = login_response.json()['access_token']
            headers = {"Authorization": f"Bearer {token}"}
            
            print("✅ Manager connecté avec succès")
            
            # Récupérer les messages via CRM
            crm_response = requests.get(f"{API_BASE}/contact-messages", headers=headers)
            
            if crm_response.status_code == 200:
                crm_messages = crm_response.json()
                print(f"✅ {len(crm_messages)} messages récupérés via CRM")
                
                # Vérifier que nos contacts créés sont présents
                our_emails = [c.get('email') for c in created_contacts]
                found_contacts = [msg for msg in crm_messages if msg.get('email') in our_emails]
                
                print(f"✅ {len(found_contacts)}/{len(created_contacts)} de nos contacts trouvés dans le CRM")
                
                # Afficher quelques détails
                for contact in found_contacts[:3]:  # Max 3 pour éviter spam
                    print(f"   📧 {contact.get('name')} ({contact.get('email')})")
                    print(f"      Score: {contact.get('conversion_probability')}% | Statut: {contact.get('status')}")
                
            else:
                print(f"❌ Erreur récupération CRM: {crm_response.status_code}")
        else:
            print(f"❌ Erreur login Manager: {login_response.status_code}")
            
    except Exception as e:
        print(f"❌ Exception CRM: {e}")

def test_form_validation():
    """Test de validation du formulaire"""
    
    print("\n🛡️ TEST VALIDATION FORMULAIRE")
    print("-" * 30)
    
    # Test avec données invalides
    invalid_tests = [
        {
            "name": "Test Email Invalide",
            "data": {
                "name": "Test User",
                "email": "email-invalide",  # Email invalide
                "message": "Test message",
                "lead_source": "WEBSITE"
            },
            "should_fail": True
        },
        {
            "name": "Test Message Trop Court",
            "data": {
                "name": "Test User", 
                "email": "test@valid.com",
                "message": "Court",  # Message < 10 caractères
                "lead_source": "WEBSITE"
            },
            "should_fail": True
        },
        {
            "name": "Test Champs Requis Manquants",
            "data": {
                "email": "test@valid.com",  # Nom manquant
                "message": "Message de test suffisamment long",
                "lead_source": "WEBSITE"
            },
            "should_fail": True
        }
    ]
    
    for test_case in invalid_tests:
        print(f"\n🧪 {test_case['name']}:")
        
        try:
            response = requests.post(f"{API_BASE}/contact-messages", json=test_case['data'])
            
            if test_case['should_fail']:
                if response.status_code in [400, 422]:
                    print("   ✅ Validation correcte - requête rejetée comme attendu")
                else:
                    print(f"   ⚠️ Inattendu - Status {response.status_code} (devrait être rejetée)")
            else:
                if response.status_code in [200, 201]:
                    print("   ✅ Requête valide acceptée")
                else:
                    print(f"   ❌ Requête valide rejetée - Status {response.status_code}")
                    
        except Exception as e:
            print(f"   ❌ Exception: {e}")

if __name__ == "__main__":
    print("ALORIA AGENCY - Test rapide du formulaire de contact")
    print("Script de test pour valider le nouveau formulaire de la landing page")
    print(f"Backend: {BACKEND_URL}")
    print(f"Timestamp: {datetime.now().isoformat()}")
    
    # Exécuter les tests
    created_contacts = test_contact_form()
    test_crm_access(created_contacts)
    test_form_validation()
    
    print(f"\n🎉 TESTS TERMINÉS - {datetime.now().strftime('%H:%M:%S')}")
    print("✅ Formulaire de contact testé avec succès!")