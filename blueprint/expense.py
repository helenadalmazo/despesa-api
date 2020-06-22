from flask import Blueprint, jsonify, request

from database.model import Expense
from database.repository import ExpenseRepository
from exception.exception import NotFoundException, ValidationException

expense_blueprint = Blueprint("expense", __name__, url_prefix="/expense")

expense_repository = ExpenseRepository()

@expense_blueprint.route("/", methods=["GET"])
def list():
    expense_list = expense_repository.list()
    return jsonify([expense.json() for expense in expense_list])


@expense_blueprint.route("/<int:id>", methods=["GET"])
def get(id):
    expense = expense_repository.get(id)

    if expense is None: 
        raise NotFoundException(f"Não foi encontrada despesa com identificador [{id}].")

    return jsonify(expense.json())


@expense_blueprint.route("/", methods=["POST"])
def save():
    json_data = request.get_json()

    params = ["name", "value"]

    validate_params(json_data, params)
    data = parse_params(json_data, params)

    expense = expense_repository.save(data)
    return jsonify(expense.json())


@expense_blueprint.route("/<int:id>", methods=["PUT"])
def update(id):
    json_data = request.get_json()

    params = ["name", "value"]

    validate_params(json_data, params)
    data = parse_params(json_data, params)

    expense = expense_repository.update(id, data)
    return jsonify(expense.json())


@expense_blueprint.route("/<int:id>", methods=["DELETE"])
def delete(id):
    expense = expense_repository.get(id)

    if expense is None: 
        raise NotFoundException(f"Não foi encontrada despesa com identificador [{id}].")

    expense_repository.delete(id)

    return jsonify(expense.json())


def validate_params(params_received, params_to_validate):
    errors = []

    for param in params_to_validate:
        if param not in params_received:
            errors.append(f"O parâmetro [{param}] é obrigatório.")

    if len(errors) > 0:
        raise ValidationException("Não foi possível processar essa requisição.", errors)


def parse_params(params_received, params_to_parse):
    data = {}

    for param in params_to_parse:
        data[param] = params_received[param]

    return data


@expense_blueprint.errorhandler(NotFoundException)
def handle_not_found_exception(exception):
    return jsonify({"message": exception.message}), exception.status_code


@expense_blueprint.errorhandler(ValidationException)
def handle_validation_exception(exception):
    return jsonify({"message": exception.message, "errors": exception.errors}), exception.status_code
