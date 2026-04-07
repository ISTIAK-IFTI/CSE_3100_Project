# Hall Dashboard UI Guide - Visual Reference

## Hall Manager Dashboard Layout

The hall.html dashboard now has these sections (in order):

### 1. Summary Section (unchanged)
```
┌─────────────────────────────────────┐
│ Summary                             │
├─────────────────────────────────────┤
│ Total Rooms | Allocated | Unpaid    │
│             Seats        Students   │
└─────────────────────────────────────┘
```

### 2. Room Allocation Section (unchanged)
```
┌─────────────────────────────────────┐
│ Allocate Room                       │
├─────────────────────────────────────┤
│ Hall Name: [Display]                │
│ Room Number: [_________]            │
│ Allocation Type: [Single / Shared 4]│
│ Student IDs: [____________________] │
│ [Allocate] [Clear Form]             │
└─────────────────────────────────────┘
```

### 3. Hall Payment Accounts Section ✨ NEW
```
┌─────────────────────────────────────┐
│ Hall Payment Accounts               │
├─────────────────────────────────────┤
│ Account Name: [______________]      │
│ Account Number: [______________]    │
│   (optional - add later)            │
│ Account Holder: [______________]    │
│                                     │
│ [Add Account] [View Accounts]       │
│                                     │
│ Bank: RUPALI BANK                   │
└─────────────────────────────────────┘
```

### 4. Create Monthly Hall Fee Section (updated)
```
┌─────────────────────────────────────┐
│ Create Monthly Hall Fee             │
├─────────────────────────────────────┤
│ Month: [____/____] (YYYY-MM)        │
│ Amount (BDT): [_____]               │
│ Deadline: [____/____/____]          │
│                                     │
│ [Create Fee]                        │
│                                     │
│ Creates fee for all students        │
└─────────────────────────────────────┘
```

### 5. Create Fee (Advanced) Section ✨ NEW
```
┌─────────────────────────────────────┐
│ Create Fee (Advanced)               │
├─────────────────────────────────────┤
│ ◉ For All Students                  │
│ ○ For Single Student                │
│                                     │
│ [Optional - shows if single selected] │
│ Student ID: [______________]        │
│                                     │
│ Month: [____/____] (YYYY-MM)        │
│ Amount (BDT): [_____]               │
│                                     │
│ [Create Fee]                        │
└─────────────────────────────────────┘
```

### 6. Room Inventory Section (unchanged - with search)
```
┌─────────────────────────────────────┐
│ Room Inventory                      │
├─────────────────────────────────────┤
│ [Search by room...] [by student...] │
│ [Clear Search]                      │
├─────────────────────────────────────┤
│ Room # | Type   | Occupancy | Status│
├─────────────────────────────────────┤
│ 101    | Single | 1/1       | FULL  │
│ 102    | Shared | 2/4       | AVAIL │
│ ...                                 │
└─────────────────────────────────────┘
```

### 7. Current Allocations Section (unchanged - with delete)
```
┌─────────────────────────────────────┐
│ Current Allocations                 │
├─────────────────────────────────────┤
│ ID | Room | Student ID | Name | Typ │
├─────────────────────────────────────┤
│ 1  | 101  | 2203177    | Ali  | S   │
│ 2  | 102  | 2203188    | Bob  | Sh  │
│ [Remove] button on each row         │
└─────────────────────────────────────┘
```

### 8. Hall Dues Section ✨ ENHANCED
```
┌──────────────────────────────────────────┐
│ Hall Dues                                │
├──────────────────────────────────────────┤
│ [Search by Student ID] [by Month YYYY-MM]│
│ [Clear Search]                           │
├──────────────────────────────────────────┤
│ Student ID | Name  | Month    | Amount   │
│            |       |          | Status   │
├──────────────────────────────────────────┤
│ 2203177    | Ahmed | 2024-01  | 500 BDT  │
│            |       |          | [🔴UNPD] │
│            |       |          | [Remove] │
│ 2203188    | Bob   | 2024-01  | 500 BDT  │
│            |       |          | [🟢PAID] │
│            |       |          | [Remove] │
├──────────────────────────────────────────┤
│ Bulk Actions:                            │
│ [Remove Selected Student's Fees]         │
│ [Remove All Fees for Month]              │
│                                          │
│ Delete for Student:                      │
│ [Enter Student ID_______] [Delete]       │
│                                          │
│ Delete for Month:                        │
│ [Select Month ____/____] [Delete]        │
└──────────────────────────────────────────┘
```

---

## Sidebar Navigation (Updated)

```
┌──────────────────────────┐
│ RUET Portal              │
│ [Hall Name]              │
├──────────────────────────┤
│ ▶ Dashboard              │
│  Room Allocation         │
│  Hall Accounts       ⭐NEW│
│  Monthly Hall Fee        │
│  Create Fee (Advanc) ⭐NEW│
│  Allocations             │
│  Hall Dues               │
├──────────────────────────┤
│                          │
│                          │
│        [Logout]          │
└──────────────────────────┘
```

---

## Color Coding in Hall Dues

### Status Badges
- **UNPAID** (Red badge) - `.bad` class
  - Background: #fef2f2 (light red)
  - Border: #fecaca (red)
  - Indicates amount is due

- **PAID** (Green badge) - `.ok` class
  - Background: #ecfdf5 (light green)
  - Border: #a7f3d0 (green)
  - Indicates payment completed

---

## Student Dashboard - Enhanced Dues Section

### Before Implementation
```
┌────────────────────────────┐
│ Current Dues               │
├────────────────────────────┤
│ Fee Type | Month | Amount  │
│          |       | Status  │
├────────────────────────────┤
│ Hall Fee | Monthly | 0     │
│          |         | PAID  │
│ Library  | Current | 200   │
│          |         | UNPAID│
└────────────────────────────┘
```

### After Implementation ✨
```
┌────────────────────────────────────┐
│ Current Dues & Monthly Fees    ⭐  │
├────────────────────────────────────┤
│ Fee Type | Month | Amount | Status │
├────────────────────────────────────┤
│ Hall Fee (2024-01) | 2024-01| 500  │
│                    |        | UNPD │
│ Hall Fee (2023-12) | 2023-12| 500  │
│                    |        | PAID │
│ Hall Fee | Monthly | 0             │
│          |         | PAID          │
│ Library  | Current | 200           │
│          |         | UNPAID        │
│ Department | Sem  | 0              │
│          |       | PAID            │
└────────────────────────────────────┘
```

---

## Data Flow Diagram

### Creating Monthly Fee for All Students

```
Hall Manager
    ↓
[Create Monthly Hall Fee Card]
    ↓
    ├─ Month: 2024-01
    ├─ Amount: 500
    └─ Deadline: Optional
    ↓
    POST /api/hall/fees/create-for-all
    ↓
    Backend:
    ├─ Create hall_monthly_fees entry
    ├─ Get all students in hall
    └─ Create hall_dues for each student
    ↓
    ✅ Success Message
    ↓
    Student Dashboard Updated
    ├─ New "Hall Fee (2024-01)" appears
    ├─ Amount: 500 BDT
    └─ Status: unpaid
```

### Creating Fee for Single Student

```
Hall Manager
    ↓
[Create Fee (Advanced) Card]
    ↓
    ├─ Select: "For Single Student"
    ├─ Student ID: 2203177
    ├─ Month: 2024-01
    └─ Amount: 500
    ↓
    POST /api/hall/fees/create-for-student
    ↓
    Backend:
    ├─ Verify student exists in hall
    ├─ Check no duplicate fee exists
    └─ Create hall_dues entry
    ↓
    ✅ Success Message
    ↓
    Only That Student's Dashboard Updated
```

### Deleting Dues

```
Hall Manager
    ↓
Hall Dues Table
    ↓
[Option 1: Click Remove on row]
    ↓
    DELETE /api/hall/dues/{id}
    ↓
    ✅ Due deleted
    
[Option 2: Enter Student ID + Delete]
    ↓
    POST /api/hall/dues/delete-all
    ├─ student_id: 2203177
    └─ hall_name: ...
    ↓
    ✅ All student's fees deleted
    
[Option 3: Select Month + Delete]
    ↓
    POST /api/hall/dues/delete-all
    ├─ month: 2024-01
    └─ hall_name: ...
    ↓
    ✅ All month's fees deleted
```

---

## Table: Hall Dues Column Explanations

| Column | Type | Example | Notes |
|--------|------|---------|-------|
| **Student ID** | Text | 2203177 | From room_allocations |
| **Student Name** | Text | Ahmed Hassan | Joined from students table |
| **Month** | Date | 2024-01 | YYYY-MM format |
| **Amount** | Number | 500 | BDT currency |
| **Status** | Badge | UNPAID | Color-coded badge |
| **Action** | Button | [Remove] | Delete single due |

---

## Form Input Validation

### When Creating Fee for All
```
Validation Order:
1. Month selected? → "Please select Month..."
2. Amount > 0? → "Please enter valid Amount..."
3. Hall exists? → "Hall not found..."
4. Fee already exists? → "Fee already exists..."
✅ All pass → Create fees for allocated students
```

### When Creating Fee for Single Student
```
Validation Order:
1. Selected "For Single Student"? 
2. Student ID entered? → "Please enter Student ID..."
3. Month selected? → "Please select Month..."
4. Amount > 0? → "Please enter valid Amount..."
5. Hall exists? → "Hall not found..."
6. Student allocated to hall? → "Student not allocated..."
7. Fee already exists? → "Fee already exists..."
✅ All pass → Create fee for single student
```

### When Deleting All Fees
```
Confirmation Dialog:
"Remove all fees for [student/month]? This action cannot be undone."
    │
    ├─ [Cancel] → Operation stopped
    │
    └─ [OK] → Proceeds with deletion
```

---

## Account Management Workflow

### Adding Account

```
New Account Form:
├─ Account Name (required): "Hamid Hall Account"
├─ Account Number (optional): [For future use]
├─ Account Holder (optional): "Hall Authority"
└─ Bank (auto): "RUPALI BANK"

[Add Account] → POST /api/hall/accounts
    ↓
✅ "Account created successfully"
```

### Viewing Accounts

```
[View Accounts] Button
    ↓
    GET /api/hall/accounts
    ↓
Alert Window Shows:
"Hall Accounts:
Hamid Hall Account
Kamal Hall Account (98765432)"
```

---

## Search & Filter Behavior

### Real-time Student Search
```
User types "2203" in Student search box
    ↓
JavaScript filters hall_dues array by student_id
    ↓
Table shows only rows matching "2203"
    ↓
User clears box → Shows all again
```

### Month Filter
```
User selects "2024-01" in Month picker
    ↓
JavaScript filters hall_dues array by month
    ↓
Table shows only rows for 2024-01
    ↓
User clicks [Clear Search] → Shows all
```

### Combined Filter
```
Student ID: "2203177" + Month: "2024-01"
    ↓
Shows only that student's fees for that month
    ↓
Typically 0-1 result
```

---

## Status Messages

### Success Messages
- "Account created successfully!"
- "Monthly fee created for 45 student(s)"
- "Monthly fee created for student successfully"
- "Due deleted successfully"
- "All dues deleted for student 2203177"

### Error Messages
- "Hall not found"
- "Student not allocated to this hall"
- "Fee already exists for this student in this month"
- "Please enter Account Name"
- "Please select Month and enter valid Amount"

### Status Bar (Bottom of cards)
- Shows current operation status
- Auto-clears on success
- Shows error details if operation fails
- Updated after API calls

---

## Responsive Behavior

### Desktop (1200px+)
- Hall Accounts: col-4 (right side)
- Monthly Fee: col-4 (right side)
- Advanced Fee: col-4 (right side)
- All 3 cards visible side-by-side

### Tablet (768px - 1199px)
- Cards stack 2-per-row

### Mobile (< 768px)
- Cards stack 1-per-row
- Sidebar hidden (toggle list)
- Full width inputs

---

## Icons/Badges Reference

| Element | Code | Appearance |
|---------|------|-----------|
| UNPAID Status | `<span class="badge bad">UNPAID</span>` | 🔴 Red box |
| PAID Status | `<span class="badge ok">PAID</span>` | 🟢 Green box |
| Remove Button | `<button class="btn">Remove</button>` | Gray button |
| Primary Button | `<button class="btn primary">Create</button>` | Dark button |

---

## Quick Reference: What's Where?

```
Hall Manager Dashboard
├─ Accounts Management
│  └─ Hall Payment Accounts Card
├─ Fee Creation
│  ├─ Create Monthly Hall Fee (for all)
│  └─ Create Fee (Advanced) (all or single)
├─ Allocation Management
│  └─ Allocate Room Card (unchanged)
├─ Hall Status
│  ├─ Summary KPIs
│  └─ Room Inventory Table
├─ Dues Management
│  └─ Hall Dues Card
│     ├─ Search by Student/Month
│     ├─ Remove button per row
│     ├─ Bulk remove by student
│     └─ Bulk remove by month
└─ Room Inventory
   └─ Room Inventory Table (unchanged)

Student Dashboard
└─ Current Dues & Monthly Fees Section
   └─ Shows all monthly hall fees integrated
```

