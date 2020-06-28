import datetime
from flask import current_app, Blueprint, jsonify, request
import jwt
from werkzeug.security import generate_password_hash, check_password_hash

from auth.decorator import token_required
from database.repository import UserRepository
from exception.exception import NotFoundException
from utils import utils

auth_blueprint = Blueprint("auth", __name__, url_prefix="/auth")

user_repository = UserRepository()

TOKEN_LIFETIME = 60 * 60 * 24

@auth_blueprint.route("/signup/", methods=["POST"])
def signup():
    json_data = request.get_json()

    params = ["username", "password"]

    utils.validate_params(json_data, params)
    data = utils.parse_params(json_data, params)
    
    data["password"] = generate_password_hash(data.get("password"))

    user = user_repository.save(data)

    return jsonify(user.json())


@auth_blueprint.route("/token/", methods=["POST"])
def login():
    json_data = request.get_json()

    params = ["username", "password"]

    utils.validate_params(json_data, params)

    username = json_data.get("username")
    password = json_data.get("password")

    user = user_repository.get_by_username(username)

    if not user:
        raise NotFoundException(f"Não foi encontrado usuário com login [{username}].")

    if not check_password_hash(user.password, password):
        return jsonify({"message": "Suas credenciais estão incorretas."}), 403

    payload = {
        "username": user.username,
        "exp": datetime.datetime.utcnow() + datetime.timedelta(seconds=TOKEN_LIFETIME)
    }

    token = jwt.encode(payload, current_app.config.get("SECRET_KEY"))

    return jsonify({"token": token.decode("utf-8"), "expires_in": TOKEN_LIFETIME})


@auth_blueprint.route("/me/", methods=["GET"])
@token_required
def me(current_user):
    print(f"current_user {current_user}")

    return jsonify(current_user.json())