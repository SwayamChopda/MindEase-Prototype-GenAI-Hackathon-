
from flask import Flask, render_template, request, redirect, url_for, jsonify
import sqlite3, datetime, os

DB = os.path.join(os.path.dirname(__file__), "mindease.db")

def init_db():
    conn = sqlite3.connect(DB)
    c = conn.cursor()
    c.execute("""CREATE TABLE IF NOT EXISTS moods (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    mood TEXT,
                    note TEXT,
                    timestamp DATETIME
                )""")
    c.execute("""CREATE TABLE IF NOT EXISTS journals (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    entry TEXT,
                    timestamp DATETIME
                )""")
    c.execute("""CREATE TABLE IF NOT EXISTS activities (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT,
                    completed_at DATETIME
                )""")
    conn.commit()
    conn.close()

def save_mood(mood, note):
    conn = sqlite3.connect(DB)
    c = conn.cursor()
    c.execute("INSERT INTO moods (mood, note, timestamp) VALUES (?,?,?)", (mood, note, datetime.datetime.now()))
    conn.commit()
    conn.close()

def get_moods():
    conn = sqlite3.connect(DB)
    c = conn.cursor()
    c.execute("SELECT timestamp, mood FROM moods ORDER BY timestamp")
    rows = c.fetchall()
    conn.close()
    return rows

def save_journal(entry):
    conn = sqlite3.connect(DB)
    c = conn.cursor()
    c.execute("INSERT INTO journals (entry, timestamp) VALUES (?,?)", (entry, datetime.datetime.now()))
    conn.commit()
    conn.close()

def count_completed_activities():
    conn = sqlite3.connect(DB)
    c = conn.cursor()
    c.execute("SELECT COUNT(*) FROM activities")
    n = c.fetchone()[0]
    conn.close()
    return n

def complete_activity(name):
    conn = sqlite3.connect(DB)
    c = conn.cursor()
    c.execute("INSERT INTO activities (name, completed_at) VALUES (?,?)", (name, datetime.datetime.now()))
    conn.commit()
    conn.close()

app = Flask(__name__)
init_db()

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/mood", methods=["GET","POST"])
def mood_check():
    if request.method=="POST":
        mood = request.form.get("mood")
        note = request.form.get("note","")
        save_mood(mood, note)
        return redirect(url_for("activities"))
    return render_template("mood.html")

@app.route("/activities")
def activities():
    return render_template("activities.html")

@app.route("/activity/<name>", methods=["GET","POST"])
def activity(name):
    if request.method=="POST":
        # mark completed and redirect to dashboard
        complete_activity(name)
        return redirect(url_for("dashboard"))
    return render_template("activity_"+name+".html", name=name.capitalize())

@app.route("/journal", methods=["GET","POST"])
def journal():
    if request.method=="POST":
        entry = request.form.get("entry","")
        save_journal(entry)
        return redirect(url_for("dashboard"))
    return render_template("journal.html")

@app.route("/dashboard")
def dashboard():
    moods = get_moods()
    # prepare labels and values
    labels = [r[0] for r in moods]
    values = [0 if r[1]=="neutral" else (3 if r[1]=="happy" else -3) for r in moods]
    completed = count_completed_activities()
    # compute simple streak (count last consecutive days with mood)
    return render_template("dashboard.html", labels=labels, values=values, completed=completed)

if __name__=="__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)
