from functools import wraps
from flask import request, abort

import config as config
from hootbot.models.dao.admin_token import AdminToken


def requires_auth(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if 'hootbot-token' not in request.headers:
            abort(401)
        token = request.headers['hootbot-token']
        if not token:  # no header set
            abort(401)
        tokens = {x.token for x in AdminToken.query.all()}
        if token not in tokens:
            abort(401)
        return f(*args, **kwargs)
    return decorated
