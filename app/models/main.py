
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
    image = db.Column(db.String(256))
    home_address = db.Column(JSON)
    phone = db.Column(db.String(32))
    registration_date = db.Column(db.DateTime, default=datetime.utcnow)
    email_confirmed = db.Column(db.Boolean)
    status = db.Column(db.String(12))
    #relations
    work_relations = db.relationship('WorkRelation', back_populates='user', lazy=True)

    def __repr__(self):
        # return '<User %r>' % self.id
        return f"<User {self.id}>"

    def serialize(self):
        return {
            "id": self.id,
            "fname" : self.fname,
            "lname" : self.lname,
            "image": self.image if self.image is not None else "https://server.com/default.png",
            "registration_date": self.registration_date,
            "home_address": self.home_address,
            "phone": self.phone,
            "user_status": self.status
        }

    def serialize_private(self):
        return {
            "email": self.email,
            "home_address": self.home_address,
            "phone": self.phone,
            "email_confirmed": self.email_confirmed
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
    name = db.Column(db.String(128), nullable=False)
    code = db.Column(db.String(128))
    image = db.Column(db.String(256))
    address = db.Column(JSON)
    contacts = db.Column(JSON)
    latitude = db.Column(db.Float(precision=8))
    longitude = db.Column(db.Float(precision=8))
    registration_date = db.Column(db.DateTime, default=datetime.utcnow)
    #relationships
    work_relations = db.relationship('WorkRelation', back_populates='company', lazy=True)
    locations = db.relationship('Location', back_populates='company', lazy=True)

    def __repr__(self) -> str:
        # return '<Company %r>' % self.id
        return f"<Company {self.id}>"

    def serialize(self) -> dict:
        return {
            "name": self.name,
            "code": self.code,
            "image": self.image if self.image is not None else "https://server.com/default.png",
            "address": self.address,
            "contacts": self.contacts,
            "latitude": self.latitude,
            "longitude": self.longitude,
            "registration_date": self.registration_date
        }


class Location(db.Model):
    __tablename__ = 'location'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(128), nullable=False)
    description = db.Column(db.Text)
    path = db.Column(JSON) #codigo para identificar la ruta desde el nodo padre hasta la raiz del arbol
    parent_id = db.Column(db.Integer, db.ForeignKey('location.id'))
    company_id = db.Column(db.Integer, db.ForeignKey('company.id'), nullable=False)
    #relations
    children = db.relationship('Location', cascade="all, delete-orphan", backref=backref('parent', remote_side=id))
    company = db.relationship('Company', back_populates='locations', uselist=False, lazy=True)

    def __repr__(self) -> str:
        # return '<location %r>' % self.id
        return f"<Location {self.id}>"

    def serialize(self) -> dict:
        return {
            'id':self.id,
            'parent_id': self.parent_id,
            'name': self.name,
            'path': 'root>' + '>'.join(str(e) for e in self.path) if self.path is not None else 'root>', #!TEST node_1>node2>node5...
            'description': self.description,
            'number_of_children': len(self.children)
        }

    def serialize_children(self) -> dict:
        return {
            'children': list(map(lambda x: x.serialize(), self.children))
        }