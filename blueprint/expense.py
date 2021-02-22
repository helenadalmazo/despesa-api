from flask import Blueprint, jsonify, request

from firebase_admin import messaging

from auth.decorator import token_required
from database.model import GroupUserRole
from database.repository import ExpenseRepository, ExpenseItemRepository, DeviceRepository, GroupRepository, UserRepository
from exception.exception import BusinessException
from transactional.decorator import transactional
from utils import utils

expense_blueprint = Blueprint("expense", __name__, url_prefix="/expense")

expense_repository = ExpenseRepository()
expense_item_repository = ExpenseItemRepository()
device_repository = DeviceRepository()
group_repository = GroupRepository()
user_repository = UserRepository()


@expense_blueprint.route("/group/<int:group_id>", methods=["GET"])
@token_required
def list(current_user, group_id):
    group = group_repository.get_or_404(current_user, group_id)

    expense_list = expense_repository.list(group)

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

    utils.validate_params(json_data, ["name", "value"])
    data = utils.parse_params(json_data, ["name", "value", "description", "items"])

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

    data = utils.parse_params(json_data, ["name", "value", "description", "items"])
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

    expense = expense_repository.get_or_404(current_user, id)

    delete_items(expense)
    expense_repository.delete(current_user, id)

    return jsonify({"success": True})


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
            data["user_id"] = user
            expense_item_repository.save(data)

    users_id = [user.id for user in users]

    for item in expense.items:
        if not item.user_id in users_id:
            expense_item_repository.delete(item.id)


def delete_items(expense):
    for item in expense.items:
        expense_item_repository.delete(item.id)


def notify(triggered_user, group, expense):
    users_to_notify = [item.user for item in expense.items]
    users_to_notify.remove(triggered_user)

    title = group.name
    body = f"{triggered_user.full_name} criou uma nova despesa: {expense.name}"

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
