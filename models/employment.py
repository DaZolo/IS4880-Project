# File: models/employment.py

from datetime import datetime
from app import app, admin_required
from flask_login import login_required
from flask import request, render_template, flash
from sqlalchemy import extract
from models.db import db
from models.alumni import Alumni
from models.degree import Degree

class Employment(db.Model):
    __tablename__ = 'employment'

    # Map the Python attribute empID to the EID column in the database
    empID      = db.Column('EID', db.Integer, primary_key=True)
    alumniID   = db.Column(db.Integer, db.ForeignKey('alumni.alumniID'))
    company    = db.Column(db.String(255))
    jobTitle   = db.Column(db.String(100))
    startDate  = db.Column(db.Date)
    endDate    = db.Column(db.Date)

    # Relationship back to Alumni
    alumni = db.relationship('Alumni', back_populates='employments', lazy=True)

@app.route(
    '/education-employment',
    endpoint='education_employment_page',
    methods=['GET']
)
@login_required
@admin_required
def education_employment_page():
    """Education & Employment Report"""
    # Gather filter parameters
    year_from  = request.args.get('yearFrom', '').strip()
    year_to    = request.args.get('yearTo',   '').strip()
    emp_start  = request.args.get('employmentStart', '').strip()
    emp_end    = request.args.get('employmentEnd',   '').strip()
    current_yn = request.args.get('currentYN', '').strip().upper()

    # Base join: Alumni → Degree → Employment
    q = db.session.query(Alumni, Employment) \
        .join(Degree, Degree.alumniID == Alumni.alumniID) \
        .join(Employment, Employment.alumniID == Alumni.alumniID)

    # Graduation‐year filters
    if year_from.isdigit():
        q = q.filter(extract('year', Degree.graduationDT) >= int(year_from))
    if year_to.isdigit():
        q = q.filter(extract('year', Degree.graduationDT) <= int(year_to))

    # Employment‐date filters
    if emp_start:
        try:
            q = q.filter(Employment.startDate >= datetime.fromisoformat(emp_start))
        except ValueError:
            flash('Invalid employmentStart date; use YYYY‑MM‑DD', 'warning')
    if emp_end:
        try:
            q = q.filter(Employment.endDate <= datetime.fromisoformat(emp_end))
        except ValueError:
            flash('Invalid employmentEnd date; use YYYY‑MM‑DD', 'warning')

    # Current‐only filter
    if current_yn == 'Y':
        q = q.filter(Employment.endDate.is_(None))

    # Execute the query and group jobs by alumni
    rows = q.order_by(Alumni.lName, Employment.startDate).all()
    grouped = {}
    for alum, job in rows:
        grouped.setdefault(alum, []).append(job)

    # Show all alumni regardless of number of employments
    grouped_data = [(alum, jobs) for alum, jobs in grouped.items()]

    return render_template(
        'educationemployment.html',
        grouped_data=grouped_data,
        year_from=year_from,
        year_to=year_to,
        emp_start=emp_start,
        emp_end=emp_end,
        current_yn=current_yn
    )