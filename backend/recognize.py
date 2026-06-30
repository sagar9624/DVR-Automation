

from flask import Blueprint, request, jsonify
import face_recognition
import numpy as np
import pickle
import base64
import cv2
import os

recognize_bp = Blueprint("recognize", __name__)


ENCODING_PATH = os.path.join("encodings", "faces.pkl")

if not os.path.exists(ENCODING_PATH):
    print("faces.pkl not found. Run train_model.py first!")
    data = {"encodings": [], "names": []}
else:
    with open(ENCODING_PATH, "rb") as f:
        data = pickle.load(f)
    print("✅ Encodings loaded successfully")


@recognize_bp.route("/recognize", methods=["POST"])
def recognize_face():
    try:
        print("📸 Recognition API Hit")

        req = request.get_json()
        image_data = req.get("image")

        if not image_data:
            return jsonify({"name": "No Image Provided"})

  
        
        img_bytes = base64.b64decode(image_data.split(",")[1])
        np_arr = np.frombuffer(img_bytes, np.uint8)
        img = cv2.imdecode(np_arr, cv2.IMREAD_COLOR)

        if img is None:
            return jsonify({"name": "Invalid Image"})

        # Convert to RGB
        rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)

        face_locations = face_recognition.face_locations(rgb)
        encodings = face_recognition.face_encodings(rgb, face_locations)

        if len(encodings) == 0:
            print(" No face detected")
            return jsonify({"name": "No Face Found"})

        encoding = encodings[0]

        matches = face_recognition.compare_faces(data["encodings"], encoding)
        face_distances = face_recognition.face_distance(data["encodings"], encoding)

        detected_name = "Unknown"

        if len(face_distances) > 0:
            best_match_index = np.argmin(face_distances)

            if matches[best_match_index]:
                full_name = data["names"][best_match_index]

 

                if "_" in full_name:
                    detected_name = full_name.split("_")[0]
                else:
                    detected_name = full_name

        print(f"✅ Detected: {detected_name}")


        return jsonify({"name": detected_name})

    except Exception as e:
        
        print(" ERROR:", str(e))
        return jsonify({"name": "Error"})