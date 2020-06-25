from database.database import database
from database.model import Expense, User

class ExpenseRepository():
    def list(self, user):
        return Expense.query.filter_by(user_id=user.id).all()

    def get(self, user, id):
        return Expense.query.filter_by(user_id=user.id, id=id).one()

    def save(self, user, _dict):
        expense = Expense(**_dict)
        expense.user_id = user.id

        database.session.add(expense)
        database.session.commit()

        return expense

    def update(self, user, id, _dict):
        expense = self.get(user, id)

        if expense:
            # Expense.query.filter_by(id=id).update(_dict)
            for key, value in _dict.items():
                if hasattr(expense, key):
                    setattr(expense, key, value)

            database.session.commit()
            return expense
        else:
            return save(user, _dict)

    def delete(self, user, id):
        expense = self.get(user, id)

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