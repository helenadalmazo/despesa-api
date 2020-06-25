from flask import Blueprint, jsonify, request

from auth.decorator import token_required
from database.repository import ExpenseRepository
from utils import utils

expense_blueprint = Blueprint("expense", __name__, url_prefix="/expense")

expense_repository = ExpenseRepository()

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

    params = ["name", "value"]

    utils.validate_params(json_data, params)
    data = utils.parse_params(json_data, params)

    expense = expense_repository.save(current_user, data)
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
    return jsonify(expense.json())


@expense_blueprint.route("/<int:id>", methods=["DELETE"])
@token_required
def delete(current_user, id):
    expense = expense_repository.get_or_404(current_user, id)

    expense_repository.delete(current_user, id)

    return jsonify(expense.json())
