from flask import Flask
import os.path

from config import Config, database_filename

def create_app():
    app = Flask(__name__)

    app.config.from_object(Config)

    from database.model import database
    database.init_app(app)

    from blueprint.app import app_blueprint
    from blueprint.expense import expense_blueprint

    app.register_blueprint(app_blueprint)
    app.register_blueprint(expense_blueprint)

    from exception.exception import NotFoundException, ValidationException
    from error_handler.error_handler import handle_not_found_exception, handle_validation_exception

    app.register_error_handler(NotFoundException, handle_not_found_exception)
    app.register_error_handler(ValidationException, handle_validation_exception)

    with app.app_context():
        if os.path.exists(database_filename) == False:
            database.create_all() 

    return app

if __name__ == "__main__":
    app = create_app()
    app.run()
