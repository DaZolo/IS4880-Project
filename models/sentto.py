from datetime import date
from models.db import db
from sqlalchemy import Column, Integer, Date, String, ForeignKey
from sqlalchemy.orm import relationship

class SentTo(db.Model):
    __tablename__ = 'sentTo'

    sentToID     = Column('sentToID',  Integer, primary_key=True)

    newsletterID = Column('newsletterID', Integer, ForeignKey('newsLetter.id'), nullable=False)
    alumniID     = Column('alumniID',     Integer, ForeignKey('alumni.alumniID'), nullable=False)

    sentDate     = Column('sentDate',     Date,    nullable=False, default=date.today)
    clickedYN    = Column('clickedYN',    String(1), nullable=False, default='N')

    newsletter = relationship('Newsletter', back_populates='recipients', lazy=True)
    alumni     = relationship('Alumni',     back_populates='sentto',    lazy=True)

    def __repr__(self):
        return (
            f"<SentTo id={self.sentToID} "
            f"newsletter={self.newsletterID} "
            f"alumni={self.alumniID} "
            f"sentDate={self.sentDate} clickedYN={self.clickedYN}>"
        )