from flask import Flask, render_template, request, session, redirect, url_for
import mysql.connector


app = Flask(__name__)
app.secret_key = "secretkey123"

# MySQL connection
db = mysql.connector.connect(
    host="localhost",
    user="root",
    password="root@123",
    database="synergai"
)

cursor = db.cursor(buffered=True)

@app.route("/")
def home():
    return render_template("login.html")


@app.route("/create_profile")
def create_profile():
    return render_template("create_profile.html")


@app.route("/save_profile", methods=["POST"])
def save_profile():

    session["profile"] = {
        "name": request.form["name"],
        "university": request.form["university"],
        "skills": request.form["skills"],
        "interests": request.form["interests"],
        "role": request.form["role"],
        "availability": request.form["availability"]
    }

    return render_template("create_account.html")

@app.route("/users")
def users():

    cursor.execute("SELECT * FROM users")

    data = cursor.fetchall()

    return render_template("users.html", users=data)


@app.route("/save_account", methods=["POST"])
def save_account():

    profile = session["profile"]

    email = request.form["email"]
    password = request.form["password"]

    query = """
    INSERT INTO users
    (name, university, skills, interests, role, availability, email, password)
    VALUES (%s,%s,%s,%s,%s,%s,%s,%s)
    """

    values = (
        profile["name"],
        profile["university"],
        profile["skills"],
        profile["interests"],
        profile["role"],
        profile["availability"],
        email,
        password
    )

    cursor.execute(query, values)
    db.commit()

    return redirect(url_for("home"))

@app.route("/login", methods=["POST"])
def login():

    email = request.form["email"]
    password = request.form["password"]

    query = "SELECT * FROM users WHERE email=%s AND password=%s"

    cursor.execute(query,(email,password))

    user = cursor.fetchone()

    if user:
        session["user"] = user[0]   # store user id
        return redirect(url_for("dashboard"))

    else:
        return "Invalid Credentials"

@app.route("/dashboard")
def dashboard():

    if "user" not in session:
        return redirect(url_for("home"))

    query = "SELECT * FROM users WHERE id=%s"

    cursor.execute(query,(session["user"],))

    user = cursor.fetchone()

    return render_template("dashboard.html", user=user)



if __name__ == "__main__":
    app.run(debug=True)
