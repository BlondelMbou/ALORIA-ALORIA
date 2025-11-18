#!/usr/bin/env python3
"""
Fix Manager password using SuperAdmin privileges
"""

import requests
import os

BACKEND_URL = os.environ.get('REACT_APP_BACKEND_URL', 'https://aloria-dev.preview.emergentagent.com')
API_BASE = f"{BACKEND_URL}/api"

def get_superadmin_token():
    login_data = {
        "email": "superadmin@aloria.com",
        "password": "SuperAdmin123!"
    }
    
    response = requests.post(f"{API_BASE}/auth/login", json=login_data)
    if response.status_code == 200:
        return response.json()['access_token']
    return None

def reset_manager_password():
    print("🔍 Resetting Manager password...")
    
    # Use the forgot password endpoint
    reset_data = {
        "email": "manager@test.com"
    }
    
    try:
        response = requests.post(f"{API_BASE}/auth/forgot-password", json=reset_data)
        
        print(f"📊 RESET STATUS: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Password reset successful!")
            print(f"   Message: {result.get('message', 'Success')}")
            temp_password = result.get('temporary_password')
            if temp_password:
                print(f"   Temporary Password: {temp_password}")
                return temp_password
            else:
                print("❌ No temporary password in response")
                return None
        else:
            print(f"❌ Reset failed: {response.status_code}")
            try:
                error = response.json()
                print(f"   Error: {error}")
            except:
                print(f"   Raw response: {response.text}")
            return None
            
    except Exception as e:
        print(f"❌ Exception: {str(e)}")
        return None

def change_manager_password(temp_password, new_password):
    print(f"🔍 Changing Manager password from {temp_password} to {new_password}")
    
    # Login with temp password
    login_data = {
        "email": "manager@test.com",
        "password": temp_password
    }
    
    try:
        login_response = requests.post(f"{API_BASE}/auth/login", json=login_data)
        
        if login_response.status_code == 200:
            token = login_response.json()['access_token']
            headers = {"Authorization": f"Bearer {token}"}
            
            # Change password
            password_change = {
                "old_password": temp_password,
                "new_password": new_password
            }
            
            change_response = requests.patch(f"{API_BASE}/auth/change-password", 
                                           json=password_change, 
                                           headers=headers)
            
            if change_response.status_code == 200:
                print(f"✅ Password changed successfully!")
                return True
            else:
                print(f"❌ Password change failed: {change_response.status_code}")
                try:
                    error = change_response.json()
                    print(f"   Error: {error}")
                except:
                    print(f"   Raw response: {change_response.text}")
                return False
        else:
            print(f"❌ Cannot login with temp password: {login_response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Exception: {str(e)}")
        return False

def test_manager_login():
    print("🔍 Testing Manager login with password123...")
    
    login_data = {
        "email": "manager@test.com",
        "password": "password123"
    }
    
    try:
        response = requests.post(f"{API_BASE}/auth/login", json=login_data)
        
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
    print("🚀 Fixing Manager password for ALORIA AGENCY")
    print("=" * 50)
    
    # Step 1: Reset Manager password
    temp_password = reset_manager_password()
    
    if temp_password:
        # Step 2: Change to password123
        if change_manager_password(temp_password, "password123"):
            # Step 3: Test login
            if test_manager_login():
                print("\n✅ MANAGER PASSWORD FIXED!")
                print("   Credentials: manager@test.com / password123")
            else:
                print("\n❌ Password change succeeded but login still fails")
        else:
            print("\n❌ Failed to change password")
    else:
        print("\n❌ Failed to reset password")
    
    print("\n" + "=" * 50)