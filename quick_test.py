#!/usr/bin/env python3
"""
Quick test of API responses without login
"""

import requests
import json
import sqlite3

API_BASE = "http://localhost:5000"

print("=" * 70)
print("QUICK PAY BUTTONS VERIFICATION TEST")
print("=" * 70)

# Get a valid student ID from database
con = sqlite3.connect(r"e:\RUET\3_1 Materials\CSE_3100_Project\database\ruet.db")
con.row_factory = sqlite3.Row
cur = con.cursor()

# Get first verified student
cur.execute("SELECT id FROM students WHERE verified=1 LIMIT 1")
row = cur.fetchone()

if not row:
    print("❌ No verified students found in database!")
    print("\nTesting with mock student ID instead...")
    student_id = "2203177"
else:
    student_id = row["id"]

print(f"\n✅ Using student ID: {student_id}")

# Close DB connection
con.close()

print("\n" + "=" * 70)
print("TEST 1: Dues API")
print("=" * 70)

try:
    resp = requests.get(f"{API_BASE}/api/student/dues?id={student_id}")
    if resp.status_code == 200:
        data = resp.json()
        items = data.get('items', [])
        print(f"✅ Got {len(items)} dues")
        for i, item in enumerate(items, 1):
            print(f"   {i}. {item.get('feeType')} - {item.get('amount')} BDT ({item.get('status')})")
    else:
        print(f"❌ Status {resp.status_code}")
except Exception as e:
    print(f"❌ Error: {e}")

print("\n" + "=" * 70)
print("TEST 2: Hall Fees API (CRITICAL - must have 'id')")
print("=" * 70)

try:
    resp = requests.get(f"{API_BASE}/api/student/hall-fees?id={student_id}")
    if resp.status_code == 200:
        data = resp.json()
        items = data.get('items', [])
        print(f"✅ Got {len(items)} hall fees")
        
        if len(items) > 0:
            for i, item in enumerate(items, 1):
                has_id = 'id' in item
                print(f"\n   Hall Fee {i}:")
                print(f"   - Month: {item.get('month')}")
                print(f"   - Amount: {item.get('amount')} BDT")
                print(f"   - Status: {item.get('status')}")
                print(f"   - ID present: {'✅ YES' if has_id else '❌ NO'}")
                if has_id:
                    print(f"   - ID value: {item.get('id')}")
                    print(f"   → Pay button WILL show for this due ✅")
                else:
                    print(f"   → Pay button WON'T show for this due ❌")
        else:
            print("   ℹ️  No hall fees (student may not be allocated to hall)")
    else:
        print(f"❌ Status {resp.status_code}")
except Exception as e:
    print(f"❌ Error: {e}")

print("\n" + "=" * 70)
print("TEST 3: Department Dues API (CRITICAL - must have 'fee_id')")
print("=" * 70)

try:
    resp = requests.get(f"{API_BASE}/api/student/department-dues?id={student_id}")
    if resp.status_code == 200:
        data = resp.json()
        items = data.get('items', [])
        print(f"✅ Got {len(items)} department dues")
        
        if len(items) > 0:
            for i, item in enumerate(items, 1):
                has_fee_id = 'fee_id' in item
                print(f"\n   Department Due {i}:")
                print(f"   - Type: {item.get('fee_type')}")
                print(f"   - Amount: {item.get('amount')} BDT")
                print(f"   - Status: {item.get('status')}")
                print(f"   - fee_id present: {'✅ YES' if has_fee_id else '❌ NO'}")
                if has_fee_id:
                    print(f"   - fee_id value: {item.get('fee_id')}")
                    print(f"   → Pay button WILL show for this due ✅")
                else:
                    print(f"   → Pay button WON'T show for this due ❌")
        else:
            print("   ℹ️  No department dues")
    else:
        print(f"❌ Status {resp.status_code}")
except Exception as e:
    print(f"❌ Error: {e}")

print("\n" + "=" * 70)
print("TEST 4: HTML & JavaScript Structure")
print("=" * 70)

try:
    with open(r"e:\RUET\3_1 Materials\CSE_3100_Project\frontend\student.html", "r", encoding='utf-8') as f:
        html_content = f.read()
    
    print("✅ student.html checks:")
    
    checks = {
        "Action column header": "<th>Action</th>",
        "Pay button link": 'href="payment.html?type=',
        "DueId extraction": "x.id || x.fee_id",
        "Unpaid check": "isUnpaid",
    }
    
    for name, pattern in checks.items():
        if pattern in html_content:
            print(f"   ✅ {name}")
        else:
            print(f"   ❌ {name} - NOT FOUND")
            
except Exception as e:
    print(f"❌ Error reading HTML: {e}")

print("\n" + "=" * 70)
print("TEST 5: Payment Page File")
print("=" * 70)

try:
    with open(r"e:\RUET\3_1 Materials\CSE_3100_Project\frontend\payment.html", "r", encoding='utf-8') as f:
        payment_content = f.read()
    
    print("✅ payment.html exists with:")
    
    checks = {
        "Payment form": '<form id="paymentForm">',
        "Fee type display": 'id="feeType"',
        "Amount field": 'id="amount"',
        "Pay button": 'id="payBtn"',
    }
    
    for name, pattern in checks.items():
        if pattern in payment_content:
            print(f"   ✅ {name}")
        else:
            print(f"   ❌ {name} - NOT FOUND")
            
except Exception as e:
    print(f"❌ Error: {e}")

print("\n" + "=" * 70)
print("✅ IMPLEMENTATION VERIFICATION COMPLETE")
print("=" * 70)
print("""
📊 SUMMARY:
If all tests above show ✅, then:
- API endpoints return correct data with ID fields
- student.html has pay buttons for each due  
- payment.html page is ready to process payments
- Complete payment flow is functional

🚀 TO TEST IN BROWSER:
1. Go to http://localhost:5000/frontend/login.html
2. Login with student credentials
3. Scroll to dues table
4. Look for "Action" column with "Pay" buttons
5. Click "Pay" on any unpaid due
6. Fill transaction details and click "Pay Now"
7. Check that due is marked as paid ✅
""")
print("=" * 70)
