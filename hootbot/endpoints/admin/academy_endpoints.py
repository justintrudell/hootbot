import json
from flask import Blueprint, request, abort

from hootbot.logging.logger import bot_log
from hootbot.models.dao.article_link import ArticleLink
from hootbot.models.dao.learning_objective import LearningObjective
from hootbot.models.dao.social_network import SocialNetwork
from hootbot.models.dao.admin_user import AdminUser
from hootbot.models.dao.admin_token import AdminToken
from hootbot.decorators.authorization import requires_auth
from hootbot.decorators.crossdomain import crossdomain
from hootbot.database.database import db, redis_store

admin_api = Blueprint("admin_api", __name__)


@admin_api.route('/get-token', methods=['OPTIONS', 'GET'])
@crossdomain(origin='https://hootbot-content-manager.hootapps.io')
def get_token():
    auth = request.authorization
    email = auth.username
    password = auth.password
    user = AdminUser.query.filter_by(email=email).first()
    if user and user.verify_password(password):
        admin_token = AdminToken.generate_and_save_token()
        return admin_token.token
    else:
        abort(401)


@admin_api.route('/social-networks', methods=['OPTIONS', 'GET'])
@crossdomain(origin='https://hootbot-content-manager.hootapps.io')
@requires_auth
def get_social_networks():
    return json.dumps([x.dict_serialize() for x in SocialNetwork.query.all()])


@admin_api.route('/learning-objectives', methods=['OPTIONS', 'GET'])
@crossdomain(origin='https://hootbot-content-manager.hootapps.io')
@requires_auth
def get_learning_objectives():
    network_query = request.args.get("network")
    if network_query:
        network = SocialNetwork.query.filter_by(display_text=network_query).first()
        objective_list = LearningObjective.query.filter_by(network=network).all()
        return json.dumps([x.dict_serialize() for x in objective_list])
    return json.dumps([x.dict_serialize() for x in LearningObjective.query.all()])


@admin_api.route('/article-links', methods=['OPTIONS', 'GET'])
@crossdomain(origin='https://hootbot-content-manager.hootapps.io')
@requires_auth
def get_article_links():
    network_query = request.args.get('network')
    objective_query = request.args.get('objective')
    if network_query:
        network = SocialNetwork.query.filter_by(display_text=network_query).first()
        if objective_query:
            objective = (LearningObjective.query
                         .filter_by(display_text=objective_query)
                         .filter_by(network=network)
                         .first())
            article_links = ArticleLink.query.filter_by(objective=objective).all()
            return json.dumps([x.dict_serialize() for x in article_links])
        else:
            all_objective_ids = [x.id for x in LearningObjective.query.filter_by(network=network).all()]
            article_links = ArticleLink.query.filter(ArticleLink.objective_id.in_(all_objective_ids)).all()
            return json.dumps([x.dict_serialize() for x in article_links])
    return json.dumps([x.dict_serialize() for x in ArticleLink.query.all()])


@admin_api.route('/social-networks/post', methods=['OPTIONS', 'POST'])
@crossdomain(origin='https://hootbot-content-manager.hootapps.io')
@requires_auth
def post_social_networks():
    payload = request.get_data()
    data = json.loads(payload)
    for item in data:
        bot_log("Admin API: Adding network " + str(item['display_text']))
        if 'id' in item:
            SocialNetwork.query.filter_by(id=item['id']).first().display_text = item['display_text']
        else:
            network = SocialNetwork(display_text=item['display_text'])
            db.session().add(network)
    db.session().commit()
    return "ok"


@admin_api.route('/learning-objectives/post', methods=['OPTIONS', 'POST'])
@crossdomain(origin='https://hootbot-content-manager.hootapps.io')
@requires_auth
def post_learning_objectives():
    payload = request.get_data()
    data = json.loads(payload)
    for item in data:
        bot_log("Admin API: Adding objective " + str(item['display_text']))
        if 'id' in item:
            LearningObjective.query.filter_by(id=item['id']).first().update_for_optional_params(json=item)
        else:
            network = SocialNetwork.query.filter_by(display_text=item['network']).first()
            objective = LearningObjective(item['display_text'], network)
            db.session().add(objective)
    db.session().commit()
    return "ok"


@admin_api.route('/article-links/post', methods=['OPTIONS', 'POST'])
@crossdomain(origin='https://hootbot-content-manager.hootapps.io')
@requires_auth
def post_article_links():
    payload = request.get_data()
    data = json.loads(payload)
    for item in data:
        bot_log("Admin API: Adding link " + str(item['title']))
        if 'id' in item:
            ArticleLink.query.filter_by(id=item['id']).first().update_for_optional_params(json=item)
        else:
            network = SocialNetwork.query.filter_by(display_text=item['network']).first()
            objective = LearningObjective.query.filter_by(display_text=item['objective'], network=network).first()
            article_link = ArticleLink(item['url'],
                                       item['title'],
                                       objective,
                                       str(item['link_type']).upper(),
                                       item.get('description'),
                                       item.get('image_url'))
            db.session().add(article_link)
    db.session().commit()
    return "ok"


@admin_api.route('/social-networks/delete', methods=['OPTIONS', 'DELETE'])
@crossdomain(origin='https://hootbot-content-manager.hootapps.io')
@requires_auth
def delete_social_networks():
    payload = request.get_data()
    data = json.loads(payload)
    for item in data:
        bot_log("Admin API: Deleting network ID " + str(item['id']))
        network = SocialNetwork.query.filter_by(id=item['id']).first()
        for objective in network.objectives:
            for link in objective.article_links:
                ArticleLink.query.filter_by(id=link.id).delete()
            LearningObjective.query.filter_by(id=objective.id).delete()
        SocialNetwork.query.filter_by(id=network.id).delete()
    db.session().commit()
    return "ok"


@admin_api.route('/learning-objectives/delete', methods=['OPTIONS', 'DELETE'])
@crossdomain(origin='https://hootbot-content-manager.hootapps.io')
@requires_auth
def delete_learning_objectives():
    payload = request.get_data()
    data = json.loads(payload)
    for item in data:
        bot_log("Admin API: Deleting objective ID " + str(item['id']))
        objective = LearningObjective.query.filter_by(id=item['id']).first()
        for link in objective.article_links:
            ArticleLink.query.filter_by(id=link.id).delete()
        LearningObjective.query.filter_by(id=objective.id).delete()
    db.session().commit()
    return "ok"


@admin_api.route('/article-links/delete', methods=['OPTIONS', 'DELETE'])
@crossdomain(origin='https://hootbot-content-manager.hootapps.io')
@requires_auth
def delete_article_links():
    payload = request.get_data()
    data = json.loads(payload)
    for item in data:
        bot_log("Admin API: Deleting article link ID " + str(item['id']))
        ArticleLink.query.filter_by(id=item['id']).delete()
    db.session().commit()
    return "ok"


# TEST ENDPOINT TO TRIGGER SCHEDULED MESSAGES
@admin_api.route('/scheduled-message', methods=['POST'])
@requires_auth
def send_message():
    from hootbot.models.dao.scheduled_message_content import ScheduledMessageContent
    from hootbot.api.facebook import facebook_requests
    day = request.args.get("day")
    fb_id = request.args.get("id")
    content = ScheduledMessageContent.query.filter_by(day=day, topic="daily_tips").first()
    facebook_requests.post_text(fb_id, content.description.replace('<br>', u'\u000A'))
    facebook_requests.post_generic_template(fb_id, content.title, content.image_url, content.link)
    return "ok"


"""
@admin_api.route('/run-script', methods=['POST'])
@requires_auth
def run_script():
    from hootbot.scripts import populate_zendesk
    populate_zendesk.run()
    return "ok"
"""


@admin_api.route('/redis/get-key', methods=['GET'])
@requires_auth
def get_key():
    reply = redis_store.get(request.args.get('id'))
    if reply:
        return reply
    return "-1"


@admin_api.route('/redis/delete-key', methods=['POST'])
@requires_auth
def delete_key():
    redis_store.delete(request.args.get('id'))
    return "ok"




