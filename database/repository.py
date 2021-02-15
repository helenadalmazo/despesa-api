import datetime

from database.database import database
from database.model import Expense, ExpenseItem, GroupUser, Group, User
from exception.exception import NotFoundException
from sqlalchemy.sql import func


class ExpenseRepository:
    def list(self, group):
        return Expense.query\
            .filter(Expense.group_id == group.id)\
            .all()

    def list_value_grouped_by_user(self, group):
        return Expense.query.\
            join(ExpenseItem). \
            filter(Expense.group_id == group.id).\
            group_by(ExpenseItem.user_id).\
            with_entities(ExpenseItem.user_id, func.sum(ExpenseItem.value).label("value")).\
            all()

    def list_value_grouped_by_year_month(self, group):
        return Expense.query.\
            join(ExpenseItem). \
            filter(Expense.group_id == group.id). \
            group_by(func.strftime("%Y-%m", Expense.date_created)).\
            with_entities(func.strftime("%Y-%m", Expense.date_created).label("date"), func.sum(ExpenseItem.value).label("value")).\
            all()

    def get(self, group, id):
        filters = (
            Expense.group_id == group.id,
            Expense.id == id
        )
        return Expense.query\
            .filter(*filters)\
            .first()

    def get_or_404(self, group, id):
        expense = self.get(group, id)

        if not expense:
            raise NotFoundException(f"Não foi encontrada despesa com identificador [{id}].")

        return expense

    def save(self, group, user, _dict):
        expense = Expense(**_dict)
        expense.created_by = user.id
        expense.date_created = datetime.datetime.now()
        expense.group_id = group.id

        database.session.add(expense)
        database.session.flush()

        return expense

    def update(self, group, id, _dict):
        expense = self.get(group, id)

        # Expense.query.filter_by(id=id).update(_dict)
        for key, value in _dict.items():
            if hasattr(expense, key):
                setattr(expense, key, value)

        return expense

    def delete(self, group, id):
        expense = self.get(group, id)

        database.session.delete(expense)


class ExpenseItemRepository:
    def get(self, id):
        return ExpenseItem.query.filter_by(id=id).first()

    def get_by_expense_and_user(self, expense, user):
        filters = (
            ExpenseItem.expense_id == expense.id,
            ExpenseItem.user_id == user.id
        )
        return ExpenseItem.query. \
            filter(*filters) \
            .first()

    def save(self, _dict):
        expense_item = ExpenseItem(**_dict)

        database.session.add(expense_item)

        return expense_item

    def update(self, id, _dict):
        expense_item = self.get(id)

        for key, value in _dict.items():
            if hasattr(expense_item, key):
                setattr(expense_item, key, value)

        return expense_item

    def delete(self, id):
        expense_item = self.get(id)

        database.session.delete(expense_item)


class GroupUserRepository:
    def get(self, group, user, id):
        filters = (
            GroupUser.group_id == group.id,
            GroupUser.user_id == user.id,
            id == id
        )
        return GroupUser.query\
            .filter(*filters)\
            .first()

    def save(self, _dict):
        group_user = GroupUser(**_dict)

        database.session.add(group_user)
        database.session.commit()

        return group_user

    def update(self, group, user, id, _dict):
        group_user = self.get(group, user, id)

        for key, value in _dict.items():
            if hasattr(group_user, key):
                setattr(group_user, key, value)

        database.session.commit()

        return group_user

    def delete(self, group, user, id):
        group_user = self.get(group, user, id)

        database.session.delete(group_user)
        database.session.commit()


class UserRepository:
    def list_not_in_by_full_name(self, users, full_name):
        filters = [
            User.id.notin_([user.id for user in users]),
        ]

        if full_name:
            filters += [
                User.full_name.startswith(full_name)
            ]

        filters = tuple(filters)

        return User.query\
            .filter(*filters)\
            .all()

    def get(self, id):
        return User.query.get(id)

    def get_or_404(self, id):
        user = self.get(id)

        if not user:
            raise NotFoundException(f"Não foi encontrado usuário com identificador [{id}].")

        return user

    def get_by_username(self, username):
        return User.query.\
            filter(User.username == username)\
            .first()

    def save(self, _dict):
        user = User(**_dict)

        database.session.add(user)
        database.session.commit()

        return user


class GroupRepository:
    def list(self, user):
        return Group.query\
            .join(GroupUser)\
            .filter(GroupUser.user_id == user.id)\
            .all()

    def get(self, user, id):
        return Group.query\
            .join(GroupUser)\
            .filter(GroupUser.user_id == user.id)\
            .filter(Group.id == id) \
            .first()

    def get_or_404(self, user, id):
        group = self.get(user, id)

        if not group:
            raise NotFoundException(f"Não foi encontrado grupo com identificador [{id}].")

        return group

    def save(self, _dict):
        group = Group(**_dict)

        database.session.add(group)
        database.session.flush()

        return group

    def update(self, user, id, _dict):
        group = self.get_or_404(user, id)

        for key, value in _dict.items():
            if hasattr(group, key):
                setattr(group, key, value)

        database.session.commit()

        return group

    def delete(self, user, id):
        group = self.get_or_404(user, id)

        database.session.delete(group)
        database.session.commit()
