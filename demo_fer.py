from face_emotion_recognizer import FaceEmotionRecognizer
from firestoreAPI import FireStoreDB


db = FireStoreDB().db
fer = FaceEmotionRecognizer(db)

fer.demonstrate(tolerance=0.5)
