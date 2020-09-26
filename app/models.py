import json

from flask_sqlalchemy import SQLAlchemy

from werkzeug.security import generate_password_hash
# from sqlalchemy.dialects.postgresql import JSON #only for postgresql

db = SQLAlchemy()

class User(db.Model):
    __tablename__: 'user'
    id = db.Column(db.Integer, primary_key=True)
    public_id = db.Column(db.String(60), unique=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    fname = db.Column(db.String(60), nullable=False)
    lname = db.Column(db.String(60), nullable=False)
    profile_picture = db.Column(db.String(120))
    phone = db.Column(db.String(16))
    activity_log = db.Column(db.Text)
    
    def __repr__(self):
        return '<User %r>' % self.lname

    def serialize_public(self):
        return {
            "public_id" : self.public_id,
            "fname" : self.fname,
            "lname" : self.lname,
            "user_picture": self.profile_picture if self.profile_picture is not None else "no_pic"
        }
    
    def serialize_contact(self):
        return {
            "email": self.email,
            "user_phone": self.phone if self.phone is not None else "no_phone"
        }

    def serialize_log(self):
        return {
            "activity_log": self.activity_log if self.activity_log is not None else list([{"l.00": "no_data"}])
        }

    @property
    def password(self):
        raise AttributeError('Cannot view password')

    @password.setter
    def password(self, password):
        self.password_hash = generate_password_hash(password, method='sha256')


class Owner(db.Model):
    __tablename__: 'owner'
    id = db.Column(db.Integer, primary_key=True)

    def __repr__(self):
        return '<Owner %r>' % self.id


class Admin(db.Model):
    __tablename__: 'admin'
    id = db.Column(db.Integer, primary_key=True)
    admin_email = db.Column(db.String(120), nullable=False) #email ingresado por el owner, que indica el usuario que está buscando como administrador de su empres
    status = db.Column(db.String(10)) #open, denied, active, paused, deleted, undefined

    def __repr__(self):
        return '<Admin %r>' % self.admin_email


class Operator(db.Model):
    __tablename__: 'operator'
    id = db.Column(db.Integer, primary_key=True)
    operator_email = db.Column(db.String(120), nullable=False) #email ingresado por el admin, que indica el usuario que está buscando como operador de su equipo.
    status = db.Column(db.String(10)) #open, denied, active, paused, deleted, undefined

    def __repr__(self):
        return '<Operator %r>' %self.operator_email


class Suscriptor(db.Model):
    __tablename__: 'suscriptor'
    id = db.Column(db.Integer, primary_key=True)
    suscriptor_email = db.Column(db.String(120), nullable=False) #email ingresado por el admin, que indica el usuario que puede suscribirse a un evento.
    status = db.Column(db.String(10)) #open, denied, active, paused, deleted, undefined

    def __repr__(self):
        return '<Suscriptor %r>' %self.suscriptor_email