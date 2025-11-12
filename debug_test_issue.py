#!/usr/bin/env python3
"""
Debug the specific test issue
"""

import requests
import json
import os
import time

# Get backend URL from environment
BACKEND_URL = os.environ.get('REACT_APP_BACKEND_URL', 'https://aloria-manager.preview.emergentagent.com')
API_BASE = f"{BACKEND_URL}/api"

# Test credentials
TEST_CREDENTIALS = {
    'manager': {'email': 'manager@test.com', 'password': 'password123'},
    'employee': {'email': 'employee@aloria.com', 'password': 'emp123'},
}

def debug_test_issue():
    session = requests.Session()
    tokens = {}
    users = {}
    
    # Login as manager and employee
    for role, credentials in TEST_CREDENTIALS.items():
        response = session.post(f"{API_BASE}/auth/login", json=credentials)
        if response.status_code == 200:
            data = response.json()
            tokens[role] = data['access_token']
            users[role] = data['user']
            print(f"✅ {role.upper()} logged in: {users[role]['full_name']} (ID: {users[role]['id']})")
        else:
            print(f"❌ {role.upper()} login failed: {response.status_code}")
            return
    
    # Create a test client with unique email
    timestamp = int(time.time())
    headers = {"Authorization": f"Bearer {tokens['manager']}"}
    client_data = {
        "email": f"test.client.chat.{timestamp}@example.com",
        "full_name": "Client Test Chat Debug",
        "phone": "+33123456789",
        "country": "France",
        "visa_type": "Work Permit (Talent Permit)",
        "message": "Test client for chat permissions"
    }
    
    response = session.post(f"{API_BASE}/clients", json=client_data, headers=headers)
    if response.status_code in [200, 201]:
        client_response = response.json()
        client_id = client_response['id']
        initial_assigned_employee_id = client_response.get('assigned_employee_id')
        print(f"✅ Client created: {client_id}")
        print(f"   Initially assigned employee ID: {initial_assigned_employee_id}")
        print(f"   Target employee ID: {users['employee']['id']}")
        print(f"   Match: {initial_assigned_employee_id == users['employee']['id']}")
        
        # Reassign client to our test employee
        reassign_url = f"{API_BASE}/clients/{client_id}/reassign?new_employee_id={users['employee']['id']}"
        reassign_response = session.patch(reassign_url, headers=headers)
        print(f"🔄 Reassign response: {reassign_response.status_code}")
        if reassign_response.status_code == 200:
            print(f"   ✅ Reassignment successful")
        else:
            print(f"   ❌ Reassign failed: {reassign_response.text}")
            return
        
        # Verify reassignment by getting client info
        client_info_response = session.get(f"{API_BASE}/clients/{client_id}", headers=headers)
        if client_info_response.status_code == 200:
            client_info = client_info_response.json()
            current_assigned_employee_id = client_info.get('assigned_employee_id')
            print(f"✅ Client info after reassignment:")
            print(f"   Current assigned employee ID: {current_assigned_employee_id}")
            print(f"   Target employee ID: {users['employee']['id']}")
            print(f"   Match: {current_assigned_employee_id == users['employee']['id']}")
        
        # Login as client
        client_login = session.post(f"{API_BASE}/auth/login", json={
            "email": f"test.client.chat.{timestamp}@example.com",
            "password": "Aloria2024!"
        })
        if client_login.status_code == 200:
            client_data = client_login.json()
            tokens['client'] = client_data['access_token']
            users['client'] = client_data['user']
            print(f"✅ Client logged in: {users['client']['full_name']} (ID: {users['client']['id']})")
            
            # Check client's own client record
            client_headers = {"Authorization": f"Bearer {tokens['client']}"}
            client_records_response = session.get(f"{API_BASE}/clients", headers=client_headers)
            if client_records_response.status_code == 200:
                client_records = client_records_response.json()
                print(f"✅ Client records from client perspective: {len(client_records)}")
                if client_records:
                    client_record = client_records[0]
                    print(f"   Client record assigned_employee_id: {client_record.get('assigned_employee_id')}")
                    print(f"   Target employee ID: {users['employee']['id']}")
                    print(f"   Match: {client_record.get('assigned_employee_id') == users['employee']['id']}")
            
            # Check available contacts for client
            contacts_response = session.get(f"{API_BASE}/users/available-contacts", headers=client_headers)
            if contacts_response.status_code == 200:
                contacts = contacts_response.json()
                print(f"✅ Client available contacts: {len(contacts)}")
                target_employee_found = False
                for contact in contacts:
                    if contact['role'] == 'EMPLOYEE':
                        print(f"   - {contact['full_name']} ({contact['role']}) ID: {contact['id']}")
                        if contact['id'] == users['employee']['id']:
                            target_employee_found = True
                            print(f"     ✅ Found our target employee in contacts!")
                
                if not target_employee_found:
                    print(f"   ❌ Our target employee not found in contacts")
                    print(f"   Target employee ID: {users['employee']['id']}")
            
            # Try to send message from client to employee
            message_data = {
                "receiver_id": users['employee']['id'],
                "message": "Debug test message - checking permissions"
            }
            message_response = session.post(f"{API_BASE}/chat/send", json=message_data, headers=client_headers)
            print(f"📨 Client to Employee message: {message_response.status_code}")
            if message_response.status_code == 200:
                print(f"   ✅ Message sent successfully!")
            else:
                print(f"   ❌ Error: {message_response.text}")
        else:
            print(f"❌ Client login failed: {client_login.status_code}")
    else:
        print(f"❌ Client creation failed: {response.status_code}")

if __name__ == "__main__":
    debug_test_issue()