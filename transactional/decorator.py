from database.database import database


def transactional(function):
    def wrapper(*args, **kwargs):
        function(*args, **kwargs)
        database.session.commit()

    return wrapper
