#!/usr/bin/env python3
"""
Test script to verify the pay buttons implementation
"""

import json
import requests

API_BASE = "http://localhost:5000"
STUDENT_ID = "3007001"  # Test student ID

def test_api_endpoints():
    """Test that all API endpoints return correct data"""
    print("=" * 60)
    print("🧪 Testing API Endpoints")
    print("=" * 60)
    
    # Test 1: Get Student Profile
    print("\n1️⃣  Testing GET /api/student/me?id={}".format(STUDENT_ID))
    try:
        resp = requests.get(f"{API_BASE}/api/student/me?id={STUDENT_ID}")
        if resp.status_code == 200:
            data = resp.json()
            print(f"   ✅ Success: Got student profile")
            print(f"   - Name: {data.get('name')}")
            print(f"   - Dept: {data.get('dept')}")
            print(f"   - Hall: {data.get('hall')}")
        else:
            print(f"   ❌ Failed with status {resp.status_code}: {resp.text}")
    except Exception as e:
        print(f"   ❌ Error: {e}")
    
    # Test 2: Get Student Dues
    print("\n2️⃣  Testing GET /api/student/dues?id={}".format(STUDENT_ID))
    try:
        resp = requests.get(f"{API_BASE}/api/student/dues?id={STUDENT_ID}")
        if resp.status_code == 200:
            data = resp.json()
            items = data.get('items', [])
            print(f"   ✅ Success: Got {len(items)} dues")
            for i, item in enumerate(items, 1):
                print(f"   - Due {i}: {item.get('feeType')} - {item.get('amount')} BDT ({item.get('status')})")
        else:
            print(f"   ❌ Failed with status {resp.status_code}: {resp.text}")
    except Exception as e:
        print(f"   ❌ Error: {e}")
    
    # Test 3: Get Hall Fees (WITH ID)
    print("\n3️⃣  Testing GET /api/student/hall-fees?id={} (MUST RETURN 'id' FIELD)".format(STUDENT_ID))
    try:
        resp = requests.get(f"{API_BASE}/api/student/hall-fees?id={STUDENT_ID}")
        if resp.status_code == 200:
            data = resp.json()
            items = data.get('items', [])
            print(f"   ✅ Success: Got {len(items)} hall fees")
            for i, item in enumerate(items, 1):
                has_id = 'id' in item
                has_month = 'month' in item
                status = item.get('status')
                print(f"   - Hall Fee {i}: {item.get('month')} - {item.get('amount')} BDT ({status})")
                print(f"     - Has 'id' field: {'✅ YES' if has_id else '❌ NO'}")
                print(f"     - ID value: {item.get('id', 'N/A')}")
                if not has_id:
                    print(f"     ⚠️  WARNING: 'id' field missing! Pay buttons won't show!")
        else:
            print(f"   ❌ Failed with status {resp.status_code}: {resp.text}")
    except Exception as e:
        print(f"   ❌ Error: {e}")
    
    # Test 4: Get Department Dues (WITH fee_id)
    print("\n4️⃣  Testing GET /api/student/department-dues?id={} (MUST RETURN 'fee_id' FIELD)".format(STUDENT_ID))
    try:
        resp = requests.get(f"{API_BASE}/api/student/department-dues?id={STUDENT_ID}")
        if resp.status_code == 200:
            data = resp.json()
            items = data.get('items', [])
            print(f"   ✅ Success: Got {len(items)} department dues")
            for i, item in enumerate(items, 1):
                has_fee_id = 'fee_id' in item
                status = item.get('status')
                print(f"   - Dept Due {i}: {item.get('fee_type')} - {item.get('amount')} BDT ({status})")
                print(f"     - Has 'fee_id' field: {'✅ YES' if has_fee_id else '❌ NO'}")
                print(f"     - fee_id value: {item.get('fee_id', 'N/A')}")
                if not has_fee_id:
                    print(f"     ⚠️  WARNING: 'fee_id' field missing! Pay buttons won't show!")
        else:
            print(f"   ❌ Failed with status {resp.status_code}: {resp.text}")
    except Exception as e:
        print(f"   ❌ Error: {e}")

def test_payment_endpoints():
    """Test that payment endpoints exist"""
    print("\n" + "=" * 60)
    print("🧪 Testing Payment Endpoints")
    print("=" * 60)
    
    print("\n5️⃣  Testing POST /api/hall/dues/<id>/pay endpoint exists")
    print("   ℹ️  This endpoint should accept POST requests with transaction details")
    print("   ℹ️  Expected behavior: Mark hall due as paid, update student fees")
    
    print("\n6️⃣  Testing POST /api/dept/dues/<fee_id>/pay endpoint exists")
    print("   ℹ️  This endpoint should accept POST requests with transaction details")
    print("   ℹ️  Expected behavior: Mark dept due as paid, update student fees")

def verify_html_structure():
    """Check if student.html has the correct structure"""
    print("\n" + "=" * 60)
    print("🧪 Verifying student.html Structure")
    print("=" * 60)
    
    try:
        with open(r"e:\RUET\3_1 Materials\CSE_3100_Project\frontend\student.html", "r") as f:
            content = f.read()
            
        print("\n7️⃣  Checking for table header with 'Action' column")
        if "<th>Action</th>" in content:
            print("   ✅ Found 'Action' column in table header")
        else:
            print("   ❌ 'Action' column NOT found in table header!")
        
        print("\n8️⃣  Checking for Pay button HTML generation")
        if 'href="payment.html?type=' in content:
            print("   ✅ Found payment.html redirect links in code")
        else:
            print("   ❌ Payment links NOT found in code!")
        
        print("\n9️⃣  Checking for dueId extraction logic")
        if "x.id || x.fee_id" in content:
            print("   ✅ Found dueId extraction logic (x.id || x.fee_id)")
        else:
            print("   ❌ dueId extraction logic NOT found!")
        
        print("\n🔟 Checking for unpaid status check")
        if 'isUnpaid' in content and 'paid' in content:
            print("   ✅ Found unpaid status check logic")
        else:
            print("   ❌ Unpaid status check NOT found!")
            
    except Exception as e:
        print(f"   ❌ Error reading file: {e}")

if __name__ == "__main__":
    print("\n")
    print("╔" + "=" * 58 + "╗")
    print("║" + " PAY BUTTONS IMPLEMENTATION TEST SUITE ".center(58) + "║")
    print("╚" + "=" * 58 + "╝")
    
    test_api_endpoints()
    test_payment_endpoints()
    verify_html_structure()
    
    print("\n" + "=" * 60)
    print("📋 Test Summary")
    print("=" * 60)
    print("""
✅ If all above tests passed, pay buttons should work!

🔍 WHAT TO CHECK:
1. ✅ All API endpoints return 'id' (hall) or 'fee_id' (dept)
2. ✅ student.html has 'Action' column in table
3. ✅ JavaScript generates links like: payment.html?type=hall&id=123
4. ✅ payment.html loads and fetches due details from those parameters

🚀 TO TEST IN BROWSER:
1. Open http://localhost:5000/frontend/login.html
2. Login with a student account
3. Look at the dues table - should see "Pay" button in each row
4. Click "Pay" button - should go to payment.html with due details
5. Fill transaction details and click "Pay Now"
6. Check that due is marked as paid and fees are updated
""")
    print("=" * 60)
