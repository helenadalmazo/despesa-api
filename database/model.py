from database.database import database


class Expense(database.Model):
    id = database.Column(database.Integer, primary_key=True)
    created_by = database.Column(database.Integer, database.ForeignKey("user.id"), nullable=False)
    date_created = database.Column(database.DateTime, nullable=False)
    group_id = database.Column(database.Integer, database.ForeignKey("group.id"), nullable=True)
    name = database.Column(database.String(127), nullable=False)
    value = database.Column(database.Float, nullable=False)
    description = database.Column(database.String(255), nullable=True)
    items = database.relationship("ExpenseItem")

    def json(self):
        return {
            "id": self.id,
            "created_by": self.created_by,
            "date_created": self.date_created.strftime("%Y-%m-%d"),
            "group_id": self.group_id,
            "name": self.name,
            "description": self.description,
            "value": self.value,
            "items": [item.json() for item in self.items]
        }


class ExpenseItem(database.Model):
    id = database.Column(database.Integer, primary_key=True)
    expense_id = database.Column(database.Integer, database.ForeignKey("expense.id"))
    user_id = database.Column(database.Integer, database.ForeignKey("user.id"), nullable=False)
    value = database.Column(database.Float, nullable=False)

    def json(self):
        return {
            "id": self.id,
            "expense_id": self.expense_id,
            "user_id": self.user_id,
            "value": self.value
        }


group_users = database.Table(
    "group_users",
    database.Column("group_id", database.Integer, database.ForeignKey("group.id")),
    database.Column("user_id", database.Integer, database.ForeignKey("user.id"))
)


class User(database.Model):
    id = database.Column(database.Integer, primary_key=True)
    username = database.Column(database.String(127), nullable=False, unique=True)
    password = database.Column(database.String(127), nullable=False)
    full_name = database.Column(database.String(127), nullable=False)

    def json(self):
        return {
            "id": self.id,
            "username": self.username,
            "full_name": self.full_name
        }


class Group(database.Model):
    id = database.Column(database.Integer, primary_key=True)
    created_by = database.Column(database.Integer, database.ForeignKey("user.id"), nullable=False)
    name = database.Column(database.String(127), nullable=False)
    users = database.relationship("User", secondary=group_users)

    def json(self):
        return {
            "id": self.id,
            "created_by": self.created_by,
            "name": self.name,
            "users": [user.json() for user in self.users]
        }
