from hootbot.models.dao.user_objectives import UserObjective
from hootbot.models.dao.learning_objective import LearningObjective


def get_unselected_objectives(network, user_id):
    """
    Gets the learning objectives that haven't already been selected in this session.
    :param network: SocialNetwork object we are seeking the learning objectives for.
    :param user_id: Facebook ID of the user used to query that User object in the database.
    :return: List of unselected LearningObjective objects
    """
    user_objective_ids = [x.objective_id for x in UserObjective.query.filter_by(user_id=user_id).all()]
    all_objectives = LearningObjective.query.filter_by(network=network)
    if user_objective_ids:
        return all_objectives.filter(~LearningObjective.id.in_(user_objective_ids)).all()
    else:
        return all_objectives.all()
