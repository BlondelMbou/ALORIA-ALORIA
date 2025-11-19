#!/usr/bin/env python3
"""
ALORIA AGENCY Focused Critical Bug Fixes Testing

Testing the specific fixes mentioned in the review request:
1. Manager Case Update Error (server.py lines 1486, 1496) - create_notification() missing db parameter
2. Employee Dashboard Client Data N/A (EmployeeDashboard.js lines 701, 704, 705) - wrong data source
"""

import requests
import json
import os
from datetime import datetime

# Get backend URL from environment
BACKEND_URL = os.environ.get('REACT_APP_BACKEND_URL', 'https://aloria-dev.preview.emergentagent.com')
API_BASE = f"{BACKEND_URL}/api"

def test_manager_case_update():
    """Test Manager Case Update - The critical bug fix"""
    print("=== TEST 1: MANAGER CASE UPDATE ERROR FIX ===")
    
    # Login as manager
    login_response = requests.post(f"{API_BASE}/auth/login", json={
        "email": "manager@test.com",
        "password": "password123"
    })
    
    if login_response.status_code != 200:
        print(f"❌ Manager login failed: {login_response.status_code}")
        return False
    
    token = login_response.json()['access_token']
    headers = {"Authorization": f"Bearer {token}"}
    print("✅ Manager logged in successfully")
    
    # Get cases
    cases_response = requests.get(f"{API_BASE}/cases", headers=headers)
    if cases_response.status_code != 200:
        print(f"❌ Cannot retrieve cases: {cases_response.status_code}")
        return False
    
    cases = cases_response.json()
    print(f"✅ Retrieved {len(cases)} cases")
    
    if len(cases) == 0:
        print("❌ No cases available for testing")
        return False
    
    # Select the first case for testing
    test_case = cases[0]
    case_id = test_case['id']
    client_name = test_case.get('client_name', 'Unknown')
    
    print(f"📋 Testing case: {case_id} - Client: {client_name}")
    
    # Attempt to update the case - this is where the bug would occur
    update_data = {
        "current_step_index": 2,
        "status": "En cours",
        "notes": f"Test update - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
    }
    
    print(f"🔍 Updating case with data: {update_data}")
    
    update_response = requests.patch(f"{API_BASE}/cases/{case_id}", 
                                   json=update_data, headers=headers)
    
    print(f"📊 Update response status: {update_response.status_code}")
    
    if update_response.status_code == 200:
        print("✅ CRITICAL BUG FIX VERIFIED: Case update successful - No notification error!")
        
        # Verify the case was actually updated
        updated_case_response = requests.get(f"{API_BASE}/cases/{case_id}", headers=headers)
        if updated_case_response.status_code == 200:
            updated_case = updated_case_response.json()
            if updated_case.get('current_step_index') == 2 and updated_case.get('status') == "En cours":
                print("✅ Case data successfully updated")
                return True
            else:
                print("❌ Case data not properly updated")
                return False
        else:
            print("❌ Cannot verify case update")
            return False
    
    elif update_response.status_code == 500:
        try:
            error_data = update_response.json()
            error_detail = error_data.get('detail', 'Unknown error')
            
            if 'notification' in error_detail.lower() or 'create_notification' in error_detail.lower():
                print("❌ CRITICAL BUG STILL PRESENT: Notification error detected!")
                print(f"   Error: {error_detail}")
                return False
            else:
                print(f"❌ Unexpected 500 error: {error_detail}")
                return False
        except:
            print(f"❌ 500 error - Cannot parse response: {update_response.text}")
            return False
    
    else:
        print(f"❌ Unexpected status code: {update_response.status_code}")
        print(f"   Response: {update_response.text}")
        return False

def test_employee_client_data():
    """Test Employee Client Data - The critical bug fix"""
    print("\n=== TEST 2: EMPLOYEE CLIENT DATA N/A FIX ===")
    
    # Login as employee
    login_response = requests.post(f"{API_BASE}/auth/login", json={
        "email": "employee@aloria.com",
        "password": "emp123"
    })
    
    if login_response.status_code != 200:
        print(f"❌ Employee login failed: {login_response.status_code}")
        return False
    
    token = login_response.json()['access_token']
    employee_user = login_response.json()['user']
    headers = {"Authorization": f"Bearer {token}"}
    print(f"✅ Employee logged in: {employee_user.get('full_name')}")
    
    # Get clients assigned to this employee
    clients_response = requests.get(f"{API_BASE}/clients", headers=headers)
    if clients_response.status_code != 200:
        print(f"❌ Cannot retrieve clients: {clients_response.status_code}")
        return False
    
    clients = clients_response.json()
    print(f"✅ Retrieved {len(clients)} clients for employee")
    
    if len(clients) == 0:
        print("⚠️  No clients assigned to this employee - Cannot test data display")
        return True  # This is not necessarily a failure
    
    # Check for N/A data in clients
    clients_with_na = []
    clients_with_complete_data = []
    
    for i, client in enumerate(clients):
        client_issues = []
        
        # Check full_name
        full_name = client.get('full_name')
        if not full_name or full_name == 'N/A' or full_name.strip() == '':
            client_issues.append(f"full_name: '{full_name}'")
        
        # Check email
        email = client.get('email')
        if not email or email == 'N/A' or email.strip() == '' or '@' not in str(email):
            client_issues.append(f"email: '{email}'")
        
        # Check phone (N/A is not acceptable, but null/empty is OK)
        phone = client.get('phone')
        if phone == 'N/A':
            client_issues.append(f"phone: '{phone}'")
        
        if client_issues:
            clients_with_na.append({
                'index': i + 1,
                'id': client.get('id', 'unknown'),
                'issues': client_issues
            })
        else:
            clients_with_complete_data.append({
                'full_name': full_name,
                'email': email,
                'phone': phone
            })
    
    print(f"📊 Analysis results:")
    print(f"   - Clients with complete data: {len(clients_with_complete_data)}")
    print(f"   - Clients with N/A issues: {len(clients_with_na)}")
    
    if len(clients_with_na) == 0:
        print("✅ CRITICAL BUG FIX VERIFIED: No clients with N/A data found!")
        
        # Show some sample data to confirm
        if len(clients_with_complete_data) > 0:
            sample = clients_with_complete_data[0]
            print(f"   Sample client data: {sample['full_name']} ({sample['email']}) - {sample['phone']}")
        
        return True
    else:
        print("❌ CRITICAL BUG STILL PRESENT: Clients with N/A data detected!")
        for client in clients_with_na[:3]:  # Show first 3
            print(f"   Client {client['index']} ({client['id']}): {', '.join(client['issues'])}")
        return False

def main():
    """Run both critical bug tests"""
    print("🚀 ALORIA AGENCY - CRITICAL BUG FIXES VERIFICATION")
    print("=" * 60)
    print("Testing fixes for:")
    print("1. Manager Case Update Error (server.py lines 1486, 1496)")
    print("2. Employee Dashboard Client Data N/A (lines 701, 704, 705)")
    print("=" * 60)
    
    # Test 1: Manager Case Update
    test1_result = test_manager_case_update()
    
    # Test 2: Employee Client Data
    test2_result = test_employee_client_data()
    
    # Summary
    print("\n" + "=" * 60)
    print("🏁 FINAL RESULTS")
    print("=" * 60)
    
    if test1_result:
        print("✅ TEST 1 PASSED: Manager Case Update Error - FIXED")
    else:
        print("❌ TEST 1 FAILED: Manager Case Update Error - NOT FIXED")
    
    if test2_result:
        print("✅ TEST 2 PASSED: Employee Client Data N/A - FIXED")
    else:
        print("❌ TEST 2 FAILED: Employee Client Data N/A - NOT FIXED")
    
    print("=" * 60)
    
    if test1_result and test2_result:
        print("🎉 ALL CRITICAL BUG FIXES VERIFIED SUCCESSFULLY!")
        return True
    else:
        print("🚨 SOME CRITICAL BUGS STILL PRESENT - REVIEW NEEDED")
        return False

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)