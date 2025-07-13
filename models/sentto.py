# File: models/sentto.py

from models.db import db
from sqlalchemy import Column, Integer, ForeignKey, Date, String
from sqlalchemy.orm import relationship

class SentTo(db.Model):
    __tablename__ = 'sentTo'  # match your actual table name

    sentToID     = Column(Integer, primary_key=True)
    newsletterID = Column(Integer, ForeignKey('newsletter.newsletterID'), nullable=False)
    alumniID     = Column(Integer, ForeignKey('alumni.alumniID'),     nullable=False)
    date         = Column(Date,    nullable=False)
    clickedYN    = Column(String(1), nullable=False)

    # back‑populates must point to the attribute names on the other side
    alumni     = relationship('Alumni',     back_populates='sentto')
    newsletter = relationship('Newsletter', back_populates='recipients')

    def __repr__(self):
        return (f'<SentTo {self.sentToID} | '
                f'NL {self.newsletterID} → Alumni {self.alumniID} | '
                f'Clicked: {self.clickedYN}>')
