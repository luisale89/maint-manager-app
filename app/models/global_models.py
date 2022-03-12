from app.extensions import db
from datetime import datetime
from sqlalchemy.orm import backref
from sqlalchemy.dialects.postgresql import JSON


class Role(db.Model):
    __tablename__ = "role"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(128), unique=True, nullable=False)
    code = db.Column(db.String(128), unique=True, nullable=False)
    global_role = db.Column(db.Boolean, default=False)
    creation_date = db.Column(db.DateTime, default=datetime.utcnow)
    permits = db.Column(JSON, default={'create': True, 'read': True, 'update': True, 'delete': True})

    def __repr__(self) -> str:
        return f"<Role {self.name}>"

    def serialize(self) -> dict:
        return {
            'id': self.id,
            'name': self.name,
            'global_role': self.global_role,
            'creation_date': self.creation_date,
            'permits': self.permits
        }

    def add_default_roles():
        commit = False
        admin = Role.query.filter_by(code='admin').first() #administrador
        if admin is None:
            admin = Role(
                name = 'Administrador', 
                code='admin', 
                global_role=True
                #default permits
            )
            
            db.session.add(admin)
            commit = True

        tech = Role.query.filter_by(code='tech').first() #tecnico ejecutor de mantenimientos
        if tech is None:
            tech = Role(
                name='Tecnico', 
                code='tech', 
                global_role=True,
                permits = {'create': False, 'read': True, 'update': True, 'delete': False}
            )

            db.session.add(tech)
            commit = True

        obs = Role.query.filter_by(code='obs').first() #observador de datos, solo lectura
        if obs is None:
            obs = Role(
                name='Observador', 
                code = 'obs', 
                global_role=True,
                permits = {'create': False, 'read': True, 'update': False, 'delete': False}
            )

            db.session.add(obs)
            commit = True

        if commit:
            db.session.commit()
        
        pass


class Plan(db.Model):
    __tablename__ = 'plan'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(128), nullable=False, unique=True)
    code = db.Column(db.String(128), unique=True, nullable=False)
    creation_date = db.Column(db.DateTime, default=datetime.utcnow)
    limits = db.Column(JSON, default={'assets': 20, 'admin': 1, 'tech': 1, 'obs': 'nl'})

    def __repr__(self) -> str:
        return f"<Role {self.name}>"

    def serialize(self) -> dict:
        return {
            'id': self.id,
            'name': self.name,
            'code': self.code,
            'creation_date': self.creation_date,
            'limits': self.limits
        }

    def add_default_plans():
        
        commit = False
        basic = Plan.query.filter_by(code='basic').first()
        if basic is None:
            basic = Plan(
                name = 'Plan Basico',
                code = 'basic'
                #default limits
            )
            
            db.session.add(basic)
            commit = True

        if commit:
            db.session.commit()

        pass