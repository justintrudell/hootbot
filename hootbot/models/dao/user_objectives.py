import datetime

from hootbot.database.database import db
from hootbot.models.dao.learning_objective import LearningObjective
from hootbot.models.dao.user import User


class UserObjective(db.Model):
    __tablename__ = "user_objectives"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.String(20), db.ForeignKey('users.id'))
    objective_id = db.Column(db.Integer, db.ForeignKey('learning_objectives.id'))
    timestamp = db.Column(db.DateTime)

    user = db.relationship(User, backref="user_objectives")
    objective = db.relationship(LearningObjective, backref="user_objectives")

    def __init__(self, user_id, objective_id, timestamp=datetime.datetime.utcnow()):
        self.user_id = user_id
        self.objective_id = objective_id
        self.timestamp = timestamp

    @classmethod
    def clear_selected_objectives(cls, user_id):
        cls.query.filter_by(user_id=user_id).delete()
        db.session().commit()
