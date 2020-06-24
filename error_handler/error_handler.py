from flask import jsonify

def handle_not_found_exception(exception):
    return jsonify({"message": exception.message}), exception.status_code

def handle_validation_exception(exception):
    return jsonify({"message": exception.message, "errors": exception.errors}), exception.status_code
