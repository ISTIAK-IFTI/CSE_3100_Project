# Unified Accounts Implementation Checklist

Use this checklist to ensure you're properly utilizing the unified accounts table in your system.

## ✅ Initial Setup & Verification

- [ ] Run verification script to confirm all accounts are present
  ```bash
  python database/verify_unified_accounts.py
  ```
  Expected: All checks pass with ✅ marks

- [ ] Database file exists at: `database/ruet.db`
  - [ ] Verify file size > 1MB
  - [ ] Check write permissions

- [ ] All 4 files created:
  - [ ] `UNIFIED_ACCOUNTS_GUIDE.md`
  - [ ] `database/verify_unified_accounts.py`
  - [ ] `database/accounts_manager.py`
  - [ ] `DATABASE_MIGRATION.md`
  - [ ] `INTEGRATION_EXAMPLES.md`
  - [ ] `ACCOUNTS_TABLE_SUMMARY.md`

---

## ✅ Account Data Verification

- [ ] **Hall Accounts**
  - [ ] All halls have accounts
  - [ ] No duplicate hall accounts
  - [ ] All have `is_active = 1`
  - [ ] Account numbers populated

- [ ] **Library Account**
  - [ ] Exactly one library account exists
  - [ ] `is_active = 1`
  - [ ] Account number set

- [ ] **Department Accounts**
  - [ ] 13 department accounts exist (00-13)
  - [ ] No missing departments
  - [ ] All have `is_active = 1`
  - [ ] Correct department code mapping

**Run this query to verify:**
```sql
-- Should show 1 library, 13 departments, N halls
SELECT account_type, COUNT(*) FROM payment_accounts 
WHERE is_active = 1 GROUP BY account_type;
```

---

## ✅ Code Integration

### In app.py

- [ ] Imported accounts_manager functions
  ```python
  from database.accounts_manager import (
      get_account_for_student,
      get_all_hall_accounts,
      get_library_account,
      # ... other imports
  )
  ```

- [ ] Replaced direct database queries with convenience functions
  - [ ] Student account lookups use `get_account_for_student()`
  - [ ] Hall account lookups use `get_hall_account()`
  - [ ] Library account uses `get_library_account()`

- [ ] Error handling in place
  ```python
  account = get_account_for_student('03')
  if not account:
      return jsonify({"message": "Account not found"}), 404
  ```

- [ ] All queries filter by `is_active = 1`
  ```python
  # ✅ Correct
  WHERE account_type = 'hall' AND is_active = 1
  
  # ❌ Wrong - might return inactive accounts
  WHERE account_type = 'hall'
  ```

---

## ✅ API Endpoints

### Existing Endpoints Using Unified Table

- [ ] `GET /api/hall/accounts` - Returns all accounts
  - [ ] Can filter by `?account_type=hall`
  - [ ] Returns correct fields

- [ ] `GET /api/student/hall-fees` - Returns fees with account info
  - [ ] Includes account details with fees
  - [ ] Account linked correctly

- [ ] `POST /api/hall/accounts` - Create new account
  - [ ] Validates `account_type` field
  - [ ] Prevents duplicate accounts
  - [ ] Returns newly created account ID

### New Endpoints (Optional but Recommended)

- [ ] `GET /api/admin/account-statistics` - Account statistics
- [ ] `GET /api/admin/department-accounts` - All department accounts
- [ ] `POST /api/admin/accounts` - Admin create account
- [ ] `PUT /api/admin/accounts/<id>` - Admin update account
- [ ] `POST /api/admin/accounts/<id>/deactivate` - Admin deactivate

---

## ✅ Payment Display in Frontend

### Student View

- [ ] Department fee section shows
  - [ ] Account name
  - [ ] Account number
  - [ ] Bank name
  - [ ] fee amount

- [ ] Hall fee section shows
  - [ ] Account name
  - [ ] Account number
  - [ ] Bank name
  - [ ] Fee amount

- [ ] Library fine section shows
  - [ ] Account name
  - [ ] Account number
  - [ ] Bank name
  - [ ] Fine amount

### Hall Manager View

- [ ] Can see all hall accounts
- [ ] Account details visible
- [ ] Can view collection status

### Admin/Librarian View

- [ ] Dashboard shows all account types
- [ ] Statistics by account type
- [ ] Can manage accounts (create/update/deactivate)

---

## ✅ Database Queries

### Verify These Work Correctly

- [ ] Get account for student by department
  ```python
  account = get_account_for_student('03')
  ```

- [ ] Get all hall accounts
  ```python
  halls = get_all_hall_accounts()
  ```

- [ ] Get library account
  ```python
  lib = get_library_account()
  ```

- [ ] Get accounts by type
  ```python
  depts = get_accounts_by_type('department')
  ```

- [ ] Get account statistics
  ```python
  stats = get_accounts_stats()
  ```

---

## ✅ Maintenance Tasks

### Monthly Checks

- [ ] Run verification script (no errors)
  ```bash
  python database/verify_unified_accounts.py
  ```

- [ ] Verify account counts haven't changed unexpectedly
  ```sql
  SELECT account_type, COUNT(*) FROM payment_accounts 
  WHERE is_active = 1 GROUP BY account_type;
  ```

- [ ] Check for orphaned/inactive accounts
  ```sql
  SELECT COUNT(*) FROM payment_accounts WHERE is_active = 0;
  ```

### When Adding New Hall

- [ ] Hall created in `halls` table
- [ ] Payment account created in `payment_accounts` using:
  ```python
  from database.accounts_manager import create_account
  create_account(
      account_type='hall',
      entity_identifier='New Hall Name',
      account_name='New Hall Name Account',
      account_number='...'
  )
  ```
- [ ] Verify account appears in API
  ```bash
  curl "http://localhost:5000/api/hall/accounts?account_type=hall"
  ```

### When Deactivating Account

- [ ] Use `deactivate_account()` function
  ```python
  deactivate_account(account_id)
  ```

- [ ] Do NOT delete from database
  - [ ] Preserves historical data
  - [ ] Prevents orphaned references

---

## ✅ Error Handling & Edge Cases

### Scenarios to Test

- [ ] Student with department but no account
  - [ ] Shows error message
  - [ ] Doesn't crash API

- [ ] Student with multiple halls (impossible but test)
  - [ ] Returns correct account

- [ ] Deactivated account lookup
  - [ ] Returns None or error
  - [ ] Doesn't show to students

- [ ] Invalid account type in query
  - [ ] Returns error
  - [ ] Doesn't query database

- [ ] Missing required fields in account
  - [ ] Validation catches it
  - [ ] Returns helpful error

### Test Queries

```python
# Test 1: Valid lookup
account = get_account_for_student('03')  # CSE
assert account is not None
assert 'account_number' in account

# Test 2: Invalid lookup
account = get_account_for_student('99')  # Invalid dept
assert account is None

# Test 3: Statistics
stats = get_accounts_stats()
assert stats['total'] > 0
assert 'hall' in stats['by_type']
```

---

## ✅ Performance & Optimization

- [ ] Indexes exist on payment_accounts
  ```sql
  SELECT name FROM sqlite_master 
  WHERE type='index' AND tbl_name='payment_accounts';
  ```

- [ ] Query response times acceptable
  - [ ] Single account lookup: < 5ms
  - [ ] List all accounts: < 20ms

- [ ] No N+1 query problems
  - [ ] Using convenience functions
  - [ ] Not querying in loops

- [ ] Connection pooling in place (if multi-threaded)

---

## ✅ Security

- [ ] Account numbers not exposed to unauthorized users
  - [ ] Only show to when user is viewing their own fees
  - [ ] Only show exact account numbers to authorized roles

- [ ] Sensitive fields protected
  - [ ] `account_holder` not shown to students
  - [ ] Bank details only in necessary views

- [ ] Input validation
  - [ ] `account_type` validated against whitelist
  - [ ] No SQL injection possible

- [ ] Access control
  - [ ] Only admins/librarians can create/edit accounts
  - [ ] Students can only view their own account info

---

## ✅ Documentation

- [ ] README or docs mention unified accounts
- [ ] New developers know about `accounts_manager.py`
- [ ] Database schema documented
- [ ] API endpoints documented with examples

**Document examples:**
```markdown
## Payment Accounts API

All payment accounts are stored in a unified `payment_accounts` table.

### Getting accounts:
- Use `get_account_for_student(dept_code)`
- Use `get_all_hall_accounts()`
- Use `get_library_account()`
```

---

## ✅ Testing

- [ ] **Unit Tests**
  ```python
  def test_get_account_for_student():
      account = get_account_for_student('03')
      assert account is not None
      assert account['account_type'] == 'department'
  ```

- [ ] **Integration Tests**
  ```python
  def test_student_fees_endpoint():
      response = client.get('/api/student/123/fees')
      assert 'account' in response.json['department']
  ```

- [ ] **End-to-End Tests**
  - [ ] Student can view fees with account info
  - [ ] Hall manager can view hall account
  - [ ] Admin can manage accounts

---

## ✅ Backup & Recovery

- [ ] Regular database backups
  ```bash
  # Weekly backup
  cp database/ruet.db database/backups/ruet_$(date +%Y%m%d).db
  ```

- [ ] Backup export to JSON (optional)
  ```python
  # In accounts_manager.py
  import json
  for account_type in ['hall', 'library', 'department']:
      accounts = get_accounts_by_type(account_type)
      with open(f'backup_{account_type}.json', 'w') as f:
          json.dump(accounts, f)
  ```

- [ ] Document restore procedure
  - [ ] How to restore from backup
  - [ ] How to verify restored data

---

## ✅ Post-Implementation Sign-Off

### For Developer

- [ ] ✅ All code integrated
- [ ] ✅ All tests passing
- [ ] ✅ No database errors
- [ ] ✅ Performance acceptable

**Developer Signature: ___________  Date: ___________**

### For QA/Tester

- [ ] ✅ All endpoints working
- [ ] ✅ All views displaying correctly
- [ ] ✅ No edge case failures
- [ ] ✅ Performance meets requirements

**QA Signature: ___________  Date: ___________**

### For Admin

- [ ] ✅ System operational
- [ ] ✅ Data integrity verified
- [ ] ✅ Backups in place
- [ ] ✅ Team trained

**Admin Signature: ___________  Date: ___________**

---

## Quick Reference Commands

```bash
# Verify system status
python database/verify_unified_accounts.py

# Run tests
python -m pytest test_accounts_manager.py

# Backup database
cp database/ruet.db database/backup_$(date +%Y%m%d_%H%M%S).db

# Check database size
ls -lh database/ruet.db

# View errors
sqlite3 database/ruet.db "SELECT * FROM payment_accounts LIMIT 5;"
```

---

## Support Contacts

For issues, refer to:
1. UNIFIED_ACCOUNTS_GUIDE.md - Architecture reference
2. DATABASE_MIGRATION.md - Troubleshooting section
3. INTEGRATION_EXAMPLES.md - Code examples
4. accounts_manager.py - Function documentation

---

## Checklist Sign-Off

- [ ] All items checked
- [ ] No blockers remaining
- [ ] System ready for production

**Completed Date: ___________**

**Completed By: ___________**

