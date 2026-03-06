from flask import Flask, render_template, request, redirect, session
import sqlite3
import pandas as pd

app = Flask(__name__)
app.secret_key = "ipl_secret_key"


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

    # check if players already loaded
    cursor.execute("SELECT COUNT(*) FROM players")
    count = cursor.fetchone()[0]

    if count == 0:
        try:
            df = pd.read_excel("players.xlsx")

            # insert rows by position (avoids column name errors)
            for row in df.itertuples(index=False):

                name = str(row[0])
                country = str(row[1])
                role = str(row[2])
                base_price = int(row[3])

                cursor.execute(
                    "INSERT INTO players(name,country,role,base_price,current_bid) VALUES(?,?,?,?,?)",
                    (name, country, role, base_price, base_price)
                )

            conn.commit()

        except Exception as e:
            print("Excel loading error:", e)

    conn.close()


# initialize database
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


@app.route("/register", methods=["GET", "POST"])
def register():

    if request.method == "POST":

        username = request.form["username"]
        password = request.form["password"]

        conn = sqlite3.connect("players.db")
        cursor = conn.cursor()

        cursor.execute(
            "INSERT INTO users(username,password) VALUES (?,?)",
            (username, password)
        )

        conn.commit()
        conn.close()

        return redirect("/login")

    return render_template("register.html")


@app.route("/login", methods=["GET", "POST"])
def login():

    if request.method == "POST":

        username = request.form["username"]
        password = request.form["password"]

        conn = sqlite3.connect("players.db")
        cursor = conn.cursor()

        cursor.execute(
            "SELECT * FROM users WHERE username=? AND password=?",
            (username, password)
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
