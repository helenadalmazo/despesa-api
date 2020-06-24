from database.database import database
from database.model import Expense, User

class ExpenseRepository():
    def list(self):
        return Expense.query.all()

    def get(self, id):
        return Expense.query.get(id)

    def save(self, _dict):
        expense = Expense(**_dict)
        database.session.add(expense)
        database.session.commit()
        return expense

    def update(self, id, _dict):
        expense = self.get(id)

        if expense:
            # Expense.query.filter_by(id=id).update(_dict)
            for key, value in _dict.items():
                if hasattr(expense, key):
                    setattr(expense, key, value)

            database.session.commit()
            return expense
        else:
            return save(_dict)

    def delete(self, id):
        expense = self.get(id)
        database.session.delete(expense)
        database.session.commit()


class UserRepository():
    def get(self, id):
        return User.query.get(id)

    def get_by_username(self, username):
        return User.query.filter_by(username=username).first()

    def save(self, _dict):
        user = User(**_dict)
        database.session.add(user)
        database.session.commit()
        return user