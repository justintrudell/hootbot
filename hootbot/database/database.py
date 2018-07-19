"""
This class exists to solve circular dependency problems with the 'db' and 'redis_store' variables.
This is an inherent problem with SQLAlchemy and this fix should be suitable to the level
of scale required for this specific application.
"""
from flask_sqlalchemy import SQLAlchemy
from flask_redis import FlaskRedis

db = SQLAlchemy()
redis_store = FlaskRedis()
