from app.extensions import db


class TokenBlacklist(db.Model):
    __tablename__ = 'tokenblacklist'
    id = db.Column(db.Integer, primary_key=True)
    jti = db.Column(db.String(36), nullable=False)
    token_type = db.Column(db.String(10), nullable=False)
    user_identity = db.Column(db.String(64), nullable=False)
    revoked = db.Column(db.Boolean, nullable=False)
    revoked_date = db.Column(db.DateTime)
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
            'revoked_date': self.revoked_date,
            'expires': self.expires
        }


class Country(db.Model):
    __tablename__ = 'country'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(128), nullable=False, unique=True)
    code = db.Column(db.String(24), unique=True)
    #relations

    def __repr__(self) -> str:
        return '<%r>' % self.name

    def serialize(self):
        return {
            "id": self.id,
            "name": self.name,
            "code": self.code
        }