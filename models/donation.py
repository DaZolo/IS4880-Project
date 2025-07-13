# File: models/donation.py

from datetime import datetime
from flask import request, render_template, redirect, url_for, flash
from flask_login import login_required
from app import app, admin_required

from models.db import db
from sqlalchemy import Column, Integer, ForeignKey, Numeric, Date, String, Text
from sqlalchemy.orm import relationship

class Donation(db.Model):
    __tablename__ = 'donation'

    donationID   = Column(Integer, primary_key=True)
    alumniID     = Column(Integer, ForeignKey('alumni.alumniID'), nullable=False)
    donationAmt  = Column('donationAmt', Numeric(10, 2), nullable=False)
    donationDT   = Column('donationDT', Date, nullable=False)
    reason       = Column(String(255))
    description  = Column(Text)

    # Bidirectional relationship with Alumni.donations
    alumni       = relationship('Alumni', back_populates='donations')

    def __repr__(self):
        return (f'<Donation #{self.donationID} '
                f'alumni={self.alumniID} '
                f'amt={self.donationAmt} '
                f'date={self.donationDT}>')

@app.route('/donations', endpoint='donations_page', methods=['GET', 'POST'])
@login_required
@admin_required
def donations_page():
    """Report 3: Donations listing with filters and pagination."""
    # Handle new‐donation form submission
    if request.method == 'POST':
        alumni_id        = request.form.get('alumniID')
        amount           = request.form.get('donationAmount')
        date_str         = request.form.get('donationDate')
        reason_text      = request.form.get('reason')
        description_text = request.form.get('description')

        if alumni_id and amount and date_str:
            try:
                new_d = Donation(
                    alumniID    = int(alumni_id),
                    donationAmt = float(amount),
                    donationDT  = datetime.fromisoformat(date_str),
                    reason      = reason_text      or "",
                    description = description_text or ""
                )
                db.session.add(new_d)
                db.session.commit()
                flash('Donation recorded successfully.', 'success')
            except Exception as e:
                db.session.rollback()
                flash(f'Error adding donation: {e}', 'danger')
        else:
            flash('Alumni ID, Amount, and Date are required.', 'warning')

        return redirect(url_for('donations_page'))

    # GET: apply filters and paginate
    start        = request.args.get('start', '').strip()
    end          = request.args.get('end',   '').strip()
    reason_query = request.args.get('reason','').strip()
    page         = request.args.get('page', 1, type=int)

    q = Donation.query

    if start:
        try:
            q = q.filter(Donation.donationDT >= datetime.fromisoformat(start))
        except ValueError:
            flash('Invalid start date; use YYYY‑MM‑DD format.', 'warning')
    if end:
        try:
            q = q.filter(Donation.donationDT <= datetime.fromisoformat(end))
        except ValueError:
            flash('Invalid end date; use YYYY‑MM‑DD format.', 'warning')
    if reason_query:
        q = q.filter(Donation.reason.ilike(f'%{reason_query}%'))

    pagination = q.order_by(Donation.donationDT.desc()) \
                  .paginate(page=page, per_page=10, error_out=False)

    donations   = pagination.items
    total_pages = pagination.pages

    # Placeholder maps for donor‐retention, averages, totals
    retention_map = {}
    avg_map       = {}
    total_map     = {}

    return render_template(
        'donations.html',
        donations     = donations,
        start         = start,
        end           = end,
        reason        = reason_query,
        page          = page,
        total_pages   = total_pages,
        retention_map = retention_map,
        avg_map       = avg_map,
        total_map     = total_map
    )