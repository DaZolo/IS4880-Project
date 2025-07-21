from flask_login import login_required
from flask import request, render_template
from sqlalchemy import extract, func
from datetime import datetime
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
    degrees     = db.relationship('Degree',     back_populates='alumni', lazy=True)
    addresses   = db.relationship('Address',    back_populates='alumni', lazy=True)
    employments = db.relationship('Employment', back_populates='alumni', lazy=True)
    skillsets   = db.relationship('Skillset',   back_populates='alumni', lazy=True)
    donations   = db.relationship('Donation',   back_populates='alumni', lazy=True)
    sentto      = db.relationship('SentTo',     back_populates='alumni', lazy=True)

    @property
    def latest_degree(self):
        if not self.degrees:
            return None
        return max(self.degrees, key=lambda d: d.graduationDT)

    def __repr__(self):
        return f'<Alumni {self.alumniID}: {self.fName} {self.lName}>'

@app.route('/alumni', methods=['GET'], endpoint='alumni_directory')
@login_required
@admin_required
def alumni_directory():
    name_query  = request.values.get('name', '').strip()
    year_from   = request.values.get('year_from', '').strip()
    year_to     = request.values.get('year_to', '').strip()
    major_query = request.values.get('major', '').strip()
    sort_by     = request.values.get('sort', 'last')
    page        = request.values.get('page', 1, type=int)
    min_year_val = db.session.query(func.min(extract('year', Degree.graduationDT))).scalar()
    min_year     = int(min_year_val) if min_year_val else datetime.now().year
    current_year = datetime.now().year
    query = Alumni.query

    if name_query:
        terms = name_query.split()
        if len(terms) == 2:
            first_term, last_term = terms
            query = query.filter(
                Alumni.fName.ilike(f'%{first_term}%'),
                Alumni.lName.ilike(f'%{last_term}%')
            )
        else:
            for term in terms:
                query = query.filter(
                    (Alumni.fName.ilike(f'%{term}%')) |
                    (Alumni.lName.ilike(f'%{term}%'))
                )

    if year_from:
        try:
            y0 = max(int(year_from), min_year)
            start_dt = datetime(y0, 1, 1)
            query = query.filter(Alumni.degrees.any(Degree.graduationDT >= start_dt))
        except ValueError:
            pass
    if year_to:
        try:
            y1 = min(int(year_to), current_year)
            end_dt = datetime(y1, 12, 31)
            query = query.filter(Alumni.degrees.any(Degree.graduationDT <= end_dt))
        except ValueError:
            pass

    if major_query:
        query = query.filter(
            Alumni.degrees.any(Degree.major == major_query)
        )

    majors = [row[0] for row in db.session.query(Degree.major).distinct().order_by(Degree.major).all()]

    if sort_by == 'first':
        order_cols = [Alumni.fName.asc(), Alumni.lName.asc()]
    else:
        order_cols = [Alumni.lName.asc(), Alumni.fName.asc()]

    pagination = query.order_by(*order_cols).distinct(Alumni.alumniID).paginate(
        page=page, per_page=10, error_out=False
    )

    display_list = []
    for alumnus in pagination.items:
        if major_query:
            matches = [d for d in alumnus.degrees if d.major == major_query]
            deg = matches[0] if matches else alumnus.latest_degree
        else:
            deg = alumnus.latest_degree

        disp_major = deg.major if deg else ''
        disp_year  = deg.graduationDT.year if deg else None
        disp_email = alumnus.email or ''

        addr = alumnus.addresses[0] if alumnus.addresses else None
        if addr:
            parts = []
            for attr in ('address', 'city', 'state', 'zipCode'):
                val = getattr(addr, attr, None)
                if val:
                    parts.append(str(val))
            disp_address = ', '.join(parts)
        else:
            disp_address = ''

        display_list.append({
            'alumnus': alumnus,
            'major':   disp_major,
            'year':    disp_year,
            'email':   disp_email,
            'address': disp_address
        })

    return render_template(
        'alumni.html',
        display_list=display_list,
        pagination=pagination,
        name_query=name_query,
        year_from=year_from,
        year_to=year_to,
        major_query=major_query,
        majors=majors,
        sort_by=sort_by,
        min_year=min_year,
        current_year=current_year
    )