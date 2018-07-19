from hootbot.database.database import db


class SocialNetwork(db.Model):
    __tablename__ = 'social_networks'

    id = db.Column(db.Integer, primary_key=True)
    display_text = db.Column(db.String(40))
    objectives = db.relationship("LearningObjective", backref=__tablename__)

    def __init__(self, display_text):
        self.display_text = display_text

    def __repr__(self):
        return "<SocialNetwork(display_text='%s')>" % (
            self.display_text)

    def dict_serialize(self):
        return {"id": self.id, "display_text": self.display_text}
