from flask import Blueprint, render_template, request, redirect, Response, session
import json, re
from datetime import date
from io import BytesIO
import pandas as pd
from reportlab.pdfgen import canvas
from werkzeug.security import generate_password_hash, check_password_hash
from app.models import Habit

main = Blueprint("main", __name__)
DATA_FILE = "data.json"

# =========================
# JSON helpers
# =========================
def load_data():
    try:
        with open(DATA_FILE) as f:
            data = json.load(f)
            if not isinstance(data, dict) or "users" not in data:
                return {"users": []}
            return data
    except:
        return {"users": []}

def save_data(data):
    with open(DATA_FILE, "w") as f:
        json.dump(data, f, indent=2)

# ⚠️ CRITIQUE : retourne la vraie référence
def get_current_user(data):
    email = session.get("user")
    if not email:
        return None

    for i, u in enumerate(data["users"]):
        if u["email"] == email:
            return data["users"][i]   # vraie référence JSON
    return None


# =========================
# Validation
# =========================
def is_valid_email(email):
    return re.match(r"^[a-zA-Z0-9._%+-]+@gmail\.com$", email)

def is_strong_password(p):
    return (
        len(p) >= 8 and
        any(c.isupper() for c in p) and
        any(c.isdigit() for c in p)
    )

# =========================
# AUTH
# =========================
@main.route("/register", methods=["GET","POST"])
def register():
    if request.method == "POST":
        data = load_data()
        email = request.form["email"]
        password = request.form["password"]

        if not is_valid_email(email):
            return render_template("register.html", error="Please enter a valid Gmail")

        if not is_strong_password(password):
            return render_template("register.html", error="Password must have 8 chars, 1 uppercase and 1 number")

        for u in data["users"]:
            if u["email"] == email:
                return render_template("register.html", error="Email already registered")

        data["users"].append({
            "email": email,
            "password": generate_password_hash(password),
            "habits": []
        })

        save_data(data)
        return redirect("/login")

    return render_template("register.html")


@main.route("/login", methods=["GET","POST"])
def login():
    if request.method == "POST":
        data = load_data()
        email = request.form["email"]
        password = request.form["password"]

        for u in data["users"]:
            if u["email"] == email and check_password_hash(u["password"], password):
                session["user"] = email
                return redirect("/")

        return render_template("login.html", error="Invalid email or password")

    return render_template("login.html")


@main.route("/logout")
def logout():
    session.clear()
    return redirect("/login")

# =========================
# DASHBOARD
# =========================
@main.route("/")
def index():
    data = load_data()
    user = get_current_user(data)
    if not user:
        return redirect("/login")

    habits = [Habit(**h) for h in user["habits"]]
    for h in habits:
        h.motivation = h.get_motivation()

    labels = [h.name for h in habits]
    values = [len(h.progress) for h in habits]

    return render_template(
        "index.html",
        habits=habits,
        labels=labels,
        values=values,
        username=user["email"]
    )

# =========================
# ADD HABIT
# =========================
@main.route("/add", methods=["POST"])
def add_habit():
    data = load_data()
    user = get_current_user(data)
    if not user:
        return redirect("/login")

    name = request.form["habit"]

    for h in user["habits"]:
        if h["name"].lower() == name.lower():
            return redirect("/")

    user["habits"].append({
        "name": name,
        "progress": [],
        "streak": 0,
        "record": 0,
        "days_missed": 0,
        "last_done": None
    })

    save_data(data)
    return redirect("/")

# =========================
# MARK DONE
# =========================
@main.route("/done", methods=["POST"])
def mark_done():
    data = load_data()
    user = get_current_user(data)
    if not user:
        return redirect("/login")

    today = date.today().isoformat()
    name = request.form["habit"]

    for i, h in enumerate(user["habits"]):
        if h["name"] == name:
            habit = Habit(**h)
            habit.mark_done(today)
            user["habits"][i] = habit.to_dict()   # 🔥 écriture correcte

    save_data(data)
    return redirect("/")

# =========================
# EXPORT CSV
# =========================
@main.route("/export/csv")
def export_csv():
    data = load_data()
    user = get_current_user(data)
    if not user:
        return redirect("/login")

    habits = [Habit(**h) for h in user["habits"]]

    rows = [{
        "name": h.name,
        "days_completed": len(h.progress),
        "streak": h.streak,
        "record": h.record
    } for h in habits]

    df = pd.DataFrame(rows)
    return Response(df.to_csv(index=False),
        mimetype="text/csv",
        headers={"Content-Disposition":"attachment; filename=habits.csv"}
    )

# =========================
# EXPORT PDF
# =========================
@main.route("/export/pdf")
def export_pdf():
    data = load_data()
    user = get_current_user(data)
    if not user:
        return redirect("/login")

    habits = [Habit(**h) for h in user["habits"]]

    buffer = BytesIO()
    pdf = canvas.Canvas(buffer)
    pdf.setFont("Helvetica-Bold", 18)

    pdf.drawCentredString(300, 820, "SMART HABIT TRACKER")
    pdf.setFont("Helvetica", 12)
    pdf.drawCentredString(300, 800, "Daily Progress Report")

    pdf.drawString(50, 760, f"User: {user['email']}")
    pdf.drawString(50, 740, f"Date: {date.today().strftime('%d %B %Y')}")

    y = 700
    pdf.setFont("Helvetica-Bold", 14)
    pdf.drawString(50, y, "SUMMARY")
    y -= 20
    pdf.setFont("Helvetica", 11)

    total_days = sum(len(h.progress) for h in habits)
    best_streak = max([h.streak for h in habits], default=0)

    pdf.drawString(50, y, f"Total habits: {len(habits)}"); y -= 15
    pdf.drawString(50, y, f"Total days completed: {total_days}"); y -= 15
    pdf.drawString(50, y, f"Best streak: {best_streak}"); y -= 30

    pdf.setFont("Helvetica-Bold", 14)
    pdf.drawString(50, y, "HABITS")
    y -= 20

    for h in habits:
        pdf.setFont("Helvetica-Bold", 12)
        pdf.drawString(50, y, h.name); y -= 15
        pdf.setFont("Helvetica", 11)
        pdf.drawString(70, y, f"Streak: {h.streak}"); y -= 15
        pdf.drawString(70, y, f"Record: {h.record}"); y -= 15
        pdf.drawString(70, y, f"Motivation: {h.get_motivation()}"); y -= 25

        if y < 100:
            pdf.showPage()
            y = 800

    pdf.save()
    buffer.seek(0)

    return Response(buffer, mimetype="application/pdf",
        headers={"Content-Disposition":"attachment; filename=smart_habits_report.pdf"}
    )

