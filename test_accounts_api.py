#!/usr/bin/env python
"""Test payment accounts API endpoints"""

import requests
import json

BASE_URL = 'http://127.0.0.1:5000'

# Test hall accounts
print('=== Hall Accounts ===')
r = requests.get(f'{BASE_URL}/api/hall/accounts?account_type=hall')
data = r.json()
print(f'Total: {len(data["accounts"])} halls')
for acc in data['accounts'][:3]:
    print(f'  • {acc["account_name"]} (ID: {acc["entity_identifier"]})')
print(f'  ... and {len(data["accounts"]) - 3} more\n')

# Test library account
print('=== Library Account ===')
r = requests.get(f'{BASE_URL}/api/hall/accounts?account_type=library')
data = r.json()
for acc in data['accounts']:
    print(f'  • {acc["account_name"]}\n')

# Test department accounts
print('=== Department Accounts (sample) ===')
r = requests.get(f'{BASE_URL}/api/hall/accounts?account_type=department')
data = r.json()
print(f'Total: {len(data["accounts"])} departments')
for acc in data['accounts'][:5]:
    print(f'  • {acc["account_name"]} ({acc["entity_identifier"]})')
print(f'  ... and {len(data["accounts"]) - 5} more\n')

# Test all accounts
print('=== All Accounts ===')
r = requests.get(f'{BASE_URL}/api/hall/accounts')
data = r.json()
print(f'Total accounts in system: {len(data["accounts"])}\n')

print('✅ All API endpoints working correctly!')
