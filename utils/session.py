from __future__ import annotations


DEFAULT_USER = {
    "id": "local-learner",
    "email": "local@learner.app",
    "name": "Learner",
}


def get_active_user() -> dict:
    return DEFAULT_USER
