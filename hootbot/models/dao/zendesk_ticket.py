from hootbot.database.database import db


class ZendeskTicket(db.Model):
    __tablename__ = 'zendesk_tickets'

    # Zendesk Ticket ID
    id = db.Column(db.String(32), primary_key=True)
    status = db.Column(db.String(80), nullable=False)

    user_id = db.Column(db.String(20), db.ForeignKey("users.id"))
    user = db.relationship("User", foreign_keys=user_id)

    def __init__(self, ticket_id, status, user_id):
        self.id = ticket_id
        self.status = status
        self.user_id = user_id

    def __repr__(self):
        return "<ZendeskTicket(id='%d', status='%s', user_id='%s')>" % (
            self.id, self.status, self.user_id)