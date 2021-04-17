from datetime import datetime

from flask import Blueprint, jsonify, request

from auth.decorator import token_required
from database.repository import ExpenseCategoryRepository, ExpenseRepository, GroupRepository, UserRepository

statistic_blueprint = Blueprint("statistic", __name__, url_prefix="/statistic")

expense_category_repository = ExpenseCategoryRepository()
expense_repository = ExpenseRepository()
group_repository = GroupRepository()
user_repository = UserRepository()


@statistic_blueprint.route("/valuegroupedbyuser/group/<int:group_id>", methods=["GET"])
@token_required
def list_value_grouped_by_user(current_user, group_id):
    group = group_repository.get_or_404(current_user, group_id)

    today = datetime.now()
    month = request.args.get("month", today.month)
    year = request.args.get("year", today.year)

    statistic_list = expense_repository.list_value_grouped_by_user(group, year, month)

    return jsonify([{"user": user_repository.get(item.user_id).json(), "value": item.value} for item in statistic_list])


@statistic_blueprint.route("/valuegroupedbycategory/group/<int:group_id>", methods=["GET"])
@token_required
def list_value_grouped_by_category(current_user, group_id):
    group = group_repository.get_or_404(current_user, group_id)

    today = datetime.now()
    month = request.args.get("month", today.month)
    year = request.args.get("year", today.year)

    statistic_list = expense_repository.list_value_grouped_by_category(group, year, month)

    return jsonify([{"group": item.group, "value": item.value} for item in statistic_list])


@statistic_blueprint.route("/valuegroupedbyyearmonth/group/<int:group_id>", methods=["GET"])
@token_required
def list_value_grouped_by_year_month(current_user, group_id):
    group = group_repository.get_or_404(current_user, group_id)

    statistic_list = expense_repository.list_value_grouped_by_year_month(group)

    return jsonify([{"date": item.date, "value": item.value} for item in statistic_list])
