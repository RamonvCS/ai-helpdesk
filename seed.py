from database import get_connection, init_db

def seed():
    init_db()
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("DELETE FROM comments")
    cursor.execute("DELETE FROM messages")
    cursor.execute("DELETE FROM assets")
    cursor.execute("DELETE FROM tickets")
    cursor.execute("DELETE FROM users")
    cursor.execute("DELETE FROM sqlite_sequence")

    cursor.executemany("""
        INSERT INTO users (name, email, role, department, employee_id, reports_to, phone_ext)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, [
        ("Ramon Valentin", "ramon@novatech.com", "technician", "IT Support", "EMP-001", "John Smith", "x4400"),
        ("Maria Gonzalez", "maria@novatech.com", "user", "Finance", "EMP-002", "Carlos Rivera", "x4421"),
        ("Carlos Reyes", "carlos@novatech.com", "user", "Manufacturing", "EMP-003", "Ana Torres", "x4388"),
    ])

    cursor.executemany("""
        INSERT INTO tickets (title, description, priority, status, category, user_id, assigned_to)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, [
        ("Cannot access Outlook after PC refresh", "User reports Outlook fails to open after PC refresh. Error message appears briefly then disappears.", "high", "open", "Email / O365", 2, "Ramon Valentin"),
        ("HP Printer not responding in MCN", "Printer offline in manufacturing floor. Users cannot print batch records.", "medium", "open", "Printers", 3, "Ramon Valentin"),
        ("Password reset - Active Directory", "User locked out of AD account after multiple failed attempts.", "low", "resolved", "Access Management", 2, "Ramon Valentin"),
        ("VPN not connecting on GETAC laptop", "VPN client times out on rugged laptop. Issue started after Windows update.", "medium", "pending", "Network / VPN", 3, "Ramon Valentin"),
    ])

    cursor.executemany("""
        INSERT INTO assets (user_id, name, type, service_tag, status)
        VALUES (?, ?, ?, ?, ?)
    """, [
        (1, "Dell Latitude 5540", "Laptop", "DL5540-RV-001", "active"),
        (2, "Dell Latitude 5540", "Laptop", "DL5540-AV-2891", "active"),
        (2, "HP Docking Station G5", "Peripheral", "HPDG5-0442", "active"),
        (3, "GETAC B360", "Rugged Laptop", "GETAC-MCN-014", "active"),
        (3, "HP LaserJet M428", "Printer", "HPLJ-MCN-007", "inactive"),
    ])

    cursor.executemany("""
        INSERT INTO comments (ticket_id, author, content)
        VALUES (?, ?, ?)
    """, [
        (1, "Ramon Valentin", "Contacted user via phone. Confirmed error appears on Outlook launch. Running Azure AD sync check now."),
        (1, "Jose Martinez", "Checked with L3 — might be related to the O365 license migration last night. Check if her account was affected."),
    ])

    conn.commit()
    conn.close()
    print("Database seeded successfully!")

if __name__ == "__main__":
    seed()