from enum import unique

from sqlalchemy.orm import backref
from app.extensions import db
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
        return '<Token %r>' % self.token_type

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


class Country(db.Model):
    __tablename__ = 'country'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(128), nullable=False, unique=True)
    code = db.Column(db.String(24), unique=True)
    #relations

    def __repr__(self) -> str:
        return '<Country %r>' % self.id

    def serialize(self):
        return {
            "id": self.id,
            "name": self.name,
            "code": self.code
        }


class Category(db.Model):
    __tablename__ = 'category'
    id = db.Column(db.Integer, primary_key=True)
    value = db.Column(db.String(128), nullable=False)
    parent_id = db.Column(db.Integer, db.ForeignKey('category.id'))
    #relations
    children = db.relationship('Category', cascade="all, delete-orphan", backref=backref('parent', remote_side=id))

    def __repr__(self) -> str:
        return '<Category %r>' % self.value

    def serialize(self) -> dict:
        return {
            "id": self.id,
            "value": self.value
        }


class Variable(db.Model):
    __tablename__ = 'variable'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(128), nullable=False)
    unit = db.Column(db.String(128))

    def __repr__(self) -> str:
        return '<Variable %r>' % self.id

    def serialize(self) -> dict:
        return {
            "id": self.id,
            "name": self.name,
            "unit": self.unit
        }