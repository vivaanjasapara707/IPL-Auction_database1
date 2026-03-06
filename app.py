from flask import Flask, render_template, request, redirect, session
import sqlite3
import pandas as pd

app = Flask(__name__)
app.secret_key = "iplauctionsecret"


# ---------- LOAD PLAYERS FROM EXCEL ----------
def load_players():
    conn = sqlite3.connect("players.db")
    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS players(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT,
        country TEXT,
        role TEXT,
        base_price INTEGER,
        current_bid INTEGER
    )
    """)

    cursor.execute("SELECT COUNT(*) FROM players")
    count = cursor.fetchone()[0]

    if count == 0:
        df = pd.read_excel("players.xlsx")

        for _, row in df.iterrows():
            cursor.execute("""
            INSERT INTO players(name,country,role,base_price,current_bid)
            VALUES(?,?,?,?,?)
            """,(
                row["Player"],
                row["Country"],
                row["Role"],
                row["Base Price"],
                row["Base Price"]
            ))

        conn.commit()

    conn.close()


# ---------- CREATE USERS TABLE ----------
def create_users():
    conn = sqlite3.connect("players.db")
    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS users(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT,
        password TEXT
    )
    """)

    conn.commit()
    conn.close()


load_players()
create_users()


# ---------- HOME ----------
@app.route("/")
def home():

    if "user" not in session:
        return redirect("/login")

    conn = sqlite3.connect("players.db")
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM players")
    players = cursor.fetchall()

    conn.close()

    return render_template("index.html", players=players, user=session["user"])


# ---------- ROLE FILTER ----------
@app.route("/role/<role>")
def role(role):

    if "user" not in session:
        return redirect("/login")

    conn = sqlite3.connect("players.db")
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM players WHERE role=?", (role,))
    players = cursor.fetchall()

    conn.close()

    return render_template("index.html", players=players, user=session["user"])


# ---------- BID ----------
@app.route("/bid/<int:id>", methods=["POST"])
def bid(id):

    bid = int(request.form["bid"])

    conn = sqlite3.connect("players.db")
    cursor = conn.cursor()

    cursor.execute("UPDATE players SET current_bid=? WHERE id=?", (bid, id))

    conn.commit()
    conn.close()

    return redirect("/")


# ---------- REGISTER ----------
@app.route("/register", methods=["GET","POST"])
def register():

    if request.method == "POST":

        username = request.form["username"]
        password = request.form["password"]

        conn = sqlite3.connect("players.db")
        cursor = conn.cursor()

        cursor.execute(
            "INSERT INTO users(username,password) VALUES(?,?)",
            (username,password)
        )

        conn.commit()
        conn.close()

        return redirect("/login")

    return render_template("register.html")


# ---------- LOGIN ----------
@app.route("/login", methods=["GET","POST"])
def login():

    if request.method == "POST":

        username = request.form["username"]
        password = request.form["password"]

        conn = sqlite3.connect("players.db")
        cursor = conn.cursor()

        cursor.execute(
            "SELECT * FROM users WHERE username=? AND password=?",
            (username,password)
        )

        user = cursor.fetchone()
        conn.close()

        if user:
            session["user"] = username
            return redirect("/")

    return render_template("login.html")


# ---------- LOGOUT ----------
@app.route("/logout")
def logout():
    session.clear()
    return redirect("/login")


if __name__ == "__main__":
    app.run(debug=True)
