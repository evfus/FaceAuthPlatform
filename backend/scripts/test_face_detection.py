import sys
from pathlib import Path
import cv2

sys.path.append(str(Path(__file__).resolve().parent.parent))

from app.services.face_detection import FaceDetector

def main():
    if len(sys.argv) != 2:
        print("Usage: python3 script.py <path_to_image>")
        sys.exit(1)

    image_path = sys.argv[1]
    image = cv2.imread(image_path)

    detector = FaceDetector()
    faces = detector.detect(image)

    print(f"Found {len(faces)} face(s)")

    for face in faces:
        print(face)
        cv2.rectangle(
            image,
            (face.x, face.y),
            (face.width + face.x, face.height + face.y),
            (0, 255, 0),
            2
        )

    output_path = "detection_result.jpg"
    cv2.imwrite(output_path, image)

    print(f"Saved result image to {output_path}")

if __name__ == "__main__":
    main()
