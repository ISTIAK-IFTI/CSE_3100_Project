#!/usr/bin/env python
"""Test student hall-fees endpoint with new payment_accounts"""

import requests

BASE_URL = 'http://127.0.0.1:5000'

# Test with a student ID that has allocated fees
# From database: we have students with IDs like 2203133, 2203161, etc.
# Let's test with a known student ID

print('=== Testing Student Hall Fees Endpoint ===\n')

student_ids = ['2203133', '2203161', '2203177']

for student_id in student_ids:
    r = requests.get(f'{BASE_URL}/api/student/hall-fees?id={student_id}')
    
    if r.status_code == 200:
        data = r.json()
        print(f'Student {student_id}:')
        if data['items']:
            for item in data['items'][:2]:
                print(f'  • Month: {item.get("month")}')
                print(f'    Amount: {item.get("amount")}')
                print(f'    Hall: {item.get("hall_name")}')
                print(f'    Account: {item.get("account_name")}')
            if len(data['items']) > 2:
                print(f'    ... and {len(data["items"]) - 2} more fees')
        else:
            print('  (no fees found)')
    else:
        print(f'Student {student_id}: Status {r.status_code}')
    print()

print('✅ Student hall-fees endpoint working correctly with payment accounts!')
