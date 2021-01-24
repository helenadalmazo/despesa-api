from flask import Blueprint, jsonify, request

from auth.decorator import token_required
from database.repository import ExpenseRepository, ExpenseItemRepository, GroupRepository, UserRepository
from exception.exception import BusinessException
from transactional.decorator import transactional
from utils import utils

expense_blueprint = Blueprint("expense", __name__, url_prefix="/expense")

expense_repository = ExpenseRepository()
expense_item_repository = ExpenseItemRepository()
group_repository = GroupRepository()
user_repository = UserRepository()


@expense_blueprint.route("/", methods=["GET"])
@token_required
def index(current_user):
    expense_list = expense_repository.list(current_user)

    return jsonify([expense.json() for expense in expense_list])


@expense_blueprint.route("/group/<int:id>", methods=["GET"])
@token_required
def list_by_group(current_user, id):
    group = group_repository.get_or_404(current_user, id)

    expense_list = expense_repository.list_by_group(group)

    return jsonify([expense.json() for expense in expense_list])


@expense_blueprint.route("/<int:id>", methods=["GET"])
@token_required
def get(current_user, id):
    expense = expense_repository.get_or_404(current_user, id)

    return jsonify(expense.json())


@expense_blueprint.route("/", methods=["POST"])
@token_required
@transactional
def save(current_user):
    json_data = request.get_json()

    utils.validate_params(json_data, ["group_id", "name", "value"])
    data = utils.parse_params(json_data, ["group_id", "name", "value", "items"])

    data_items = []

    if "items" in data:
        utils.validate_params(data, ["user_id", "value"], "items")
        data_items = data.pop("items")

        if data["value"] != sum(data_item["value"] for data_item in data_items):
            raise BusinessException("A soma dos valores dos items não equivale ao total da despesa.")

    expense = expense_repository.save(current_user, data)
    save_items(current_user, expense, data_items)

    return jsonify(expense.json())


@expense_blueprint.route("/<int:id>", methods=["PUT"])
@token_required
@transactional
def update(current_user, id):
    expense = expense_repository.get_or_404(current_user, id)

    json_data = request.get_json()

    data = utils.parse_params(json_data, ["name", "value", "items"])
    data_items = []

    if "items" in data:
        utils.validate_params(data, ["user_id", "value"], "items")
        data_items = data.pop("items")

        if data["value"] != sum(data_item["value"] for data_item in data_items):
            raise BusinessException("A soma dos valores dos não equivale ao total da despesa.")

    expense = expense_repository.update(current_user, id, data)
    update_items(current_user, expense, data_items)

    return jsonify(expense.json())


@expense_blueprint.route("/<int:id>", methods=["DELETE"])
@token_required
@transactional
def delete(current_user, id):
    expense = expense_repository.get_or_404(current_user, id)

    delete_items(expense)
    expense_repository.delete(current_user, id)

    return jsonify({ "success": True })


def save_items(current_user, expense, data_items):
    value = None
    users = []

    if data_items:
        value = data_items[0]["value"]
        users = [user_repository.get_or_404(item["user_id"]) for item in data_items]
    else:
        group = group_repository.get(current_user, expense.group_id)

        value = expense.value / len(group.users)
        users = group.users

    for user in users:
        data = {
            "expense_id": expense.id,
            "value": value,
            "user_id": user.id
        }

        expense_item_repository.save(data)


def update_items(current_user, expense, data_items):
    value = None
    users = []

    if data_items:
        value = data_items[0]["value"]
        users = [user_repository.get_or_404(item["user_id"]) for item in data_items]
    else:
        group = group_repository.get(current_user, expense.group_id)

        value = expense.value / len(group.users)
        users = group.users

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