import sqlite3

con = sqlite3.connect('database/ruet.db')
cur = con.cursor()

print('=== DATABASE STATISTICS ===\n')

# Count students
cur.execute("SELECT COUNT(*) as cnt FROM students")
print(f'Students: {cur.fetchone()[0]}')

# Count halls
cur.execute("SELECT COUNT(*) as cnt FROM halls")
print(f'Halls: {cur.fetchone()[0]}')

# Count rooms
cur.execute("SELECT COUNT(*) as cnt FROM rooms")
print(f'Rooms: {cur.fetchone()[0]}')

# Count allocations
cur.execute("SELECT COUNT(*) as cnt FROM room_allocations")
print(f'Room Allocations: {cur.fetchone()[0]}')

# Show halls
print('\n=== HALLS ===')
cur.execute("SELECT id, email, hall_name FROM halls LIMIT 10")
for row in cur.fetchall():
    print(f'  {row[1]:40s} -> {row[2]}')

# Show allocations
print('\n=== ROOM ALLOCATIONS ===')
cur.execute("SELECT COUNT(*) as cnt FROM room_allocations")
allocation_count = cur.fetchone()[0]
print(f'Total allocations: {allocation_count}')

if allocation_count > 0:
    cur.execute('''
        SELECT ra.id, h.hall_name, r.room_number, s.id as student_id
        FROM room_allocations ra
        JOIN halls h ON ra.hall_id = h.id
        JOIN rooms r ON ra.room_id = r.id  
        JOIN students s ON ra.student_id = s.id
        LIMIT 5
    ''')
    for row in cur.fetchall():
        print(f'  Allocation {row[0]}: Hall={row[1]}, Room={row[2]}, Student={row[3]}')

con.close()
