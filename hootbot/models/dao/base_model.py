from hootbot.database.database import db


class BaseModel:

    @classmethod
    def get_or_create(cls, search_key, **kwargs):
        """
        Gets an instance of the model in the DB if it exists, otherwise creates it.
        :param cls: Provided model to check in the database.
        :param search_key Key used to query the database for an existing instance.
        :param kwargs: Keyword arguments used to create a model in the database.
        :return: Tuple of instance, and whether or not the instance existed or was created
        """
        instance = cls.query.filter_by(**search_key).first()
        if instance:
            return instance, True
        else:
            instance = cls(**kwargs)
            db.session().add(instance)
            db.session().commit()
            return instance, False

