from hootbot.database.database import db
from hootbot.models.dao.social_network import SocialNetwork
from hootbot.models.dao.learning_objective import LearningObjective


class ArticleLink(db.Model):
    __tablename__ = 'article_links'

    id = db.Column(db.Integer, primary_key=True)
    url = db.Column(db.String(240), nullable=False)
    title = db.Column(db.String(80), nullable=False)
    description = db.Column(db.String(80))
    image_url = db.Column(db.String(240))
    link_type = db.Column(db.String(80))

    objective_id = db.Column(db.Integer, db.ForeignKey("learning_objectives.id"))
    objective = db.relationship('LearningObjective', foreign_keys=objective_id)

    def __init__(self, url, title, objective, link_type, description=None, image_url=None):
        self.url = url
        self.title = title
        self.objective = objective
        self.link_type = link_type
        if not description and not image_url:
            raise ValueError("Must be provided either a description or image url - both cannot be empty.")
        if description:
            self.description = description
        if image_url:
            self.image_url = image_url

    def __repr__(self):
        return "<ArticleLink(title='%s', url='%s', objective='%s')>" % (
            self.title, self.url, self.objective.display_text)

    def dict_serialize(self):
        return {
            "id": self.id,
            "url": self.url,
            "title": self.title,
            "description": self.description,
            "image_url": self.image_url,
            "link_type": self.link_type,
            "objective": self.objective.display_text,
            "network": self.objective.network.display_text
        }

    def update_for_optional_params(self, json):
        if 'url' in json:
            self.url = json['url']
        if 'title' in json:
            self.title = json['title']
        if 'description' in json:
            self.description = json['description']
        if 'image_url' in json:
            self.image_url = json['image_url']
        if 'link_type' in json:
            self.link_type = str(json['link_type']).upper()
        if 'objective' in json:
            network = SocialNetwork.query.filter_by(display_text=json['network']).first()
            objective = LearningObjective.query.filter_by(display_text=json['objective'], network=network).first()
            self.objective = objective

