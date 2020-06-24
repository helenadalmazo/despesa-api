from database.database import database

class Expense(database.Model):
    id = database.Column(database.Integer, primary_key=True)
    name = database.Column(database.String(124), nullable=False)
    value = database.Column(database.Float, nullable=False)
    user_id = database.Column(database.Integer, database.ForeignKey("user.id"), nullable=False)

    def json(self):
        return {
            "id": self.id,
            "user_id": self.user_id,
            "name": self.name,
            "value": self.value
        }

class User(database.Model):
    id = database.Column(database.Integer, primary_key=True)
    username = database.Column(database.String(124), nullable=False, unique=True)
    password = database.Column(database.String(124), nullable=False)

    def json(self):
        return {
            "id": self.id,
            "username": self.username,
            "password": self.password
        }