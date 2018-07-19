from hootbot.database.database import db


# The contents (articles, videos) that will be sent to users that have signed up for scheduled messages.
class ScheduledMessageContent(db.Model):
    __tablename__ = 'scheduled_message_contents'

    id = db.Column(db.Integer, primary_key=True)
    day = db.Column(db.Integer)
    topic = db.Column(db.String(80), nullable=False)
    title = db.Column(db.String(80))
    description = db.Column(db.String(400))
    link = db.Column(db.String(240))
    image_url = db.Column(db.String(240))

    def __init__(self, day, topic, title, description, link):
        if day < 1:
            raise ValueError("Day must be greater than zero")
        self.day = day
        self.topic = topic
        self.title = title
        self.description = description
        self.link = link

    def __repr__(self):
        return "<ScheduleMessageContent(day='%s', topic='%s', title='%s'," \
               "description='%s', link='%s')>" % (
                   self.day, self.topic, self.title, self.description, self.link)
