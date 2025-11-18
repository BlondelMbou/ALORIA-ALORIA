#!/usr/bin/env python3
"""
Test existing users and create manager if needed
"""

import requests
import os

BACKEND_URL = os.environ.get('REACT_APP_BACKEND_URL', 'https://aloria-refactor.preview.emergentagent.com')
API_BASE = f"{BACKEND_URL}/api"

# Test credentials from review request
TEST_CREDENTIALS = [
    {'email': 'superadmin@aloria.com', 'password': 'SuperAdmin123!', 'role': 'SUPERADMIN'},
    {'email': 'manager@test.com', 'password': 'password123', 'role': 'MANAGER'},
    {'email': 'employee@aloria.com', 'password': 'emp123', 'role': 'EMPLOYEE'},
    {'email': 'consultant@aloria.com', 'password': 'consultant123', 'role': 'CONSULTANT'},
]

def test_login(email, password, role):
    print(f"🔍 Testing {role}: {email}")
    
    login_data = {
        "email": email,
        "password": password
    }
    
    try:
        response = requests.post(f"{API_BASE}/auth/login", json=login_data)
        
        if response.status_code == 200:
            result = response.json()
            print(f"   ✅ Login successful! Token: {result['access_token'][:20]}...")
            return result['access_token']
        else:
            print(f"   ❌ Login failed: {response.status_code}")
            try:
                error = response.json()
                print(f"      Error: {error.get('detail', 'Unknown error')}")
            except:
                print(f"      Raw response: {response.text}")
            return None
            
    except Exception as e:
        print(f"   ❌ Exception: {str(e)}")
        return None

def create_manager_with_password123(superadmin_token):
    print("🔍 Creating Manager with password123...")
    
    headers = {"Authorization": f"Bearer {superadmin_token}"}
    
    # First, try to create the user account
    user_data = {
        "email": "manager@test.com",
        "full_name": "Test Manager",
        "phone": "+33123456789",
        "role": "MANAGER",
        "send_email": False
    }
    
    try:
        response = requests.post(f"{API_BASE}/users/create", 
                               json=user_data, 
                               headers=headers)
        
        print(f"📊 CREATE USER STATUS: {response.status_code}")
        
        if response.status_code in [200, 201]:
            result = response.json()
            print(f"✅ Manager user created!")
            print(f"   Email: {result['email']}")
            temp_password = result.get('temporary_password')
            print(f"   Temporary Password: {temp_password}")
            
            # Now try to change the password to 'password123'
            if temp_password:
                # Login with temp password first
                temp_login = requests.post(f"{API_BASE}/auth/login", json={
                    "email": "manager@test.com",
                    "password": temp_password
                })
                
                if temp_login.status_code == 200:
                    temp_token = temp_login.json()['access_token']
                    temp_headers = {"Authorization": f"Bearer {temp_token}"}
                    
                    # Change password
                    password_change = {
                        "old_password": temp_password,
                        "new_password": "password123"
                    }
                    
                    change_response = requests.patch(f"{API_BASE}/auth/change-password", 
                                                   json=password_change, 
                                                   headers=temp_headers)
                    
                    if change_response.status_code == 200:
                        print(f"✅ Password changed to 'password123'")
                        return True
                    else:
                        print(f"❌ Password change failed: {change_response.status_code}")
                        return False
                else:
                    print(f"❌ Cannot login with temp password: {temp_login.status_code}")
                    return False
            else:
                print("❌ No temporary password provided")
                return False
                
        elif response.status_code == 400:
            try:
                error = response.json()
                if "existe déjà" in error.get('detail', ''):
                    print("ℹ️ Manager user already exists")
                    return True
                else:
                    print(f"❌ Error: {error}")
                    return False
            except:
                print(f"❌ Raw response: {response.text}")
                return False
        else:
            print(f"❌ Failed to create Manager: {response.status_code}")
            try:
                error = response.json()
                print(f"   Error: {error}")
            except:
                print(f"   Raw response: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Exception: {str(e)}")
        return False

if __name__ == "__main__":
    print("🚀 Testing existing users for ALORIA AGENCY")
    print("=" * 50)
    
    working_tokens = {}
    
    # Test all credentials
    for cred in TEST_CREDENTIALS:
        token = test_login(cred['email'], cred['password'], cred['role'])
        if token:
            working_tokens[cred['role']] = token
    
    print(f"\n📊 WORKING CREDENTIALS: {len(working_tokens)}")
    for role in working_tokens:
        print(f"   ✅ {role}")
    
    # If SuperAdmin works but Manager doesn't, try to create/fix Manager
    if 'SUPERADMIN' in working_tokens and 'MANAGER' not in working_tokens:
        print(f"\n🔧 Attempting to create/fix Manager account...")
        if create_manager_with_password123(working_tokens['SUPERADMIN']):
            # Test manager login again
            manager_token = test_login('manager@test.com', 'password123', 'MANAGER')
            if manager_token:
                working_tokens['MANAGER'] = manager_token
                print(f"✅ Manager account is now working!")
    
    print(f"\n🎯 FINAL RESULT:")
    print(f"   Working accounts: {len(working_tokens)}")
    if 'MANAGER' in working_tokens:
        print(f"   ✅ Manager credentials: manager@test.com / password123")
    else:
        print(f"   ❌ Manager credentials not working")
    
    print("\n" + "=" * 50)