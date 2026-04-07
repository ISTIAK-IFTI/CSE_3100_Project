# Financial Management System Guide

## Overview
Complete implementation of hall account management, monthly fee creation, and hall dues tracking system for RUET Portal.

---

## 🗄️ Database Structure

### New Table: `hall_accounts`
Stores account information for each hall (for payment purposes with RUPALI BANK).

**Columns:**
- `id` - Primary key
- `hall_id` - Foreign key to halls table
- `account_name` - Account name (e.g., "Hamid Hall Account")
- `account_number` - Account number (NULL initially, add real account number later)
- `bank_name` - Bank name (default: "RUPALI BANK")
- `account_holder` - Account holder name
- `is_active` - Active status (1 = active)
- `created_at` - Creation timestamp

### Updated Table: `hall_dues`
Now includes `month` field for better tracking and searching.

**Columns:**
- `id` - Primary key
- `hall_id` - Hall reference
- `student_id` - Student reference
- `month` - Month in YYYY-MM format
- `amount` - Fee amount
- `status` - "paid" or "unpaid"
- `paid_date` - Payment date (if paid)
- `created_at` - Creation timestamp
- **Unique constraint:** (student_id, month) - prevents duplicate fees

---

## 🔧 Backend API Endpoints

### Hall Accounts Management

#### GET `/api/hall/accounts`
Retrieve all accounts for a hall.

**Query Parameters:**
- `hall_name` - Name of the hall (required)

**Response:**
```json
{
  "accounts": [
    {
      "id": 1,
      "account_name": "Hamid Hall Account",
      "account_number": null,
      "bank_name": "RUPALI BANK",
      "account_holder": "Hall Authority",
      "is_active": 1,
      "created_at": "2024-01-15T10:30:00"
    }
  ]
}
```

#### POST `/api/hall/accounts`
Create a new hall account.

**Request Body:**
```json
{
  "account_name": "Hamid Hall Account",
  "account_number": null,
  "account_holder": "Hall Authority",
  "hall_name": "Shahid Abdul Hamid Hall"
}
```

**Response:** `201 Created`
```json
{
  "message": "Account created successfully",
  "account_id": 1
}
```

---

### Monthly Fee Management

#### POST `/api/hall/fees/create-for-all`
Create monthly fee for **all allocated students** in a hall.

**Request Body:**
```json
{
  "month": "2024-01",
  "amount": 500,
  "deadline": "2024-01-15",
  "hall_name": "Shahid Abdul Hamid Hall"
}
```

**Response:** `200 OK`
```json
{
  "message": "Monthly fee created for 45 student(s)",
  "created_count": 45,
  "total_students": 50
}
```

**Note:** 
- Automatically creates dues entries in `hall_dues` table
- Won't duplicate if fee already exists for the month
- Only creates fees for students already allocated to the hall

#### POST `/api/hall/fees/create-for-student`
Create monthly fee for a **single student**.

**Request Body:**
```json
{
  "student_id": "2203177",
  "month": "2024-01",
  "amount": 500,
  "hall_name": "Shahid Abdul Hamid Hall"
}
```

**Response:** `201 Created`
```json
{
  "message": "Monthly fee created for student successfully",
  "student_id": "2203177",
  "month": "2024-01",
  "amount": 500
}
```

**Error Handling:**
- Returns `409 Conflict` if fee already exists for student in that month
- Returns `404` if student not allocated to hall
- Returns `404` if hall not found

---

### Hall Dues Management

#### GET `/api/hall/dues`
Fetch all dues for a hall.

**Query Parameters:**
- `hall_name` - Name of the hall (required)

**Response:** `200 OK`
```json
{
  "dues": [
    {
      "id": 1,
      "student_id": "2203177",
      "student_name": "Ahmed Hassan",
      "month": "2024-01",
      "amount": 500,
      "status": "unpaid",
      "paid_date": null,
      "created_at": "2024-01-10T08:30:00"
    }
  ]
}
```

#### DELETE `/api/hall/dues/<due_id>`
Delete a single due entry.

**Response:** `200 OK`
```json
{
  "message": "Due deleted successfully"
}
```

#### POST `/api/hall/dues/delete-all`
Delete all dues by **student ID** or **month**.

**Request Body (Delete for specific student):**
```json
{
  "student_id": "2203177",
  "hall_name": "Shahid Abdul Hamid Hall"
}
```

**Request Body (Delete for specific month):**
```json
{
  "month": "2024-01",
  "hall_name": "Shahid Abdul Hamid Hall"
}
```

**Response:** `200 OK`
```json
{
  "message": "All dues deleted for student 2203177",
  "deleted_count": 12
}
```

#### GET `/api/hall/dues/search`
Search dues by **student ID** or **month**.

**Query Parameters:**
- `hall_name` - Name of the hall (required)
- `student_id` - Student ID to search (optional)
- `month` - Month in YYYY-MM format (optional)

**Response:** `200 OK`
```json
{
  "total": 5,
  "dues": [
    {
      "id": 1,
      "student_id": "2203177",
      "student_name": "Ahmed Hassan",
      "month": "2024-01",
      "amount": 500,
      "status": "unpaid",
      "paid_date": null,
      "created_at": "2024-01-10T08:30:00"
    }
  ]
}
```

---

### Student API

#### GET `/api/student/hall-fees`
Get all monthly hall fees for a student.

**Query Parameters:**
- `id` - Student ID (required)

**Response:** `200 OK`
```json
{
  "items": [
    {
      "id": 1,
      "month": "2024-01",
      "amount": 500,
      "status": "unpaid",
      "paid_date": null
    },
    {
      "id": 2,
      "month": "2023-12",
      "amount": 500,
      "status": "paid",
      "paid_date": "2023-12-28T05:15:00"
    }
  ]
}
```

---

## 🖼️ Frontend Features

### Hall Manager Dashboard (hall.html)

#### 1. **Hall Payment Accounts Section**
- **Add Account**: Create new account with name, number (optional), and holder
- **View Accounts**: View all active accounts for the hall
- Default bank: RUPALI BANK
- Account numbers can be added later when real details are available

#### 2. **Create Monthly Hall Fee**
Two methods available:

**Simple Method:**
- Select month and amount
- Automatically creates fee for all allocated students
- Prevents duplicates

**Advanced Method:**
- Choose "For All Students" or "For Single Student"
- If single student, enter student ID
- Create fees without duplicate constraints

#### 3. **Enhanced Hall Dues**
**Search Features:**
- Search by Student ID
- Search by Month
- Real-time filtering

**Management Features:**
- Remove individual due entry
- Remove all fees for a specific student
- Remove all fees for a specific month

**Table Display:**
- Student ID
- Student Name
- Month
- Amount
- Status (PAID/UNPAID badge)
- Action buttons

---

### Student Dashboard (student.html)

**Monthly Fees Integration:**
- All monthly hall fees automatically appear in the "Current Dues & Monthly Fees" section
- Shows month, amount, and payment status
- Includes with other fees (Library, Department, etc.)
- Contributes to total due calculation

---

## 📋 Usage Workflow

### For Hall Manager

#### Step 1: Create Hall Accounts
1. Go to "Hall Payment Accounts" section
2. Enter account name (e.g., "Hamid Hall Account")
3. (Optional) Enter account number when available
4. (Optional) Enter account holder name
5. Click "Add Account"

#### Step 2: Create Monthly Fees
**Option A - All Students:**
1. Go to "Create Monthly Hall Fee"
2. Select month (YYYY-MM format)
3. Enter amount in BDT
4. (Optional) Set deadline
5. Click "Create Fee"
✅ Automatically creates fees for all allocated students

**Option B - Single Student:**
1. Go to "Create Fee (Advanced)"
2. Select "For Single Student"
3. Enter student ID
4. Select month
5. Enter amount
6. Click "Create Fee"
✅ Creates fee only for that student

#### Step 3: Manage Hall Dues
1. Go to "Hall Dues" section
2. **Search Features:**
   - Use "Search by Student ID" to find specific student's fees
   - Use "Search by Month" to find all fees for a month
   - Clear search to view all
3. **Delete Options:**
   - Click "Remove" button on any row to delete single due
   - Enter student ID and click "Delete" to remove all fees for that student
   - Select month and click "Delete" to remove all fees for that month

---

### For Students

#### View Monthly Fees
1. Login to student dashboard
2. Go to "Current Dues & Monthly Fees" section
3. Monthly fees appear with format: "Hall Fee (2024-01)"
4. Shows month, amount, and payment status
5. Included in total due calculation

---

## 🔄 Database Initialization

The new `hall_accounts` table is created automatically when you run:

```bash
python database/init_hall_db.py
```

If the table already exists, it will be skipped (safe to run multiple times).

---

## ✅ Features Summary

### Account Management ✅
- [x] Create hall accounts for payment
- [x] View all accounts
- [x] Support for RUPALI BANK integration
- [x] Placeholder for future account numbers

### Monthly Fee Creation ✅
- [x] Create fee for all students at once
- [x] Create fee for individual student
- [x] Automatic duplicate prevention
- [x] Month validation (YYYY-MM format)

### Hall Dues ✅
- [x] Delete single due entry
- [x] Delete all fees for specific student
- [x] Delete all fees for specific month
- [x] Search by student ID
- [x] Search by month
- [x] View with student name and paid_date

### Student Dashboard Integration ✅
- [x] Monthly fees appear in student dashboard
- [x] Shows in "Current Dues & Monthly Fees" section
- [x] Included in total due calculation
- [x] Displays payment status

---

## 🚀 Future Enhancements

1. **Payment Integration**: Connect to RUPALI BANK payment gateway
2. **Real Account Numbers**: Add actual RUPALI BANK account numbers to accounts table
3. **SMS/Email Notifications**: Notify students about due dates
4. **Automatic Calculation**: Calculate penalties for late payments
5. **Receipt Generation**: Generate payment receipts
6. **Batch Processing**: Bulk fee creation from CSV

---

## 📞 Support

For issues or questions:
1. Check database integrity: `SELECT * FROM hall_accounts;`
2. Verify hall exists: `SELECT * FROM halls;`
3. Check student allocation: `SELECT * FROM room_allocations WHERE student_id=?;`
4. Review browser console for API errors

