import os
from database import get_connection, init_db, is_postgres

def seed():
    init_db()
    conn = get_connection()
    cursor = conn.cursor()

    if is_postgres():
        cursor.execute("TRUNCATE comments, messages, assets, tickets, users RESTART IDENTITY CASCADE")
    else:
        cursor.execute("DELETE FROM comments")
        cursor.execute("DELETE FROM messages")
        cursor.execute("DELETE FROM assets")
        cursor.execute("DELETE FROM tickets")
        cursor.execute("DELETE FROM users")
        cursor.execute("DELETE FROM sqlite_sequence")

    users = [
        ("Ramon Valentin", "ramon@novatech.com", "technician", "IT Support", "EMP-001", "John Smith", "x4400"),
        ("Maria Gonzalez", "maria@novatech.com", "user", "Finance", "EMP-002", "Carlos Rivera", "x4421"),
        ("Carlos Reyes", "carlos@novatech.com", "user", "Manufacturing", "EMP-003", "Ana Torres", "x4388"),
    ]

    for u in users:
        if is_postgres():
            cursor.execute("""
                INSERT INTO users (name, email, role, department, employee_id, reports_to, phone_ext)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
            """, u)
        else:
            cursor.execute("""
                INSERT INTO users (name, email, role, department, employee_id, reports_to, phone_ext)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, u)

    tickets = [
        ("Cannot access Outlook after PC refresh", "User reports Outlook fails to open after PC refresh.", "high", "open", "Email / O365", 2, "Ramon Valentin"),
        ("HP Printer not responding in MCN", "Printer offline in manufacturing floor.", "medium", "open", "Printers", 3, "Ramon Valentin"),
        ("Password reset - Active Directory", "User locked out of AD account.", "low", "resolved", "Access Management", 2, "Ramon Valentin"),
        ("VPN not connecting on GETAC laptop", "VPN client times out after Windows update.", "medium", "pending", "Network / VPN", 3, "Ramon Valentin"),
    ]

    for t in tickets:
        if is_postgres():
            cursor.execute("""
                INSERT INTO tickets (title, description, priority, status, category, user_id, assigned_to)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
            """, t)
        else:
            cursor.execute("""
                INSERT INTO tickets (title, description, priority, status, category, user_id, assigned_to)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, t)

    assets = [
        (1, "Dell Latitude 5540", "Laptop", "DL5540-RV-001", "active"),
        (2, "Dell Latitude 5540", "Laptop", "DL5540-AV-2891", "active"),
        (2, "HP Docking Station G5", "Peripheral", "HPDG5-0442", "active"),
        (3, "GETAC B360", "Rugged Laptop", "GETAC-MCN-014", "active"),
        (3, "HP LaserJet M428", "Printer", "HPLJ-MCN-007", "inactive"),
    ]

    for a in assets:
        if is_postgres():
            cursor.execute("""
                INSERT INTO assets (user_id, name, type, service_tag, status)
                VALUES (%s, %s, %s, %s, %s)
            """, a)
        else:
            cursor.execute("""
                INSERT INTO assets (user_id, name, type, service_tag, status)
                VALUES (?, ?, ?, ?, ?)
            """, a)

    comments = [
        (1, "Ramon Valentin", "Contacted user via phone. Running Azure AD sync check now."),
        (1, "Jose Martinez", "Might be related to the O365 license migration last night."),
    ]

    for c in comments:
        if is_postgres():
            cursor.execute("""
                INSERT INTO comments (ticket_id, author, content)
                VALUES (%s, %s, %s)
            """, c)
        else:
            cursor.execute("""
                INSERT INTO comments (ticket_id, author, content)
                VALUES (?, ?, ?)
            """, c)

    conn.commit()
    conn.close()
    print("Database seeded successfully!")

if __name__ == "__main__":
    seed()