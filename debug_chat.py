#!/usr/bin/env python3
"""
Debug script for chat permissions issue
"""

import requests
import json
import os

# Get backend URL from environment
BACKEND_URL = os.environ.get('REACT_APP_BACKEND_URL', 'https://agence-debug.preview.emergentagent.com')
API_BASE = f"{BACKEND_URL}/api"

# Test credentials
TEST_CREDENTIALS = {
    'manager': {'email': 'manager@test.com', 'password': 'password123'},
    'employee': {'email': 'employee@aloria.com', 'password': 'emp123'},
}

def debug_chat_permissions():
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
    
    # Create a test client
    headers = {"Authorization": f"Bearer {tokens['manager']}"}
    client_data = {
        "email": "debug.client@example.com",
        "full_name": "Debug Client",
        "phone": "+33123456789",
        "country": "France",
        "visa_type": "Work Permit",
        "message": "Debug client for chat permissions"
    }
    
    response = session.post(f"{API_BASE}/clients", json=client_data, headers=headers)
    if response.status_code in [200, 201]:
        client_response = response.json()
        print(f"✅ Client created: {client_response['id']}")
        print(f"   Assigned employee ID: {client_response.get('assigned_employee_id')}")
        print(f"   User ID: {client_response.get('user_id')}")
        
        # Login as client
        client_login = session.post(f"{API_BASE}/auth/login", json={
            "email": "debug.client@example.com",
            "password": "Aloria2024!"
        })
        if client_login.status_code == 200:
            client_data = client_login.json()
            tokens['client'] = client_data['access_token']
            users['client'] = client_data['user']
            print(f"✅ Client logged in: {users['client']['full_name']} (ID: {users['client']['id']})")
            
            # Check client record in database
            client_headers = {"Authorization": f"Bearer {tokens['client']}"}
            client_info_response = session.get(f"{API_BASE}/clients", headers=client_headers)
            if client_info_response.status_code == 200:
                client_records = client_info_response.json()
                print(f"✅ Client records found: {len(client_records)}")
                if client_records:
                    client_record = client_records[0]
                    print(f"   Client record assigned_employee_id: {client_record.get('assigned_employee_id')}")
                    print(f"   Employee user ID from login: {users['employee']['id']}")
                    print(f"   Match: {client_record.get('assigned_employee_id') == users['employee']['id']}")
            
            # Check available contacts for client
            contacts_response = session.get(f"{API_BASE}/users/available-contacts", headers=client_headers)
            if contacts_response.status_code == 200:
                contacts = contacts_response.json()
                print(f"✅ Client available contacts: {len(contacts)}")
                for contact in contacts:
                    print(f"   - {contact['full_name']} ({contact['role']}) ID: {contact['id']}")
                    if contact['role'] == 'EMPLOYEE':
                        print(f"     Employee match: {contact['id'] == users['employee']['id']}")
            
            # Try to send message from client to employee
            message_data = {
                "receiver_id": users['employee']['id'],
                "message": "Debug test message"
            }
            message_response = session.post(f"{API_BASE}/chat/send", json=message_data, headers=client_headers)
            print(f"📨 Client to Employee message: {message_response.status_code}")
            if message_response.status_code != 200:
                print(f"   Error: {message_response.text}")
            
            # Try to send message from employee to client
            employee_headers = {"Authorization": f"Bearer {tokens['employee']}"}
            message_data = {
                "receiver_id": users['client']['id'],
                "message": "Debug test message from employee"
            }
            message_response = session.post(f"{API_BASE}/chat/send", json=message_data, headers=employee_headers)
            print(f"📨 Employee to Client message: {message_response.status_code}")
            if message_response.status_code != 200:
                print(f"   Error: {message_response.text}")
        else:
            print(f"❌ Client login failed: {client_login.status_code}")
    else:
        print(f"❌ Client creation failed: {response.status_code}")

if __name__ == "__main__":
    debug_chat_permissions()