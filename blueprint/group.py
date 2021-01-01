from flask import Blueprint, jsonify, request

from auth.decorator import token_required
from database.repository import GroupRepository, UserRepository
from utils import utils

group_blueprint = Blueprint("group", __name__, url_prefix="/group")

group_repository = GroupRepository()
user_repository = UserRepository()


@group_blueprint.route("/", methods=["GET"])
@token_required
def index(current_user):
    group_list = group_repository.list(current_user)

    return jsonify([group.json() for group in group_list])


@group_blueprint.route("/<int:id>", methods=["GET"])
@token_required
def get(current_user, id):
    group = group_repository.get_or_404(current_user, id)

    return jsonify(group.json())


@group_blueprint.route("/", methods=["POST"])
@token_required
def save(current_user):
    json_data = request.get_json()

    utils.validate_params(json_data, ["name"])
    data = utils.parse_params(json_data, ["name", "users"])

    data["users"] = parse_users(current_user, data)

    group = group_repository.save(current_user, data)

    return jsonify(group.json())


@group_blueprint.route("/<int:id>", methods=["PUT"])
@token_required
def update(current_user, id):
    group_repository.get_or_404(current_user, id)

    json_data = request.get_json()

    utils.validate_params(json_data, ["name"])
    data = utils.parse_params(json_data, ["name", "users"])

    data["users"] = parse_users(current_user, data)

    group = group_repository.update(current_user, id, data)

    return jsonify(group.json())


@group_blueprint.route("/<int:id>", methods=["DELETE"])
@token_required
def delete(current_user, id):
    group_repository.get_or_404(current_user, id)

    group_repository.delete(current_user, id)

    return jsonify({"success": True})


def parse_users(current_user, data):
    user_id_list = data.get("users", [])
    user_list = []

    if user_id_list:
        user_list.append(list(map(lambda user_id: user_repository.get(user_id), user_id_list)))

    if current_user.id not in user_id_list:
        user_list.append(current_user)

    return user_list
