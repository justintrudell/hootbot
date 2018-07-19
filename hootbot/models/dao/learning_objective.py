from hootbot.database.database import db
from hootbot.models.dao.social_network import SocialNetwork


class LearningObjective(db.Model):
    __tablename__ = 'learning_objectives'

    id = db.Column(db.Integer, primary_key=True)
    display_text = db.Column(db.String(40), nullable=False)

    network_id = db.Column(db.Integer, db.ForeignKey("social_networks.id"))
    network = db.relationship("SocialNetwork", foreign_keys=network_id)

    article_links = db.relationship("ArticleLink", backref=__tablename__)

    def __init__(self, display_text, network):
        self.display_text = display_text
        self.network = network

    def __repr__(self):
        return "<LearningObjective(display_text='%s', network='%s')>" % (
            self.display_text, self.network.display_text)

    def dict_serialize(self):
        return {
            "id": self.id,
            "display_text": self.display_text,
            "network": self.network.display_text
        }

    def update_for_optional_params(self, json):
        if 'display_text' in json:
            self.display_text = json['display_text']
        if 'network' in json:
            network = SocialNetwork.query.filter_by(display_text=json['network']).first()
            self.network = network
