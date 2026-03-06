import os
import sqlite3
import pandas as pd
from flask import Flask, render_template, request, redirect, session

# FORCE Flask to use the templates folder

app = Flask(**name**, template_folder="templates")
app.secret_key = "secret123"

def init_db():
conn = sqlite3.connect("players.db")
cursor = conn.cursor()

```
cursor.execute("""
CREATE TABLE IF NOT EXISTS players(
    id INTEGER PRIMARY KEY,
    name TEXT,
    country TEXT,
    role TEXT,
    base_price INTEGER,
    current_bid INTEGER
)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS users(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT,
    password TEXT
)
""")

# Load Excel data if DB empty
cursor.execute("SELECT COUNT(*) FROM players")
count = cursor.fetchone()[0]

if count == 0:
    df = pd.read_excel("players.xlsx")

    for _, row in df.iterrows():
        cursor.execute(
            "INSERT INTO players VALUES (?,?,?,?,?,?)",
            (
                int(row["id"]),
                row["name"],
                row["country"],
                row["role"],
                int(row["base_price"]),
                int(row["current_bid"])
            )
        )

conn.commit()
conn.close()
```

@app.route("/")
def home():
if "user" not in session:
return redirect("/login")

```
conn = sqlite3.connect("players.db")
cursor = conn.cursor()
cursor.execute("SELECT * FROM players")
players = cursor.fetchall()
conn.close()

return render_template("index.html", players=players)
```

@app.route("/login", methods=["GET", "POST"])
def login():
if request.method == "POST":
username = request.form["username"]
password = request.form["password"]

```
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
```

@app.route("/register", methods=["GET", "POST"])
def register():
if request.method == "POST":
username = request.form["username"]
password = request.form["password"]

```
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
```

@app.route("/bid/[int:id](int:id)", methods=["POST"])
def bid(id):
bid = int(request.form["bid"])

```
conn = sqlite3.connect("players.db")
cursor = conn.cursor()

cursor.execute("SELECT current_bid FROM players WHERE id=?", (id,))
current = cursor.fetchone()[0]

if bid > current:
    cursor.execute(
        "UPDATE players SET current_bid=? WHERE id=?",
        (bid, id)
    )

conn.commit()
conn.close()

return redirect("/")
```

if **name** == "**main**":
init_db()
app.run(debug=True)
