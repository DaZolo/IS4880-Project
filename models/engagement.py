# File: models/engagement.py

from datetime import datetime
from app import app, admin_required
from flask_login import login_required
from flask import render_template, request, flash
# File: models/engagement.py

from models.db import db
from sqlalchemy import Column, Integer, String, Date, ForeignKey
from sqlalchemy.orm import relationship

class Engagement(db.Model):
    __tablename__ = 'engagement'

    engagementID = Column(Integer, primary_key=True)
    newsletterID = Column(Integer, ForeignKey('newsletter.newsletterID'), nullable=False)
    alumniID     = Column(Integer, ForeignKey('alumni.alumniID'),     nullable=False)
    date         = Column(Date)
    clickedYN    = Column(String(1))

    # relationships
    alumni     = relationship('Alumni',     back_populates='engagements')
    newsletter = relationship('Newsletter', back_populates='engagements')

    def __repr__(self):
        return (f'<Engagement {self.engagementID} | '
                f'Newsletter {self.newsletterID} → Alumni {self.alumniID} | '
                f'Clicked: {self.clickedYN}>')


@app.route('/engagement', endpoint='engagement_page', methods=['GET'])
@login_required
@admin_required
def engagement_page():
    """Report 4: Newsletter Engagement stats with optional headline filter."""
    start          = request.args.get('start', '').strip()
    end            = request.args.get('end',   '').strip()
    headline_query = request.args.get('headline', '').strip()

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
        q = q.filter(Newsletter.headline.ilike(f'%{headline_query}%'))

    engagements = q.order_by(Engagement.date.desc()).all()

    return render_template(
        'engagement.html',
        engagements    = engagements,
        start          = start,
        end            = end,
        headline_query = headline_query
    )
