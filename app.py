from flask import Flask, render_template, request, redirect, session
import sqlite3
import pandas as pd

app = Flask(__name__)
app.secret_key = "ipl_secret"


def init_db():

    conn = sqlite3.connect("players.db")
    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS users(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT,
        password TEXT
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS players(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT,
        country TEXT,
        role TEXT,
        base_price INTEGER,
        current_bid INTEGER,
        team TEXT
    )
    """)

    cursor.execute("SELECT COUNT(*) FROM players")
    count = cursor.fetchone()[0]

    if count == 0:

        df = pd.read_excel("players.xlsx")

        for row in df.values:

            name = row[0]
            country = row[1]
            role = row[2]
            base_price = int(row[3])

            cursor.execute("""
            INSERT INTO players(name,country,role,base_price,current_bid,team)
            VALUES(?,?,?,?,?,?)
            """,(name,country,role,base_price,base_price,"None"))

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


@app.route("/bid/<int:player_id>", methods=["POST"])
def bid(player_id):

    team = request.form.get("team")
    bid_amount = request.form.get("bid")

    if not team or not bid_amount:
        return redirect("/")

    bid_amount = int(bid_amount)

    conn = sqlite3.connect("players.db")
    cursor = conn.cursor()

    cursor.execute("SELECT current_bid, team FROM players WHERE id=?", (player_id,))
    player = cursor.fetchone()

    current_bid = player[0]
    last_team = player[1]

    # prevent same team twice
    if team == last_team:
        conn.close()
        return redirect("/")

    # prevent lower bids
    if bid_amount <= current_bid:
        conn.close()
        return redirect("/")

    cursor.execute("""
    UPDATE players
    SET current_bid=?, team=?
    WHERE id=?
    """,(bid_amount, team, player_id))

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

        cursor.execute("INSERT INTO users(username,password) VALUES (?,?)",(username,password))

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

        cursor.execute("SELECT * FROM users WHERE username=? AND password=?",(username,password))
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
