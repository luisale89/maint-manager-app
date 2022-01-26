from sqlalchemy.orm import backref
from app.extensions import db
from datetime import datetime


class WorkRelation(db.Model):
    __tablename__ = 'work_relation'
    id = db.Column(db.Integer, primary_key=True)
    rel_date = db.Column(db.DateTime, default=datetime.utcnow)
    #associations
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    company_id = db.Column(db.Integer, db.ForeignKey('company.id'), nullable=False)
    #relations
    user = db.relationship('User', back_populates='work_relations', uselist=False, lazy=True)
    company = db.relationship('Company', back_populates='work_relations', uselist=False, lazy=True)

    def __repr__(self) -> str:
        # return '<work_relation %r' % self.id
        return f"<work_relation {self.id}>"

    def serialize(self) -> dict:
        return {
            "id": self.id,
            "rel_date": self.rel_date,
        }


#helper tables - many 2 many
# WorkRelation_workOrder = db.Table('WorkRelation_workorder', 
#     db.Column('work_relation_id', db.Integer, db.ForeignKey('work_relation.id'), primary_key=True),
#     db.Column('work_order_id', db.Integer, db.ForeignKey('work_order.id'), primary_key=True)
# )

# mPlan_asset = db.Table('mPlan_asset',
#     db.Column('mPlan_id', db.Integer, db.ForeignKey('maintenance_plan.id'), primary_key=True),
#     db.Column('asset_id', db.Integer, db.ForeignKey('asset.id'), primary_key=True)
# )