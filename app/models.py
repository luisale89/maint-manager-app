
from .extensions import db
from datetime import datetime

from werkzeug.security import generate_password_hash
# from sqlalchemy.dialects.postgresql import JSON #only for postgresql


class Country(db.Model):
    __tablename__: 'country'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False, unique=True)
    code = db.Column(db.Integer, nullable=False, unique=True)
    currency = db.Column(db.String(10), nullable=False)
    usd_rate = db.Column(db.Float, nullable=False)
    utc_dif = db.Column(db.Integer, nullable=False)
    #relations
    users = db.relationship('User', back_populates='country', lazy=True)
    companies = db.relationship('Company', back_populates="country", lazy=True)

    def __repr__(self):
        return '<Country %r>' % self.name

    def serialize(self):
        return {
            'id': self.id,
            'name': self.name,
            'code': self.code,
            'currency': self.currency,
            'usd_rate': self.usd_rate,
            'utc_dif': self.utc_dif
        }


class User(db.Model):
    __tablename__: 'user'
    id = db.Column(db.Integer, primary_key=True)
    public_id = db.Column(db.String(60), unique=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(256))
    fname = db.Column(db.String(60), nullable=False)
    lname = db.Column(db.String(60), nullable=False)
    profile_img = db.Column(db.String(120))
    user_since = db.Column(db.DateTime, default=datetime.utcnow)
    country_id = db.Column(db.Integer, db.ForeignKey('country.id'))
    phone = db.Column(db.String(18))
    #relations
    country = db.relationship('Country', back_populates='users', lazy=True, uselist=False)
    admin = db.relationship('Admin', back_populates='user', lazy=True, uselist=False)
    operator = db.relationship('Operator', back_populates='user', lazy=True, uselist=False)
    suscriptor = db.relationship('Suscriptor', back_populates='user', lazy=True, uselist=False)
    notifications = db.relationship('Notification', backref='user', lazy=True)
    companies = db.relationship('Company', back_populates='user', lazy=True)

    def __repr__(self):
        return '<User %r>' % self.public_id

    def serialize(self):
        return {
            "public_id" : self.public_id,
            "fname" : self.fname,
            "lname" : self.lname,
            "user_img": self.profile_img if self.profile_img is not None else "no_pic",
            "user_since": self.user_since,
            "country": self.country.serialize() if self.country is not None else "no_country"
        }

    def serialize_contact(self):
        return {
            "email": self.email,
            "phone": self.phone if self.phone is not None else "no_phone"
        }

    def serialize_notifications(self):
        return list(map(lambda x: x.serialize(), self.notifications)) if len(self.notifications) != 0 else 'no_notifications'

    def serialize_relations(self):
        return {
            "companies": list(map(lambda x: x.serialize(), self.companies)) if len(self.companies) != 0 else 'no_companies',
            "admin": self.admin.serialize() if self.admin is not None else "no_admin",
            "operator": self.operator.serialize() if self.operator is not None else "no_operator",
            "suscriptor": self.suscriptor.serialize() if self.suscriptor is not None else "no_suscriptions"
        }

    @property
    def password(self):
        raise AttributeError('Cannot view password')

    @password.setter
    def password(self, password):
        self.password_hash = generate_password_hash(password, method='sha256')


class Admin(db.Model):
    __tablename__: 'admin'
    id = db.Column(db.Integer, db.ForeignKey('user.id'), primary_key=True)
    company_id = db.Column(db.Integer, db.ForeignKey('company.id'))
    #relations
    user = db.relationship('User', back_populates='admin', uselist=False, lazy=True)
    company = db.relationship('Company', back_populates='admins', uselist=False, lazy=True)

    def __repr__(self):
        return '<Admin %r>' % self.id

    def serialize(self):
        return {
            "id": self.id
        }

    def serialize_user(self):
        return self.user.serialize()


class Operator(db.Model):
    __tablename__: 'operator'
    id = db.Column(db.Integer, db.ForeignKey('user.id'), primary_key=True)
    company_id = db.Column(db.Integer, db.ForeignKey('company.id'))
    #relations
    user = db.relationship('User', back_populates='operator', uselist=False, lazy=True)
    company = db.relationship('Company', back_populates='operators', uselist=False, lazy=True)

    def __repr__(self):
        return '<Operator %r>' % self.id

    def serialize(self):
        return {
            "id": self.id
        }

    def serialize_user(self):
        return self.user.serialize()


class Suscriptor(db.Model):
    __tablename__: 'suscriptor'
    id = db.Column(db.Integer, db.ForeignKey('user.id'), primary_key=True)
    #relations
    user = db.relationship('User', back_populates='suscriptor', uselist=False, lazy=True)

    def __repr__(self):
        return '<Suscriptor %r>' % self.id

    def serialize(self):
        return {
            "id": self.id
        }

    def serialize_user(self):
        return self.user.serialize()


class Notification(db.Model):
    __tablename__: 'notification'
    id = db.Column(db.Integer, primary_key=True)
    user_email = db.Column(db.String(120)) #cuando se crea una noti, se debe agregar el email del usuario target en caso de que no se encuentre en la bd como un usuario registrado.
    title = db.Column(db.String(120), nullable=False)
    content = db.Column(db.Text, nullable=False)
    date = db.Column(db.DateTime, default=datetime.utcnow)
    readed = db.Column(db.Boolean, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    def __repr__(self):
        return '<Notification %r>' % self.id

    def serialize(self):
        return dict({
            'title': self.title,
            'content': self.content,
            'date': self.date,
            'readed': self.readed
        })


class Company(db.Model):
    __tablename__: 'company'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), unique=True, nullable=False)
    rif = db.Column(db.String(60), unique=True)
    logo = db.Column(db.Text)
    city = db.Column(db.String(120))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id')) #owner of the company
    country_id = db.Column(db.Integer, db.ForeignKey('country.id')) #country of the company
    #relations
    user = db.relationship('User', back_populates='companies', uselist=False, lazy=True)
    country = db.relationship('Country', back_populates='companies', uselist=False, lazy=True)
    admins = db.relationship('Admin', back_populates="company", lazy=True)
    operators = db.relationship('Operator', back_populates='company', lazy=True)
    clients = db.relationship('Client', back_populates='company', lazy=True)

    def __repr__(self):
        return '<Company %r>' % self.name

    def serialize(self):
        return {
            "id": self.id,
            "name": self.name,
            "rif": self.rif,
            "logo": self.logo,
            "city": self.city,
            "country": self.country.serialize() if self.country is not None else "no_country"
        }


class Client(db.Model):
    __tablename__:'client'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), unique=True, nullable=False)
    rif = db.Column(db.String(120), unique=True)
    logo = db.Column(db.String(db.Text))
    description = db.Column(db.Text)
    billing = db.Column(db.String(120)) #This must be a json field, to store all the billing emails to send invoics
    company_id = db.Column(db.Integer, db.ForeignKey('company.id')) #service company with contract
    #reations
    company = db.relationship('Company', back_populates='clients', lazy=True, uselist=False)
    offices = db.relationship('Office', back_populates='client', lazy=True)

    def __repr__(self):
        return '<Client %r>' %self.name

    def serialize(self):
        return {
            "id": self.id,
            "name": self.name,
            "rif": self.rif,
            "logo": self.logo,
            "description": self.description,
            "billing": self.billing
        }

class Office(db.Model):
    __tablename__:'office'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), unique=True, nullable=False)
    address = db.Column(db.String(120))
    city = db.Column(db.String(120))
    location = db.Column(db.Text) # this must be a json field, to store the latitude and longitude of the local
    op_constant = db.Column(db.Float, default=1.0)
    client_id = db.Column(db.Integer, db.ForeignKey('client.id'))
    #relations
    client = db.relationship('Client', back_populates='offices', lazy=True, uselist=False)

    def __repr__(self):
        return '<Local %r>' % self.id

    def serialize(self):
        return {
            "id": self.id,
            "name": self.name,
            "address": self.address,
            "city": self.city,
            "location": self.location,
            "op_constant": self.op_constant
        }


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