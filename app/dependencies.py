from app.config.config import HackplateRequest


def get_session(request: HackplateRequest):
    return request.app.state.config.db.get_session()
