import os
import cv2
import face_recognition
import pickle

# PATH SETUP 
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATASET_PATH = os.path.join(BASE_DIR, "dataset")
ENCODINGS_DIR = os.path.join(BASE_DIR, "encodings")
ENCODINGS_PATH = os.path.join(ENCODINGS_DIR, "faces.pkl")

known_encodings = []
known_names = []

print("🔄 Training started...\n")

# CHECK DATASET 
if not os.path.exists(DATASET_PATH):
    print("Dataset folder not found!")
    exit()

#  LOOP DATASET 
for folder_name in os.listdir(DATASET_PATH):
    folder_path = os.path.join(DATASET_PATH, folder_name)

    if not os.path.isdir(folder_path):
        continue

    if "_" not in folder_name:
        print(f"⚠️ Skipping invalid folder: {folder_name}")
        continue

    print(f"📁 Processing: {folder_name}")

    for image_name in os.listdir(folder_path):
        image_path = os.path.join(folder_path, image_name)

        try:
            image = cv2.imread(image_path)

            if image is None:
                print(f"⚠️ Cannot read: {image_path}")
                continue

            rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

            face_locations = face_recognition.face_locations(rgb)

            if len(face_locations) == 0:
                print(f"⚠️ No face found: {image_name}")
                continue

            encodings = face_recognition.face_encodings(rgb, face_locations)

            for encoding in encodings:
                known_encodings.append(encoding)
                known_names.append(folder_name) 

            print(f"   ✔ {image_name}")

        except Exception as e:
            print(f"Error: {image_name} → {e}")

# SAVE MODEL 
os.makedirs(ENCODINGS_DIR, exist_ok=True)

data = {
    "encodings": known_encodings,
    "names": known_names
}

with open(ENCODINGS_PATH, "wb") as f:
    pickle.dump(data, f)

print("\n✅ Training completed successfully!")
print(f"📦 Saved at: {ENCODINGS_PATH}")