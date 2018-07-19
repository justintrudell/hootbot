from passlib.hash import pbkdf2_sha256

from hootbot.database.database import db
from hootbot.models.dao.base_model import BaseModel


class AdminUser(db.Model, BaseModel):
    __tablename__ = 'admin_users'

    email = db.Column(db.String(240), primary_key=True)
    password = db.Column(db.String(240), nullable=False)

    def __init__(self, email, password):
        self.email = email
        self.password = password

    def __repr__(self):
        return "<AdminUser(email='%s')>" % self.email

    @staticmethod
    def hash_password(password):
        return pbkdf2_sha256.hash(password)

    def verify_password(self, password):
        return pbkdf2_sha256.verify(password, self.password)

