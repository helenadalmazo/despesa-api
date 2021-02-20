from flask import Flask
from flask_script import Manager
from flask_migrate import Migrate, MigrateCommand
from config import Config


def create_manager():
    app = Flask(__name__)

    app.config.from_object(Config)

    from database.model import database
    database.init_app(app)

    migrate = Migrate(app, database)

    manager = Manager(app)

    manager.add_command("db", MigrateCommand)

    return manager


if __name__ == "__main__":
    manager = create_manager()
    manager.run()
