from app.extensions import db
from datetime import datetime

from sqlalchemy.dialects.postgresql import JSON


class Asset(db.Model):
    __tablename__= 'assets'
    id = db.Column(db.Integer, primary_key = True)
    name = db.Column(db.String(64), nullable = False)

    def __repr__(self) -> str:
        return '<Asset %r>' % self.id

    def serialize(self):
        return {
            "name": self.name
        }

