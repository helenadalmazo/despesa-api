from flask import Flask
import os.path

import firebase_admin
from firebase_admin import credentials

from config import Config, database_filename


def create_app():
    app = Flask(__name__)

    app.config.from_object(Config)

    from database.model import database
    database.init_app(app)

    from blueprint.app import app_blueprint
    from blueprint.auth import auth_blueprint
    from blueprint.group import group_blueprint
    from blueprint.expense import expense_blueprint
    from blueprint.statistic import statistic_blueprint

    app.register_blueprint(app_blueprint)
    app.register_blueprint(auth_blueprint)
    app.register_blueprint(group_blueprint)
    app.register_blueprint(expense_blueprint)
    app.register_blueprint(statistic_blueprint)

    from exception.exception import BusinessException, ForbiddenException, NotFoundException, ValidationException
    from error_handler.error_handler import handle_business_exception, handle_forbidden_exception, handle_not_found_exception, handle_validation_exception, handle_exception

    app.register_error_handler(BusinessException, handle_business_exception)
    app.register_error_handler(ForbiddenException, handle_forbidden_exception)
    app.register_error_handler(NotFoundException, handle_not_found_exception)
    app.register_error_handler(ValidationException, handle_validation_exception)
    app.register_error_handler(Exception, handle_exception)

    with app.app_context():
        if not os.path.exists(database_filename):
            database.create_all()

    cred = credentials.Certificate("config/despesa-app-firebase-adminsdk-hkz0j-7f12ba7b1a.json")
    firebase_admin.initialize_app(cred)

    return app


if __name__ == "__main__":
    app = create_app()
    app.run()
