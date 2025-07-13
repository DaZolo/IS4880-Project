# File: models/engagement.py

from datetime import date, datetime
from app import app, admin_required
from flask_login import login_required
from flask import render_template, request, flash, jsonify

from models.db import db
from sqlalchemy import Column, Integer, Date, ForeignKey
from sqlalchemy.orm import relationship

class Engagement(db.Model):
    __tablename__ = 'engagement'

    # primary key
    id           = Column('id', Integer, primary_key=True)
    # link back to newsletter.id
    newsletterID = Column('newsletterID', Integer, ForeignKey('newsLetter.id'), nullable=False)
    date         = Column('date',         Date,    nullable=False, default=date.today)
    recipients   = Column('recipients',   Integer, nullable=False, default=0)
    clicks       = Column('clicks',       Integer, nullable=False, default=0)

    # show newsletter headline in joins
    newsletter   = relationship('Newsletter', back_populates='engagements', lazy=True)

    def __repr__(self):
        return (f"<Engagement id={self.id} newsletter={self.newsletterID} "
                f"date={self.date} recipients={self.recipients} clicks={self.clicks}>")

@app.route('/engagement', endpoint='engagement_page', methods=['GET'])
@login_required
@admin_required
def engagement_page():
    """Report 4: Newsletter Engagement stats with optional headline filter."""
    start          = request.args.get('start', '').strip()
    end            = request.args.get('end',   '').strip()
    headline_query = request.args.get('headline', '').strip()

    # import here to avoid circular imports
    from models.newsletter import Newsletter

    q = Engagement.query.join(Newsletter)

    if start:
        try:
            q = q.filter(Engagement.date >= datetime.fromisoformat(start))
        except ValueError:
            flash('Invalid start date; use YYYY‑MM‑DD', 'warning')
    if end:
        try:
            q = q.filter(Engagement.date <= datetime.fromisoformat(end))
        except ValueError:
            flash('Invalid end date; use YYYY‑MM‑DD', 'warning')
    if headline_query:
        q = q.filter(Newsletter.headlines.ilike(f'%{headline_query}%'))

    engagements = q.order_by(Engagement.date.desc()).all()

    return render_template(
        'engagement.html',
        engagements    = engagements,
        start          = start,
        end            = end,
        headline_query = headline_query
    )

@app.route('/api/reports/engagement', endpoint='engagement_api', methods=['GET'])
@login_required
@admin_required
def engagement_api():
    """JSON API for Engagement report (filters: start, end, NID, headline)."""
    start          = request.args.get('start', '').strip()
    end            = request.args.get('end',   '').strip()
    nid            = request.args.get('NID',   '').strip()
    headline_query = request.args.get('headline', '').strip()

    from models.newsletter import Newsletter

    q = Engagement.query.join(Newsletter)

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
    if headline_query:
        q = q.filter(Newsletter.headlines.ilike(f'%{headline_query}%'))

    results = []
    for rec in q.order_by(Engagement.date.desc()).all():
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