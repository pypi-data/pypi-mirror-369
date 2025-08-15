class CommunicationError(Exception):
    pass


class DisconnectedError(CommunicationError):
    pass


class SendError(CommunicationError):
    pass
