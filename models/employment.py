from datetime import datetime
from app import app, admin_required
from flask_login import login_required
from flask import request, render_template, flash
from sqlalchemy import extract, func
from models.db import db
from models.alumni import Alumni
from models.degree import Degree

class Employment(db.Model):
    __tablename__ = 'employment'

    empID      = db.Column('EID', db.Integer, primary_key=True)
    alumniID   = db.Column(db.Integer, db.ForeignKey('alumni.alumniID'))
    company    = db.Column(db.String(255))
    jobTitle   = db.Column(db.String(100))
    startDate  = db.Column(db.Date)
    endDate    = db.Column(db.Date)

    alumni = db.relationship('Alumni', back_populates='employments', lazy=True)

@app.route(
    '/education-employment',
    endpoint='education_employment_page',
    methods=['GET']
)
@login_required
@admin_required
def education_employment_page():
    year_from   = request.args.get('yearFrom', '').strip()
    year_to     = request.args.get('yearTo', '').strip()
    emp_start   = request.args.get('employmentStart', '').strip()
    emp_end     = request.args.get('employmentEnd', '').strip()
    current_yn  = request.args.get('currentYN', '').strip().upper()
    employer    = request.args.get('employer', '').strip()
    major       = request.args.get('major', '').strip()
    position    = request.args.get('position', '').strip()

    min_year     = db.session.query(func.min(func.year(Degree.graduationDT))).scalar() or datetime.now().year
    current_year = datetime.now().year

    majors = [m[0] for m in db.session.query(Degree.major).distinct().order_by(Degree.major).all()]

    q = db.session.query(Alumni, Degree, Employment) \
        .join(Degree, Degree.alumniID == Alumni.alumniID) \
        .join(Employment, Employment.alumniID == Alumni.alumniID)

    if year_from.isdigit():
        q = q.filter(extract('year', Degree.graduationDT) >= int(year_from))
    if year_to.isdigit():
        q = q.filter(extract('year', Degree.graduationDT) <= int(year_to))

    if major:
        q = q.filter(Degree.major == major)

    if emp_start:
        try:
            q = q.filter(Employment.startDate >= datetime.fromisoformat(emp_start))
        except ValueError:
            flash('Invalid employmentStart date; use YYYY-MM-DD', 'warning')
    if emp_end:
        try:
            q = q.filter(Employment.endDate <= datetime.fromisoformat(emp_end))
        except ValueError:
            flash('Invalid employmentEnd date; use YYYY-MM-DD', 'warning')

    if current_yn == 'Y':
        q = q.filter(Employment.endDate.is_(None))
    elif current_yn == 'N':
        q = q.filter(Employment.endDate.isnot(None))

    if employer:
        q = q.filter(Employment.company.ilike(f'%{employer}%'))

    if position:
        q = q.filter(Employment.jobTitle.ilike(f'%{position}%'))

    rows = q.order_by(Alumni.lName, Employment.startDate).all()

    alumni_map = {}
    for alum, deg, job in rows:
        grad_dt = deg.graduationDT
        rec = {
            'alumni_id': alum.alumniID,
            'name': f"{alum.fName} {alum.lName}",
            'major': deg.major,
            'graduation_date': grad_dt.strftime('%Y-%m-%d'),
            'company': job.company,
            'job_title': job.jobTitle,
            'start_date': job.startDate.strftime('%Y-%m-%d'),
            'end_date': job.endDate.strftime('%Y-%m-%d') if job.endDate else 'Current'
        }
        existing = alumni_map.get(alum.alumniID)
        if not existing:
            alumni_map[alum.alumniID] = rec
        else:
            existing_date = datetime.fromisoformat(existing['graduation_date']).date()
            if existing_date < grad_dt:
                alumni_map[alum.alumniID] = rec

    records = list(alumni_map.values())

    return render_template(
        'educationemployment.html',
        records=records,
        year_from=year_from,
        year_to=year_to,
        emp_start=emp_start,
        emp_end=emp_end,
        current_yn=current_yn,
        employer=employer,
        major=major,
        position=position,
        majors=majors,
        min_year=min_year,
        current_year=current_year
    )