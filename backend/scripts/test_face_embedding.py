import cv2
import numpy as np
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parent.parent))

from app.services.face_detection import FaceDetector
from app.services.face_embedding import FaceEmbedder

def get_embedding(detector, embedder, image_path):
    image = cv2.imread(image_path)
    
    if image is None:
        print("Could not load image")
        sys.exit(1)

    faces = detector.detect(image)

    if not faces:
        print("No faces detected in input image")
        sys.exit(1)

    face = max(faces, key = lambda f: f.confidence)

    return embedder.embed(image, face)

def cosine_similarity(a, b):
    return (np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b)))

def main():
    if len(sys.argv) != 3:
        print("Usage: python3 script.py <path_to_image1> <path_to_image2>")
        sys.exit(1)

    detector = FaceDetector()
    embedder = FaceEmbedder()

    emb1 = get_embedding(detector, embedder, sys.argv[1])
    emb2 = get_embedding(detector, embedder, sys.argv[2])

    similarity = cosine_similarity(emb1, emb2)

    print(f"Cosine similarity: {similarity:.4f}")

if __name__ == "__main__":
    main()
