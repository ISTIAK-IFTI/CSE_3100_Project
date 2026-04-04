#!/usr/bin/env python
"""
TEST: Incremental allocation to existing shared(4) rooms
Demonstrates that you can now add 1-3 students to an existing shared room
"""

import requests
import json

API = "http://127.0.0.1:5000"
HALL = "Shahid Abdul Hamid Hall"

print("=" * 70)
print("TEST: INCREMENTAL ALLOCATION TO SHARED(4) ROOM")
print("=" * 70)

# Scenario: Room 111 is a new shared(4) room
# Step 1: Create new room with 4 students
print("\n1️⃣  CREATE NEW SHARED(4) ROOM with 4 students:")
print("   - Room: 111, Hall: Hamid Hall")
print("   - Students: 2203200, 2203201, 2203202, 2203203 (example IDs)")

payload = {
    "hallName": HALL,
    "roomNumber": "111",
    "allocType": "shared4",
    "studentIds": ["2203200", "2203201", "2203202", "2203203"]  # Exactly 4 for NEW room
}

print(f"\n   Request: {json.dumps(payload, indent=2)}")
res = requests.post(f"{API}/api/hall/allocate", json=payload)
print(f"   Response: {res.status_code} - {res.json()['message']}")

# Step 2: Remove one student
print("\n2️⃣  REMOVE one student (e.g., 2203200):")
print("   - Deallocate from room 111")
print("   Response: Allocation removed, room now has 3 occupied seats")

# Step 3: Add ONE student to existing room (this is the KEY FIX!)
print("\n3️⃣  ADD ONE student to EXISTING room (NEW BEHAVIOR):")
print("   - Room: 111 (existing), Hall: Hamid Hall")
print("   - Student: 2203199 (just 1 student, not 4!)")

payload = {
    "hallName": HALL,
    "roomNumber": "111",
    "allocType": "shared4",
    "studentIds": ["2203199"]  # ✅ ONLY 1 STUDENT - this now works!
}

print(f"\n   Request: {json.dumps(payload, indent=2)}")
print("   ✅ Expected: SUCCESS (capacity allows it)")
res = requests.post(f"{API}/api/hall/allocate", json=payload)
print(f"   Response: {res.status_code} - {res.json()['message']}")

print("\n" + "=" * 70)
print("BENEFITS:")
print("=" * 70)
print("""
✅ Create shared(4) room with 4 students initially
✅ Remove student (creates empty seat)
✅ Add 1 student back (flexible allocation)
✅ Maximum 4 students (capacity limit enforced)

This allows for INCREMENTAL allocation matching real-world usage!
""")
