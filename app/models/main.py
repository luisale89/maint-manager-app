
from app.extensions import db
from datetime import datetime

from werkzeug.security import generate_password_hash
from sqlalchemy.dialects.postgresql import JSON
from sqlalchemy.orm import backref

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
    company_users = db.relationship('CompanyUser', back_populates='user', lazy=True)
    companies = db.relationship('Company', back_populates='user', lazy=True) #companies owned by the user.

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
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    #relationships
    user = db.relationship('User', back_populates='companies', uselist=False, lazy=True) #owner of the company
    company_users = db.relationship('CompanyUser', back_populates='company', lazy=True)
    providers = db.relationship('Provider', back_populates='company', lazy=True)
    assets = db.relationship('Asset', back_populates='company', lazy=True)
    maint_activities = db.relationship('MaintenanceActivity', back_populates='company', lazy=True)
    maint_plans = db.relationship('MaintenancePlan', back_populates='company', lazy=True)
    locations = db.relationship('Location', back_populates='company', lazy=True)
    spare_parts = db.relationship('SparePart', back_populates='company', lazy=True)
    supplies = db.relationship('Supply', back_populates='company', lazy=True)

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
    company_id = db.Column(db.Integer, db.ForeignKey('company.id'), nullable=False)
    #relations
    company = db.relationship('Company', back_populates='providers', uselist=False, lazy=True)

    def __repr__(self) -> str:
        return '<provider %r>' % self.id

    def serialize(self) -> dict:
        return {
            "id": self.id,
            "name": self.provider_name,
            "address": self.provider_address
        }


class SparePart(db.Model):
    __tablename__ = 'spare_part'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(128), nullable=False)
    description = db.Column(db.Text)
    company_id = db.Column(db.Integer, db.ForeignKey('company.id'), nullable=False)
    #relations
    company = db.relationship('Company', back_populates='spare_parts', uselist=False, lazy=True)
    asset_spare_parts = db.relationship('AssetSparePart', cascade='all, delete-orphan', back_populates='spare_part', lazy=True)

    def __repr__(self) -> str:
        return '<Spare %r>' % self.name

    def serialize(self) -> dict:
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'company_id': self.company_id
        }


class Supply(db.Model):
    __tablename__= 'supply'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(128), nullable=False)
    description = db.Column(db.Text)
    company_id = db.Column(db.Integer, db.ForeignKey('company.id'), nullable=False)
    #relations
    company = db.relationship('Company', back_populates='supplies', uselist=False, lazy=True)

    def __repr__(self) -> str:
        return '<supply %r>' % self.id

    def serialize(self) -> dict:
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "company_id": self.company_id
        }


class Asset(db.Model):
    __tablename__ = 'asset'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(128), nullable=False)
    description = db.Column(db.Text)
    asset_type = db.Column(db.String(128), nullable=False) #asset, part or component
    company_id = db.Column(db.Integer, db.ForeignKey('company.id'), nullable=False)
    parent_id = db.Column(db.Integer, db.ForeignKey('asset.id'))
    location_id = db.Column(db.Integer, db.ForeignKey('location.id'))
    #relations
    children = db.relationship('Asset', cascade="all, delete-orphan", backref=backref('parent', remote_side=id))
    company = db.relationship('Company', back_populates='assets', uselist=False, lazy=True)
    location = db.relationship('Location', back_populates='assets', uselist=False, lazy=True) #* revisar cascade
    asset_spare_parts = db.relationship('AssetSparePart', cascade='all, delete-orphan', back_populates='asset', lazy=True)

    def __repr__(self) -> str:
        return '<asset %r>' % self.name

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
    company_user_id = db.Column(db.Integer, db.ForeignKey('company_user.id'))
    #relations
    company_user = db.relationship('CompanyUser', back_populates='', uselist=False, lazy=True)

    def __repr__(self) -> str:
        return '<WorkOrder %r>' % self.id

    def serialize(self) -> dict:
        return {
            'id': self.id,
            'name': self.name,
            'description': self.descriptions
        }


class MaintenanceActivity(db.Model):
    __tablename__ = 'maintenance_activity'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(128), nullable=False)
    description = db.Column(db.Text)
    company_id = db.Column(db.Integer, db.ForeignKey('company.id'), nullable=False)
    #relations
    company = db.relationship('Company', back_populates='maint_activities', uselist=False, lazy=True)

    def __repr__(self) -> str:
        return '<maint %r>' % self.name

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
    company_id = db.Column(db.Integer, db.ForeignKey('company.id'), nullable=False)
    #relations
    company = db.relationship('Company', back_populates='maint_plans', uselist=False, lazy=True)
    assets = db.relationship('Asset', secondary='mPlan_asset', lazy='subquery', backref=db.backref('mPlan', lazy=True))

    def __repr__(self) -> str:
        return '<maintenance_plan %r>' % self.id

    def serialize(self) -> dict:
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
        }


class Location(db.Model):
    __tablename__ = 'location'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(128), nullable=False)
    description = db.Column(db.Text)
    company_id = db.Column(db.Integer, db.ForeignKey('company.id'), nullable=False)
    parent_id = db.Column(db.Integer, db.ForeignKey('location.id'))
    #relations
    children = db.relationship('Location', cascade="all, delete-orphan", backref=backref('parent', remote_side=id))
    company = db.relationship('Company', back_populates='locations', uselist=False, lazy=True)
    assets = db.relationship('Asset', back_populates='location', lazy=True)

    def __repr__(self) -> str:
        return '<location %r>' % self.id

    def serialize(self) -> dict:
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description
        }