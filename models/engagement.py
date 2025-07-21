from datetime import date, datetime
from app import app, admin_required
from flask_login import login_required
from flask import render_template, request, flash, jsonify

from models.db import db
from sqlalchemy import Column, Integer, Date, ForeignKey
from sqlalchemy.orm import relationship

class Engagement(db.Model):
    __tablename__ = 'engagement'

    id           = Column('id', Integer, primary_key=True)
    newsletterID = Column('newsletterID', Integer, ForeignKey('newsLetter.id'), nullable=False)
    date         = Column('date', Date, nullable=False, default=date.today)
    recipients   = Column('recipients', Integer, nullable=False, default=0)
    clicks       = Column('clicks', Integer, nullable=False, default=0)

    newsletter   = relationship('Newsletter', back_populates='engagements', lazy=True)

    def __repr__(self):
        return (f"<Engagement id={self.id} newsletter={self.newsletterID} "
                f"date={self.date} recipients={self.recipients} clicks={self.clicks}>")

@app.route('/engagement', endpoint='engagement_page', methods=['GET'])
@login_required
@admin_required
def engagement_page():
    start          = request.args.get('start', '').strip()
    end            = request.args.get('end',   '').strip()
    headline_query = request.args.get('headline', '').strip()

    from models.newsletter import Newsletter

    q = Engagement.query
    if start:
        try:
            q = q.filter(Engagement.date >= datetime.fromisoformat(start))
        except ValueError:
            flash('Invalid start date; use YYYY-MM-DD', 'warning')
    if end:
        try:
            q = q.filter(Engagement.date <= datetime.fromisoformat(end))
        except ValueError:
            flash('Invalid end date; use YYYY-MM-DD', 'warning')
    existing_engs = q.order_by(Engagement.date.desc()).all()

    eng_ids = {e.newsletterID for e in existing_engs}

    news_q = Newsletter.query.order_by(Newsletter.date.desc())
    if start:
        try:
            news_q = news_q.filter(Newsletter.date >= datetime.fromisoformat(start).date())
        except ValueError:
            pass
    if end:
        try:
            news_q = news_q.filter(Newsletter.date <= datetime.fromisoformat(end).date())
        except ValueError:
            pass
    newsletters = news_q.all()

    missing_engs = []
    for nl in newsletters:
        if nl.newsletterID in eng_ids:
            continue
        if headline_query and headline_query.lower() not in nl.headlines.lower():
            continue
        fake = Engagement(
            newsletterID = nl.newsletterID,
            date         = nl.date,
            recipients   = 0,
            clicks       = 0
        )
        fake.newsletter = nl
        missing_engs.append(fake)
    all_engs = existing_engs + missing_engs
    all_engs.sort(key=lambda e: e.date, reverse=True)

    return render_template(
        'engagement.html',
        engagements    = all_engs,
        start          = start,
        end            = end,
        headline_query = headline_query
    )

@app.route('/api/reports/engagement', endpoint='engagement_api', methods=['GET'])
@login_required
@admin_required
def engagement_api():
    start          = request.args.get('start', '').strip()
    end            = request.args.get('end',   '').strip()
    nid            = request.args.get('NID',   '').strip()
    headline_query = request.args.get('headline', '').strip()

    from models.newsletter import Newsletter

    q = Engagement.query
    if start:
        try:
            q = q.filter(Engagement.date >= datetime.fromisoformat(start))
        except ValueError:
            pass
    if end:
        try:
            q = q.filter(Engagement.date <= datetime.fromisoformat(end))
        except ValueError:
            pass
    if nid:
        try:
            q = q.filter(Engagement.newsletterID == int(nid))
        except ValueError:
            pass

    results = []
    for rec in q.order_by(Engagement.date.desc()).all():
        # Filter by headline if provided
        if headline_query and headline_query.lower() not in rec.newsletter.headlines.lower():
            continue
        rate = rec.clicks / rec.recipients * 100 if rec.recipients else 0
        results.append({
            'newsletterID': rec.newsletterID,
            'headline':     rec.newsletter.headlines,
            'date':         rec.date.isoformat(),
            'recipients':   rec.recipients,
            'clicks':       rec.clicks,
            'click_rate':   round(rate, 1)
        })
    return jsonify(results)