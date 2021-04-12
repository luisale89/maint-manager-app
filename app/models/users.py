
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
    fname = db.Column(db.String(60))
    lname = db.Column(db.String(60))
    profile_img = db.Column(db.String(120))
    home_address = db.Column(JSON)
    personal_phone = db.Column(db.String(30))
    since = db.Column(db.DateTime, default=datetime.utcnow)
    email_confirm = db.Column(db.Boolean)
    status = db.Column(db.String(12))
    #relationships
    work_relations = db.relationship('WorkRelation', back_populates='user', lazy=True)

    def __repr__(self):
        return '<User %r>' % self.id

    def serialize(self):
        return {
            "public_id" : self.public_id,
            "fname" : self.fname,
            "lname" : self.lname,
            "profile_img": self.profile_img if self.profile_img is not None else "https://server.com/default.png",
            "home_address": self.home_address,
            "personal_phone": self.personal_phone,
            "user_since": self.since,
            "user_status": self.status
        }

    def serialize_private(self):
        return {
            "email": self.email,
        }

    def serialize_companies(self):
        return {
            'companies': list(map(lambda x: x.serialize_company(), self.work_relations))
        }

    @property
    def password(self):
        raise AttributeError('Cannot view password')

    @password.setter
    def password(self, password):
        self.password_hash = generate_password_hash(password, method='sha256')


class Company(db.Model):
    __tablename__ = 'company'
    id = db.Column(db.Integer, primary_key=True)
    public_id = db.Column(db.String(60), unique=True, nullable=False)
    name = db.Column(db.String(60), nullable=False)
    address = db.Column(JSON)
    geo_cordinates = db.Column(JSON)
    logo = db.Column(db.String(120))
    #relationships
    work_relations = db.relationship('WorkRelation', back_populates='company', lazy=True)

    def __repr__(self) -> str:
        return '<Company %r>' %self.id

    def serialize(self):
        return {
            "id": self.id,
            "public_id": self.public_id,
            "name": self.name,
            "address": self.address,
            "geo_cordinates": self.geo_cordinates,
            "logo": self.logo
        }

    def serialize_users(self):
        return {
            'users': list(map(lambda x: x.serialize_user(), self.work_relations))
        }
        

class WorkRelation(db.Model):
    __tablename__= 'workrelation'
    id = db.Column(db.Integer, primary_key=True)
    rel_date = db.Column(db.DateTime, default=datetime.utcnow)
    user_role = db.Column(db.String(12), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    company_id = db.Column(db.Integer, db.ForeignKey('company.id'), nullable=False)
    #relationships
    company = db.relationship('Company', back_populates='work_relations', lazy=True, uselist=False)
    user = db.relationship('User', back_populates='work_relations', lazy=True, uselist=False)

    def __repr__(self) -> str:
        return '<WorkRelation %r>' %self.id

    def serialize_company(self):
        return {
            'relation_date': self.rel_date,
            'user_role': self.user_role,
            'company_profile': self.company.serialize()
        }
        
    def serialize_user(self):
        return {
            'relation_date': self.rel_date,
            'user_role': self.user_role,
            'user_profile': self.user.serialize()
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