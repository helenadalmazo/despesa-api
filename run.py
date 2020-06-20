from flask import Flask
import os.path

from config import Config, database_filename

def create_app():
    app = Flask(__name__)

    app.config.from_object(Config)

    from database.model import database
    database.init_app(app)

    from blueprint.app import app_blueprint

    app.register_blueprint(app_blueprint)

    with app.app_context():
        if os.path.exists(database_filename) == False:
            database.create_all() 

    return app

if __name__ == "__main__":
    app = create_app()
    app.run()
