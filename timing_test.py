#!/usr/bin/env python3
"""
Test timing issue for case creation
"""

import requests
import json
import os
import time

BACKEND_URL = os.environ.get('REACT_APP_BACKEND_URL', 'https://migration-hub.preview.emergentagent.com')
API_BASE = f"{BACKEND_URL}/api"

# Login Manager
manager_login = requests.post(f"{API_BASE}/auth/login", json={
    'email': 'manager@test.com', 
    'password': 'password123'
})

if manager_login.status_code == 200:
    manager_token = manager_login.json()['access_token']
    headers = {"Authorization": f"Bearer {manager_token}"}
    
    print("=== TEST TIMING CASE CREATION ===")
    
    # Create client
    client_data = {
        "email": "timing.test@test.com",
        "full_name": "Timing Test Client",
        "phone": "+237600000888",
        "country": "Canada",
        "visa_type": "Permis de travail",
        "message": "Test timing"
    }
    
    client_response = requests.post(f"{API_BASE}/clients", json=client_data, headers=headers)
    print(f"Client creation status: {client_response.status_code}")
    
    if client_response.status_code in [200, 201]:
        client_data_response = client_response.json()
        user_id = client_data_response['user_id']
        print(f"User ID: {user_id}")
        
        # Test case retrieval with different delays
        for delay in [0, 1, 3, 5]:
            print(f"\n--- Test avec délai de {delay} secondes ---")
            time.sleep(delay)
            
            cases_response = requests.get(f"{API_BASE}/cases", headers=headers)
            if cases_response.status_code == 200:
                cases = cases_response.json()
                client_case = next((c for c in cases if c.get('client_id') == user_id), None)
                
                if client_case:
                    print(f"✅ Case trouvé après {delay}s: {client_case['id']}")
                    print(f"   Workflow steps: {len(client_case.get('workflow_steps', []))}")
                    break
                else:
                    print(f"❌ Case non trouvé après {delay}s")
            else:
                print(f"❌ Erreur API: {cases_response.status_code}")