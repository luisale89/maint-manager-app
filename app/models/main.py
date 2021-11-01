
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
    work_relations = db.relationship('WorkRelation', back_populates='user', lazy=True)

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
    work_relations = db.relationship('WorkRelation', back_populates='company', lazy=True)
    spares = db.relationship('Spare', back_populates='company', lazy=True)
    providers = db.relationship('Provider', back_populates='company', lazy=True)
    workorders = db.relationship('WorkOrder', back_populates='company', lazy=True)
    assets = db.relationship('Asset', back_populates='company', lazy=True)
    maint_activities = db.relationship('MaintenanceActivity', back_populates='company', lazy=True)
    maint_plans = db.relationship('MaintenancePlan', back_populates='company', lazy=True)

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
    assoc_workorders = db.relationship('AssocProviderWorkorder', cascade='all, delete-orphan', back_populates='provider', lazy=True)
    assoc_spares = db.relationship('AssocProviderSpare', cascade='all, delete-orphan', back_populates='provider', lazy=True)

    def __repr__(self) -> str:
        return '<provider %r>' % self.id

    def serialize(self) -> dict:
        return {
            "id": self.id,
            "name": self.provider_name,
            "address": self.provider_address
        }


class Spare(db.Model):
    __tablename__ = 'spare'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(128), nullable=False)
    description = db.Column(db.Text)
    company_id = db.Column(db.Integer, db.ForeignKey('company.id'), nullable=False)
    #relations
    company = db.relationship('Company', back_populates='spares', uselist=False, lazy=True)
    assoc_providers = db.relationship('AssocProviderSpare', cascade='all, delete-orphan', back_populates='spare', lazy=True)
    assoc_assets = db.relationship('AssocSpareAsset', cascade='all, delete-orphan', back_populates='spare', lazy=True)

    def __repr__(self) -> str:
        return '<Spare %r>' % self.name

    def serialize(self) -> dict:
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description
        }


class Asset(db.Model):
    __tablename__ = 'asset'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(128), nullable=False)
    description = db.Column(db.Text)
    asset_type = db.Column(db.String(128), nullable=False) #asset or location
    company_id = db.Column(db.Integer, db.ForeignKey('company.id'), nullable=False)
    parent_id = db.Column(db.Integer, db.ForeignKey('asset.id'))
    #relations
    children = db.relationship('Asset', cascade="all, delete-orphan", backref=backref('parent', remote_side=id))
    company = db.relationship('Company', back_populates='assets', uselist=False, lazy=True)
    assoc_spares = db.relationship('AssocSpareAsset', cascade='all, delete-orphan', back_populates='asset', lazy=True)
    assoc_activities = db.relationship('AssocActivityAsset', cascade='all, delete-orphan',back_populates='asset', lazy=True)

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
    company_id = db.Column(db.Integer, db.ForeignKey('company.id'), nullable=False)
    #relations
    company = db.relationship('Company', back_populates='workorders', uselist=False, lazy=True)
    assoc_providers = db.relationship('AssocProviderWorkorder', cascade='all, delete-orphan', back_populates='workorder', lazy=True)

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
    company_id = db.Column(db.Integer, db.ForeignKey('company.id'), nullable=False)
    #relations
    company = db.relationship('Company', back_populates='maint_activities', uselist=False, lazy=True)
    assoc_assets = db.relationship('AssocActivityAsset', cascade='all, delete-orphan', back_populates='maint_activity', lazy=True)

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

    def __repr__(self) -> str:
        return '<maintenance_plan %r>' % self.id

    def serialize(self) -> dict:
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
        }