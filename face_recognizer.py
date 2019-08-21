import io
import requests
import numpy as np
import cv2
from PIL import Image
import face_recognition
from firestoreAPI import FireStore

class FaceRecognizer:

    def __init__(self):
        self.video = cv2.VideoCapture(0)
        self.db = FireStore().db
        self.known_face_names, self.known_face_features = self.fetch_known_faces()

    def authorize(self, num_trial=100, tolerance=0.5):
        detected = False
        for n in range(num_trial):
            ret, frame = self.video.read()
            small_frame = cv2.resize(frame, (0, 0), fx=0.25, fy=0.25)
            rgb_small_frame = small_frame[:, :, ::-1]

            face_locations = face_recognition.face_locations(rgb_small_frame)
            face_features = face_recognition.face_encodings(rgb_small_frame, face_locations)
            face_names = []

            for feature in face_features:
                matches = face_recognition.compare_faces(self.known_face_features, feature, tolerance=tolerance)
                name = "Unknown"

                distances = face_recognition.face_distance(self.known_face_features, feature)
                best_match_index = np.argmin(distances)
                if matches[best_match_index]:
                    name = self.known_face_names[best_match_index]

                face_names.append(name)

            flag = False
            detected_name = None
            for name in face_names:
                if name != 'Unknown':
                    flag = True
                    detected_name = name

            if flag:
                detected = True
                break

            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

        if detected:
            return detected_name
        else:
            return None

    def quit(self):
        self.video.release()
        cv2.destroyAllWindows()

    def fetch_known_faces(self):
        users_ref = self.db.collection('users')
        records = [doc.to_dict() for doc in users_ref.get()]
        face_imgs = [self.load_img_from_url(record['img_url']) for record in records]
        face_features = [face_recognition.face_encodings(img)[0] for img in face_imgs]
        return records, face_features

    @staticmethod
    def load_img_from_url(url):
        im = Image.open(io.BytesIO(requests.get(url).content)).convert('RGB')
        return np.array(im)
