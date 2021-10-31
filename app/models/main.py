
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
            "name": self.company_name,
            "address": self.company_address,
            "start_date": self.start_date
        }


class Provider(db.Model):
    __tablename__ = 'provider'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(128), nullable=False)
    address = db.Column(JSON)
    contacts = db.Column(JSON)
    #relations
    assoc_work_order = db.relationship('ProviderWorkorder', back_populates='provider', lazy=True)

    def __repr__(self) -> str:
        return '<provider %r>' % self.id

    def serialize(self) -> dict:
        return {
            "id": self.id,
            "name": self.provider_name,
            "address": self.provider_address
        }


class Spares(db.Model):
    __tablename__ = 'spares'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(128), nullable=False)
    description = db.Column(db.Text)

    def __repr__(self) -> str:
        return '<Spare %r>' % self.id

    def serialize(self) -> dict:
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description
        }


class Location(db.Model):
    __tablename__ = 'location'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(128), nullable=False)
    address = db.Column(JSON)
    contacts = db.Column(JSON)

    def __repr__(self) -> str:
        return '<Location %r>' % self.id

    def serialize(self) -> dict:
        return {
            'id': self.id,
            'name': self.name,
            'address': self.address,
        }


class Asset(db.Model):
    __tablename__ = 'asset'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(128), nullable=False)
    description = db.Column(db.Text)

    def __repr__(self) -> str:
        return '<asset %r>' % self.id

    def serialize(self) -> dict:
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description
        }


class WorkOrder(db.Model):
    __tablename__ = 'work_order'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(128), nullable=False)
    description = db.Column(db.Text)
    #relations
    assoc_provider = db.relationship('ProviderWorkorder', back_poppulates='work_order', lazy=True)

    def __repr__(self) -> str:
        return '<WorkOrder %r>' % self.id

    def serialize(self) -> dict:
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description
        }


class MaintenanceActivity(db.Model):
    __tablename__ = 'maintenance_activity'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(128), nullable=False)
    description = db.Column(db.Text)
    #relations

    def __repr__(self) -> str:
        return '<maintenance_activity %r>' % self.id

    def serialize(self) -> dict:
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
        }


class MaintenancePlan(db.Model):
    __tablename__ = 'maintenance_plan'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(128), nullable=False)
    description = db.Column(db.Text)

    def __repr__(self) -> str:
        return '<maintenance_plan %r>' % self.id

    def serialize(self) -> dict:
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
        }