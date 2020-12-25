from flask import Blueprint, current_app, jsonify

app_blueprint = Blueprint("app", __name__, url_prefix="/")


@app_blueprint.route("/", methods=["GET"])
def index():
    return jsonify(get_routes_available())


def get_routes_available():
    rule_list = []

    for rule in current_app.url_map.iter_rules():
        path = str(rule)

        if path == "/static/<path:filename>":
            continue

        rule_list.append({
            "methods": [method for method in rule.methods if method not in ["OPTIONS", "HEAD"]],
            "path": path
        })

    return rule_list
