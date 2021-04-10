from flask import jsonify


def handle_business_exception(exception):
    return jsonify({"message": exception.message}), exception.status_code


def handle_forbidden_exception(exception):
    return jsonify({"message": exception.message}), exception.status_code


def handle_not_found_exception(exception):
    return jsonify({"message": exception.message}), exception.status_code


def handle_validation_exception(exception):
    return jsonify({"message": exception.message, "errors": exception.errors}), exception.status_code


def handle_http_exception(exception):
    return jsonify({"message": exception.description}), exception.code


def handle_exception(exception):
    print(exception)
    return jsonify({"message": "Ocorreu um erro interno no servidor"}), 500
