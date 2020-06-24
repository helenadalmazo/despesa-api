from database.database import database

class Expense(database.Model):
    id = database.Column(database.Integer, primary_key=True)
    name = database.Column(database.String(124), nullable=False)
    value = database.Column(database.Float, nullable=False)

    def json(self):
        return {
            "id": self.id,
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