from flask import Blueprint, jsonify

from auth.decorator import token_required
from database.repository import ExpenseRepository, GroupRepository, UserRepository

statistic_blueprint = Blueprint("statistic", __name__, url_prefix="/statistic")

expense_repository = ExpenseRepository()
group_repository = GroupRepository()
user_repository = UserRepository()


@statistic_blueprint.route("/valuegroupedbyuser/group/<int:group_id>", methods=["GET"])
@token_required
def list_value_grouped_by_user(current_user, group_id):
    group = group_repository.get_or_404(current_user, group_id)

    statistic_list = expense_repository.list_value_grouped_by_user(group)

    return jsonify([{"user": user_repository.get(item.user_id).json(), "value": item.value} for item in statistic_list])


@statistic_blueprint.route("/valuegroupedbyyearmonth/group/<int:group_id>", methods=["GET"])
@token_required
def list_value_grouped_by_year_month(current_user, group_id):
    group = group_repository.get_or_404(current_user, group_id)

    statistic_list = expense_repository.list_value_grouped_by_year_month(group)

    return jsonify([{"date": item.date, "value": item.value} for item in statistic_list])
