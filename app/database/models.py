from sqlalchemy import Table, Column, Integer, String
from sqlalchemy.orm import mapper
#from ..database.database import metadata, db_session
from ..__init__ import db

class Tracker(db.Model):
    __tablename__ = 'trackers'
    query = db.session.query_property()
    room = db.Column(db.String(40), primary_key=True)
    ip = db.Column(db.String(12), nullable=False, unique=False)
    port = db.Column(db.Integer, nullable=False, unique=False)
    
    def to_json(self):
        return {
            'room': self.room,
            'ip': self.ip,
            'port': self.port,
        }