#!/usr/bin/env python3
"""
Debug test for specific issues found in refactoring tests
"""

import requests
import json
import os

BACKEND_URL = os.environ.get('REACT_APP_BACKEND_URL', 'https://aloria-dev.preview.emergentagent.com')
API_BASE = f"{BACKEND_URL}/api"

# Login as manager
manager_login = requests.post(f"{API_BASE}/auth/login", json={
    'email': 'manager@test.com', 
    'password': 'password123'
})

if manager_login.status_code == 200:
    manager_token = manager_login.json()['access_token']
    headers = {"Authorization": f"Bearer {manager_token}"}
    
    print("=== DEBUG: Case Creation Issue ===")
    
    # Create a client
    client_data = {
        "email": "debug.client@test.com",
        "full_name": "Debug Client",
        "phone": "+237600000999",
        "country": "Canada",
        "visa_type": "Permis de travail",
        "message": "Debug test"
    }
    
    client_response = requests.post(f"{API_BASE}/clients", json=client_data, headers=headers)
    print(f"Client creation status: {client_response.status_code}")
    
    if client_response.status_code in [200, 201]:
        client_data_response = client_response.json()
        client_id = client_data_response['id']
        user_id = client_data_response['user_id']
        
        print(f"Client ID: {client_id}")
        print(f"User ID: {user_id}")
        
        # Check cases immediately
        cases_response = requests.get(f"{API_BASE}/cases", headers=headers)
        print(f"Cases response status: {cases_response.status_code}")
        
        if cases_response.status_code == 200:
            cases = cases_response.json()
            print(f"Total cases found: {len(cases)}")
            
            # Look for our client's case
            client_case = None
            for case in cases:
                print(f"Case client_id: {case.get('client_id')}, looking for: {user_id}")
                if case.get('client_id') == user_id:
                    client_case = case
                    break
            
            if client_case:
                print("✅ Case found for client!")
                print(f"Case ID: {client_case['id']}")
                print(f"Workflow steps: {len(client_case.get('workflow_steps', []))}")
            else:
                print("❌ Case NOT found for client")
                print("Available case client_ids:")
                for case in cases[-5:]:  # Show last 5 cases
                    print(f"  - {case.get('client_id')}")

print("\n=== DEBUG: Prospect Conversion Issue ===")

# Login as employee
employee_login = requests.post(f"{API_BASE}/auth/login", json={
    'email': 'employee@aloria.com', 
    'password': 'emp123'
})

if employee_login.status_code == 200:
    employee_token = employee_login.json()['access_token']
    employee_headers = {"Authorization": f"Bearer {employee_token}"}
    employee_user = employee_login.json()['user']
    
    # Create prospect
    prospect_data = {
        "name": "Debug Prospect",
        "email": "debug.prospect@test.com",
        "phone": "+237600000888",
        "country": "Canada",
        "visa_type": "Permis de travail",
        "budget_range": "3000-5000€",
        "urgency_level": "Normal",
        "message": "Debug prospect conversion test",
        "lead_source": "Site web",
        "how_did_you_know": "Test debug"
    }
    
    prospect_response = requests.post(f"{API_BASE}/contact-messages", json=prospect_data)
    print(f"Prospect creation status: {prospect_response.status_code}")
    
    if prospect_response.status_code in [200, 201]:
        prospect_data_response = prospect_response.json()
        prospect_id = prospect_data_response['id']
        print(f"Prospect ID: {prospect_id}")
        
        # Check if we need to assign the prospect first
        # Login as superadmin to assign
        superadmin_login = requests.post(f"{API_BASE}/auth/login", json={
            'email': 'superadmin@aloria.com', 
            'password': 'SuperAdmin123!'
        })
        
        if superadmin_login.status_code == 200:
            superadmin_token = superadmin_login.json()['access_token']
            superadmin_headers = {"Authorization": f"Bearer {superadmin_token}"}
            
            # Assign prospect to employee
            assign_data = {"assigned_to": employee_user['id']}
            assign_response = requests.patch(f"{API_BASE}/contact-messages/{prospect_id}/assign", 
                                           json=assign_data, headers=superadmin_headers)
            print(f"Prospect assignment status: {assign_response.status_code}")
            
            if assign_response.status_code == 200:
                print("✅ Prospect assigned to employee")
                
                # Now try conversion
                conversion_data = {
                    "first_payment_amount": 1500,
                    "country": "Canada",
                    "visa_type": "Permis de travail"
                }
                
                conversion_response = requests.post(
                    f"{API_BASE}/contact-messages/{prospect_id}/convert-to-client",
                    json=conversion_data,
                    headers=employee_headers
                )
                print(f"Conversion status: {conversion_response.status_code}")
                
                if conversion_response.status_code == 200:
                    print("✅ Prospect conversion successful!")
                    conversion_result = conversion_response.json()
                    print(f"New client ID: {conversion_result.get('client_id')}")
                else:
                    print(f"❌ Conversion failed: {conversion_response.text}")
            else:
                print(f"❌ Assignment failed: {assign_response.text}")