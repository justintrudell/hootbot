import datetime

from hootbot.database.database import db
from hootbot.models.dao.base_model import BaseModel
from hootbot.models.enums.zendesk_status import ZendeskStatus


class User(db.Model, BaseModel):
    __tablename__ = 'users'

    id = db.Column(db.String(20), primary_key=True)  # Facebook Page ID
    first_name = db.Column(db.String(80))
    last_name = db.Column(db.String(80))
    created_date = db.Column(db.DateTime)
    email = db.Column(db.String(256))
    zendesk_id = db.Column(db.String(32))

    tickets = db.relationship("ZendeskTicket", backref=__tablename__)

    def __init__(self, fb_id, first_name="", last_name="", created_date=datetime.datetime.utcnow(), email="", zendesk_id=""):
        self.id = fb_id
        self.first_name = first_name
        self.last_name = last_name
        self.created_date = created_date
        self.email = email
        self.zendesk_id = zendesk_id

    def __repr__(self):
        return "<User(id='%s', email='%s')>" % (
            self.id, self.email)

    def get_open_tickets(self):
        return [x for x in self.tickets if x.status == ZendeskStatus.OPEN.value]

    def get_solved_tickets(self):
        return [x for x in self.tickets if x.status == ZendeskStatus.SOLVED.value]
