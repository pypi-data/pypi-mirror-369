from elemental_tools.logger import Logger

from elemental_tools.Jarvis.tools import BrainiacRequest

logger = Logger('JARVIS', 'exceptions').log


class Error(Exception):
    def __init__(self, request: BrainiacRequest = None, message="An error occurred"):
        message = message
        super().__init__(message)
        logger('error', f'Error occurred with request: {vars(request)}')


class InvalidOption(Exception):
    def __init__(self, missing: str = None, message_intro: str = "You must provide a valid"):
        message = f"{message_intro} {missing}"
        super().__init__(message)
        logger('error', f'Invalid Option Found. Missing: {missing}')


class Unauthorized(Exception):
    def __init__(self, message):
        message = message
        super().__init__(message)
        logger("error", "User Unauthorized")


class ParserError(Exception):
    def __init__(self, message):
        logger("error", "User Unauthorized")
        message = message
        super().__init__(message)
