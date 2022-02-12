from app.extensions import db
from datetime import datetime
from sqlalchemy.orm import backref
from sqlalchemy.dialects.postgresql import JSON


class TokenBlacklist(db.Model):
    __tablename__ = 'tokenblacklist'
    id = db.Column(db.Integer, primary_key=True)
    jti = db.Column(db.String(36), nullable=False)
    token_type = db.Column(db.String(10), nullable=False)
    user_identity = db.Column(db.String(64), nullable=False)
    revoked = db.Column(db.Boolean, nullable=False)
    revoked_date = db.Column(db.DateTime)
    expires = db.Column(db.DateTime, nullable=False)

    def __repr__(self):
        # return '<Token %r>' % self.token_type
        return f"<Token {self.token_type}>"

    def serialize(self):
        return {
            'token_id': self.id,
            'jti': self.jti,
            'token_type': self.token_type,
            'user_identity': self.user_identity,
            'revoked': self.revoked,
            'revoked_date': self.revoked_date,
            'expires': self.expires
        }


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