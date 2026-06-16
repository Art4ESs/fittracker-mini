from flask import Flask, render_template, request, redirect, url_for
import sqlite3
from datetime import datetime
import os

app = Flask(__name__)

# Путь к базе
DB_PATH = "data/fitness.db"

# Убедимся, что папка data существует
os.makedirs("data", exist_ok=True)

# Инициализация базы
def init_db():
    with sqlite3.connect(DB_PATH) as conn:
        # Тренировки
        conn.execute("""
            CREATE TABLE IF NOT EXISTS workouts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                date TEXT,
                workout_type TEXT,
                exercise TEXT,
                sets_reps TEXT,
                weight REAL,
                completed BOOLEAN
            )
        """)
        # Замеры тела
        conn.execute("""
            CREATE TABLE IF NOT EXISTS measurements (
                date TEXT PRIMARY KEY,
                weight REAL,
                waist REAL,
                chest REAL,
                biceps REAL,
                hips REAL,
                neck REAL
            )
        """)
        # Питание — нормы
        conn.execute("""
            CREATE TABLE IF NOT EXISTS nutrition_goals (
                id INTEGER PRIMARY KEY,
                age INTEGER,
                weight REAL,
                height REAL,
                activity REAL,
                calories REAL,
                protein REAL,
                fat REAL,
                carbs REAL
            )
        """)
        # Напоминания
        conn.execute("""
            CREATE TABLE IF NOT EXISTS reminders (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                date TEXT,
                title TEXT,
                priority TEXT,
                completed BOOLEAN
            )
        """)

init_db()

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/workouts", methods=["GET", "POST"])
def workouts():
    if request.method == "POST":
        date = request.form["date"]
        workout_type = request.form["workout_type"]
        exercise = request.form["exercise"]
        sets_reps = request.form["sets_reps"]
        weight = request.form["weight"] or None
        completed = "completed" in request.form
        with sqlite3.connect(DB_PATH) as conn:
            conn.execute("""
                INSERT INTO workouts (date, workout_type, exercise, sets_reps, weight, completed)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (date, workout_type, exercise, sets_reps, weight, completed))
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.execute("SELECT * FROM workouts ORDER BY date DESC")
        entries = cursor.fetchall()
    return render_template("workouts.html", entries=entries)

@app.route("/measurements", methods=["GET", "POST"])
def measurements():
    if request.method == "POST":
        date = request.form["date"]
        weight = request.form["weight"]
        waist = request.form["waist"] or None
        chest = request.form["chest"] or None
        biceps = request.form["biceps"] or None
        hips = request.form["hips"] or None
        neck = request.form["neck"] or None
        with sqlite3.connect(DB_PATH) as conn:
            conn.execute("""
                INSERT OR REPLACE INTO measurements 
                (date, weight, waist, chest, biceps, hips, neck)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (date, weight, waist, chest, biceps, hips, neck))
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.execute("SELECT * FROM measurements ORDER BY date DESC")
        entries = cursor.fetchall()
    return render_template("measurements.html", entries=entries)

@app.route("/nutrition", methods=["GET", "POST"])
def nutrition():
    result = {}
    if request.method == "POST":
        age = int(request.form["age"])
        weight = float(request.form["weight"])
        height = float(request.form["height"])
        activity = float(request.form["activity"])
        # TDEE по Миффлину — Сан Жеору
        tdee = (10 * weight + 6.25 * height - 5 * age + 5) * activity
        deficit = tdee - 400
        protein = 2 * weight
        fat = 0.25 * deficit / 9
        carbs = (deficit - protein * 4 - fat * 9) / 4
        result = {
            "tdee": round(tdee),
            "deficit": round(deficit),
            "protein": round(protein),
            "fat": round(fat),
            "carbs": round(carbs)
        }
        # Сохраняем цели
        with sqlite3.connect(DB_PATH) as conn:
            conn.execute("""
                INSERT OR REPLACE INTO nutrition_goals 
                (id, age, weight, height, activity, calories, protein, fat, carbs)
                VALUES (1, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (age, weight, height, activity, deficit, protein, fat, carbs))
    return render_template("nutrition.html", result=result)

@app.route("/reminders", methods=["GET", "POST"])
def reminders():
    if request.method == "POST":
        date = request.form["date"]
        title = request.form["title"]
        priority = request.form["priority"]
        completed = "completed" in request.form
        with sqlite3.connect(DB_PATH) as conn:
            conn.execute("""
                INSERT INTO reminders (date, title, priority, completed)
                VALUES (?, ?, ?, ?)
            """, (date, title, priority, completed))
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.execute("SELECT * FROM reminders ORDER BY date DESC")
        entries = cursor.fetchall()
    return render_template("reminders.html", entries=entries)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
