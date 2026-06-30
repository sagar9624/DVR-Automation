from flask import request, jsonify

# 🎯 Register routes
def register_camera_routes(app):

    @app.route("/capture", methods=["POST"])
    def capture():
        try:
            data = request.get_json()

            name = data.get("name")
            emp_id = data.get("emp_id")

            # 🔒 Validation
            if not name or not emp_id:
                return jsonify({
                    "status": "error",
                    "message": "Name and Employee ID required"
                }), 400

  
            print(f"Frontend camera started for {name} ({emp_id})")

            return jsonify({
                "status": "success",
                "message": f"Camera ready for {name}"
            })

        except Exception as e:
            print("API Error:", e)
            return jsonify({
                "status": "error",
                "message": "Failed to initialize camera"
            }), 500


    @app.route("/stop-camera", methods=["POST"])
    def stop_camera():
        try:
            print("Camera stopped from frontend")

            return jsonify({
                "status": "success",
                "message": "Camera stopped"
            })

        except Exception as e:
            print("❌ Stop Error:", e)
            return jsonify({
                "status": "error",
                "message": "Failed to stop camera"
            }), 500