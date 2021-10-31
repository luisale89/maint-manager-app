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
    user = db.relationship('User', back_populates='work_relations', uselist=False, lazy=False)
    company = db.relationship('Company', back_populates='work_relations', uselist=False, lazy=False)

    def __repr__(self) -> str:
        return '<work_relation %r' % self.id

    def serialize(self) -> dict:
        return {
            "id": self.id,
            "rel_date": self.rel_date,
        }


class ProviderWorkorder(db.Model):
    __tablename__ = 'provider_workorder'
    id = db.Column(db.Integer, primary_key=True)
    #associations
    provider_id = db.Column(db.Integer, db.ForeignKey('provider.id'), nullable=False)
    work_order_id = db.Column(db.Integer, db.ForeignKey('work_order.id'), nullable=False)
    #relations
    provider = db.relationship('Provider', back_populates='assoc_work_order', uselist=False, lazy=True)
    work_order = db.relationship('MaintenanceActivity', back_populates='assoc_provider', uselist=False, lazy=True)

    def __repr__(self) -> str:
        return '<Provider_Activiy_list %r>' % self.id

    def serialize(self):
        return {
            'id': self.id,
        }