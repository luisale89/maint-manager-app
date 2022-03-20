
from app.extensions import db
from datetime import datetime

from sqlalchemy.dialects.postgresql import JSON
from sqlalchemy.orm import backref


class Asset(db.Model):
    __tablename__ = 'asset'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(128), nullable=False)
    description = db.Column(db.Text)
    parent_id = db.Column(db.Integer, db.ForeignKey('asset.id'))
    # company_id = db.Column(db.Integer, db.ForeignKey('company.id'), nullable=False)
    #relations
    children = db.relationship('Asset', cascade="all, delete-orphan", backref=backref('parent', remote_side=id))
    # company = db.relationship('Company', back_populates='assets', uselist=False, lazy=True)

    def __repr__(self) -> str:
        # return '<Asset %r>' % self.id
        return f"<Asset {self.id}>"

    def serialize(self) -> dict:
        return {
            'id':self.id,
            'name': self.name,
            'description': self.description,
        }

    def serialize_path(self) -> dict: #path to root
        return {
            ** self.serialize(),
            'parent': self.parent.serialize_path() if self.parent is not None else 'root'
        }

    def serialize_children(self) -> dict:
        return {
            'children': list(map(lambda x: x.serialize(), self.children))
        }