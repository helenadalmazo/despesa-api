class NotFoundException(Exception):
    status_code = 404

    def __init__(self, message):
        Exception.__init__(self)
        self.message = message


class ValidationException(Exception):
    status_code = 422
    errors = []

    def __init__(self, message, errors):
        Exception.__init__(self)
        self.message = message
        self.errors = errors


class BusinessException(Exception):
    status_code = 400

    def __init__(self, message):
        Exception.__init__(self)
        self.message = message
