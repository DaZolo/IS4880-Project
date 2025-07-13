# File: models/alumni.py

from flask_login import login_required
from flask import request, render_template
from sqlalchemy import extract
from models.db import db
from models.degree import Degree
from app import app, admin_required

class Alumni(db.Model):
    __tablename__ = 'alumni'

    alumniID       = db.Column(db.Integer, primary_key=True)
    fName          = db.Column(db.String(100))
    lName          = db.Column(db.String(100))
    phone          = db.Column(db.String(20))
    email          = db.Column(db.String(120))
    DOB            = db.Column(db.Date)
    gender         = db.Column(db.String(20))
    ethnicity      = db.Column(db.String(50))
    website        = db.Column(db.String(255))
    linkedIn_link  = db.Column(db.String(255))
    twitter_link   = db.Column(db.String(255))
    facebook_link  = db.Column(db.String(255))
    instagram_link = db.Column(db.String(255))
    guestSpeakerYN = db.Column(db.String(1))
    newsLetterYN   = db.Column(db.String(1))
    imageThumb     = db.Column(db.String(255))

    # relationships
    degrees     = db.relationship('Degree',     back_populates='alumni', lazy=True)
    addresses   = db.relationship('Address',    back_populates='alumni', lazy=True)
    employments = db.relationship('Employment', back_populates='alumni', lazy=True)
    skillsets   = db.relationship('Skillset',   back_populates='alumni', lazy=True)
    donations   = db.relationship('Donation',   back_populates='alumni', lazy=True)
    sentto      = db.relationship('SentTo',     back_populates='alumni', lazy=True)

    def __repr__(self):
        return f'<Alumni {self.alumniID}: {self.fName} {self.lName}>'

@app.route('/alumni', methods=['GET', 'POST'], endpoint='alumni_directory')
@login_required
@admin_required
def alumni_directory():
    """Alumni Directory page with filtering and pagination."""
    # 1) Read filters from the query string
    name_query   = request.values.get('name',      '').strip()
    year_from    = request.values.get('year_from', '').strip()
    year_to      = request.values.get('year_to',   '').strip()
    major_query  = request.values.get('major',     '').strip()
    page         = request.values.get('page', 1,    type=int)

    # 2) Build base query
    query = Alumni.query

    # 3) Apply name partial‐match
    if name_query:
        query = query.filter(
            (Alumni.fName.ilike(f'%{name_query}%')) |
            (Alumni.lName.ilike(f'%{name_query}%'))
        )

    # 4) Apply graduation‐year range (they live on Degree.graduationDT)
    if year_from:
        try:
            y0 = int(year_from)
            query = query.filter(
                extract('year', Degree.graduationDT) >= y0
            )
        except ValueError:
            pass
    if year_to:
        try:
            y1 = int(year_to)
            query = query.filter(
                extract('year', Degree.graduationDT) <= y1
            )
        except ValueError:
            pass

    # 5) Apply major dropdown (partial match)
    if major_query:
        query = query.filter(
            Alumni.degrees.any(Degree.major.ilike(f'%{major_query}%'))
        )

    # 6) Grab distinct list of majors for the <select>
    majors = [
        row[0]
        for row in db.session
                     .query(Degree.major)
                     .distinct()
                     .order_by(Degree.major)
                     .all()
    ]

    # 7) Paginate & sort by last name
    pagination  = (
        query
        .order_by(Alumni.lName.asc(), Alumni.fName.asc())
        .paginate(page=page, per_page=10, error_out=False)
    )
    alumni_list = pagination.items

    # 8) Render template with all context
    return render_template(
        'alumni.html',
        alumni_list=alumni_list,
        pagination=pagination,
        name_query=name_query,
        year_from=year_from,
        year_to=year_to,
        major_query=major_query,
        majors=majors
    )