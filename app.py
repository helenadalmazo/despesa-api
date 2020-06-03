from flask import Flask, jsonify

app = Flask(__name__)

@app.route("/", methods=["GET"])
def index():
    return jsonify(get_routes_available())

def get_routes_available():
    rule_list = []

    for rule in app.url_map.iter_rules():
        path = str(rule)

        if path == "/static/<path:filename>":
            continue

        rule_list.append({
            "methods": [method for method in rule.methods if method not in ["OPTIONS", "HEAD"]],
            "path": path
        })

    return rule_list

if __name__ == "__main__":
    app.run(debug=True)
