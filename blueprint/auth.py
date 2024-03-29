import datetime
from flask import current_app, Blueprint, jsonify, request
import jwt
from werkzeug.security import generate_password_hash, check_password_hash

from auth.decorator import token_required
from database.repository import UserRepository, DeviceRepository
from exception.exception import NotFoundException
from utils import utils

auth_blueprint = Blueprint("auth", __name__, url_prefix="/auth")

user_repository = UserRepository()
device_repository = DeviceRepository()

TOKEN_LIFETIME = 60 * 60 * 24


@auth_blueprint.route("/signup", methods=["POST"])
def signup():
    json_data = request.get_json()

    params = ["full_name", "username", "password", "confirm_password"]

    utils.validate_params(json_data, params)
    data = utils.parse_params(json_data, params)

    existing_user = user_repository.get_by_username(data["username"])

    # sqlalchemy.exc.IntegrityError
    if existing_user:
        return jsonify({"message": f"Usuário {data['username']} não está disponível."}), 409

    if data["password"] != data["confirm_password"]:
        return jsonify({"message": "As senhas não coincidem."}), 409
    
    data["password"] = generate_password_hash(data.get("password"))

    del data["confirm_password"]
    user = user_repository.save(data)

    return jsonify(user.json())


@auth_blueprint.route("/token", methods=["POST"])
def token():
    json_data = request.get_json()

    utils.validate_params(json_data, ["username", "password", "device"])
    utils.validate_params(json_data, ["token"], "device")

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

    device_token = json_data.get("device").get("token")
    save_device(user, device_token)

    return jsonify({"token": token.decode("utf-8"), "expires_in": TOKEN_LIFETIME})


@auth_blueprint.route("/me", methods=["GET"])
@token_required
def me(current_user):
    return jsonify(current_user.json())


def save_device(user, token):
    existing_device = device_repository.get_by_user(user)

    if not existing_device:
        data_device = {
            "user_id": user.id,
            "token": token
        }
        device_repository.save(data_device)
    elif existing_device.token != token:
        data_device = {
            "token": token
        }
        device_repository.update(user, data_device)
