from models.db import db

class Degree(db.Model):
    __tablename__ = 'degree'

    degreeID     = db.Column(db.Integer, primary_key=True)
    alumniID     = db.Column(db.Integer, db.ForeignKey('alumni.alumniID'))
    major        = db.Column(db.String(100))
    minor        = db.Column(db.String(100))
    graduationDT = db.Column(db.Date)
    university   = db.Column(db.String(255))
    city         = db.Column(db.String(100))
    state        = db.Column(db.String(50))
    alumni = db.relationship('Alumni', back_populates='degrees', lazy=True)