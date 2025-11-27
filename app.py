import os
from datetime import datetime
from flask import Flask, render_template, request, redirect, url_for, session
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)

db_url = os.environ.get("DATABASE_URL")
if not db_url:
    db_url = "sqlite:///job_tracker.db"

app.config["SQLALCHEMY_DATABASE_URI"] = db_url
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["SECRET_KEY"] = "change-this-secret"

db = SQLAlchemy(app)

class User(db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    jobs = db.relationship("JobApplication", backref="user", lazy=True)

class JobApplication(db.Model):
    __tablename__ = "job_applications"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    company = db.Column(db.String(100), nullable=False)
    role = db.Column(db.String(100), nullable=False)
    job_link = db.Column(db.String(255))
    status = db.Column(db.String(50), nullable=False, default="Applied")
    applied_date = db.Column(db.Date)
    notes = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

STATUSES = ["Applied", "Online Assessment", "Interview", "Offer", "Rejected"]

with app.app_context():
    db.create_all()

def get_current_user_id():
    return session.get("user_id")

@app.route("/")
def home():
    if get_current_user_id():
        return redirect(url_for("jobs"))
    return redirect(url_for("login"))

@app.route("/register", methods=["GET", "POST"])
def register():
    if get_current_user_id():
        return redirect(url_for("jobs"))

    if request.method == "POST":
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "").strip()

        if not email or not password:
            return render_template("register.html", error="Email and password are required.")

        existing = User.query.filter_by(email=email).first()
        if existing:
            return render_template("register.html", error="Email is already registered.")

        password_hash = generate_password_hash(password)
        user = User(email=email, password_hash=password_hash)
        db.session.add(user)
        db.session.commit()
        session["user_id"] = user.id
        return redirect(url_for("jobs"))

    return render_template("register.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    if get_current_user_id():
        return redirect(url_for("jobs"))

    if request.method == "POST":
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "").strip()

        user = User.query.filter_by(email=email).first()
        if not user or not check_password_hash(user.password_hash, password):
            return render_template("login.html", error="Invalid email or password.")

        session["user_id"] = user.id
        return redirect(url_for("jobs"))

    return render_template("login.html")

@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))

@app.route("/jobs")
def jobs():
    user_id = get_current_user_id()
    if not user_id:
        return redirect(url_for("login"))

    status_filter = request.args.get("status")
    query = JobApplication.query.filter_by(user_id=user_id)
    if status_filter:
        query = query.filter_by(status=status_filter)
    apps = query.order_by(JobApplication.created_at.desc()).all()
    return render_template("index.html", apps=apps, status_filter=status_filter, statuses=STATUSES)

@app.route("/jobs/add", methods=["POST"])
def add_job():
    user_id = get_current_user_id()
    if not user_id:
        return redirect(url_for("login"))

    company = request.form.get("company", "").strip()
    role = request.form.get("role", "").strip()
    job_link = request.form.get("job_link", "").strip()
    status = request.form.get("status", "Applied").strip()
    applied_date_str = request.form.get("applied_date", "").strip()
    notes = request.form.get("notes", "").strip()

    applied_date = None
    if applied_date_str:
        try:
            applied_date = datetime.strptime(applied_date_str, "%Y-%m-%d").date()
        except ValueError:
            applied_date = None

    if not company or not role:
        return redirect(url_for("jobs"))

    app_obj = JobApplication(
        user_id=user_id,
        company=company,
        role=role,
        job_link=job_link or None,
        status=status or "Applied",
        applied_date=applied_date,
        notes=notes or None,
    )
    db.session.add(app_obj)
    db.session.commit()
    return redirect(url_for("jobs"))

@app.route("/jobs/update/<int:id>", methods=["POST"])
def update_job(id):
    user_id = get_current_user_id()
    if not user_id:
        return redirect(url_for("login"))

    app_obj = JobApplication.query.filter_by(id=id, user_id=user_id).first_or_404()
    status = request.form.get("status", "").strip()
    notes = request.form.get("notes", "").strip()
    applied_date_str = request.form.get("applied_date", "").strip()

    if status:
        app_obj.status = status
    if notes:
        app_obj.notes = notes

    if applied_date_str:
        try:
            app_obj.applied_date = datetime.strptime(applied_date_str, "%Y-%m-%d").date()
        except ValueError:
            pass

    db.session.commit()
    return redirect(url_for("jobs"))

@app.route("/jobs/delete/<int:id>", methods=["POST"])
def delete_job(id):
    user_id = get_current_user_id()
    if not user_id:
        return redirect(url_for("login"))

    app_obj = JobApplication.query.filter_by(id=id, user_id=user_id).first_or_404()
    db.session.delete(app_obj)
    db.session.commit()
    return redirect(url_for("jobs"))

if __name__ == "__main__":
    app.run(debug=True)
