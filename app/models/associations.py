from sqlalchemy.orm import backref
from app.extensions import db
from datetime import datetime


class WorkRelation(db.Model):
    __tablename__ = 'work_relation'
    id = db.Column(db.Integer, primary_key=True)
    rel_date = db.Column(db.DateTime, default=datetime.utcnow)
    user_role = db.Column(db.String(24), nullable=False)
    user_salary = db.Column(db.Float, nullable=False)
    #associations
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    company_id = db.Column(db.Integer, db.ForeignKey('company.id'), nullable=False)
    #relations
    user = db.relationship('User', back_populates='work_relations', uselist=False, lazy=True)
    company = db.relationship('Company', back_populates='work_relations', uselist=False, lazy=True)
    wOrders = db.relationship('WorkOrder', secondary='wRelation_wOrder', lazy='subquery', backref=db.backref('wRelations', lazy=True))

    def __repr__(self) -> str:
        return '<work_relation %r' % self.id

    def serialize(self) -> dict:
        return {
            "id": self.id,
            "rel_date": self.rel_date,
        }


class AssocProviderWorkorder(db.Model):
    __tablename__ = 'assoc_provider_workorder'
    id = db.Column(db.Integer, primary_key=True)
    provider_id = db.Column(db.Integer, db.ForeignKey('provider.id'), nullable=False)
    work_order_id = db.Column(db.Integer, db.ForeignKey('work_order.id'), nullable=False)
    #relations
    provider = db.relationship('Provider', back_populates='assoc_workorders', uselist=False, lazy=True)
    workorder = db.relationship('WorkOrder', back_populates='assoc_providers', uselist=False, lazy=True)

    def __repr__(self) -> str:
        return '<assoc provider %r workorder %r>' %(self.provider_id %self.work_order_id)

    def serialize(self):
        return {
            'id': self.id
        }


class AssocProviderSpare(db.Model):
    __tablename__ = 'assoc_provider_spare'
    id = db.Column(db.Integer, primary_key=True)
    provider_id = db.Column(db.Integer, db.ForeignKey('provider.id'), nullable=False)
    spare_id = db.Column(db.Integer, db.ForeignKey('spare.id'), nullable=False)
    #relations
    provider = db.relationship('Provider', back_populates='assoc_spares', uselist=False, lazy=True)
    spare = db.relationship('Spare', back_populates='assoc_providers', uselist=False, lazy=True)

    def __repr__(self) -> str:
        return '<Assoc provider %r spare %r>' %(self.provider_id, self.spare_id)

    def serialize(self) -> dict:
        return {
            "id": self.id
        }


class AssocSpareAsset(db.Model):
    __tablename__ = 'assoc_spare_asset'
    id = db.Column(db.Integer, primary_key=True)
    spare_id = db.Column(db.Integer, db.ForeignKey('spare.id'), nullable=False)
    asset_id = db.Column(db.Integer, db.ForeignKey('asset.id'), nullable=False)
    #relations
    spare = db.relationship('Spare', back_populates='assoc_assets', uselist=False, lazy=True)
    asset = db.relationship('Asset', back_populates='assoc_spares', uselist=False, lazy=True)

    def __repr__(self) -> str:
        return '<Assoc spare %r asset %r>' %(self.spare_id, self.asset_id)

    def serialize(self) -> dict:
        return {
            "id": self.id
        }


#helper tables - many 2 many
wRelation_wOrder = db.Table('wRelation_wOrder', 
    db.Column('wRelation_id', db.Integer, db.ForeignKey('work_relation.id'), primary_key=True),
    db.Column('wOrder_id', db.Integer, db.ForeignKey('work_order.id'), primary_key=True)
)

mPlan_asset = db.Table('mPlan_asset',
    db.Column('mPlan_id', db.Integer, db.ForeignKey('maintenance_plan.id'), primary_key=True),
    db.Column('asset_id', db.Integer, db.ForeignKey('asset.id'), primary_key=True)
)