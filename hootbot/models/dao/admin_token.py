import datetime
import binascii
import os

from hootbot.database.database import db
from hootbot.models.dao.base_model import BaseModel


class AdminToken(db.Model, BaseModel):
    __tablename__ = 'admin_tokens'

    token = db.Column(db.String(64), primary_key=True)
    created_date = db.Column(db.DateTime)

    def __init__(self, token, created_date=datetime.datetime.utcnow()):
        self.token = token
        self.created_date = created_date

    def __repr__(self):
        return "<AdminToken(token='%s', created_date='%s')>" % (
            self.token, self.created_date)

    @staticmethod
    def generate_and_save_token():
        token = AdminToken(binascii.hexlify(os.urandom(32)))
        db.session().add(token)
        db.session().commit()
        return token
