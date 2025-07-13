# File: models/donation.py

from datetime import datetime
from app import app, admin_required
from flask_login import login_required
from flask import request, render_template, redirect, url_for, flash

from models.db import db
from sqlalchemy import Column, Integer, ForeignKey, Numeric, Date, String
from sqlalchemy.orm import relationship

class Donation(db.Model):
    __tablename__ = 'donation'

    donationID   = Column(Integer, primary_key=True)
    alumniID     = Column(Integer, ForeignKey('alumni.alumniID'), nullable=False)
    amount       = Column(Numeric(10, 2), nullable=False)
    date         = Column(Date, nullable=False)
    reason       = Column(String(255))

    # Establish bidirectional relationship with Alumni.donations
    alumni       = relationship('Alumni', back_populates='donations')

    def __repr__(self):
        return (f'<Donation {self.donationID} | '
                f'Alumni {self.alumniID} | '
                f'Amount {self.amount} | '
                f'Date {self.date}>')

@app.route('/donations', endpoint='donations_page', methods=['GET', 'POST'])
@login_required
@admin_required
def donations_page():
    """Report 3: Donations with filters and pagination."""
    # Handle new‐donation form
    if request.method == 'POST':
        alumni_id   = request.form.get('alumniID')
        amount      = request.form.get('donationAmount')
        date_str    = request.form.get('donationDate')
        dtype       = request.form.get('donationType')
        comments    = request.form.get('comments')
        if alumni_id and amount and date_str:
            try:
                new_d = Donation(
                    alumniID     = int(alumni_id),
                    donationAmt  = float(amount),
                    donationDate = datetime.fromisoformat(date_str),
                    donationType = dtype or "",
                    comments     = comments or ""
                )
                db.session.add(new_d)
                db.session.commit()
                flash('Donation record added successfully.', 'success')
            except Exception as e:
                db.session.rollback()
                flash(f'Error adding donation: {e}', 'danger')
        else:
            flash('Please provide Alumni ID, Amount, and Date.', 'warning')
        return redirect(url_for('donations_page'))

    # GET → apply filters & paginate
    start        = request.args.get('start', '').strip()
    end          = request.args.get('end',   '').strip()
    reason_query = request.args.get('reason', '').strip()
    min_retention= request.args.get('minRetention', '').strip()
    page         = request.args.get('page', 1, type=int)

    q = Donation.query
    if start:
        try:
            q = q.filter(Donation.donationDate >= datetime.fromisoformat(start))
        except ValueError:
            flash('Invalid start date; use YYYY‑MM‑DD', 'warning')
    if end:
        try:
            q = q.filter(Donation.donationDate <= datetime.fromisoformat(end))
        except ValueError:
            flash('Invalid end date; use YYYY‑MM‑DD', 'warning')
    if reason_query:
        q = q.filter(Donation.comments.ilike(f'%{reason_query}%'))

    pagination = q.order_by(Donation.donationDate.desc()) \
                  .paginate(page=page, per_page=10, error_out=False)
    page_items  = pagination.items
    total_pages = pagination.pages

    # Stub metrics maps (fill in with your actual logic if needed)
    retention_map = {}
    avg_map       = {}
    total_map     = {}

    return render_template(
        'donations.html',
        donations     = page_items,
        start         = start,
        end           = end,
        reason_query  = reason_query,
        min_retention = min_retention,
        page          = page,
        total_pages   = total_pages,
        retention_map = retention_map,
        avg_map       = avg_map,
        total_map     = total_map
    )