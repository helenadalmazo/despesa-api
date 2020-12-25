from flask import Blueprint, jsonify, request

from auth.decorator import token_required
from database.repository import ExpenseRepository, ExpenseItemRepository, GroupRepository, UserRepository
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


@expense_blueprint.route("/<int:id>", methods=["GET"])
@token_required
def get(current_user, id):
    expense = expense_repository.get_or_404(current_user, id)

    return jsonify(expense.json())


@expense_blueprint.route("/", methods=["POST"])
@token_required
def save(current_user):
    json_data = request.get_json()

    utils.validate_params(json_data, ["name", "value"])
    data = utils.parse_params(json_data, ["name", "value", "group_id"])

    expense = expense_repository.save(current_user, data)
    save_items(expense)

    return jsonify(expense.json())


@expense_blueprint.route("/<int:id>", methods=["PUT"])
@token_required
def update(current_user, id):
    expense = expense_repository.get_or_404(current_user, id)

    json_data = request.get_json()

    params = ["name", "value"]

    utils.validate_params(json_data, params)
    data = utils.parse_params(json_data, params)

    expense = expense_repository.update(current_user, id, data)
    update_items(expense)

    return jsonify(expense.json())


@expense_blueprint.route("/<int:id>", methods=["DELETE"])
@token_required
def delete(current_user, id):
    expense = expense_repository.get_or_404(current_user, id)

    expense_repository.delete(current_user, id)

    return jsonify({ "success": True })


def save_items(expense):
    user = user_repository.get(expense.created_by)
    group = group_repository.get(user, expense.group_id)

    splitted_value = expense.value / len(group.users)

    data = {
        "expense_id": expense.id,
        "value": splitted_value
    }

    for user in group.users:
        data["user_id"] = user.id
        expense_item_repository.save(data)


def update_items(expense):
    user = user_repository.get(expense.created_by)
    group = group_repository.get(user, expense.group_id)

    splitted_value = expense.value / len(group.users)

    data = {
        "value": splitted_value
    }

    for user in group.users:
        expense_item = expense_item_repository.get_by_user(user)
        
        if expense_item:
            expense_item_repository.update(expense_item.id, data)
        else:
            data["expense_id"] = expense.id
            expense_item_repository.save(data)

    for item in expense.items:
        if not item.user_id in group.users:
            expense_item_repository.delete(item.id)
