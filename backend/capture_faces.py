import cv2
import os
import sys


def capture_images(name, emp_id):
    # ✅ ALWAYS USE name_empid FORMAT
    folder_name = f"{name.lower()}_{emp_id}"
    save_path = os.path.join("dataset", folder_name)

    os.makedirs(save_path, exist_ok=True)

    cap = cv2.VideoCapture(0)

    if not cap.isOpened():
        print("❌ Cannot open camera")
        return

    print(f"✅ Capturing for {name} ({emp_id})")
    print("👉 Press SPACE to capture | ESC to exit")

    count = 0

    while True:
        ret, frame = cap.read()
        if not ret:
            print("❌ Failed to grab frame")
            break

        # ✅ Show camera safely
        cv2.namedWindow("Camera", cv2.WINDOW_NORMAL)
        cv2.imshow("Camera", frame)

        key = cv2.waitKey(1)

        if key == 32:  # SPACE
            img_name = os.path.join(save_path, f"{count}.jpg")
            cv2.imwrite(img_name, frame)
            print(f"📸 Saved {img_name}")
            count += 1

        elif key == 27:  # ESC
            break

    cap.release()
    cv2.destroyAllWindows()


if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("❌ Usage: python capture_faces.py <name> <emp_id>")
        sys.exit(1)

    name = sys.argv[1]
    emp_id = sys.argv[2]

    capture_images(name, emp_id)