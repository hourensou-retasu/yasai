import io
import requests
import numpy as np
import cv2
from PIL import Image
import face_recognition
from keras.preprocessing.image import img_to_array
from keras.models import load_model
from freeeAPI import freeeAPI


class FaceEmotionRecognizer:

    def __init__(self, db):
        self.video = cv2.VideoCapture(0)
        self.company_id = freeeAPI().getCompanyID()
        self.db = db
        self.known_face_names, self.known_face_features = self.fetch_known_faces()
        self.emoclf = self._init_emoclf()

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

            detected = False
            detected_name = None
            for i, name in enumerate(face_names):
                if name != 'Unknown':
                    detected = True
                    detected_name = name.copy()
                    emotion = self.recognize_emotion(small_frame, face_locations[i])
                    detected_name['emotion'] = emotion
                    break

            if detected:
                break

            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

        if detected:
            return detected_name
        else:
            return None

    def recognize_emotion(self, frame, location):
        top, right, bottom, left = location
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        roi = gray[top:bottom, left:right]
        roi = cv2.resize(roi, (64, 64))
        roi = roi.astype("float") / 255.0
        roi = img_to_array(roi)
        roi = np.expand_dims(roi, axis=0)
        preds = self.emoclf.predict(roi)[0]
        if preds.argmax() in [3, 5]:
            emotion = 1
        else:
            emotion = -1
        return emotion

    def quit(self):
        self.video.release()
        cv2.destroyAllWindows()

    def fetch_known_faces(self):
        users_ref = self.db.collection(str(self.company_id))
        records = [doc.to_dict() for doc in users_ref.get()]
        face_imgs = [self.load_img_from_url(record['img_url']) for record in records]
        face_features = [face_recognition.face_encodings(img)[0] for img in face_imgs]
        return records, face_features

    @staticmethod
    def _init_emoclf():
        model_path = 'models/mini_XCEPTION.hdf5'
        clf = load_model(model_path, compile=False)
        return clf

    @staticmethod
    def load_img_from_url(url):
        im = Image.open(io.BytesIO(requests.get(url).content)).convert('RGB')
        return np.array(im)
