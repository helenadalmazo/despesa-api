import copy
from datetime import datetime

from flask import Blueprint, jsonify, request

from firebase_admin import messaging

from auth.decorator import token_required
from database.model import GroupUserRole
from database.repository import ExpenseCategoryRepository, ExpenseRepository, ExpenseItemRepository, DeviceRepository, GroupRepository, UserRepository
from exception.exception import BusinessException
from transactional.decorator import transactional
from utils import utils

expense_blueprint = Blueprint("expense", __name__, url_prefix="/expense")

expense_category_repository = ExpenseCategoryRepository()
expense_repository = ExpenseRepository()
expense_item_repository = ExpenseItemRepository()
device_repository = DeviceRepository()
group_repository = GroupRepository()
user_repository = UserRepository()


@expense_blueprint.route("/group/<int:group_id>", methods=["GET"])
@token_required
def index(current_user, group_id):
    group = group_repository.get_or_404(current_user, group_id)

    today = datetime.now()
    month = request.args.get("month", today.month)
    year = request.args.get("year", today.year)

    expense_list = expense_repository.list_by_year_month(group, year, month)

    return jsonify([expense.json() for expense in expense_list])


@expense_blueprint.route("/group/<int:group_id>/<int:id>", methods=["GET"])
@token_required
def get(current_user, id, group_id):
    group = group_repository.get_or_404(current_user, group_id)

    expense = expense_repository.get_or_404(group, id)

    return jsonify(expense.json())


@expense_blueprint.route("/group/<int:group_id>", methods=["POST"])
@token_required
@transactional
def save(current_user, group_id):
    group = group_repository.get_or_404(current_user, group_id)

    utils.check_permission(current_user, group, [GroupUserRole.OWNER, GroupUserRole.ADMIN])

    json_data = request.get_json()

    utils.validate_params(json_data, ["name", "category_id", "value"])
    data = utils.parse_params(json_data, ["name", "category_id", "value", "description", "items"])

    data_items = []

    if "items" in data:
        utils.validate_params(data, ["user_id", "value"], "items")
        data_items = data.pop("items")

        if data["value"] != sum(data_item["value"] for data_item in data_items):
            raise BusinessException("A soma dos valores dos items não equivale ao total da despesa.")

    expense = expense_repository.save(group, current_user, data)
    save_items(expense, data_items, group)
    notify(current_user, group, expense)

    return jsonify(expense.json())


@expense_blueprint.route("/group/<int:group_id>/<int:id>", methods=["PUT"])
@token_required
@transactional
def update(current_user, id, group_id):
    group = group_repository.get_or_404(current_user, group_id)

    utils.check_permission(current_user, group, [GroupUserRole.OWNER, GroupUserRole.ADMIN])

    expense = expense_repository.get_or_404(group, id)

    json_data = request.get_json()

    data = utils.parse_params(json_data, ["name", "category_id", "value", "description", "items"])
    data_items = []

    if "items" in data:
        utils.validate_params(data, ["user_id", "value"], "items")
        data_items = data.pop("items")

        if data["value"] != sum(data_item["value"] for data_item in data_items):
            raise BusinessException("A soma dos valores dos não equivale ao total da despesa.")

    expense = expense_repository.update(group, id, data)
    update_items(expense, data_items, group)

    return jsonify(expense.json())


@expense_blueprint.route("/group/<int:group_id>/<int:id>", methods=["DELETE"])
@token_required
@transactional
def delete(current_user, id, group_id):
    group = group_repository.get_or_404(current_user, group_id)

    utils.check_permission(current_user, group, [GroupUserRole.OWNER, GroupUserRole.ADMIN])

    expense = expense_repository.get_or_404(group, id)

    delete_items(expense)
    expense_repository.delete(group, id)

    return jsonify({"success": True})


@expense_blueprint.route("/categories", methods=["GET"])
@token_required
def list_categories(current_user):
    expense_category_list = expense_category_repository.list()

    return jsonify([expense_category.json() for expense_category in expense_category_list])


@expense_blueprint.route("/group/<int:group_id>/balance", methods=["GET"])
@token_required
def balance(current_user, group_id):
    group = group_repository.get_or_404(current_user, group_id)

    today = datetime.now()
    month = request.args.get("month", today.month)
    year = request.args.get("year", today.year)

    expense_list = expense_repository.list_by_year_month(group, year, month)

    if not expense_list:
        return jsonify({"statement": [], "balance": None, "split": []})

    balance_list = []
    current_user_statement_list = []

    for expense in expense_list:
        credit_balance_item = get_balance_item(balance_list, expense.created_by)
        credit_balance_item["value"] = credit_balance_item["value"] + expense.value

        if expense.created_by == current_user.id:
            credit_statement_item = {
                "expense_id": expense.id,
                "name": expense.name,
                "value": expense.value
            }
            current_user_statement_list.append(credit_statement_item)

        for item in expense.items:
            debit_balance_item = get_balance_item(balance_list, item.user_id)
            debit_balance_item["value"] = debit_balance_item["value"] + item.value * -1

            if item.user_id == current_user.id:
                debit_statement_item = {
                    "expense_id": expense.id,
                    "expense_item_id": item.id,
                    "name": expense.name,
                    "value": item.value * -1
                }
                current_user_statement_list.append(debit_statement_item)

    balance = sum(balance_item["value"] for balance_item in balance_list)
    if balance != 0:
        raise Exception(f"O balancete do grupo [{group_id}] não fechou.")

    split_list = get_split_list(copy.deepcopy(balance_list))

    current_user_split_list = []
    for split_item in split_list:
        if split_item["receiver"] == current_user.id or split_item["payer"] == current_user.id:
            current_user_split_item = {
                "payer": user_repository.get(split_item["payer"]).json(),
                "receiver": user_repository.get(split_item["receiver"]).json(),
                "value": split_item["value"]
            }
            current_user_split_list.append(current_user_split_item)

    current_user_balance = next(filter(lambda b: b["user_id"] == current_user.id, balance_list), None)["value"]

    return jsonify({"statement": current_user_statement_list, "balance": current_user_balance, "split": current_user_split_list})


def save_items(expense, data_items, group):
    value = None
    users = []

    if data_items:
        value = data_items[0]["value"]
        users = [user_repository.get_or_404(item["user_id"]) for item in data_items]
    else:
        value = expense.value / len(group.users)
        users = [user_repository.get(group_user.user_id) for group_user in group.users]

    for user in users:
        data = {
            "expense_id": expense.id,
            "value": value,
            "user_id": user.id
        }

        expense_item_repository.save(data)


def update_items(expense, data_items, group):
    value = None
    users = []

    if data_items:
        value = data_items[0]["value"]
        users = [user_repository.get_or_404(item["user_id"]) for item in data_items]
    else:
        value = expense.value / len(group.users)
        users = [user_repository.get(group_user.user_id) for group_user in group.users]

    for user in users:
        expense_item = expense_item_repository.get_by_expense_and_user(expense, user)

        data = {
            "value": value
        }

        if expense_item:
            expense_item_repository.update(expense_item.id, data)
        else:
            data["expense_id"] = expense.id
            data["user_id"] = user.id
            expense_item_repository.save(data)

    users_id = [user.id for user in users]

    for item in expense.items:
        if not item.user_id in users_id:
            expense_item_repository.delete(item.id)


def delete_items(expense):
    for item in expense.items:
        expense_item_repository.delete(item.id)


def notify(trigger_user, group, expense):
    users_to_notify = [item.user for item in expense.items]

    if trigger_user in users_to_notify:
        users_to_notify.remove(trigger_user)

    title = group.name
    body = f"{trigger_user.full_name} criou uma nova despesa: {expense.name}"

    for user in users_to_notify:
        device = device_repository.get_by_user(user)

        if device:
            message = messaging.Message(
                notification=messaging.Notification(
                    title=title,
                    body=body,
                ),
                token=device.token
            )

            response = messaging.send(message)


def get_balance_item(balance_list, user_id):
    balance_item = next(filter(lambda bi: bi["user_id"] == user_id, balance_list), None)
    if balance_item:
        return balance_item

    balance_item = {
        "user_id": user_id,
        "statements": [],
        "value": 0
    }
    balance_list.append(balance_item)
    return balance_item


def get_split_list(balance_list):
    credit_balance_list = list(filter(lambda si: si["value"] > 0, balance_list))
    credit_balance_list = sorted(credit_balance_list, key=lambda si: si["value"], reverse=True)

    debit_balance_list = list(filter(lambda si: si["value"] < 0, balance_list))

    def lambda_positive_value(si):
        si["value"] = si["value"] * -1
        return si

    debit_balance_list = list(map(lambda si: lambda_positive_value(si), debit_balance_list))
    debit_balance_list = sorted(debit_balance_list, key=lambda si: si["value"], reverse=True)

    split_list = []

    for credit_balance_item in credit_balance_list:
        while credit_balance_item["value"] > 0:
            split_item = {
                "receiver": credit_balance_item["user_id"]
            }

            debit_balance_item = debit_balance_list[0]

            split_item["payer"] = debit_balance_item["user_id"]

            value = 0

            if debit_balance_item["value"] > credit_balance_item["value"]:
                value = credit_balance_item["value"]
                debit_balance_item["value"] = debit_balance_item["value"] - value
            else:
                value = debit_balance_item["value"]
                debit_balance_list.remove(debit_balance_item)

            credit_balance_item["value"] = credit_balance_item["value"] - value

            split_item["value"] = value
            split_list.append(split_item)

        credit_balance_list.remove(credit_balance_item)

    return split_list