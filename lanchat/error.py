class LanChatError(Exception):
    pass


class ServerNotFound(LanChatError):
    pass


class InvalidCommand(LanChatError):
    pass
