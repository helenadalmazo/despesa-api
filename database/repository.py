from database.database import database
from database.model import Expense, Group, User
from exception.exception import NotFoundException

class ExpenseRepository():
    def list(self, user):
        return Expense.query.filter_by(created_by=user.id).all()

    def get(self, user, id):
        return Expense.query.filter_by(created_by=user.id, id=id).first()

    def get_or_404(self, user, id):
        expense = self.get(user, id)

        if not expense: 
            raise NotFoundException(f"Não foi encontrada despesa com identificador [{id}].")

    def save(self, user, _dict):
        expense = Expense(**_dict)
        expense.created_by = user.id

        database.session.add(expense)
        database.session.commit()

        return expense

    def update(self, user, id, _dict):
        expense = self.get(user, id)

        # Expense.query.filter_by(id=id).update(_dict)
        for key, value in _dict.items():
            if hasattr(expense, key):
                setattr(expense, key, value)

        database.session.commit()

        return expense

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



class GroupRepository():
    def list(self, user):
        return Group.query.filter_by(created_by=user.id).all()

    def get(self, user, id):
        return Group.query.filter_by(created_by=user.id, id=id).first()

    def get_or_404(self, user, id):
        group = self.get(user, id)

        if not group: 
            raise NotFoundException(f"Não foi encontrado group com identificador [{id}].")

    def save(self, user, _dict):
        group = Group(**_dict)
        group.created_by = user.id
        group.users.append(user)

        database.session.add(group)
        database.session.commit()

        return group

    def update(self, user, id, _dict):
        group = self.get(user, id)

        for key, value in _dict.items():
            if hasattr(group, key):
                setattr(group, key, value)

        database.session.commit()

        return group

    def delete(self, user, id):
        group = self.get(user, id)

        database.session.delete(group)
        database.session.commit()