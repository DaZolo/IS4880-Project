from models.db import db

class Address(db.Model):
    __tablename__ = 'address'
    addressID = db.Column(db.Integer, primary_key=True)
    alumniID = db.Column(db.Integer, db.ForeignKey('alumni.alumniID'))
    address = db.Column(db.String(255))
    city = db.Column(db.String(100))
    state = db.Column(db.String(50))
    zipCode = db.Column(db.String(20))
    activeYN = db.Column(db.String(1))
    primaryYN = db.Column(db.String(1))
    alumni = db.relationship('Alumni', back_populates='addresses', lazy=True)