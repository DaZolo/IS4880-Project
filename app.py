import os
import sys
from datetime import datetime, timedelta
from flask import (
    Flask, render_template, request, redirect,
    url_for, flash, session, abort, jsonify
)
from flask_login import (
    LoginManager, login_user, logout_user,
    login_required, current_user
)
from werkzeug.security import check_password_hash
from flask_wtf.csrf import CSRFProtect, generate_csrf

sys.modules['app'] = sys.modules[__name__]

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'supersecretkey')
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get(
    'DATABASE_URL',
    'mysql+pymysql://alumni_user:StrongPassword!@localhost/alumni_db'
)
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SESSION_COOKIE_SECURE']   = True
app.config['SESSION_COOKIE_HTTPONLY'] = True
app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(minutes=30)

from models.db import db
db.init_app(app)
csrf = CSRFProtect(app)
app.jinja_env.globals['csrf_token'] = generate_csrf

login_manager = LoginManager()
login_manager.login_view = 'login'
login_manager.init_app(app)

@login_manager.user_loader
def load_user(user_id):
    from models.user import User
    try:
        return User.query.get(int(user_id))
    except:
        return None

def admin_required(func):
    from functools import wraps
    @wraps(func)
    def wrapper(*args, **kwargs):
        if not current_user.is_authenticated or getattr(current_user, 'role', '') != 'admin':
            abort(403)
        return func(*args, **kwargs)
    return wrapper

@app.before_request
def make_session_permanent():
    session.permanent = True
    if current_user.is_authenticated:
        last_active = session.get('last_active')
        now = datetime.utcnow()
        if last_active:
            try:
                last_dt = datetime.fromisoformat(last_active)
            except:
                last_dt = now
            if now - last_dt > app.config['PERMANENT_SESSION_LIFETIME']:
                logout_user()
                session.clear()
                flash('Session timed out due to inactivity. Please log in again.', 'warning')
                return redirect(url_for('login'))
        session['last_active'] = now.isoformat()

@app.route('/', methods=['GET'])
def home():
    if not current_user.is_authenticated:
        return redirect(url_for('login'))
    return redirect(url_for('alumni_directory'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    from models.user import User

    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        user = None

        if username:
            if username.isdigit():
                user = User.query.get(int(username))
            if not user:
                user = User.query.filter(
                    (User.fName == username) |
                    (User.lName == username)
                ).first()

        if not user or not check_password_hash(user.password, password):
            flash('Invalid credentials. Please try again.', 'danger')
            return render_template('login.html')

        login_user(user)
        session.permanent = True
        flash(f'Welcome, {user.fName}!', 'success')
        return redirect(url_for('alumni_directory'))

    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    session.clear()
    flash('You have been logged out.', 'info')
    return redirect(url_for('login'))

@app.route('/api/reports/alumni')
@login_required
@admin_required
def api_alumni():
    from sqlalchemy import extract
    from models.alumni import Alumni
    from models.degree import Degree

    name    = request.args.get('name', '').strip()
    year_f  = request.args.get('yearFrom', '').strip()
    year_t  = request.args.get('yearTo', '').strip()
    major   = request.args.get('major', '').strip()
    page    = request.args.get('page', 1, type=int)
    per_pg  = request.args.get('per_page', 10, type=int)

    query = Alumni.query

    if name:
        query = query.filter(
            (Alumni.fName.ilike(f'%{name}%')) |
            (Alumni.lName.ilike(f'%{name}%'))
        )
    if year_f:
        try:
            yf = int(year_f)
            query = query.filter(extract('year', Degree.graduationDT) >= yf)
        except ValueError:
            pass
    if year_t:
        try:
            yt = int(year_t)
            query = query.filter(extract('year', Degree.graduationDT) <= yt)
        except ValueError:
            pass
    if major:
        query = query.filter(
            Alumni.degrees.any(Degree.major.ilike(f'%{major}%'))
        )

    query = query.order_by(Alumni.lName.asc(), Alumni.fName.asc())
    pagination = query.paginate(page=page, per_page=per_pg, error_out=False)

    alumni_data = []
    for a in pagination.items:
        ld = a.latest_degree
        alumni_data.append({
            "id": a.alumniID,
            "firstName": a.fName,
            "lastName": a.lName,
            "phone": a.phone,
            "major": ld.major if ld else None,
            "gradYear": ld.graduationDT.year if ld else None
        })

    return jsonify({
        "page": pagination.page,
        "pages": pagination.pages,
        "total": pagination.total,
        "per_page": pagination.per_page,
        "alumni": alumni_data
    })

import models.address
import models.alumni
import models.degree
import models.donation
import models.employment
import models.engagement
import models.newsletter
import models.sentto
import models.skillset
import models.user

if __name__ == '__main__':
    from waitress import serve
    print("The server is now running.")
    serve(app, host='0.0.0.0', port=5000)