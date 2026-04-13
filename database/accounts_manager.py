"""
Unified Accounts Manager Module

This module provides convenient functions to manage and access unified accounts
from the payment_accounts table without worrying about account types.

Usage in your app:
    from database.accounts_manager import get_account_for_student, get_hall_account, etc.
"""

import sqlite3
from pathlib import Path
from typing import Optional, Dict, List
from datetime import datetime


BASE_DIR = Path(__file__).resolve().parent.parent
DB_PATH = BASE_DIR / "database" / "ruet.db"

DEPT_CODES = {
    '00': 'CIVIL', '01': 'EEE', '02': 'ME', '03': 'CSE', '04': 'ETE',
    '05': 'IPE', '06': 'GCE', '07': 'URP', '08': 'MTE', '09': 'ARCH',
    '10': 'ECE', '11': 'CHE', '12': 'BECM', '13': 'MSE'
}


def _get_db():
    """Get database connection."""
    con = sqlite3.connect(DB_PATH)
    con.row_factory = sqlite3.Row
    return con


def get_account_for_student(student_dept: str) -> Optional[Dict]:
    """
    Get the payment account for a student based on their department.
    
    Args:
        student_dept: Department code or name (e.g., '03' or 'CSE')
        
    Returns:
        Dictionary with account details or None if not found
        
    Example:
        account = get_account_for_student('03')  # CSE department
        print(account['account_name'])  # "CSE Department Account"
        print(account['account_number'])
        print(account['bank_name'])
    """
    con = _get_db()
    cur = con.cursor()
    
    # Normalize department code
    dept_code = student_dept
    if student_dept in DEPT_CODES:
        dept_code = [k for k, v in DEPT_CODES.items() if v.upper() == student_dept.upper()]
        if dept_code:
            dept_code = dept_code[0]
    
    cur.execute("""
        SELECT 
            id, account_type, entity_identifier, account_name,
            account_number, bank_name, account_holder, is_active, created_at
        FROM payment_accounts
        WHERE account_type = 'department'
        AND entity_identifier = ?
        AND is_active = 1
        LIMIT 1
    """, (dept_code,))
    
    row = cur.fetchone()
    con.close()
    
    return dict(row) if row else None


def get_hall_account(hall_name: str) -> Optional[Dict]:
    """
    Get the payment account for a specific hall.
    
    Args:
        hall_name: Name of the hall (e.g., 'Shahid Abdul Hamid Hall')
        
    Returns:
        Dictionary with account details or None if not found
        
    Example:
        account = get_hall_account('Shahid Abdul Hamid Hall')
        print(account['account_number'])
    """
    con = _get_db()
    cur = con.cursor()
    
    cur.execute("""
        SELECT 
            id, account_type, entity_identifier, account_name,
            account_number, bank_name, account_holder, is_active, created_at
        FROM payment_accounts
        WHERE account_type = 'hall'
        AND entity_identifier = ?
        AND is_active = 1
        LIMIT 1
    """, (hall_name,))
    
    row = cur.fetchone()
    con.close()
    
    return dict(row) if row else None


def get_all_hall_accounts() -> List[Dict]:
    """
    Get all active hall accounts.
    
    Returns:
        List of account dictionaries
        
    Example:
        halls = get_all_hall_accounts()
        for hall in halls:
            print(f"{hall['entity_identifier']}: {hall['account_number']}")
    """
    con = _get_db()
    cur = con.cursor()
    
    cur.execute("""
        SELECT 
            id, account_type, entity_identifier, account_name,
            account_number, bank_name, account_holder, is_active, created_at
        FROM payment_accounts
        WHERE account_type = 'hall'
        AND is_active = 1
        ORDER BY created_at DESC
    """)
    
    rows = cur.fetchall()
    con.close()
    
    return [dict(row) for row in rows]


def get_library_account() -> Optional[Dict]:
    """
    Get the library payment account.
    
    Returns:
        Dictionary with account details or None if not found
        
    Example:
        lib_account = get_library_account()
        if lib_account:
            print(f"Send to: {lib_account['account_number']}")
    """
    con = _get_db()
    cur = con.cursor()
    
    cur.execute("""
        SELECT 
            id, account_type, entity_identifier, account_name,
            account_number, bank_name, account_holder, is_active, created_at
        FROM payment_accounts
        WHERE account_type = 'library'
        AND is_active = 1
        LIMIT 1
    """)
    
    row = cur.fetchone()
    con.close()
    
    return dict(row) if row else None


def get_all_department_accounts() -> List[Dict]:
    """
    Get all active department accounts.
    
    Returns:
        List of account dictionaries
        
    Example:
        depts = get_all_department_accounts()
        for dept in depts:
            dept_name = DEPT_CODES.get(dept['entity_identifier'])
            print(f"{dept_name}: {dept['account_number']}")
    """
    con = _get_db()
    cur = con.cursor()
    
    cur.execute("""
        SELECT 
            id, account_type, entity_identifier, account_name,
            account_number, bank_name, account_holder, is_active, created_at
        FROM payment_accounts
        WHERE account_type = 'department'
        AND is_active = 1
        ORDER BY entity_identifier ASC
    """)
    
    rows = cur.fetchall()
    con.close()
    
    return [dict(row) for row in rows]


def get_account_by_id(account_id: int) -> Optional[Dict]:
    """
    Get a specific account by its ID.
    
    Args:
        account_id: The account ID
        
    Returns:
        Dictionary with account details or None if not found
    """
    con = _get_db()
    cur = con.cursor()
    
    cur.execute("""
        SELECT 
            id, account_type, entity_identifier, account_name,
            account_number, bank_name, account_holder, is_active, created_at
        FROM payment_accounts
        WHERE id = ?
        LIMIT 1
    """, (account_id,))
    
    row = cur.fetchone()
    con.close()
    
    return dict(row) if row else None


def get_accounts_by_type(account_type: str, active_only: bool = True) -> List[Dict]:
    """
    Get all accounts of a specific type.
    
    Args:
        account_type: 'hall', 'library', or 'department'
        active_only: Filter only active accounts (default: True)
        
    Returns:
        List of account dictionaries
        
    Example:
        all_accounts = get_accounts_by_type('hall', active_only=True)
        inactive_accounts = get_accounts_by_type('department', active_only=False)
    """
    if account_type not in ['hall', 'library', 'department']:
        raise ValueError("account_type must be 'hall', 'library', or 'department'")
    
    con = _get_db()
    cur = con.cursor()
    
    query = """
        SELECT 
            id, account_type, entity_identifier, account_name,
            account_number, bank_name, account_holder, is_active, created_at
        FROM payment_accounts
        WHERE account_type = ?
    """
    params = [account_type]
    
    if active_only:
        query += " AND is_active = 1"
    
    query += " ORDER BY created_at DESC"
    
    cur.execute(query, params)
    rows = cur.fetchall()
    con.close()
    
    return [dict(row) for row in rows]


def create_account(
    account_type: str,
    entity_identifier: str,
    account_name: str,
    account_number: str = None,
    bank_name: str = "RUPALI BANK",
    account_holder: str = None
) -> Optional[int]:
    """
    Create a new account in the unified table.
    
    Args:
        account_type: 'hall', 'library', or 'department'
        entity_identifier: Hall name, 'library', or dept_code
        account_name: Display name for the account
        account_number: Bank account number (optional)
        bank_name: Bank name (default: RUPALI BANK)
        account_holder: Account holder name (optional)
        
    Returns:
        New account ID or None if failed
        
    Example:
        account_id = create_account(
            account_type='hall',
            entity_identifier='New Hall',
            account_name='New Hall Account',
            account_number='123456789',
            account_holder='Hall Manager'
        )
    """
    if account_type not in ['hall', 'library', 'department']:
        raise ValueError("account_type must be 'hall', 'library', or 'department'")
    
    if not all([account_type, entity_identifier, account_name]):
        raise ValueError("account_type, entity_identifier, and account_name are required")
    
    con = _get_db()
    cur = con.cursor()
    
    try:
        cur.execute("""
            INSERT INTO payment_accounts 
            (account_type, entity_identifier, account_name, account_number, bank_name, account_holder, is_active)
            VALUES (?, ?, ?, ?, ?, ?, 1)
        """, (account_type, entity_identifier, account_name, account_number, bank_name, account_holder))
        
        con.commit()
        account_id = cur.lastrowid
        con.close()
        return account_id
        
    except sqlite3.IntegrityError as e:
        con.close()
        print(f"Error: Duplicate account for {account_type} - {entity_identifier}")
        return None


def update_account(account_id: int, **kwargs) -> bool:
    """
    Update an existing account.
    
    Args:
        account_id: The account ID to update
        **kwargs: Fields to update (account_name, account_number, account_holder, bank_name, is_active)
        
    Returns:
        True if successful, False otherwise
        
    Example:
        update_account(5, account_number='987654321', account_holder='New Manager')
        update_account(5, is_active=0)  # Deactivate
    """
    allowed_fields = {'account_name', 'account_number', 'account_holder', 'bank_name', 'is_active'}
    update_fields = {k: v for k, v in kwargs.items() if k in allowed_fields}
    
    if not update_fields:
        return False
    
    con = _get_db()
    cur = con.cursor()
    
    try:
        set_clause = ", ".join([f"{k} = ?" for k in update_fields.keys()])
        values = list(update_fields.values()) + [account_id]
        
        cur.execute(f"""
            UPDATE payment_accounts
            SET {set_clause}
            WHERE id = ?
        """, values)
        
        con.commit()
        con.close()
        return True
        
    except Exception as e:
        con.close()
        print(f"Error updating account: {e}")
        return False


def deactivate_account(account_id: int) -> bool:
    """
    Deactivate an account.
    
    Args:
        account_id: The account ID to deactivate
        
    Returns:
        True if successful, False otherwise
    """
    return update_account(account_id, is_active=0)


def activate_account(account_id: int) -> bool:
    """
    Activate an account.
    
    Args:
        account_id: The account ID to activate
        
    Returns:
        True if successful, False otherwise
    """
    return update_account(account_id, is_active=1)


def get_accounts_stats() -> Dict:
    """
    Get statistics about accounts in the system.
    
    Returns:
        Dictionary with statistics
        
    Example:
        stats = get_accounts_stats()
        print(f"Total: {stats['total']}")
        print(f"Hall Accounts: {stats['by_type']['hall']}")
    """
    con = _get_db()
    cur = con.cursor()
    
    # Total accounts
    cur.execute("SELECT COUNT(*) as count FROM payment_accounts")
    total = cur.fetchone()['count']
    
    # Active accounts
    cur.execute("SELECT COUNT(*) as count FROM payment_accounts WHERE is_active = 1")
    active = cur.fetchone()['count']
    
    # By type
    cur.execute("""
        SELECT account_type, COUNT(*) as count
        FROM payment_accounts
        GROUP BY account_type
    """)
    by_type = {row['account_type']: row['count'] for row in cur.fetchall()}
    
    # Active by type
    cur.execute("""
        SELECT account_type, COUNT(*) as count
        FROM payment_accounts
        WHERE is_active = 1
        GROUP BY account_type
    """)
    active_by_type = {row['account_type']: row['count'] for row in cur.fetchall()}
    
    con.close()
    
    return {
        'total': total,
        'active': active,
        'inactive': total - active,
        'by_type': by_type,
        'active_by_type': active_by_type
    }


# Convenience functions for common queries

def get_student_account_info(student_dept: str) -> Optional[Dict]:
    """
    Get formatted account info for student's department fees.
    
    Args:
        student_dept: Department code
        
    Returns:
        Formatted account info or None
    """
    account = get_account_for_student(student_dept)
    if not account:
        return None
    
    return {
        'type': 'department',
        'name': account['account_name'],
        'number': account['account_number'],
        'bank': account['bank_name'],
        'holder': account.get('account_holder', 'N/A'),
        'entity_id': account['entity_identifier']
    }


def get_hall_payment_info(hall_name: str) -> Optional[Dict]:
    """
    Get formatted account info for hall fees.
    
    Args:
        hall_name: Hall name
        
    Returns:
        Formatted account info or None
    """
    account = get_hall_account(hall_name)
    if not account:
        return None
    
    return {
        'type': 'hall',
        'name': account['account_name'],
        'number': account['account_number'],
        'bank': account['bank_name'],
        'holder': account.get('account_holder', 'N/A'),
        'entity_id': account['entity_identifier']
    }


def get_library_payment_info() -> Optional[Dict]:
    """
    Get formatted account info for library fines.
    
    Returns:
        Formatted account info or None
    """
    account = get_library_account()
    if not account:
        return None
    
    return {
        'type': 'library',
        'name': account['account_name'],
        'number': account['account_number'],
        'bank': account['bank_name'],
        'holder': account.get('account_holder', 'Library'),
        'entity_id': account['entity_identifier']
    }


if __name__ == "__main__":
    # Test functions and display examples
    print("=" * 70)
    print("UNIFIED ACCOUNTS MANAGER - USAGE EXAMPLES")
    print("=" * 70)
    
    print("\n1. Get Department Account for Student:")
    account = get_account_for_student('03')
    if account:
        print(f"   Account: {account['account_name']}")
        print(f"   Number: {account['account_number']}")
        print(f"   Bank: {account['bank_name']}")
    
    print("\n2. Get All Hall Accounts:")
    halls = get_all_hall_accounts()
    print(f"   Found {len(halls)} halls")
    for hall in halls[:3]:  # Show first 3
        print(f"   - {hall['entity_identifier']}: {hall['account_number']}")
    
    print("\n3. Get Library Account:")
    lib = get_library_account()
    if lib:
        print(f"   Account: {lib['account_name']}")
        print(f"   Number: {lib['account_number']}")
    
    print("\n4. Get Account Statistics:")
    stats = get_accounts_stats()
    print(f"   Total: {stats['total']}")
    print(f"   Active: {stats['active']}")
    print(f"   By Type: {stats['by_type']}")
    
    print("\n✅ All examples completed successfully!")
