import os
from datetime import datetime
from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)

db_url = os.environ.get("DATABASE_URL")
if db_url and db_url.startswith("mysql://"):
    db_url = db_url.replace("mysql://", "mysql+pymysql://", 1)
if not db_url:
    db_url = "sqlite:///job_tracker.db"

app.config["SQLALCHEMY_DATABASE_URI"] = db_url
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db = SQLAlchemy(app)

class JobApplication(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    company = db.Column(db.String(100), nullable=False)
    position = db.Column(db.String(100), nullable=False)
    status = db.Column(db.String(50), default="Applied")
    applied_date = db.Column(db.Date, default=datetime.utcnow)
    notes = db.Column(db.Text, nullable=True)

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        company = request.form.get("company")
        position = request.form.get("position")
        status = request.form.get("status") or "Applied"
        applied_date_str = request.form.get("applied_date")
        notes = request.form.get("notes")

        if applied_date_str:
            try:
                applied_date = datetime.strptime(applied_date_str, "%Y-%m-%d").date()
            except ValueError:
                applied_date = datetime.utcnow().date()
        else:
            applied_date = datetime.utcnow().date()

        new_app = JobApplication(
            company=company,
            position=position,
            status=status,
            applied_date=applied_date,
            notes=notes,
        )
        db.session.add(new_app)
        db.session.commit()
        return redirect(url_for("index"))

    applications = JobApplication.query.order_by(JobApplication.applied_date.desc()).all()
    return render_template("index.html", applications=applications)

@app.route("/update/<int:app_id>", methods=["POST"])
def update(app_id):
    application = JobApplication.query.get_or_404(app_id)
    status = request.form.get("status")
    notes = request.form.get("notes")

    if status:
        application.status = status
    if notes is not None:
        application.notes = notes

    db.session.commit()
    return redirect(url_for("index"))

@app.route("/delete/<int:app_id>", methods=["POST"])
def delete(app_id):
    application = JobApplication.query.get_or_404(app_id)
    db.session.delete(application)
    db.session.commit()
    return redirect(url_for("index"))

@app.route("/init-db")
def init_db():
    db.create_all()
    return "Database initialized"

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
import os
from datetime import datetime
from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)

db_url = os.environ.get("DATABASE_URL")
if db_url and db_url.startswith("mysql://"):
    db_url = db_url.replace("mysql://", "mysql+pymysql://", 1)
if not db_url:
    db_url = "sqlite:///job_tracker.db"

app.config["SQLALCHEMY_DATABASE_URI"] = db_url
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db = SQLAlchemy(app)

class JobApplication(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    company = db.Column(db.String(100), nullable=False)
    position = db.Column(db.String(100), nullable=False)
    status = db.Column(db.String(50), default="Applied")
    applied_date = db.Column(db.Date, default=datetime.utcnow)
    notes = db.Column(db.Text, nullable=True)

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        company = request.form.get("company")
        position = request.form.get("position")
        status = request.form.get("status") or "Applied"
        applied_date_str = request.form.get("applied_date")
        notes = request.form.get("notes")

        if applied_date_str:
            try:
                applied_date = datetime.strptime(applied_date_str, "%Y-%m-%d").date()
            except ValueError:
                applied_date = datetime.utcnow().date()
        else:
            applied_date = datetime.utcnow().date()

        new_app = JobApplication(
            company=company,
            position=position,
            status=status,
            applied_date=applied_date,
            notes=notes,
        )
        db.session.add(new_app)
        db.session.commit()
        return redirect(url_for("index"))

    applications = JobApplication.query.order_by(JobApplication.applied_date.desc()).all()
    return render_template("index.html", applications=applications)

@app.route("/update/<int:app_id>", methods=["POST"])
def update(app_id):
    application = JobApplication.query.get_or_404(app_id)
    status = request.form.get("status")
    notes = request.form.get("notes")

    if status:
        application.status = status
    if notes is not None:
        application.notes = notes

    db.session.commit()
    return redirect(url_for("index"))

@app.route("/delete/<int:app_id>", methods=["POST"])
def delete(app_id):
    application = JobApplication.query.get_or_404(app_id)
    db.session.delete(application)
    db.session.commit()
    return redirect(url_for("index"))

@app.route("/init-db")
def init_db():
    db.create_all()
    return "Database initialized"

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
