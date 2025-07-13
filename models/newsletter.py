# File: models/newsletter.py

from datetime import datetime
from flask import render_template, request, flash, redirect, url_for
from flask_login import login_required
from app import app, admin_required
from models.db import db
from models.alumni import Alumni
from models.sentto import SentTo
from models.engagement import Engagement
from sqlalchemy import Column, Integer, String, Date, Text

class Newsletter(db.Model):
    __tablename__ = 'newsLetter'  # matches the MySQL table name

    # map attributes to actual column names
    newsletterID = Column('id',            Integer, primary_key=True)
    date         = Column('newsDate',      Date,    nullable=False)
    headlines    = Column('headline',      String(255), nullable=False)
    subject      = Column('category',      String(50),  nullable=False)
    body         = Column('content',       Text,   nullable=False)

    # relationships (back_populates must match attribute names in SentTo & Engagement)
    recipients   = db.relationship('SentTo',     back_populates='newsletter', lazy=True)
    engagements  = db.relationship('Engagement', back_populates='newsletter', lazy=True)

    def __repr__(self):
        return f'<Newsletter {self.newsletterID}: "{self.headlines}">'

@app.route('/newsletter', endpoint='newsletter_page', methods=['GET', 'POST'])
@login_required
@admin_required
def newsletter_page():
    """Newsletter Report"""
    if request.method == 'POST':
        # collect form data
        headlines = request.form.get('headlines', '').strip()
        subject   = request.form.get('subject',   '').strip()
        body      = request.form.get('body',      '').strip()
        date_str  = request.form.get('date') or datetime.utcnow().date().isoformat()

        # create and flush new newsletter record
        nl = Newsletter(
            headlines = headlines,
            subject   = subject,
            body      = body,
            date      = datetime.fromisoformat(date_str).date()
        )
        db.session.add(nl)
        db.session.flush()

        # determine recipients
        choice = request.form.get('recipient_group')
        if choice == 'all':
            targets = Alumni.query.all()
        else:
            targets = Alumni.query.filter(Alumni.newsLetterYN == 'Y').all()

        # seed SentTo records
        for alum in targets:
            record = SentTo(
                newsletterID = nl.newsletterID,
                alumniID     = alum.alumniID,
                date         = datetime.utcnow().date(),
                clickedYN    = 'N'
            )
            db.session.add(record)

        db.session.commit()
        flash(f'Newsletter "{headlines}" sent to {len(targets)} alumni.', 'success')
        return redirect(url_for('newsletter_page'))

    # GET: display form + last five newsletters
    recent = Newsletter.query.order_by(Newsletter.date.desc()).limit(5).all()
    return render_template('newsletter.html', articles=recent)