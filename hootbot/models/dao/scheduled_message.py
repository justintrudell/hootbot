from hootbot.database.database import db
from hootbot.models.dao.base_model import BaseModel


# The actual instances of users having signed up for scheduled messages - this entire table is queried every day
# to determine which users need to receive a scheduled message.
class ScheduledMessage(db.Model, BaseModel):
    __tablename__ = 'scheduled_messages'

    id = db.Column(db.Integer, primary_key=True)
    facebook_id = db.Column(db.String(40))
    topic = db.Column(db.String(80), nullable=False)
    next_day_to_send = db.Column(db.Integer)

    def __init__(self, facebook_id, topic, next_day_to_send=1):
        self.facebook_id = facebook_id
        self.topic = topic
        self.next_day_to_send = next_day_to_send

    def __repr__(self):
        return "<ScheduleMessage(user_id='%s', topic='%s', next_day_to_send='%s')>" % (
            self.day, self.topic, self.next_day_to_send)
