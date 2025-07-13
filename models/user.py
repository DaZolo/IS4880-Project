from models.db import db
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

class User(db.Model, UserMixin):
    __tablename__ = 'user'
    UID = db.Column(db.Integer, primary_key=True)
    password = db.Column(db.String(255), nullable=False)
    fName = db.Column(db.String(100))
    lName = db.Column(db.String(100))
    jobDescription = db.Column(db.String(255))
    viewPriveledgeYN = db.Column(db.String(1), default='N')
    insertPriveledgeYN = db.Column(db.String(1), default='N')
    updatePriveledgeYN = db.Column(db.String(1), default='N')
    deletePriveledgeYN = db.Column(db.String(1), default='N')

    def __init__(self, password=None, fName=None, lName=None, jobDescription=None, **kwargs):
        self.fName = fName
        self.lName = lName
        self.jobDescription = jobDescription
        if password:
            self.set_password(password)
        for key, value in kwargs.items():
            if hasattr(self, key):
                setattr(self, key, value)

    def set_password(self, raw_password):
        self.password = generate_password_hash(raw_password)

    def check_password(self, raw_password):
        return check_password_hash(self.password, raw_password)

    @property
    def role(self):
        if (self.insertPriveledgeYN == 'Y' or self.updatePriveledgeYN == 'Y' or self.deletePriveledgeYN == 'Y'):
            return 'admin'
        else:
            return 'user'

    def get_id(self):
        return str(self.UID)