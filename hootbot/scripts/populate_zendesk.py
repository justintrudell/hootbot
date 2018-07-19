import csv
import os

from hootbot.database.database import db
from hootbot.models.dao.user import User
from hootbot.models.dao.zendesk_ticket import ZendeskTicket
from hootbot.models.enums.zendesk_status import ZendeskStatus


def run():
    __location__ = os.path.realpath(
        os.path.join(os.getcwd(), os.path.dirname(__file__)))

    with open(os.path.join(__location__, 'zd_dump.csv')) as _file:
        for row in csv.reader(_file, delimiter=','):
            ticket_id = row[0]
            name = str(row[2]).replace(' ', '').lower()
            email = row[3]
            zendesk_id = row[4]
            user = User(fb_id=zendesk_id, zendesk_id=zendesk_id, first_name=name, email=email)
            ticket = ZendeskTicket(ticket_id=ticket_id, status=ZendeskStatus.OPEN.value, user_id=zendesk_id)
            db.session().add(user)
            db.session().add(ticket)
        db.session().commit()
