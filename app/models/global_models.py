from app.extensions import db
from datetime import datetime
from sqlalchemy.orm import backref


class Role(db.Model):
    __tablename__ = "role"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(128))
    global_role = db.Column(db.Boolean)
    creation_date = db.Column(db.DateTime, default=datetime.utcnow)
    creator_user = db.Column(db.Integer)

    def __repr__(self) -> str:
        return f"<Role {self.name}>"

    def serialize(self) -> dict:
        return {
            'name': self.name,
            'creation_date': self.creation_date
        }


class Permit(db.Model):
    __tablename__ = "permit"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(128))
    description = db.Column(db.Text)

    def __repr__(self) -> str:
        return f'<Permit {self.name}>'

    def serialize(self) -> dict:
        return {
            'name': self.name,
            'description': self.description
        }