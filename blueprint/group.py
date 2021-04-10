from flask import Blueprint, jsonify, request

from auth.decorator import token_required
from database.model import GroupUserRole
from database.repository import GroupUserRepository, GroupRepository, UserRepository
from exception.exception import BusinessException
from transactional.decorator import transactional
from utils import utils

group_blueprint = Blueprint("group", __name__, url_prefix="/group")

group_user_repository = GroupUserRepository()
group_repository = GroupRepository()
user_repository = UserRepository()


@group_blueprint.route("", methods=["GET"])
@token_required
def index(current_user):
    group_list = group_repository.list(current_user)

    return jsonify([group.json() for group in group_list])


@group_blueprint.route("/<int:id>", methods=["GET"])
@token_required
def get(current_user, id):
    group = group_repository.get_or_404(current_user, id)

    return jsonify(group.json())


@group_blueprint.route("", methods=["POST"])
@token_required
@transactional
def save(current_user):
    json_data = request.get_json()

    utils.validate_params(json_data, ["name"])
    data = utils.parse_params(json_data, ["name"])

    group = group_repository.save(data)

    data_group_user = {
        "group_id": group.id,
        "user_id": current_user.id,
        "role": GroupUserRole.OWNER.name
    }
    group_user_repository.save(data_group_user)

    return jsonify(group.json())


@group_blueprint.route("/<int:id>", methods=["PUT"])
@token_required
def update(current_user, id):
    group = group_repository.get_or_404(current_user, id)

    utils.check_permission(current_user, group, [GroupUserRole.OWNER, GroupUserRole.ADMIN])

    json_data = request.get_json()

    utils.validate_params(json_data, ["name"])
    data = utils.parse_params(json_data, ["name"])

    group = group_repository.update(current_user, id, data)

    return jsonify(group.json())


@group_blueprint.route("/<int:id>", methods=["DELETE"])
@token_required
def delete(current_user, id):
    group = group_repository.get_or_404(current_user, id)

    utils.check_permission(current_user, group, [GroupUserRole.OWNER])

    for group_user in group.users:
        group_user_repository.delete(group, group_user.user)

    group_repository.delete(id)

    return jsonify({"success": True})


@group_blueprint.route("/<int:id>/searchnewuser", methods=["GET"])
@token_required
def search_new_user(current_user, id):
    group = group_repository.get_or_404(current_user, id)

    users_not_in_list = [user_repository.get(group_user.user_id) for group_user in group.users]

    full_name = request.args.get("fullname")

    user_list = user_repository.list_not_in_by_full_name(users_not_in_list, full_name)

    return jsonify([user.json() for user in user_list])


@group_blueprint.route("/<int:id>/adduser/<int:user_id>", methods=["POST"])
@token_required
def add_user(current_user, id, user_id):
    group = group_repository.get_or_404(current_user, id)
    user = user_repository.get_or_404(user_id)

    group_users = [user_repository.get(group_user.user_id) for group_user in group.users]
    if user in group_users:
        raise BusinessException("O usuário já encontra-se no grupo.")

    json_data = request.get_json()

    utils.validate_params(json_data, ["role"])
    data = utils.parse_params(json_data, ["role"])

    group_user_role = GroupUserRole(data["role"])

    if group_user_role == GroupUserRole.USER:
        utils.check_permission(current_user, group, [GroupUserRole.OWNER, GroupUserRole.ADMIN])

    if group_user_role == GroupUserRole.ADMIN:
        utils.check_permission(current_user, group, [GroupUserRole.OWNER])

    if group_user_role == GroupUserRole.OWNER:
        raise BusinessException("O grupo só pode ter um dono.")

    data["group_id"] = group.id
    data["user_id"] = user.id

    group_user_repository.save(data)

    return jsonify(group.json())


@group_blueprint.route("/<int:id>/updateuser/<int:user_id>", methods=["PUT"])
@token_required
def update_user(current_user, id, user_id):
    group = group_repository.get_or_404(current_user, id)
    user = user_repository.get_or_404(user_id)

    before_group_user_role = group.get_user_role(user)

    if current_user == user and before_group_user_role == GroupUserRole.OWNER:
        raise BusinessException("Você é o dono e não pode ser alterado.")

    json_data = request.get_json()

    utils.validate_params(json_data, ["role"])
    data = utils.parse_params(json_data, ["role"])

    group_user_role = GroupUserRole(data["role"])

    if group_user_role in [GroupUserRole.USER, GroupUserRole.ADMIN]:
        utils.check_permission(current_user, group, [GroupUserRole.OWNER])

    if group_user_role == GroupUserRole.OWNER:
        raise BusinessException("O grupo só pode ter um dono.")

    data["group_id"] = group.id
    data["user_id"] = user.id

    group_user_repository.update(group, user, data)

    return jsonify(group.json())


@group_blueprint.route("/<int:id>/removeuser/<int:user_id>", methods=["DELETE"])
@token_required
def remove_user(current_user, id, user_id):
    group = group_repository.get_or_404(current_user, id)
    user = user_repository.get_or_404(user_id)

    group_user_role = group.get_user_role(user)

    if current_user == user and group_user_role == GroupUserRole.OWNER:
        raise BusinessException("Você é o dono e não pode ser removido.")

    if group_user_role == GroupUserRole.USER:
        utils.check_permission(current_user, group, [GroupUserRole.OWNER, GroupUserRole.ADMIN])

    if group_user_role == GroupUserRole.ADMIN:
        utils.check_permission(current_user, group, [GroupUserRole.OWNER])

    if group_user_role == GroupUserRole.OWNER:
        raise BusinessException("O grupo só pode ter um dono.")

    group_user_repository.delete(group, user)

    return jsonify(group.json())
