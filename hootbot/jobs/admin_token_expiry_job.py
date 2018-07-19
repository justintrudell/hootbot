from datetime import datetime, timedelta

from hootbot.database.database import db, redis_store
from hootbot.logging.logger import bot_log
from hootbot.models.dao.admin_token import AdminToken


def admin_token_expiry_job(app, token):
    """
    Scheduled job used to expire stale auth tokens
    """
    with app.app_context():
        try:
            if redis_store.get('SCHEDULED_JOB_TOKEN') != token:
                return
            bot_log("Running auth token expiry job")
            AdminToken.query.filter(AdminToken.created_date <= datetime.utcnow() - timedelta(hours=24)).delete()
            db.session().commit()
        except Exception as e:
            print(e.message)
            raise
