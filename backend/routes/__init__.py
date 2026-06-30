from flask import request, jsonify
from services.auth_service import login_user


def register_routes(app):

    @app.route("/")
    def home():
        return {"message": "DVR Face Recognition Backend Running"}

    # LOGIN API
    @app.route("/login", methods=["POST"])
    def login():
        data = request.get_json()

        username = data.get("username")
        password = data.get("password")

        if not username or not password:
            return jsonify({
                "status": False,
                "message": "Username and password required"
            }), 400

        result = login_user(username, password)
        return jsonify(result)