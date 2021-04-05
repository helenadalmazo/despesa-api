from database.database import database
import enum


class ExpenseCategory(database.Model):
    id = database.Column(database.Integer, primary_key=True)
    group = database.Column(database.String(127), nullable=False)
    name = database.Column(database.String(127), nullable=False)

    def json(self):
        return {
            "id": self.id,
            "group": self.group,
            "name": self.name
        }


class Expense(database.Model):
    id = database.Column(database.Integer, primary_key=True)
    created_by = database.Column(database.Integer, database.ForeignKey("user.id"), nullable=False)
    date_created = database.Column(database.DateTime, nullable=False)
    group_id = database.Column(database.Integer, database.ForeignKey("group.id"), nullable=False)
    category_id = database.Column(database.Integer, database.ForeignKey("expense_category.id"), nullable=False)
    name = database.Column(database.String(127), nullable=False)
    value = database.Column(database.Float, nullable=False)
    description = database.Column(database.String(255), nullable=True)
    items = database.relationship("ExpenseItem")

    created_by_user = database.relationship("User")
    category = database.relationship("ExpenseCategory")

    def json(self):
        return {
            "id": self.id,
            "created_by": self.created_by_user.json(),
            "date_created": self.date_created.strftime("%Y-%m-%d"),
            "group_id": self.group_id,
            "category": self.category.json(),
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

    user = database.relationship("User")

    def json(self):
        return {
            "id": self.id,
            "user": self.user.json(),
            "value": self.value
        }


class GroupUserRole(enum.Enum):
    OWNER = "OWNER"
    ADMIN = "ADMIN"
    USER = "USER"


class GroupUser(database.Model):
    group_id = database.Column(database.Integer, database.ForeignKey("group.id"), primary_key=True)
    user_id = database.Column(database.Integer, database.ForeignKey("user.id"), primary_key=True)
    role = database.Column(database.String(127), nullable=False)

    user = database.relationship("User")

    def json(self):
        return {
            "user": self.user.json(),
            "role": self.role
        }


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
    name = database.Column(database.String(127), nullable=False)
    users = database.relationship("GroupUser")

    def get_user_role(self, user):
        for group_user in self.users:
            if group_user.user_id == user.id:
                return GroupUserRole(group_user.role)
        return None

    def json(self):
        return {
            "id": self.id,
            "name": self.name,
            "users": [group_user.json() for group_user in self.users]
        }


class Device(database.Model):
    id = database.Column(database.Integer, primary_key=True)
    user_id = database.Column(database.Integer, database.ForeignKey("user.id"), nullable=False)
    token = database.Column(database.String(127), nullable=False)

    def json(self):
        return {
            "id": self.id,
            "user_id": self.user_id,
            "token": self.token
        }