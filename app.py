from flask import Flask, render_template, request, jsonify
from dotenv import load_dotenv
from database import get_connection, init_db
import os

load_dotenv()

app = Flask(__name__)
init_db()

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
    return jsonify({"id": ticket_id, "message": "Ticket created successfully"}), 201

if __name__ == "__main__":
    app.run(debug=True)