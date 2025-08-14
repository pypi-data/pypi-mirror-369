import uuid


def random_uuid():
    return str(uuid.uuid4())


def simple_uuid():
    return str(uuid.uuid4()).replace('-', '')