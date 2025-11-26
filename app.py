import os
from datetime import datetime
from flask import Flask, render_template, request, redirect, url_for, session, flash
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.secret_key = "hk-secret-key"

db_url = os.environ.get("DATABASE_URL")
if db_url and db_url.startswith("mysql://"):
    db_url = db_url.replace("mysql://", "mysql+pymysql://", 1)
if not db_url:
    db_url = "sqlite:///job_tracker.db"

app.config["SQLALCHEMY_DATABASE_URI"] = db_url
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db = SQLAlchemy(app)

class JobApplication(db.Model):
    __tablename__ = "job_applications"
    id = db.Column(db.Integer, primary_key=True)
    company = db.Column(db.String(120), nullable=False)
    job_title = db.Column(db.String(120), nullable=False)
    status = db.Column(db.String(50), nullable=False, default="Applied")
    location = db.Column(db.String(120))
    source = db.Column(db.String(120))
    applied_date = db.Column(db.Date)
    notes = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        company = request.form.get("company")
        job_title = request.form.get("job_title")
        status = request.form.get("status") or "Applied"
        location = request.form.get("location")
        source = request.form.get("source")
        applied_date_str = request.form.get("applied_date")
        notes = request.form.get("notes")
        applied_date = None
        if applied_date_str:
            try:
                applied_date = datetime.strptime(applied_date_str, "%Y-%m-%d").date()
            except:
                flash("Invalid date format.", "error")
        if not company or not job_title:
            flash("Company and Job Title are required.", "error")
        else:
            job = JobApplication(
                company=company,
                job_title=job_title,
                status=status,
                location=location,
                source=source,
                applied_date=applied_date,
                notes=notes,
            )
            db.session.add(job)
            db.session.commit()
            flash("Added.", "success")
        return redirect(url_for("index"))
    jobs = JobApplication.query.order_by(JobApplication.created_at.desc()).all()
    return render_template("index.html", jobs=jobs)

@app.route("/edit/<int:job_id>", methods=["GET", "POST"])
def edit_job(job_id):
    job = JobApplication.query.get_or_404(job_id)
    if request.method == "POST":
        job.company = request.form.get("company")
        job.job_title = request.form.get("job_title")
        job.status = request.form.get("status")
        job.location = request.form.get("location")
        job.source = request.form.get("source")
        applied_date_str = request.form.get("applied_date")
        job.notes = request.form.get("notes")
        if applied_date_str:
            try:
                job.applied_date = datetime.strptime(applied_date_str, "%Y-%m-%d").date()
            except:
                flash("Invalid date.", "error")
        if not job.company or not job.job_title:
            flash("Required fields missing.", "error")
            return redirect(url_for("edit_job", job_id=job.id))
        db.session.commit()
        flash("Updated.", "success")
        return redirect(url_for("index"))
    return render_template("edit.html", job=job)

@app.route("/delete/<int:job_id>", methods=["POST"])
def delete_job(job_id):
    job = JobApplication.query.get_or_404(job_id)
    db.session.delete(job)
    db.session.commit()
    flash("Deleted.", "success")
    return redirect(url_for("index"))

if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(debug=True)
