import json
import textwrap

from flask import Blueprint, request, abort

from hootbot.database.database import db
from hootbot.models.dao.zendesk_ticket import ZendeskTicket
from hootbot.models.enums.zendesk_status import ZendeskStatus
from hootbot.api.facebook import facebook_requests
from hootbot.constants import constants
from hootbot.logging.logger import bot_log


zendesk_api = Blueprint("zendesk_api", __name__)


@zendesk_api.route('/open-ticket', methods=['POST'])
def open_ticket():
    """
    Zendesk will POST to this endpoint when a ticket that's been tagged with 'hootbot' is set to Open from Solved
    """
    data = json.loads(request.get_data())
    try:
        ZendeskTicket.query.filter_by(id=data['ticket']['id']).first().status = ZendeskStatus.OPEN.value
        db.session().commit()
    except AttributeError as e:
        bot_log(e)
        abort(404)
    return "ok"


@zendesk_api.route('/solve-ticket', methods=['POST'])
def solve_ticket():
    """
    Zendesk will POST to this endpoint when a ticket that's been tagged with 'hootbot' is set to Solved
    """
    data = json.loads(request.get_data())
    try:
        ZendeskTicket.query.filter_by(id=data['ticket']['id']).first().status = ZendeskStatus.SOLVED.value
        db.session().commit()
    except AttributeError as e:
        bot_log(e)
        abort(404)
    return "ok"


@zendesk_api.route('/close-ticket', methods=['POST'])
def close_ticket():
    """
    Zendesk will POST to this endpoint when a ticket that's been tagged with 'hootbot' is set to Closed
    """
    data = json.loads(request.get_data())
    try:
        ZendeskTicket.query.filter_by(id=data['ticket']['id']).delete()
        db.session().commit()
    except AttributeError as e:
        bot_log(e)
        abort(404)
    return "ok"


@zendesk_api.route('/add-comment', methods=['POST'])
def add_comment():
    """
    Zendesk will POST to this endpoint when a support advocate publicly comments on a ticket tagged with 'hootbot'
    """
    data = json.loads(request.get_data())
    try:
        ticket = ZendeskTicket.query.filter_by(id=data['ticket']['id']).first()
        comment = data['ticket']['comment'].encode('utf-8')
        # Trim the Hootsuite signature footer
        if comment.endswith(constants.END_OF_TICKET_SIGNATURE):
            comment = comment[:-len(constants.END_OF_TICKET_SIGNATURE)]
        # Facebook only allows sending on 640 characters max, split if the text is larger
        comments = textwrap.wrap(comment, 640, replace_whitespace=False)
        for text in comments:
            facebook_requests.post_text(ticket.user_id, text)
    except AttributeError as e:
        bot_log(e)
        abort(404)
    except KeyError as e:
        bot_log(e)
        abort(500)
    return "ok"
