from database import get_connection, init_db

def seed():
    init_db()

    conn = get_connection()
    cursor = conn.cursor()

    # Limpiar datos antes de insertar
    cursor.execute("DELETE FROM messages")
    cursor.execute("DELETE FROM tickets")
    cursor.execute("DELETE FROM users")
    cursor.execute("DELETE FROM sqlite_sequence")

    # INSERT — agregar usuarios
    cursor.executemany("""
        INSERT OR IGNORE INTO users (name, email, role) VALUES (?, ?, ?)
    """, [
        ("Ramon Valentin", "ramon@abbvie.com", "technician"),
        ("Maria Gonzalez", "maria@abbvie.com", "user"),
        ("Carlos Reyes", "carlos@abbvie.com", "user"),
    ])

    # INSERT — agregar tickets
    cursor.executemany("""
        INSERT OR IGNORE INTO tickets (title, description, priority, status, user_id)
        VALUES (?, ?, ?, ?, ?)
    """, [
        ("Cannot access Outlook after PC refresh", "User reports Outlook fails to open after PC refresh.", "high", "open", 2),
        ("HP Printer not responding in MCN", "Printer offline in manufacturing floor.", "medium", "open", 3),
        ("Password reset - Active Directory", "User locked out of AD account.", "low", "resolved", 2),
        ("VPN not connecting on GETAC laptop", "VPN client times out on rugged laptop.", "medium", "pending", 3),
    ])

    conn.commit()

    # READ - ver todos los tickets abiertos
    print("\n--- Tickets abiertos ---")
    cursor.execute("SELECT id, title, priority, status FROM tickets WHERE status = 'open'")
    rows = cursor.fetchall()
    for row in rows:
        print(f"ID: {row['id']} | {row['title']} | {row['priority']} | {row['status']}")

    # READ - contar tickets por status
    print("\n--- Tickets por status ---")
    cursor.execute("SELECT status, COUNT(*) as total FROM tickets GROUP BY status")
    rows = cursor.fetchall()
    for row in rows:
        print(f"{row['status']}: {row['total']} tickets")

    conn.close()
    print("Database seeded successfully!")

if __name__ == "__main__":
    seed()