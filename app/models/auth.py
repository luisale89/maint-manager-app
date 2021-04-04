
from app.extensions import db
from datetime import datetime

from werkzeug.security import generate_password_hash
from sqlalchemy.dialects.postgresql import JSON


class User(db.Model):
    __tablename__ = 'user'
    id = db.Column(db.Integer, primary_key=True)
    public_id = db.Column(db.String(60), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    fname = db.Column(db.String(60), nullable=False)
    lname = db.Column(db.String(60), nullable=False)
    user_since = db.Column(db.DateTime, default=datetime.utcnow)
    #relationships
    profile = db.relationship('Profile', back_populates='user', uselist=False, lazy=True) #1-1 with profile

    def __repr__(self):
        return '<User %r>' % self.public_id

    def serialize(self):
        return {
            "public_id" : self.public_id,
            "fname" : self.fname,
            "lname" : self.lname,
            "user_since": self.user_since,
            "profile": self.profile.serialize()
        }

    @property
    def password(self):
        raise AttributeError('Cannot view password')

    @password.setter
    def password(self, password):
        self.password_hash = generate_password_hash(password, method='sha256')


class Profile(db.Model):
    __tablename__ = 'profile'
    id = db.Column(db.Integer, primary_key=True)
    profile_img = db.Column(db.String(120))
    home_address = db.Column(JSON)
    personal_phone = db.Column(db.String(30))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    #relationships
    user = db.relationship('User', back_populates='profile', uselist=False, lazy=True) #1-1 with user

    def __repr__(self):
        return '<Profile %r>' % self.id

    def serialize(self):
        return {
            "profile_img": self.profile_img if self.profile_img is not None else "https://server.com/default.png",
            'home_address': self.home_address,
            'personal_phone': self.personal_phone
        }


class TokenBlacklist(db.Model):
    __tablename__ = 'tokenblacklist'
    id = db.Column(db.Integer, primary_key=True)
    jti = db.Column(db.String(36), nullable=False)
    token_type = db.Column(db.String(10), nullable=False)
    user_identity = db.Column(db.String(50), nullable=False)
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