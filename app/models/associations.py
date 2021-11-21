from sqlalchemy.orm import backref
from app.extensions import db
from datetime import datetime


class CompanyUser(db.Model):
    __tablename__ = 'company_user'
    id = db.Column(db.Integer, primary_key=True)
    rel_date = db.Column(db.DateTime, default=datetime.utcnow)
    user_role = db.Column(db.String(24), nullable=False)
    user_salary = db.Column(db.Float, nullable=False)
    #associations
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    company_id = db.Column(db.Integer, db.ForeignKey('company.id'), nullable=False)
    #relations
    user = db.relationship('User', back_populates='company_users', uselist=False, lazy=True)
    company = db.relationship('Company', back_populates='company_users', uselist=False, lazy=True)
    work_orders = db.relationship('WorkOrder', back_populates='company_user', lazy=False)

    def __repr__(self) -> str:
        return '<company_user %r' % self.id

    def serialize(self) -> dict:
        return {
            "id": self.id,
            "rel_date": self.rel_date,
        }


class AssetSparePart(db.Model):
    __tablename__ = 'asset_spare_part'
    id = db.Column(db.Integer, primary_key=True)
    asset_id = db.Column(db.Integer, db.ForeignKey('asset.id'), nullable=False)
    spare_part_id = db.Column(db.Integer, db.ForeignKey('spare_part.id'), nullable=False)
    #relations
    asset = db.relationship('Asset', back_populates='asset_spare_parts', uselist=False, lazy=True)
    spare_part = db.relationship('SparePart', back_populates='asset_spare_parts', uselist=False, lazy=True)

    def __repr__(self) -> str:
        return '<Assoc spare %r asset %r>' %(self.spare_part_id, self.asset_id)

    def serialize(self) -> dict:
        return {
            "id": self.id
        }


#helper tables - many 2 many
# companyUser_workOrder = db.Table('companyuser_workorder', 
#     db.Column('company_user_id', db.Integer, db.ForeignKey('company_user.id'), primary_key=True),
#     db.Column('work_order_id', db.Integer, db.ForeignKey('work_order.id'), primary_key=True)
# )

mPlan_asset = db.Table('mPlan_asset',
    db.Column('mPlan_id', db.Integer, db.ForeignKey('maintenance_plan.id'), primary_key=True),
    db.Column('asset_id', db.Integer, db.ForeignKey('asset.id'), primary_key=True)
)