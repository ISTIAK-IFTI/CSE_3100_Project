# Quick Start Guide - Financial Management System

## ⚡ Get Started in 3 Steps

### 1. Initialize Database
```bash
cd database
python init_hall_db.py
```
✅ Creates `hall_accounts` table (plus updates existing hall tables)

### 2. Start Backend
```bash
cd backend
python app.py
```
Server runs at: `http://127.0.0.1:5000`

### 3. Access Hall Manager Dashboard
Open: `http://127.0.0.1:5000/frontend/hall.html`
Login with: `hall001@hall.ruet.ac.bd` (password: `676`)

---

## 🎯 Common Tasks

### Add Payment Account
```
Hall Manager Dashboard
→ Hall Payment Accounts (right sidebar)
→ Enter: Account Name, Number (optional), Account Holder
→ Click: "Add Account"
```

### Create Monthly Fee for All Students
```
Hall Manager Dashboard
→ Create Monthly Hall Fee (card on right)
→ Select Month (YYYY-MM)
→ Enter Amount (BDT)
→ Click: "Create Fee"
```

### Create Fee for Single Student
```
Hall Manager Dashboard
→ Create Fee (Advanced) (card on right bottom)
→ Select: "For Single Student"
→ Enter: Student ID
→ Select: Month
→ Enter: Amount
→ Click: "Create Fee"
```

### Remove Student's All Fees
```
Hall Manager Dashboard
→ Hall Dues section (bottom)
→ In "Delete fees for Student ID" field
→ Enter: Student ID
→ Click: "Delete"
```

### Remove All Fees for a Month
```
Hall Manager Dashboard
→ Hall Dues section (bottom)
→ In "Delete fees for Month" field
→ Select: Month
→ Click: "Delete"
```

### Search Dues by Student
```
Hall Manager Dashboard
→ Hall Dues section (top)
→ In search box: Enter Student ID
→ View filtered results
```

### Search Dues by Date
```
Hall Manager Dashboard
→ Hall Dues section (top)
→ In month filter: Select Month
→ View filtered results
```

---

## 📊 Database Reference

### Add Hall Account Manually (SQL)
```sql
INSERT INTO hall_accounts (hall_id, account_name, account_number, bank_name, account_holder)
VALUES (1, 'Hamid Hall Account', '12345678', 'RUPALI BANK', 'Hall Authority');
```

### Create Fee for All Students
```sql
-- First, create the monthly fee entry
INSERT INTO hall_monthly_fees (hall_id, month, amount, deadline)
VALUES (1, '2024-01', 500, '2024-01-15');

-- Then create dues for each student in the hall
INSERT INTO hall_dues (hall_id, student_id, month, amount, status)
SELECT ra.hall_id, ra.student_id, '2024-01', 500, 'unpaid'
FROM room_allocations ra
WHERE ra.hall_id = 1;
```

### Update Account Number (Add Real Account)
```sql
UPDATE hall_accounts
SET account_number = '12345678901234'
WHERE account_name = 'Hamid Hall Account';
```

### Mark Due as Paid
```sql
UPDATE hall_dues
SET status = 'paid', paid_date = datetime('now')
WHERE id = 1;
```

---

## 🔍 Database Tables

### hall_accounts
```
id | hall_id | account_name | account_number | bank_name | account_holder | is_active
```

### hall_dues
```
id | hall_id | student_id | month | amount | status | paid_date | created_at
```

### hall_monthly_fees
```
id | hall_id | month | amount | deadline | created_at
```

---

## API Reference (Quick)

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/api/hall/accounts` | GET | Get all accounts |
| `/api/hall/accounts` | POST | Create account |
| `/api/hall/fees/create-for-all` | POST | Create fee for all |
| `/api/hall/fees/create-for-student` | POST | Create fee for single |
| `/api/hall/dues` | GET | Get all dues |
| `/api/hall/dues/<id>` | DELETE | Delete single due |
| `/api/hall/dues/delete-all` | POST | Delete dues (by student/month) |
| `/api/hall/dues/search` | GET | Search dues |
| `/api/student/hall-fees` | GET | Get student's fees |

---

## 💡 Tips

1. **Duplicate Prevention**: System automatically prevents creating the same fee twice for one student in one month
2. **Search Before Delete**: Always search to verify entries before bulk deletion
3. **Month Format**: Always use YYYY-MM format (e.g., 2024-01 for January 2024)
4. **Account Numbers**: Initially null - add real RUPALI BANK account numbers later
5. **Status Tracking**: Status can be "paid" or "unpaid" - use Hall Dues mark paid feature
6. **Student View**: Students automatically see their monthly fees in dashboard

---

## ⚠️ Important Notes

- Fees are only created for **already allocated** students
- Each student can have **only one fee per month** (enforced by database)
- Deleting a due **permanently removes** it from database
- Account numbers are **not mandatory** - add later when available
- All transactions use **RUPALI BANK** (default)

---

## 📱 Features Checklist

- ✅ Hall accounts management (payment details)
- ✅ Monthly fee creation (all students or single)
- ✅ Hall dues tracking (student, month, amount, status)
- ✅ Search by student ID
- ✅ Search by date/month
- ✅ Remove single fee
- ✅ Remove all fees for student
- ✅ Remove all fees for month
- ✅ Student dashboard integration
- ✅ Duplicate prevention

---

## 🐛 Troubleshooting

**Issue**: "Hall not found"
→ Check sidebar login, verify hall exists in database

**Issue**: "Student not allocated to hall"
→ Must allocate student to room first, then create fee

**Issue**: Fee not appearing in student dashboard
→ Run `python database/init_hall_db.py` to ensure tables exist

**Issue**: "Fee already exists"
→ This prevents duplicates - delete old fee first if you need to recreate

