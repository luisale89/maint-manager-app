
from app.extensions import db
from datetime import datetime

from werkzeug.security import generate_password_hash
from sqlalchemy.dialects.postgresql import JSON


class User(db.Model):
    __tablename__ = 'user'
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(256), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    fname = db.Column(db.String(128))
    lname = db.Column(db.String(128))
    profile_img = db.Column(db.String(256))
    home_address = db.Column(JSON)
    personal_phone = db.Column(db.String(32))
    since = db.Column(db.DateTime, default=datetime.utcnow)
    email_confirm = db.Column(db.Boolean)
    status = db.Column(db.String(12))
    #relations
    work_relations = db.relationship('WorkRelation', back_populates='user', lazy=False)

    def __repr__(self):
        return '<User %r>' % self.id

    def serialize(self):
        return {
            "id": self.id,
            "fname" : self.fname,
            "lname" : self.lname,
            "profile_img": self.profile_img if self.profile_img is not None else "https://server.com/default.png",
            "user_since": self.since,
            "user_status": self.status
        }

    def serialize_private(self):
        return {
            "email": self.email,
            "home_address": self.home_address,
            "personal_phone": self.personal_phone,
            "email_confirmed": self.email_confirm
        }

    @property
    def password(self):
        raise AttributeError('Cannot view password')

    @password.setter
    def password(self, password):
        self.password_hash = generate_password_hash(password, method='sha256')


class WorkRelation(db.Model):
    __tablename__ = 'work_relation'
    id = db.Column(db.Integer, primary_key=True)
    rel_date = db.Column(db.DateTime, default=datetime.utcnow)
    user_role = db.Column(db.String(24), nullable=False)
    user_salary = db.Column(db.Float, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    company_id = db.Column(db.Integer, db.ForeignKey('company.id'), nullable=False)
    #relations
    user = db.relationship('User', back_populates='work_relations', uselist=False, lazy=False)
    company = db.relationship('Company', back_populates='work_relations', uselist=False, lazy=False)

    def __repr__(self) -> str:
        return '<work_relation %r' % self.id

    def serialize(self) -> dict:
        return {
            "id": self.id,
            "rel_date": self.rel_date,
        }


class Company(db.Model):
    __tablename__ = 'company'
    id = db.Column(db.Integer, primary_key=True)
    company_name = db.Column(db.String(128), nullable=False)
    company_address = db.Column(JSON)
    start_date = db.Column(db.DateTime, default=datetime.utcnow)
    #relationships
    work_relations = db.relationship('WorkRelation', back_populates='company', lazy=False)
    
    def __repr__(self) -> str:
        return '<Company %r>' % self.id

    def serialize(self) -> dict:
        return {
            "company_name": self.company_name,
            "company_address": self.company_address,
            "start_date": self.start_date
        }