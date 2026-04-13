# Database Migration & Best Practices Guide

## Current Status: ✅ UNIFIED ACCOUNTS ALREADY IMPLEMENTED

Your system has already transitioned to a unified accounts table (`payment_accounts`). This document shows you how to leverage it properly and maintain it going forward.

## Database Structure

### The Unified Table: `payment_accounts`

```
payment_accounts:
├── id (PRIMARY KEY)
├── account_type (hall | library | department)
├── entity_identifier (hall_name | 'library' | dept_code)
├── account_name
├── account_number
├── bank_name
├── account_holder
├── is_active
└── created_at
```

### Why This Design?

1. **Single Source of Truth**: All payment accounts in one location
2. **Type Discrimination**: `account_type` field allows filtering by type
3. **Flexible**: Easy to add new account types in future
4. **Performant**: Indexes on `account_type` and `entity_identifier`
5. **Maintainable**: Single UNIQUE constraint prevents duplicates

## Current Implementation in Your Code

### In Backend (app.py)

```python
# Getting accounts via API
@app.route("/api/hall/accounts")
def get_hall_accounts():
    # Returns accounts filtered by account_type
    cur.execute("""
        SELECT * FROM payment_accounts
        WHERE is_active = 1
        ORDER BY account_type
    """)
```

### In Database Init (init_hall_db.py)

```python
# Populating accounts on initialization
def init_hall_tables():
    # Creates payment_accounts table
    cur.execute("""
        CREATE TABLE IF NOT EXISTS payment_accounts (
            account_type TEXT NOT NULL,         -- 'hall', 'library', 'department'
            entity_identifier TEXT NOT NULL,    -- hall name, 'library', or dept_code
            ...
        )
    """)
```

## How to Use in Your Application

### Option 1: Direct Database Queries (Simple)

```python
# Get student's department account
cur.execute("""
    SELECT account_name, account_number, bank_name
    FROM payment_accounts
    WHERE account_type = 'department'
    AND entity_identifier = ?
    AND is_active = 1
""", (student_dept_code,))
```

### Option 2: Using Convenience Module (Recommended)

```python
from database.accounts_manager import (
    get_account_for_student,
    get_hall_account,
    get_library_account,
    get_accounts_stats
)

# Get department account
account = get_account_for_student('03')  # CSE department
print(account['account_number'])

# Get hall account
hall_acc = get_hall_account('Shahid Abdul Hamid Hall')

# Get library account
lib_acc = get_library_account()

# Get statistics
stats = get_accounts_stats()
```

## Integration Guide

### Displaying Fees to Student

```python
@app.route("/api/student/<student_id>/fees")
def get_fees(student_id):
    # 1. Get student info
    cur.execute("SELECT dept FROM students WHERE id = ?", (student_id,))
    student = cur.fetchone()
    
    # 2. Get corresponding account
    cur.execute("""
        SELECT account_name, account_number, bank_name
        FROM payment_accounts
        WHERE account_type = 'department'
        AND entity_identifier = ?
        AND is_active = 1
    """, (student['dept'],))
    
    account = cur.fetchone()
    
    # 3. Return fee info with account
    return jsonify({
        'fees': fee_amount,
        'pay_to': account['account_name'],
        'account_number': account['account_number'],
        'bank': account['bank_name']
    })
```

### Hall Fee Collection

```python
# Get all active hall accounts for fee collection dashboard
@app.route("/api/librarian/hall-accounts")
def get_all_halls_for_collection():
    cur.execute("""
        SELECT 
            pa.id,
            pa.entity_identifier,
            pa.account_name,
            pa.account_number,
            COUNT(hd.id) as pending_fees
        FROM payment_accounts pa
        LEFT JOIN hall_dues hd ON hd.hall_id = (
            SELECT id FROM halls WHERE hall_name = pa.entity_identifier
        ) AND hd.status = 'unpaid'
        WHERE pa.account_type = 'hall'
        AND pa.is_active = 1
        GROUP BY pa.id
    """)
    
    return jsonify({'halls': [dict(row) for row in cur.fetchall()]})
```

## Maintenance Tasks

### 1. Regular Verification

Run the verification script:
```bash
python database/verify_unified_accounts.py
```

This checks:
- ✅ Table structure
- ✅ Indexes
- ✅ Data integrity
- ✅ No duplicates
- ✅ Statistics

### 2. Add New Account

**Method 1: Direct SQL**
```python
cur.execute("""
    INSERT INTO payment_accounts 
    (account_type, entity_identifier, account_name, account_number, bank_name, is_active)
    VALUES ('hall', 'New Hall', 'New Hall Account', '123456789', 'RUPALI BANK', 1)
""")
```

**Method 2: Using accounts_manager**
```python
from database.accounts_manager import create_account

account_id = create_account(
    account_type='hall',
    entity_identifier='New Hall',
    account_name='New Hall Account',
    account_number='123456789',
    bank_name='RUPALI BANK'
)
```

### 3. Update Account

```python
from database.accounts_manager import update_account

# Update account details
update_account(account_id, account_holder='New Manager', account_number='999999999')

# Deactivate (without deleting)
update_account(account_id, is_active=0)
```

### 4. Backup Accounts

```bash
# Export to CSV
sqlite3 ruet.db "SELECT * FROM payment_accounts;" > accounts_backup.csv

# Export to JSON (use Python)
python -c "
import sqlite3, json
from database.accounts_manager import get_accounts_by_type
accounts = {
    'hall': get_accounts_by_type('hall'),
    'library': get_accounts_by_type('library'),
    'department': get_accounts_by_type('department')
}
with open('accounts_backup.json', 'w') as f:
    json.dump(accounts, f, indent=2)
"
```

## Common Queries

### Get Payment Info for Dashboard

```python
def get_payment_summary():
    cur.execute("""
        SELECT 
            account_type,
            COUNT(*) as account_count,
            SUM(CASE WHEN is_active = 1 THEN 1 ELSE 0 END) as active_count
        FROM payment_accounts
        GROUP BY account_type
    """)
    return {row['account_type']: row for row in cur.fetchall()}
```

### List All Active Accounts with Details

```python
cur.execute("""
    SELECT 
        account_type,
        entity_identifier,
        account_name,
        account_number,
        bank_name,
        created_at
    FROM payment_accounts
    WHERE is_active = 1
    ORDER BY account_type, created_at DESC
""")
```

### Check for Orphaned Student Assignments

```python
# Verify all students' departments have accounts
cur.execute("""
    SELECT DISTINCT s.dept
    FROM students s
    WHERE NOT EXISTS (
        SELECT 1 FROM payment_accounts pa
        WHERE pa.account_type = 'department'
        AND pa.entity_identifier = s.dept
        AND pa.is_active = 1
    )
""")

missing = cur.fetchall()
if missing:
    print(f"Missing accounts for departments: {missing}")
```

## Recommendations

### ✅ DO:

1. **Use the accounts_manager module** in new features
   ```python
   from database.accounts_manager import get_account_for_student
   ```

2. **Always filter by is_active = 1** in queries
   ```python
   WHERE account_type = 'hall' AND is_active = 1
   ```

3. **Use entity_identifier for lookups**
   ```python
   # This works for all types
   WHERE entity_identifier = ? AND account_type = ?
   ```

4. **Deactivate instead of deleting**
   ```python
   # Don't: DELETE FROM payment_accounts WHERE id = 1
   # Do:
   UPDATE payment_accounts SET is_active = 0 WHERE id = 1
   ```

5. **Validate account_type values**
   ```python
   if account_type not in ['hall', 'library', 'department']:
       raise ValueError("Invalid account type")
   ```

### ❌ DON'T:

1. **Create duplicate accounts**
   - The UNIQUE constraint prevents this
   - Check before inserting

2. **Delete accounts**
   - Deactivate with `is_active = 0` instead
   - Preserves historical data

3. **Use hardcoded account IDs**
   - Always look up by `account_type` and `entity_identifier`

4. **Forget to filter by is_active in queries**
   - Can return inactive/outdated accounts

5. **Store account data elsewhere**
   - Always query from this unified table

## Future Enhancement Ideas

### 1. Balance Tracking

```sql
ALTER TABLE payment_accounts ADD COLUMN current_balance INTEGER DEFAULT 0;
ALTER TABLE payment_accounts ADD COLUMN last_balance_update TEXT;
```

### 2. Transaction Log

```sql
CREATE TABLE account_transactions (
    id INTEGER PRIMARY KEY,
    account_id INTEGER,
    transaction_date TEXT,
    amount INTEGER,
    transaction_type TEXT,  -- 'credit', 'debit'
    description TEXT,
    FOREIGN KEY (account_id) REFERENCES payment_accounts(id)
);
```

### 3. Account Verification Status

```sql
ALTER TABLE payment_accounts ADD COLUMN is_verified INTEGER DEFAULT 0;
ALTER TABLE payment_accounts ADD COLUMN verification_date TEXT;
ALTER TABLE payment_accounts ADD COLUMN verifier_notes TEXT;
```

### 4. Multi-Bank Support Enhancement

```sql
ALTER TABLE payment_accounts ADD COLUMN bank_branch TEXT;
ALTER TABLE payment_accounts ADD COLUMN account_ifsc_code TEXT;
ALTER TABLE payment_accounts ADD COLUMN account_swift_code TEXT;
```

## Troubleshooting

### Problem: "Duplicate account error"
**Solution**: Check if account already exists
```python
cur.execute("""
    SELECT id FROM payment_accounts
    WHERE account_type = ? AND entity_identifier = ?
""", (account_type, entity_identifier))
```

### Problem: "Account not found for student"
**Solution**: Verify department code mapping
```python
# Check if department exists
cur.execute("""
    SELECT DISTINCT entity_identifier FROM payment_accounts
    WHERE account_type = 'department'
""")
```

### Problem: "Queries returning inactive accounts"
**Solution**: Always add filter
```python
WHERE account_type = 'hall' AND is_active = 1
```

## Summary

✅ Your system is well-designed with unified accounts!

**Files created to support this:**
1. `UNIFIED_ACCOUNTS_GUIDE.md` - Comprehensive documentation
2. `database/verify_unified_accounts.py` - Verification script
3. `database/accounts_manager.py` - Convenience functions module
4. `DATABASE_MIGRATION.md` - This file

**Quick start:**
```python
# In your code, use:
from database.accounts_manager import get_account_for_student
account = get_account_for_student('03')
```

**Verify status:**
```bash
python database/verify_unified_accounts.py
```

