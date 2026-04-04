from fastapi import Request

from lifespan import Hackplate


class HackplateRequest(Request):
    app: Hackplate


def get_session(request: HackplateRequest):
    return request.app.state.config.db.get_session()
