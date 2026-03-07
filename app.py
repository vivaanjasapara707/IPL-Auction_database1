from flask import Flask, render_template, request, redirect, session
import sqlite3
import pandas as pd

app = Flask(__name__)
app.secret_key = "ipl_secret"


def init_db():
    conn = sqlite3.connect("players.db")
    cursor = conn.cursor()

    # USERS TABLE
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS users(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT,
        password TEXT
    )
    """)

    # PLAYERS TABLE
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

        # normalize column names
        df.columns = df.columns.str.strip().str.lower()

        name_col = None
        country_col = None
        role_col = None
        price_col = None

        for col in df.columns:
            if "player" in col or "name" in col:
                name_col = col
            elif "country" in col:
                country_col = col
            elif "role" in col:
                role_col = col
            elif "price" in col:
                price_col = col

        for _, row in df.iterrows():

            name = str(row[name_col])
            country = str(row[country_col])
            role = str(row[role_col])
            base_price = int(row[price_col])

            cursor.execute("""
            INSERT INTO players(name,country,role,base_price,current_bid)
            VALUES(?,?,?,?,?)
            """,(name,country,role,base_price,base_price))

        conn.commit()

    conn.close()


init_db()


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


@app.route("/bid/<int:player_id>", methods=["POST"])
def bid(player_id):

    bid_amount = int(request.form["bid"])

    conn = sqlite3.connect("players.db")
    cursor = conn.cursor()

    cursor.execute(
        "UPDATE players SET current_bid=? WHERE id=?",
        (bid_amount, player_id)
    )

    conn.commit()
    conn.close()

    return redirect("/")


@app.route("/register", methods=["GET","POST"])
def register():

    if request.method == "POST":

        username = request.form["username"]
        password = request.form["password"]

        conn = sqlite3.connect("players.db")
        cursor = conn.cursor()

        cursor.execute(
            "INSERT INTO users(username,password) VALUES (?,?)",
            (username,password)
        )

        conn.commit()
        conn.close()

        return redirect("/login")

    return render_template("register.html")


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


@app.route("/logout")
def logout():
    session.clear()
    return redirect("/login")


if __name__ == "__main__":
    app.run(debug=True)
