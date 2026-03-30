from flask import Flask, render_template, request, session, redirect, url_for, jsonify
import mysql.connector
import time
import sys
import os

# ── AI Matching Engine (Custom Neural Network) ──
# Ensure Backend/ directory is in path for imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
try:
    from ai_model import get_ai_matches
except ImportError:
    # Fallback if ai_model.py is not in the same folder
    def get_ai_matches(curr, others): return []

app = Flask(__name__)
app.secret_key = "secretkey123"


# ──────────────────────────────────────────
# Database
# ──────────────────────────────────────────
def get_db():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="root@123",
        database="synergai"
    )


# ──────────────────────────────────────────
# Routes
# ──────────────────────────────────────────

@app.route("/")
def home():
    return render_template("login.html")


@app.route("/create_profile")
def create_profile():
    return render_template("create_profile.html")


# ── Save profile (AJAX / JSON) ───────────
@app.route("/save_profile", methods=["POST"])
def save_profile():
    data = request.get_json()
    session["profile_data"] = {
        "name":         data.get("name"),
        "university":   data.get("university"),
        "skills":       data.get("skills"),
        "interests":    data.get("interests"),
        "role":         data.get("role"),
        "availability": data.get("availability")
    }
    return jsonify({"status": "success"})


# ── Save account (form POST) ─────────────
@app.route("/save_account", methods=["POST"])
def save_account():
    profile = session.get("profile_data")
    if not profile:
        return redirect(url_for("create_profile"))

    email    = request.form["email"]
    password = request.form["password"]

    db = get_db()
    cursor = db.cursor(buffered=True)
    query = """
    INSERT INTO users 
    (name, university, skills, interests, role, availability, email, password) 
    VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
    """
    values = (
        profile["name"], profile["university"], profile["skills"],
        profile["interests"], profile["role"], profile["availability"],
        email, password
    )
    cursor.execute(query, values)
    db.commit()
    cursor.close()
    db.close()

    session.pop("profile_data", None)
    return redirect(url_for("home"))


# ── Login ─────────────────────────────────
@app.route("/login", methods=["POST"])
def login():
    email    = request.form["email"]
    password = request.form["password"]

    db = get_db()
    cursor = db.cursor(buffered=True)
    query = "SELECT * FROM users WHERE email=%s AND password=%s"
    cursor.execute(query, (email, password))
    user = cursor.fetchone()
    cursor.close()
    db.close()

    if user:
        session["user_id"] = user[0]
        return redirect(url_for("dashboard"))
    else:
        return render_template("login.html", error="Invalid email or password.")


# ── Dashboard ─────────────────────────────
@app.route("/dashboard")
def dashboard():
    if "user_id" not in session:
        return redirect(url_for("home"))

    db = get_db()
    cursor = db.cursor(dictionary=True, buffered=True)

    cursor.execute("SELECT * FROM users WHERE id=%s", (session["user_id"],))
    current_user = cursor.fetchone()

    if not current_user:
        cursor.close()
        db.close()
        session.clear()
        return redirect(url_for("home"))

    cursor.close()
    db.close()

    return render_template("dashboard.html", user=current_user)


# ── API: AI-Powered Matching ─────────────
@app.route("/api/matches")
def api_matches():
    """Run the AI matching engine and return results as JSON."""

    if "user_id" not in session:
        return jsonify({"error": "Not logged in"}), 401

    db = get_db()
    cursor = db.cursor(dictionary=True, buffered=True)

    cursor.execute("SELECT * FROM users WHERE id=%s", (session["user_id"],))
    current_user = cursor.fetchone()

    if not current_user:
        cursor.close()
        db.close()
        return jsonify({"matches": [], "fallback": True})

    # Exclude the current user AND anyone they already have an invite/connection with
    query = """
    SELECT u.* FROM users u
    WHERE u.id != %s
    AND u.id NOT IN (
        SELECT receiver_id FROM invites WHERE sender_id = %s
        UNION
        SELECT sender_id FROM invites WHERE receiver_id = %s
    )
    """
    cursor.execute(query, (session["user_id"], session["user_id"], session["user_id"]))
    other_users = cursor.fetchall()
    cursor.close()
    db.close()

    # If no other users exist, return example fallback
    if not other_users:
        time.sleep(1.5)
        return jsonify({
            "fallback": True,
            "matches": [
                {
                    "name": "Riya Gupta",
                    "skills": "React, UI Design, Frontend",
                    "score": 92,
                    "role": "Frontend Developer"
                },
                {
                    "name": "Arjun Mehta",
                    "skills": "Python, Machine Learning, Data",
                    "score": 85,
                    "role": "ML Engineer"
                }
            ]
        })

    # ── Run neural AI matching ──
    matches = get_ai_matches(current_user, other_users)

    # Small delay so frontend animation feels natural
    time.sleep(1.2)

    return jsonify({
        "fallback": False,
        "matches": matches[:2],
        "engine": "Neural Team Complementarity Model"
    })


# ── My Matches ────────────────────────────
@app.route("/my_matches")
def my_matches():
    if "user_id" not in session:
        return redirect(url_for("home"))

    db = get_db()
    cursor = db.cursor(dictionary=True, buffered=True)
    
    # Fetch current user
    cursor.execute("SELECT * FROM users WHERE id=%s", (session["user_id"],))
    user = cursor.fetchone()
    
    # Fetch ONLY accepted matches
    query = """
    SELECT u.* FROM users u
    JOIN invites i ON (i.sender_id = u.id OR i.receiver_id = u.id)
    WHERE (i.sender_id = %s OR i.receiver_id = %s)
    AND i.status = 'accepted'
    AND u.id != %s
    """
    cursor.execute(query, (session["user_id"], session["user_id"], session["user_id"]))
    matches = cursor.fetchall()
    
    cursor.close()
    db.close()
    
    return render_template("my_matches.html", user=user, matches=matches)

# ── API: Persistent Invites & Chat ───────

@app.route("/api/user_state")
def api_user_state():
    if "user_id" not in session:
        return jsonify({"error": "Not logged in"}), 401
    
    uid = session["user_id"]
    db = get_db()
    cursor = db.cursor(dictionary=True, buffered=True)
    
    # 1. Fetch Inbound Pending Invites
    cursor.execute("""
        SELECT u.id, u.name, u.role, u.skills, u.university, u.interests, u.availability
        FROM users u
        JOIN invites i ON i.sender_id = u.id
        WHERE i.receiver_id = %s AND i.status = 'pending'
    """, (uid,))
    pending_inbound = cursor.fetchall()
    
    # 2. Fetch Active Teammates
    cursor.execute("""
        SELECT u.id, u.name, u.role, u.skills, u.university, u.interests, u.availability
        FROM users u
        JOIN invites i ON (i.sender_id = u.id OR i.receiver_id = u.id)
        WHERE (i.sender_id = %s OR i.receiver_id = %s) 
          AND i.status = 'accepted'
          AND u.id != %s
    """, (uid, uid, uid))
    teammates = cursor.fetchall()
    
    cursor.close()
    db.close()
    
    return jsonify({
        "pending_inbound": pending_inbound,
        "teammates": teammates
    })

@app.route("/api/invite", methods=["POST"])
def api_send_invite():
    if "user_id" not in session: return jsonify({"error": "Not logged in"}), 401
    
    data = request.get_json()
    receiver_id = data.get("receiver_id")
    
    db = get_db()
    cursor = db.cursor()
    cursor.execute("""
        INSERT INTO invites (sender_id, receiver_id, status)
        VALUES (%s, %s, 'pending')
    """, (session["user_id"], receiver_id))
    db.commit()
    cursor.close()
    db.close()
    
    return jsonify({"success": True})

@app.route("/api/invite/respond", methods=["POST"])
def api_respond_invite():
    if "user_id" not in session: return jsonify({"error": "Not logged in"}), 401
    
    data = request.get_json()
    sender_id = data.get("sender_id")
    status = data.get("status") # 'accepted' or 'rejected'
    
    db = get_db()
    cursor = db.cursor()
    cursor.execute("""
        UPDATE invites 
        SET status = %s 
        WHERE sender_id = %s AND receiver_id = %s AND status = 'pending'
    """, (status, sender_id, session["user_id"]))
    db.commit()
    cursor.close()
    db.close()
    
    return jsonify({"success": True})

@app.route("/api/messages/<int:teammate_id>")
def api_get_messages(teammate_id):
    if "user_id" not in session: return jsonify({"error": "Not logged in"}), 401
    uid = session["user_id"]
    
    db = get_db()
    cursor = db.cursor(dictionary=True)
    cursor.execute("""
        SELECT * FROM messages
        WHERE (sender_id = %s AND receiver_id = %s)
           OR (sender_id = %s AND receiver_id = %s)
        ORDER BY timestamp ASC
    """, (uid, teammate_id, teammate_id, uid))
    messages = cursor.fetchall()
    cursor.close()
    db.close()
    
    return jsonify(messages)

@app.route("/api/messages", methods=["POST"])
def api_send_message():
    if "user_id" not in session: return jsonify({"error": "Not logged in"}), 401
    uid = session["user_id"]
    
    data = request.get_json()
    receiver_id = data.get("receiver_id")
    text = data.get("text")
    
    db = get_db()
    cursor = db.cursor()
    cursor.execute("""
        INSERT INTO messages (sender_id, receiver_id, text)
        VALUES (%s, %s, %s)
    """, (uid, receiver_id, text))
    db.commit()
    cursor.close()
    db.close()
    
    return jsonify({"success": True})

# ──────────────────────────────────────────
if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)
