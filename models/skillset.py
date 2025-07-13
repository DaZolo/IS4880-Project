# File: models/skillset.py

from models.db import db
from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship

class Skillset(db.Model):
    __tablename__ = 'skillset'

    skillsetID = Column(Integer, primary_key=True)
    alumniID   = Column(Integer, ForeignKey('alumni.alumniID'), nullable=False)
    skill      = Column(String(100), nullable=False)
    level      = Column(String(50))  # e.g. 'Beginner', 'Intermediate', 'Expert'

    # back-populates the Alumni.skillsets relationship
    alumni     = relationship('Alumni', back_populates='skillsets')

    def __repr__(self):
        return f'<Skillset {self.skillsetID}: {self.skill} ({self.level})>'