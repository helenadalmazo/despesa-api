from flask import Flask

from config import Config

def create_app():
    app = Flask(__name__)

    app.config.from_object(Config)

    from blueprint.app import app_blueprint

    app.register_blueprint(app_blueprint)

    return app

if __name__ == "__main__":
    app = create_app()
    app.run()
