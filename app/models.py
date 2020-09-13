from flask_sqlalchemy import SQLAlchemy

from werkzeug.security import generate_password_hash
from sqlalchemy.dialects.postgresql import JSON

db = SQLAlchemy()

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    fname = db.Column(db.String(60), nullable=False)
    lname = db.Column(db.String(60), nullable=False)
    phone = db.Column(db.String(20))
    p_language = db.Column(db.String(20))
    
    def __repr__(self):
        return '<User %r>' % self.lname

    def serialize(self):
        return {
            "id" : self.id,
            "email" : self.email,
            "fname" : self.fname,
            "lname" : self.lname,
            "p_lang" : self.p_language
        }

    @property
    def password(self):
        raise AttributeError('Cannot view password')

    @password.setter
    def password(self, password):
        self.password_hash = generate_password_hash(password)