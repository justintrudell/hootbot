import atexit
import logging
from logging.handlers import RotatingFileHandler
import binascii
import os

from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from apscheduler.triggers.interval import IntervalTrigger
from flask import Flask

import config
from hootbot.database.database import db, redis_store
from hootbot.endpoints.admin.academy_endpoints import admin_api
from hootbot.endpoints.facebook.messenger_endpoints import facebook_api
from hootbot.endpoints.zendesk.ticket_endpoints import zendesk_api
from hootbot.logging.logger import bot_log

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = ("mysql://%s:%s@%s:%s/%s"
                                         % (config.DB_USER,
                                            config.DB_PASS,
                                            config.DB_URL,
                                            config.DB_PORT,
                                            config.DB_NAME))
app.config['REDIS_URL'] = config.REDIS_URL
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.register_blueprint(facebook_api)
app.register_blueprint(admin_api)
app.register_blueprint(zendesk_api)
db.init_app(app)
redis_store.init_app(app)


def configure_logging():
    """
    Configures logging functionality.
    """
    if config.LOCATION != 'deis':
        formatter = logging.Formatter('%(asctime)s - %(levelname)s: %(message)s')
        handler = RotatingFileHandler('hootbot.log', maxBytes=10 ** 8, backupCount=1)
        handler.setLevel(logging.DEBUG)
        handler.setFormatter(formatter)
        app.logger.addHandler(handler)
        app.logger.setLevel(logging.DEBUG)
    bot_log("Starting application...")


def configure_scheduler():
    """
    Configures and starts jobs that need to run on a schedule
    """
    if config.ENVIRONMENT != 'production':
        return
    token = binascii.hexlify(os.urandom(32))
    redis_store.set('SCHEDULED_JOB_TOKEN', token)

    bot_log("Configuring scheduled jobs...")
    from hootbot.jobs.daily_tip_job import daily_tip_job
    daily_tip_scheduler = BackgroundScheduler()
    daily_tip_scheduler.start()
    daily_tip_scheduler.add_job(
        func=(lambda: daily_tip_job(app, token)),
        trigger=CronTrigger(day_of_week='mon-fri',
                            hour='16',
                            timezone='UTC'),
        id='daily_tips_job',
        name="Sends daily scheduled tips at 9am PST",
        replace_existing=True
    )
    atexit.register(lambda: daily_tip_scheduler.shutdown())

    from hootbot.jobs.user_objective_expiry_job import user_objective_expiry_job
    objective_expiry_scheduler = BackgroundScheduler()
    objective_expiry_scheduler.start()
    objective_expiry_scheduler.add_job(
        func=(lambda: user_objective_expiry_job(app, token)),
        trigger=IntervalTrigger(hours=1,
                                timezone="UTC"),
        id='user_objective_expiry_job',
        name="Periodically clears stale user_objective entries",
        replace_existing=True
    )
    atexit.register(lambda: objective_expiry_scheduler.shutdown())

    from hootbot.jobs.admin_token_expiry_job import admin_token_expiry_job
    admin_token_expiry_scheduler = BackgroundScheduler()
    admin_token_expiry_scheduler.start()
    admin_token_expiry_scheduler.add_job(
        func=(lambda: admin_token_expiry_job(app, token)),
        trigger=IntervalTrigger(hours=8,
                                timezone="UTC"),
        id='admin_token_expiry_job',
        name="Periodically clears stale admin auth tokens",
        replace_existing=True
    )
    atexit.register(lambda: admin_token_expiry_scheduler.shutdown())


configure_logging()
configure_scheduler()

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
