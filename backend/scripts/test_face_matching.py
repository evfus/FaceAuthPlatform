from pathlib import Path
import sys
import cv2

sys.path.append(str(Path(__file__).resolve().parent.parent))

from app.core.database import SessionLocal
from app.models.user import User
from app.services.face_detection import FaceDetector
from app.services.face_embedding import FaceEmbedder
from app.services.face_matching import match_face_to_user

TEST_EMAIL = "testing6@gmail.com"
TEST_IMAGE_PATH = "/home/mefiu/face_auth_faces/guy_4.png"


def main():
    db = SessionLocal()
    detector = FaceDetector()
    embedder = FaceEmbedder()

    user = db.query(User).filter(User.email == TEST_EMAIL).first()
    if not user:
        print(f"No user found with email {TEST_EMAIL}")
        return

    frame = cv2.imread(TEST_IMAGE_PATH)
    if frame is None:
        print(f"Could not load image at {TEST_IMAGE_PATH}")
        return

    result = match_face_to_user(frame, user, db, detector, embedder)
    print(f"matched={result.matched}")
    print(f"confidence={result.confidence}")
    print(f"reason={result.reason}")

    db.close() 

if __name__ == "__main__":
    main()
