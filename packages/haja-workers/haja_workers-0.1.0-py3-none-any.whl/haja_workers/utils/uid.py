from uuid import uuid4

def uid() -> str:
    return uuid4().hex
