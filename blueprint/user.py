# from flask import Blueprint, jsonify, request
#
# from auth.decorator import token_required
# from database.repository import UserRepository
#
# user_blueprint = Blueprint("user", __name__, url_prefix="/user")
#
# user_repository = UserRepository()
#
#
# @user_blueprint.route("", methods=["GET"])
# @token_required
# def index(current_user):
#     user_list = user_repository.list()
#
#     return jsonify([user.json() for user in user_list])
#
#
# @group_blueprint.route("/<int:id>", methods=["PUT"])
# @token_required
# def update(current_user, id):
#     group = group_repository.get_or_404(current_user, id)
#
#     utils.check_permission(current_user, group, [GroupUserRole.OWNER, GroupUserRole.ADMIN])
#
#     json_data = request.get_json()
#
#     utils.validate_params(json_data, ["name"])
#     data = utils.parse_params(json_data, ["name"])
#
#     group = group_repository.update(current_user, id, data)
#
#     return jsonify(group.json())
#
