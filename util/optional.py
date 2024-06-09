import uuid


def get_hash() -> str:
    return uuid.uuid4().hex[:8]
