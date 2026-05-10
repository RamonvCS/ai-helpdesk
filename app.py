from flask import Flask, render_template, request, jsonify
from dotenv import load_dotenv
from database import get_connection, init_db
from groq import Groq
import os

load_dotenv()

app = Flask(__name__)
init_db()

client = Groq(api_key=os.getenv("GROQ_API_KEY"))

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/api/tickets", methods=["GET"])
def get_tickets():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT t.id, t.title, t.description, t.priority, t.status,
               t.created_at, u.name as user_name
        FROM tickets t
        LEFT JOIN users u ON t.user_id = u.id
        ORDER BY t.created_at DESC
    """)
    tickets = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return jsonify(tickets)

@app.route("/api/tickets/<int:ticket_id>", methods=["GET"])
def get_ticket(ticket_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT t.*, u.name as user_name, u.email as user_email,
               u.role as user_role, u.department as user_department,
               u.employee_id as user_employee_id, u.reports_to as user_reports_to,
               u.phone_ext as user_phone_ext,
               (SELECT COUNT(*) FROM tickets WHERE user_id = t.user_id) as user_ticket_count
        FROM tickets t
        LEFT JOIN users u ON t.user_id = u.id
        WHERE t.id = ?
    """, (ticket_id,))
    row = cursor.fetchone()
    if not row:
        conn.close()
        return jsonify({"error": "Ticket not found"}), 404
    ticket = dict(row)

    cursor.execute("""
        SELECT name, type, service_tag, status
        FROM assets WHERE user_id = ?
    """, (ticket['user_id'],))
    ticket['assets'] = [dict(a) for a in cursor.fetchall()]
    conn.close()
    return jsonify(ticket)

@app.route("/api/tickets/<int:ticket_id>/status", methods=["PUT"])
def update_status(ticket_id):
    data = request.get_json()
    new_status = data.get("status")
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        UPDATE tickets SET status = ?, updated_at = CURRENT_TIMESTAMP
        WHERE id = ?
    """, (new_status, ticket_id))
    conn.commit()
    conn.close()
    return jsonify({"message": "Status updated"})

@app.route("/api/tickets/<int:ticket_id>/chat", methods=["POST"])
def chat(ticket_id):
    data = request.get_json()
    user_message = data.get("message", "")
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM tickets WHERE id = ?", (ticket_id,))
    ticket = dict(cursor.fetchone())
    cursor.execute("""
        SELECT role, content FROM messages
        WHERE ticket_id = ? ORDER BY created_at ASC
    """, (ticket_id,))
    history = cursor.fetchall()
    cursor.execute("""
        INSERT INTO messages (ticket_id, role, content)
        VALUES (?, 'user', ?)
    """, (ticket_id, user_message))
    conn.commit()
    messages = [{"role":"system","content":f"""You are an expert IT helpdesk assistant at NovaTech Solutions
Ticket #{ticket_id}: "{ticket['title']}"
Description: {ticket['description']}
Priority: {ticket['priority']} | Status: {ticket['status']}
Give concise, technical, actionable advice. Max 150 words."""}]
    for msg in history:
        messages.append({"role": msg["role"] if msg["role"]=="user" else "assistant","content": msg["content"]})
    messages.append({"role":"user","content":user_message})
    response = client.chat.completions.create(model="llama-3.3-70b-versatile",messages=messages,max_tokens=300)
    ai_response = response.choices[0].message.content
    cursor.execute("INSERT INTO messages (ticket_id, role, content) VALUES (?, 'assistant', ?)",(ticket_id, ai_response))
    conn.commit()
    conn.close()
    return jsonify({"response": ai_response})

@app.route("/api/tickets/<int:ticket_id>/messages", methods=["GET"])
def get_messages(ticket_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT role, content, created_at FROM messages WHERE ticket_id = ? ORDER BY created_at ASC",(ticket_id,))
    messages = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return jsonify(messages)

@app.route("/api/tickets/<int:ticket_id>/comments", methods=["GET"])
def get_comments(ticket_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM comments WHERE ticket_id = ? ORDER BY created_at ASC",(ticket_id,))
    comments = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return jsonify(comments)

@app.route("/api/tickets/<int:ticket_id>/comments", methods=["POST"])
def add_comment(ticket_id):
    data = request.get_json()
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO comments (ticket_id, author, content) VALUES (?, ?, ?)",(ticket_id, data.get("author","Ramon Valentin"), data["content"]))
    conn.commit()
    conn.close()
    return jsonify({"message": "Comment added"}), 201

@app.route("/api/users", methods=["GET"])
def get_users():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT u.id, u.name, u.email, u.role, u.created_at,
               COUNT(t.id) as ticket_count
        FROM users u
        LEFT JOIN tickets t ON t.user_id = u.id
        GROUP BY u.id
        ORDER BY u.created_at DESC
    """)
    users = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return jsonify(users)

@app.route("/api/users", methods=["POST"])
def create_user():
    data = request.get_json()
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("INSERT INTO users (name, email, role) VALUES (?, ?, ?)",(data["name"], data["email"], data.get("role","user")))
        conn.commit()
        user_id = cursor.lastrowid
        conn.close()
        return jsonify({"id": user_id, "message": "User created"}), 201
    except Exception as e:
        conn.close()
        return jsonify({"error": str(e)}), 400

@app.route("/api/users/<int:user_id>", methods=["DELETE"])
def delete_user(user_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM users WHERE id = ?", (user_id,))
    conn.commit()
    conn.close()
    return jsonify({"message": "User deleted"})

@app.route("/seed")
def run_seed():
    from seed import seed
    seed()
    return jsonify({"message": "Database seeded!"})

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=False)