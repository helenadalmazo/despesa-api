from flask import Flask

def create_app():
    app = Flask(__name__)

    from blueprint.app import app_blueprint

    app.register_blueprint(app_blueprint)

    return app

if __name__ == "__main__":
    app = create_app()
    app.run(debug=True)
