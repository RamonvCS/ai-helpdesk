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

@app.route("/api/tickets", methods=["POST"])
def create_ticket():
    data = request.get_json()
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO tickets (title, description, priority, status, user_id)
        VALUES (?, ?, ?, 'open', 1)
    """, (data["title"], data["description"], data.get("priority", "medium")))
    conn.commit()
    ticket_id = cursor.lastrowid
    conn.close()
    return jsonify({"id": ticket_id, "message": "Ticket created"}), 201

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

    messages = [
        {
            "role": "system",
            "content": f"""You are an expert IT helpdesk assistant at a pharmaceutical company (AbbVie).
Ticket #{ticket_id}: "{ticket['title']}"
Description: {ticket['description']}
Priority: {ticket['priority']} | Status: {ticket['status']}
Give concise, technical, actionable advice. Max 150 words."""
        }
    ]

    for msg in history:
        messages.append({
            "role": msg["role"] if msg["role"] == "user" else "assistant",
            "content": msg["content"]
        })

    messages.append({"role": "user", "content": user_message})

    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=messages,
        max_tokens=300
    )

    ai_response = response.choices[0].message.content

    cursor.execute("""
        INSERT INTO messages (ticket_id, role, content)
        VALUES (?, 'assistant', ?)
    """, (ticket_id, ai_response))
    conn.commit()
    conn.close()

    return jsonify({"response": ai_response})

@app.route("/api/tickets/<int:ticket_id>/messages", methods=["GET"])
def get_messages(ticket_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT role, content, created_at FROM messages
        WHERE ticket_id = ? ORDER BY created_at ASC
    """, (ticket_id,))
    messages = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return jsonify(messages)

if __name__ == "__main__":
    app.run(debug=True)