from database.database import database

class Expense(database.Model):
    id = database.Column(database.Integer, primary_key=True)
    user_id = database.Column(database.Integer, database.ForeignKey("user.id"), nullable=False)
    name = database.Column(database.String(124), nullable=False)
    value = database.Column(database.Float, nullable=False)

    def json(self):
        return {
            "id": self.id,
            "user_id": self.user_id,
            "name": self.name,
            "value": self.value
        }


group_users = database.Table(
    "group_users",
    database.Column("group_id", database.Integer, database.ForeignKey("group.id")),
    database.Column("user_id", database.Integer, database.ForeignKey("user.id"))
)


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


class Group(database.Model):
    id = database.Column(database.Integer, primary_key=True)
    user_id = database.Column(database.Integer, database.ForeignKey("user.id"), nullable=False)
    name = database.Column(database.String(124), nullable=False)
    users = database.relationship("User", secondary=group_users)

    def json(self):
        return {
            "id": self.id,
            "user_id": self.user_id,
            "name": self.name,
            "users": [user.id for user in self.users]
        }