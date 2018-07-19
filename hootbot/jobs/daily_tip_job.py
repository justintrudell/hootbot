from hootbot.database.database import db
from hootbot.api.facebook import facebook_requests
from hootbot.logging.logger import bot_log
from hootbot.models.dao.scheduled_message import ScheduledMessage
from hootbot.models.dao.scheduled_message_content import ScheduledMessageContent
import config
from hootbot.database.database import redis_store


# TODO: Optimize (memoize) queries for ScheduledMessageContent - or investigate to make sure that's happening in the bg
def daily_tip_job(app, token):
    """
    Scheduled job used to send users their daily tips
    """
    if config.ENVIRONMENT != 'production':
        return
    with app.app_context():
        try:
            if redis_store.get('SCHEDULED_JOB_TOKEN') != token:
                return
            bot_log("Running daily tip job")
            # If the amount of rows in the table starts getting considerably large, consider using a
            # yield_per() type of method to get the objects in batches
            scheduled_messages = ScheduledMessage.query.all()
            for message in scheduled_messages:
                try:
                    content = ScheduledMessageContent.query.filter_by(day=message.next_day_to_send,
                                                                      topic="daily_tips").first()
                    # Facebook only seems to accept unicode linebreak in this case so we do string replacement
                    facebook_requests.post_text(message.facebook_id, content.description.replace('<br>', u'\u000A'))
                    facebook_requests.post_generic_template(message.facebook_id,
                                                            content.title,
                                                            content.image_url,
                                                            content.link)
                    if message.next_day_to_send < 11:
                        message.next_day_to_send += 1
                    else:
                        ScheduledMessage.query.filter_by(id=message.id).delete()
                except Exception as e:
                    # Swallow inner exception to allow other jobs to continue
                    print(e.message)
            db.session().commit()
        except Exception as e:
            # Raise outer layer exception as it's likely catastrophic to the job
            print(e.message)
            raise
