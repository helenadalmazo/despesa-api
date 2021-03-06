from flask import current_app, request, jsonify
from functools import wraps
import jwt

from database.repository import UserRepository

user_repository = UserRepository()


def token_required(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        token = request.headers.get("Authorization")

        if not token:
            return jsonify({"message": "Token não informado."}), 401

        if not "Bearer " in token:
            return jsonify({"message": "Bearer token mal formatado."}), 401
        
        token = token.replace("Bearer ", "")

        try:
            token_decoded = jwt.decode(token, current_app.config.get("SECRET_KEY"))

            current_user = user_repository.get_by_username(token_decoded.get("username"))
        except jwt.ExpiredSignatureError as ese:
            return jsonify({"message": "Token expirado."}), 401
        except Exception as e:
            return jsonify({"message": "Token inválido."}), 401

        return func(current_user=current_user, *args, **kwargs)
    return wrapper
