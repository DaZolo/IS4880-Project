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
    __tablename__ = 'newsLetter'
    newsletterID = Column('id',            Integer, primary_key=True)
    date         = Column('newsDate',      Date,    nullable=False)
    headlines    = Column('headline',      String(255), nullable=False)
    subject      = Column('category',      String(50),  nullable=False)
    body         = Column('content',       Text,   nullable=False)
    recipients   = db.relationship('SentTo',     back_populates='newsletter', lazy=True)
    engagements  = db.relationship('Engagement', back_populates='newsletter', lazy=True)

    def __repr__(self):
        return f'<Newsletter {self.newsletterID}: "{self.headlines}">'

@app.route('/newsletter', endpoint='newsletter_page', methods=['GET', 'POST'])
@login_required
@admin_required
def newsletter_page():
    if request.method == 'POST':
        headlines = request.form.get('headlines', '').strip()
        subject   = request.form.get('subject',   '').strip()
        body      = request.form.get('body',      '').strip()
        date_str  = request.form.get('date') or datetime.utcnow().date().isoformat()
        nl = Newsletter(
            headlines = headlines,
            subject   = subject,
            body      = body,
            date      = datetime.fromisoformat(date_str).date()
        )
        db.session.add(nl)
        db.session.flush()

        choice = request.form.get('recipient_group')
        if choice == 'all':
            targets = Alumni.query.all()
        else:
            targets = Alumni.query.filter(Alumni.newsLetterYN == 'Y').all()

        for alum in targets:
            record = SentTo(
                newsletterID = nl.newsletterID,
                alumniID     = alum.alumniID,
                date         = datetime.utcnow().date(),
                clickedYN    = 'N'
            )
            db.session.add(record)

        eng = Engagement(
            newsletterID = nl.newsletterID,
            date         = datetime.utcnow().date(),
            recipients   = len(targets),
            clicks       = 0
        )
        db.session.add(eng)

        db.session.commit()
        flash(f'Newsletter "{headlines}" sent to {len(targets)} alumni.', 'success')
        return redirect(url_for('newsletter_page'))

    recent = Newsletter.query.order_by(Newsletter.date.desc()).limit(5).all()
    return render_template('newsletter.html', articles=recent)

@app.route('/newsletter/<int:nid>', endpoint='newsletter_detail', methods=['GET'])
@login_required
@admin_required
def newsletter_detail(nid):
    nl = Newsletter.query.get_or_404(nid)
    return render_template('newsletter_detail.html', article=nl)