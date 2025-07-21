from datetime import datetime
from flask import request, render_template, redirect, url_for, flash
from flask_login import login_required
from app import app, admin_required

from models.db import db
from sqlalchemy import func
from models.degree import Degree
from models.alumni import Alumni

class Donation(db.Model):
    __tablename__ = 'donation'

    donationID   = db.Column(db.Integer, primary_key=True)
    alumniID     = db.Column(db.Integer, db.ForeignKey('alumni.alumniID'), nullable=False)
    donationAmt  = db.Column('donationAmt', db.Numeric(10, 2), nullable=False)
    donationDT   = db.Column('donationDT', db.Date, nullable=False)
    reason       = db.Column(db.String(255))
    description  = db.Column(db.Text)

    alumni       = db.relationship('Alumni', back_populates='donations')

    def __repr__(self):
        return (f'<Donation #{self.donationID} '
                f'alumni={self.alumniID} '
                f'amt={self.donationAmt} '
                f'date={self.donationDT}>')

@app.route('/donations', endpoint='donations_page', methods=['GET', 'POST'])
@login_required
@admin_required
def donations_page():
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

    start         = request.args.get('start', '').strip()
    end           = request.args.get('end',   '').strip()
    reason_query  = request.args.get('reason','').strip()
    degree_type   = request.args.get('degree','').strip()
    grad_year     = request.args.get('gradYear','').strip()
    min_retention = request.args.get('minRetention', 0, type=float)
    page          = request.args.get('page', 1, type=int)

    q = Donation.query.join(Alumni).join(Degree)

    if start:
        try:
            q = q.filter(Donation.donationDT >= datetime.fromisoformat(start))
        except ValueError:
            flash('Invalid start date; use YYYY-MM-DD format.', 'warning')
    if end:
        try:
            q = q.filter(Donation.donationDT <= datetime.fromisoformat(end))
        except ValueError:
            flash('Invalid end date; use YYYY-MM-DD format.', 'warning')
    if reason_query:
        q = q.filter(Donation.reason.ilike(f'%{reason_query}%'))
    if degree_type:
        q = q.filter(Degree.major == degree_type)
    if grad_year:
        try:
            q = q.filter(func.year(Degree.graduationDT) == int(grad_year))
        except ValueError:
            flash('Invalid graduation year.', 'warning')

    all_donations = Donation.query.join(Alumni).join(Degree).all()
    donors_global = {}
    for d in all_donations:
        donors_global.setdefault(d.alumniID, []).append(d)

    current_year      = datetime.now().year
    retention_global  = {}
    avg_global        = {}
    total_global      = {}

    for alumni_id, don_list in donors_global.items():
        years_donated   = {d.donationDT.year for d in don_list}
        alum            = don_list[0].alumni
        grad_year_alum  = alum.degrees[0].graduationDT.year if alum.degrees else current_year
        years_since     = max(current_year - grad_year_alum + 1, 1)

        retention_val = (len(years_donated) / years_since * 100) if years_since > 0 else 0
        total_amt     = sum(float(x.donationAmt) for x in don_list)
        avg_val       = (total_amt / len(years_donated)) if years_donated else 0

        retention_global[alumni_id] = round(retention_val, 1)
        avg_global[alumni_id]       = round(avg_val, 2)
        total_global[alumni_id]     = round(total_amt, 2)

    if min_retention > 0:
        allowed_ids = [aid for aid, ret in retention_global.items() if ret >= min_retention]
        if allowed_ids:
            q = q.filter(Donation.alumniID.in_(allowed_ids))
        else:
            q = q.filter(Donation.donationID == None)

    pagination  = q.order_by(Donation.donationDT.desc()) \
                    .paginate(page=page, per_page=10, error_out=False)
    donations   = pagination.items
    total_pages = pagination.pages

    degree_types     = [d.major for d in Degree.query.with_entities(Degree.major)
                        .distinct().order_by(Degree.major).all()]
    graduation_years = sorted(
        y[0] for y in db.session.query(func.year(Degree.graduationDT))
                        .distinct().all() if y[0] is not None
    )

    return render_template(
        'donations.html',
        donations        = donations,
        start            = start,
        end              = end,
        reason_query     = reason_query,
        degree_types     = degree_types,
        graduation_years = graduation_years,
        degree_type      = degree_type,
        grad_year        = grad_year,
        min_retention    = min_retention,
        page             = page,
        total_pages      = total_pages,
        retention_map    = retention_global,
        avg_map          = avg_global,
        total_map        = total_global
    )