#!/usr/bin/env python3
"""
Create SuperAdmin for testing
"""

import requests
import os

BACKEND_URL = os.environ.get('REACT_APP_BACKEND_URL', 'https://aloria-dev.preview.emergentagent.com')
API_BASE = f"{BACKEND_URL}/api"

def create_superadmin():
    print("🔍 Creating SuperAdmin...")
    
    superadmin_data = {
        "email": "superadmin@aloria.com",
        "full_name": "Super Administrator",
        "phone": "+33123456789",
        "password": "SuperAdmin123!"
    }
    
    # The secret key from the backend code
    secret_key = "ALORIA_SUPER_SECRET_2024"
    
    try:
        response = requests.post(f"{API_BASE}/auth/create-superadmin", 
                               json=superadmin_data,
                               params={"secret_key": secret_key})
        
        print(f"📊 RESPONSE STATUS: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ SuperAdmin created successfully!")
            print(f"   Email: {result['user']['email']}")
            print(f"   Name: {result['user']['full_name']}")
            print(f"   ID: {result['user']['id']}")
            return True
        else:
            print(f"❌ Failed to create SuperAdmin: {response.status_code}")
            try:
                error = response.json()
                print(f"   Error: {error}")
            except:
                print(f"   Raw response: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Exception: {str(e)}")
        return False

def test_superadmin_login():
    print("🔍 Testing SuperAdmin login...")
    
    login_data = {
        "email": "superadmin@aloria.com",
        "password": "SuperAdmin123!"
    }
    
    try:
        response = requests.post(f"{API_BASE}/auth/login", json=login_data)
        
        print(f"📊 LOGIN STATUS: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ SuperAdmin login successful!")
            print(f"   Token: {result['access_token'][:20]}...")
            return result['access_token']
        else:
            print(f"❌ Login failed: {response.status_code}")
            try:
                error = response.json()
                print(f"   Error: {error}")
            except:
                print(f"   Raw response: {response.text}")
            return None
            
    except Exception as e:
        print(f"❌ Exception: {str(e)}")
        return None

def create_manager(superadmin_token):
    print("🔍 Creating Manager...")
    
    headers = {"Authorization": f"Bearer {superadmin_token}"}
    manager_data = {
        "email": "manager@test.com",
        "full_name": "Test Manager",
        "phone": "+33123456789",
        "role": "MANAGER",
        "send_email": False
    }
    
    try:
        response = requests.post(f"{API_BASE}/users/create", 
                               json=manager_data, 
                               headers=headers)
        
        print(f"📊 CREATE MANAGER STATUS: {response.status_code}")
        
        if response.status_code in [200, 201]:
            result = response.json()
            print(f"✅ Manager created successfully!")
            print(f"   Email: {result['email']}")
            print(f"   Temporary Password: {result.get('temporary_password', 'Not provided')}")
            return result.get('temporary_password')
        else:
            print(f"❌ Failed to create Manager: {response.status_code}")
            try:
                error = response.json()
                print(f"   Error: {error}")
            except:
                print(f"   Raw response: {response.text}")
            return None
            
    except Exception as e:
        print(f"❌ Exception: {str(e)}")
        return None

def test_manager_login(password):
    print(f"🔍 Testing Manager login with password: {password}")
    
    login_data = {
        "email": "manager@test.com",
        "password": password
    }
    
    try:
        response = requests.post(f"{API_BASE}/auth/login", json=login_data)
        
        print(f"📊 MANAGER LOGIN STATUS: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Manager login successful!")
            print(f"   Token: {result['access_token'][:20]}...")
            return True
        else:
            print(f"❌ Manager login failed: {response.status_code}")
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
    print("🚀 Setting up test users for ALORIA AGENCY")
    print("=" * 50)
    
    # Step 1: Create SuperAdmin
    if create_superadmin():
        # Step 2: Login as SuperAdmin
        superadmin_token = test_superadmin_login()
        
        if superadmin_token:
            # Step 3: Create Manager
            manager_password = create_manager(superadmin_token)
            
            if manager_password:
                # Step 4: Test Manager login
                if test_manager_login(manager_password):
                    print("\n✅ ALL SETUP COMPLETE!")
                    print(f"   SuperAdmin: superadmin@aloria.com / SuperAdmin123!")
                    print(f"   Manager: manager@test.com / {manager_password}")
                else:
                    # Try with default password
                    print("🔍 Trying with default password 'password123'")
                    if test_manager_login("password123"):
                        print("\n✅ SETUP COMPLETE!")
                        print(f"   SuperAdmin: superadmin@aloria.com / SuperAdmin123!")
                        print(f"   Manager: manager@test.com / password123")
    
    print("\n" + "=" * 50)