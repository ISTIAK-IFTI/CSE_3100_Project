# Unified Accounts Table Guide

## Overview
The `payment_accounts` table is a unified storage solution for all account types in your RUET Financial System.

## Table Schema

```sql
CREATE TABLE payment_accounts (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    account_type TEXT NOT NULL,           -- 'hall', 'library', 'department'
    entity_identifier TEXT NOT NULL,      -- hall_name, 'library', or dept_code
    account_name TEXT NOT NULL,           -- e.g., "Hamid Hall Account", "Library Account", "CSE Department Account"
    account_number TEXT,                  -- Real account number or placeholder
    bank_name TEXT DEFAULT 'RUPALI BANK',
    account_holder TEXT,
    is_active INTEGER DEFAULT 1,
    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(account_type, entity_identifier)
)
```

## Account Types

### 1. Hall Accounts
- **account_type**: 'hall'
- **entity_identifier**: Hall name (e.g., 'Shahid Abdul Hamid Hall')
- **account_name**: e.g., "Shahid Abdul Hamid Hall Account"
- **account_number**: Hall identifier (currently hall_name)

**Usage:**
```sql
SELECT * FROM payment_accounts 
WHERE account_type = 'hall' AND is_active = 1;
```

### 2. Library Account
- **account_type**: 'library'
- **entity_identifier**: 'library' (singleton)
- **account_name**: "Library Account"
- **account_number**: 'library'

**Usage:**
```sql
SELECT * FROM payment_accounts 
WHERE account_type = 'library' AND is_active = 1;
```

### 3. Department Accounts
- **account_type**: 'department'
- **entity_identifier**: Department code (e.g., '03' for CSE)
- **account_name**: e.g., "CSE Department Account"
- **account_number**: Department code

**Usage:**
```sql
SELECT * FROM payment_accounts 
WHERE account_type = 'department' AND is_active = 1;
```

## Department Code Mapping

| Code | Department |
|------|-----------|
| 00 | CIVIL |
| 01 | EEE |
| 02 | ME |
| 03 | CSE |
| 04 | ETE |
| 05 | IPE |
| 06 | GCE |
| 07 | URP |
| 08 | MTE |
| 09 | ARCH |
| 10 | ECE |
| 11 | CHE |
| 12 | BECM |
| 13 | MSE |

## API Endpoints

### Get All Accounts
```
GET /api/hall/accounts?account_type=hall|library|department
```

**Response:**
```json
{
  "accounts": [
    {
      "id": 1,
      "account_type": "hall",
      "entity_identifier": "Shahid Abdul Hamid Hall",
      "account_name": "Shahid Abdul Hamid Hall Account",
      "account_number": "Shahid Abdul Hamid Hall",
      "bank_name": "RUPALI BANK",
      "account_holder": null,
      "is_active": 1,
      "created_at": "2024-01-15T10:30:00"
    }
  ]
}
```

### Create/Update Account
```
POST /api/hall/accounts
Content-Type: application/json

{
  "account_type": "hall",
  "entity_identifier": "Hamid Hall",
  "account_name": "Hamid Hall Account",
  "account_number": "123456789",
  "bank_name": "RUPALI BANK",
  "account_holder": "Hall Manager"
}
```

## Benefits of Unified Table

1. **Single Source of Truth**: All accounts are in one place
2. **Easy Access**: No joining multiple tables
3. **Type-based Filtering**: Simple WHERE clause with `account_type`
4. **Scalability**: Easy to add new account types in future
5. **Indexed Performance**: Optimized queries with indexes on `account_type` and `entity_identifier`
6. **Consistency**: UNIQUE constraint on (account_type, entity_identifier) prevents duplicates

## Query Examples

### Get all active hall accounts
```sql
SELECT * FROM payment_accounts 
WHERE account_type = 'hall' AND is_active = 1
ORDER BY created_at DESC;
```

### Get library account
```sql
SELECT * FROM payment_accounts 
WHERE account_type = 'library' AND is_active = 1
LIMIT 1;
```

### Get CSE department account
```sql
SELECT * FROM payment_accounts 
WHERE account_type = 'department' 
AND entity_identifier = '03'
AND is_active = 1
LIMIT 1;
```

### Get account by name
```sql
SELECT * FROM payment_accounts 
WHERE account_name = 'CSE Department Account'
AND is_active = 1;
```

### Count accounts by type
```sql
SELECT account_type, COUNT(*) as count 
FROM payment_accounts 
WHERE is_active = 1
GROUP BY account_type;
```

### Disable an account
```sql
UPDATE payment_accounts 
SET is_active = 0 
WHERE account_type = 'hall' 
AND entity_identifier = 'Old Hall';
```

### Reactivate an account
```sql
UPDATE payment_accounts 
SET is_active = 1
WHERE id = 5;
```

## Data Flow in Application

### For Student Fee Payment:
```
Student Info (dept) → Get Payment Accounts
    ↓
SELECT FROM payment_accounts 
WHERE account_type = 'department' 
AND entity_identifier = student.dept_code
    ↓
Return Account Details (account_name, account_number, bank_name)
    ↓
Display to Student
```

### For Hall Fee Collection:
```
Student Info (hall) → Get Hall Dues
    ↓
SELECT payment_accounts WHERE account_type='hall' 
AND entity_identifier = hall_name
    ↓
Join with hall_dues table for fee details
    ↓
Return fee info with account details
```

## Indexes for Performance

```sql
-- Existing indexes
CREATE INDEX idx_accounts_type ON payment_accounts(account_type);
CREATE INDEX idx_accounts_identifier ON payment_accounts(entity_identifier);

-- Query plan uses these indexes for fast lookups:
-- Example: WHERE account_type = 'hall' -- Uses idx_accounts_type
-- Example: WHERE entity_identifier = '03' -- Uses idx_accounts_identifier
```

## Backup & Maintenance

### Backup data
```sql
-- Export accounts
sqlite3 ruet.db "SELECT * FROM payment_accounts;" > accounts_backup.csv
```

### Verify data integrity
```sql
-- Check for any duplicate account combinations
SELECT account_type, entity_identifier, COUNT(*) 
FROM payment_accounts 
GROUP BY account_type, entity_identifier 
HAVING COUNT(*) > 1;

-- Should return 0 rows if data is clean
```

## Common Use Cases

### 1. Display Fee Details to Student
**Query**: Get all fees due by student
```python
# Get department code from student
dept_code = student.dept  # e.g., '03'

# Query department account
account = db.query("""
    SELECT * FROM payment_accounts 
    WHERE account_type = 'department' 
    AND entity_identifier = ?
    AND is_active = 1
""", (dept_code,))

# Use account_name and account_number in fee display
```

### 2. Generate Payment Report
**Query**: Sum fees by account type
```python
report = db.query("""
    SELECT 
        pa.account_type,
        pa.account_name,
        COUNT(*) as transaction_count,
        SUM(COALESCE(hd.amount, 0)) as total_collected
    FROM payment_accounts pa
    LEFT JOIN hall_dues hd ON pa.account_type='hall' 
        AND pa.entity_identifier = h.hall_name
    WHERE pa.is_active = 1
    GROUP BY pa.account_type, pa.account_name
""")
```

### 3. Add New Department Account
```python
db.execute("""
    INSERT INTO payment_accounts 
    (account_type, entity_identifier, account_name, account_number, bank_name, is_active)
    VALUES ('department', ?, ?, ?, 'RUPALI BANK', 1)
""", ('14', 'NEW Department Account', '14'))
```

## Migration Notes

Currently your system:
- ✅ Uses `payment_accounts` for all accounts
- ✅ Properly structured with account_type discrimination
- ✅ Has proper indexes
- ✅ APIs already support filtering by account_type

**No migration needed** - your unified approach is already implemented!

## Future Enhancements

1. **Account Balance Tracking**: Add `balance` and `last_updated` fields
2. **Transaction History**: Create `account_transactions` table for audit trail
3. **Account Verification**: Add `is_verified` and `verification_date` fields
4. **Multiple Bank Support**: Already supports different `bank_name` values
5. **Account Hierarchy**: For multi-level department accounts structure

