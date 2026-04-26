import requests

student_id = 'demo_2203177'

print('Testing Hall Fees API with test data...')
response = requests.get(f'http://localhost:5000/api/student/hall-fees?id={student_id}')

if response.status_code == 200:
    data = response.json()
    items = data.get('items', [])
    
    print(f'\n✅ API returned {len(items)} hall fees\n')
    
    for i, item in enumerate(items, 1):
        print(f'Hall Fee #{i}:')
        print(f'  - ID: {item.get("id")} ← THIS is the Pay Button ID!')
        print(f'  - Month: {item.get("month")}')
        print(f'  - Amount: {item.get("amount")} BDT')
        print(f'  - Status: {item.get("status")}')
        print(f'  - Hall Name: {item.get("hall_name")}')
        print()
        
        # Show what the pay button would look like
        if item.get('status') != 'paid':
            due_id = item.get('id')
            url = f'payment.html?type=hall&id={due_id}'
            print(f'  → Pay Button: <a href="{url}">Pay</a>')
            print(f'  → This will redirect to payment page with ID {due_id}')
else:
    print(f'❌ Failed: {response.status_code}')
    print(response.json())
