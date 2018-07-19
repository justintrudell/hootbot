from datetime import datetime, timedelta

from hootbot.database.database import db, redis_store
from hootbot.logging.logger import bot_log
from hootbot.models.dao.user_objectives import UserObjective


def user_objective_expiry_job(app, token):
    """
    Scheduled job used to expire old user_objectives entries
    """
    with app.app_context():
        try:
            if redis_store.get('SCHEDULED_JOB_TOKEN') != token:
                return
            bot_log("Running objective expiry job")
            # If the amount of rows in the table starts getting considerably large, consider using a
            # yield_per() type of method to get the objects in batches
            UserObjective.query.filter(UserObjective.timestamp <= datetime.utcnow() - timedelta(hours=6)).delete()
            db.session().commit()
        except Exception as e:
            print(e.message)
            raise
