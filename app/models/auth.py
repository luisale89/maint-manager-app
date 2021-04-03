
from app.extensions import db
from datetime import datetime

from werkzeug.security import generate_password_hash
# from sqlalchemy.dialects.postgresql import JSON #only for postgresql


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    public_id = db.Column(db.String(60), unique=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(256))
    fname = db.Column(db.String(60), nullable=False)
    lname = db.Column(db.String(60), nullable=False)
    profile_img = db.Column(db.String(120))
    user_since = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return '<User %r>' % self.public_id

    def serialize(self):
        return {
            "public_id" : self.public_id,
            "fname" : self.fname,
            "lname" : self.lname,
            "profile_img": self.profile_img if self.profile_img is not None else "https://server.com/default.png",
            "user_since": self.user_since
        }

    @property
    def password(self):
        raise AttributeError('Cannot view password')

    @password.setter
    def password(self, password):
        self.password_hash = generate_password_hash(password, method='sha256')


class TokenBlacklist(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    jti = db.Column(db.String(36), nullable=False)
    token_type = db.Column(db.String(10), nullable=False)
    user_identity = db.Column(db.String(50), nullable=False)
    revoked = db.Column(db.Boolean, nullable=False)
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
            'expires': self.expires
        }