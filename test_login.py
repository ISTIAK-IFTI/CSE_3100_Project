import requests
import json

# Test login endpoint
url = 'http://127.0.0.1:5000/api/auth/login'
payload = {
    'email': 'hamid@hall.ruet.ac.bd',
    'password': 'hamid'
}

print('Testing login endpoint...')
print(f'URL: {url}')
print(f'Payload: {json.dumps(payload, indent=2)}')

try:
    response = requests.post(url, json=payload)
    print(f'\nStatus Code: {response.status_code}')
    print(f'Response:')
    print(json.dumps(response.json(), indent=2))
except Exception as e:
    print(f'Error: {e}')
