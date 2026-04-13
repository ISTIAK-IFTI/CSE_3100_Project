# Integration Examples & Before/After Guide

This file shows how to use the new `accounts_manager` module to improve your existing code.

## Before & After Comparison

### Example 1: Getting Student Department Account

#### ❌ BEFORE (Current Code in app.py)

```python
@app.route("/api/student/department-account")
def student_department_account():
    """Get department payment account for student"""
    student_id = request.args.get("id")
    
    con = get_db()
    cur = con.cursor()
    
    # First query to get student dept
    cur.execute("SELECT dept FROM students WHERE id = ?", (student_id,))
    student = cur.fetchone()
    if not student:
        return jsonify({"message": "Student not found"}), 404
    
    # Second query to get account
    cur.execute("""
        SELECT account_name, account_number, bank_name
        FROM payment_accounts
        WHERE account_type = 'department'
        AND entity_identifier = ?
        AND is_active = 1
    """, (student['dept'],))
    
    account = cur.fetchone()
    con.close()
    
    if not account:
        return jsonify({"message": "Account not found"}), 404
    
    return jsonify(dict(account))
```

#### ✅ AFTER (Using accounts_manager)

```python
from database.accounts_manager import get_account_for_student

@app.route("/api/student/department-account")
def student_department_account():
    """Get department payment account for student"""
    student_id = request.args.get("id")
    
    con = get_db()
    cur = con.cursor()
    
    # Get student dept
    cur.execute("SELECT dept FROM students WHERE id = ?", (student_id,))
    student = cur.fetchone()
    if not student:
        return jsonify({"message": "Student not found"}), 404
    
    con.close()
    
    # Use convenience function
    account = get_account_for_student(student['dept'])
    
    if not account:
        return jsonify({"message": "Account not found"}), 404
    
    return jsonify(account)
```

**Benefits:**
- Cleaner code
- Reusable function
- Better error handling
- No manual database connection

---

### Example 2: Getting All Hall Accounts

#### ❌ BEFORE

```python
@app.route("/api/librarian/all-hall-accounts")
def get_all_hall_payment_accounts():
    con = get_db()
    cur = con.cursor()
    
    cur.execute("""
        SELECT id, entity_identifier, account_name, account_number, bank_name
        FROM payment_accounts
        WHERE account_type = 'hall'
        AND is_active = 1
        ORDER BY created_at DESC
    """)
    
    accounts = [dict(row) for row in cur.fetchall()]
    con.close()
    
    return jsonify({"accounts": accounts}), 200
```

#### ✅ AFTER

```python
from database.accounts_manager import get_all_hall_accounts

@app.route("/api/librarian/all-hall-accounts")
def get_all_hall_payment_accounts():
    accounts = get_all_hall_accounts()
    return jsonify({"accounts": accounts}), 200
```

**Benefits:**
- Single line instead of 12
- Instantly readable
- Automatic error handling

---

### Example 3: Getting Library Account

#### ❌ BEFORE

```python
@app.route("/api/student/library-payment-account")
def get_library_payment_account():
    con = get_db()
    cur = con.cursor()
    
    cur.execute("""
        SELECT id, account_name, account_number, bank_name, account_holder
        FROM payment_accounts
        WHERE account_type = 'library'
        AND is_active = 1
        LIMIT 1
    """)
    
    account = cur.fetchone()
    con.close()
    
    if not account:
        return jsonify({"message": "Library account not configured"}), 404
    
    return jsonify(dict(account))
```

#### ✅ AFTER

```python
from database.accounts_manager import get_library_account

@app.route("/api/student/library-payment-account")
def get_library_payment_account():
    account = get_library_account()
    
    if not account:
        return jsonify({"message": "Library account not configured"}), 404
    
    return jsonify(account)
```

**Benefits:**
- Encapsulation makes intent clear
- Database connection handled internally
- Easy to modify later

---

## New Endpoints You Can Add

### Get Account Statistics

```python
from database.accounts_manager import get_accounts_stats

@app.route("/api/admin/account-statistics")
def account_statistics():
    """Get statistics about all accounts in system"""
    stats = get_accounts_stats()
    
    return jsonify({
        "total_accounts": stats['total'],
        "active_accounts": stats['active'],
        "inactive_accounts": stats['inactive'],
        "by_type": stats['by_type'],
        "active_by_type": stats['active_by_type']
    }), 200
```

### List All Department Accounts

```python
from database.accounts_manager import get_all_department_accounts

@app.route("/api/admin/department-accounts")
def list_department_accounts():
    """Get all department accounts"""
    depts = get_all_department_accounts()
    
    dept_names = {
        '00': 'CIVIL', '01': 'EEE', '02': 'ME', '03': 'CSE', '04': 'ETE',
        '05': 'IPE', '06': 'GCE', '07': 'URP', '08': 'MTE', '09': 'ARCH',
        '10': 'ECE', '11': 'CHE', '12': 'BECM', '13': 'MSE'
    }
    
    formatted = [
        {
            **dept,
            'department_name': dept_names.get(dept['entity_identifier'], 'Unknown')
        }
        for dept in depts
    ]
    
    return jsonify({"accounts": formatted}), 200
```

### Create New Account

```python
from database.accounts_manager import create_account

@app.route("/api/admin/accounts", methods=["POST"])
def create_new_account():
    """Create a new payment account"""
    data = request.json or {}
    
    # Validate input
    required = ['account_type', 'entity_identifier', 'account_name']
    if not all(data.get(k) for k in required):
        return jsonify({"message": f"Required: {', '.join(required)}"}), 400
    
    # Create account
    account_id = create_account(
        account_type=data['account_type'],
        entity_identifier=data['entity_identifier'],
        account_name=data['account_name'],
        account_number=data.get('account_number'),
        bank_name=data.get('bank_name', 'RUPALI BANK'),
        account_holder=data.get('account_holder')
    )
    
    if not account_id:
        return jsonify({"message": "Failed to create account"}), 400
    
    return jsonify({
        "message": "Account created successfully",
        "account_id": account_id
    }), 201
```

### Update Account

```python
from database.accounts_manager import update_account, get_account_by_id

@app.route("/api/admin/accounts/<int:account_id>", methods=["PUT"])
def edit_account(account_id):
    """Update an existing account"""
    data = request.json or {}
    
    # Verify account exists
    account = get_account_by_id(account_id)
    if not account:
        return jsonify({"message": "Account not found"}), 404
    
    # Update
    success = update_account(account_id, **data)
    
    if success:
        return jsonify({"message": "Account updated successfully"}), 200
    else:
        return jsonify({"message": "Failed to update account"}), 400
```

### Deactivate Account

```python
from database.accounts_manager import deactivate_account, get_account_by_id

@app.route("/api/admin/accounts/<int:account_id>/deactivate", methods=["POST"])
def deactivate_account_endpoint(account_id):
    """Deactivate an account"""
    account = get_account_by_id(account_id)
    if not account:
        return jsonify({"message": "Account not found"}), 404
    
    if deactivate_account(account_id):
        return jsonify({"message": "Account deactivated successfully"}), 200
    else:
        return jsonify({"message": "Failed to deactivate account"}), 400
```

---

## Refactoring Your app.py

### Current Issue

Your `get_hall_accounts()` function works but could be improved:

```python
@app.route("/api/hall/accounts")
def get_hall_accounts():
    con = get_db()
    cur = con.cursor()
    
    account_type = (request.args.get("account_type") or "").strip() or None
    
    query = """
        SELECT * FROM payment_accounts
        WHERE is_active = 1
    """
    params = []
    
    if account_type:
        query += " AND account_type = ?"
        params.append(account_type)
    
    query += " ORDER BY account_type, created_at DESC"
    
    cur.execute(query, params)
    rows = cur.fetchall()
    con.close()
    
    accounts = [dict(row) for row in rows]
    return jsonify({"accounts": accounts}), 200
```

### Improved Version

```python
from database.accounts_manager import get_accounts_by_type

@app.route("/api/hall/accounts")
def get_hall_accounts():
    """Get payment accounts (filterable by type)"""
    account_type = (request.args.get("account_type") or "").strip() or None
    
    if account_type:
        # Validate account type
        if account_type not in ['hall', 'library', 'department']:
            return jsonify({"message": "Invalid account type"}), 400
        accounts = get_accounts_by_type(account_type, active_only=True)
    else:
        # Get all active accounts from all types
        accounts = get_accounts_by_type('hall', active_only=True)
        accounts += get_accounts_by_type('library', active_only=True)
        accounts += get_accounts_by_type('department', active_only=True)
    
    return jsonify({"accounts": accounts}), 200
```

**Improvements:**
- Uses convenience functions
- Built-in validation
- Better code organization
- Easier to test and maintain

---

## Step-by-Step Integration

### Step 1: Add Import at Top of app.py

```python
from database.accounts_manager import (
    get_account_for_student,
    get_hall_account,
    get_library_account,
    get_all_hall_accounts,
    get_all_department_accounts,
    get_accounts_by_type,
    create_account,
    update_account,
    deactivate_account,
    get_accounts_stats
)
```

### Step 2: Refactor Existing Endpoints

Find all queries that access `payment_accounts` and replace with convenience functions.

### Step 3: Add New Endpoints

Add the new endpoints shown above for admin functionality.

### Step 4: Test

```python
if __name__ == "__main__":
    # Test the module
    from database.accounts_manager import get_accounts_stats
    stats = get_accounts_stats()
    print(f"✅ System loaded with {stats['total']} accounts")
    print(f"   Active: {stats['active']}")
    print(f"   By Type: {stats['by_type']}")
```

---

## Complete Example: Enhanced Fee Display

### Old Way (Multiple DB Calls)

```python
@app.route("/api/student/<student_id>/complete-fees")
def get_complete_fees_old(student_id):
    con = get_db()
    cur = con.cursor()
    
    # Get student info
    cur.execute("SELECT name, dept, hall FROM students WHERE id = ?", (student_id,))
    student = cur.fetchone()
    if not student:
        return jsonify({"message": "Student not found"}), 404
    
    # Get dept fee
    dept_fee = 0  # Calculate based on student dept
    cur.execute("""
        SELECT account_number FROM payment_accounts
        WHERE account_type = 'department' AND entity_identifier = ? AND is_active = 1
    """, (student['dept'],))
    dept_account = cur.fetchone()
    
    # Get library account
    cur.execute("""
        SELECT account_number FROM payment_accounts
        WHERE account_type = 'library' AND is_active = 1
    """)
    lib_account = cur.fetchone()
    
    # Get hall account
    cur.execute("""
        SELECT account_number FROM payment_accounts
        WHERE account_type = 'hall' AND entity_identifier = ? AND is_active = 1
    """, (student['hall'],))
    hall_account = cur.fetchone()
    
    con.close()
    
    # Format response
    return jsonify({
        "student": dict(student),
        "fees": {
            "department": {"amount": dept_fee, "account": dict(dept_account) if dept_account else None},
            "library": {"account": dict(lib_account) if lib_account else None},
            "hall": {"account": dict(hall_account) if hall_account else None}
        }
    })
```

### New Way (Using accounts_manager)

```python
from database.accounts_manager import (
    get_account_for_student,
    get_library_account,
    get_hall_account
)

@app.route("/api/student/<student_id>/complete-fees")
def get_complete_fees(student_id):
    con = get_db()
    cur = con.cursor()
    
    # Get student info (only necessary DB call)
    cur.fetchone("""
        SELECT name, dept, hall FROM students WHERE id = ?
    """, (student_id,))
    student = cur.fetchone()
    con.close()
    
    if not student:
        return jsonify({"message": "Student not found"}), 404
    
    # Get accounts using convenience functions
    dept_account = get_account_for_student(student['dept'])
    lib_account = get_library_account()
    hall_account = get_hall_account(student['hall']) if student['hall'] else None
    
    # Calculate or get dept fee (based on your logic)
    dept_fee = calculate_dept_fee(student['dept'])
    
    # Format response
    return jsonify({
        "student": dict(student),
        "fees": {
            "department": {
                "amount": dept_fee,
                "account": dept_account
            },
            "library": {
                "account": lib_account
            },
            "hall": {
                "account": hall_account
            }
        }
    })
```

**Benefits:**
- ✅ Cleaner code
- ✅ Fewer database connections
- ✅ Reusable logic
- ✅ Easier maintenance
- ✅ Better testability

---

## Testing Your Integration

### Test Script

```python
# test_accounts_integration.py

from database.accounts_manager import (
    get_account_for_student,
    get_hall_account,
    get_library_account,
    get_all_hall_accounts,
    get_accounts_stats
)

def test_accounts_manager():
    print("Testing accounts_manager integration...\n")
    
    # Test 1: Get student account
    print("✓ Test 1: Get student account (CSE)")
    account = get_account_for_student('03')
    assert account is not None
    print(f"  Account: {account['account_name']}")
    assert 'account_number' in account
    print("  ✅ PASS\n")
    
    # Test 2: Get all halls
    print("✓ Test 2: Get all hall accounts")
    halls = get_all_hall_accounts()
    print(f"  Found {len(halls)} halls")
    print("  ✅ PASS\n")
    
    # Test 3: Get library account
    print("✓ Test 3: Get library account")
    lib = get_library_account()
    assert lib is not None
    print(f"  Account: {lib['account_name']}")
    print("  ✅ PASS\n")
    
    # Test 4: Get statistics
    print("✓ Test 4: Get account statistics")
    stats = get_accounts_stats()
    print(f"  Total: {stats['total']}")
    print(f"  Active: {stats['active']}")
    print(f"  By Type: {stats['by_type']}")
    print("  ✅ PASS\n")
    
    print("✅ All tests passed!")

if __name__ == "__main__":
    test_accounts_manager()
```

Run with:
```bash
python test_accounts_integration.py
```

