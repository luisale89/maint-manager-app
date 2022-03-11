
from email.policy import default
from app.extensions import db
from datetime import datetime
from sqlalchemy.orm import backref


class Role(db.Model):
    __tablename__ = "role"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(128))
    global_role = db.Column(db.Boolean)
    creation_date = db.Column(db.DateTime, default=datetime.utcnow)
    creator_user_id = db.Column(db.Integer)
    #relations
    permits = db.relationship('Permit', back_populates='role', lazy=True)

    def __repr__(self) -> str:
        return f"<Role {self.name}>"

    def serialize(self) -> dict:
        return {
            'id': self.id,
            'name': self.name,
            'global_role': self.global_role,
            'creation_date': self.creation_date,
            'creator_user_id': self.creator_user_id,
        }

    def serialize_features(self) -> dict:
        return {
            'features': list(map(lambda x : dict(
                {**x.serialize_feature(), 'permits': x.serialize()}
            ), self.permits))
        }


class Permit(db.Model):
    __tablename__ = "permit"
    id = db.Column(db.Integer, primary_key=True)
    create = db.Column(db.Boolean, default=False)
    read = db.Column(db.Boolean, default=False)
    update = db.Column(db.Boolean, default=False)
    delete = db.Column(db.Boolean, default=False)
    role_id = db.Column(db.Integer, db.ForeignKey('role.id'))
    feature_id = db.Column(db.Integer, db.ForeignKey('feature.id'))
    #relations
    role = db.relationship('Role', back_populates='permits', lazy=True)
    feature = db.relationship('Feature', back_populates='permits', lazy=True)

    def __repr__(self) -> str:
        return f'<Permit {self.id}>'

    def serialize(self) -> dict:
        return {
            'create': self.create,
            'read': self.read,
            'update': self.update,
            'delete': self.delete
        }

    def serialize_feature(self) -> dict:
        return self.feature.serialize()


class Feature(db.Model):
    __tablename__ = "feature"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(128))
    description = db.Column(db.Text)
    #relations
    permits = db.relationship('Permit', back_populates='feature', lazy=True)

    def __repr__(self) -> str:
        return f'<Feature {self.name}>'

    def serialize(self) -> dict:
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description
        }