from database.database import database
from functools import wraps


def transactional(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        function_return = func(*args, **kwargs)
        database.session.commit()
        return function_return

    return wrapper
