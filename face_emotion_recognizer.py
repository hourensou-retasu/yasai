import io
import requests
import numpy as np
import cv2
from PIL import Image, ImageFont, ImageDraw
import face_recognition
from keras.preprocessing.image import img_to_array
from keras.models import load_model
import tensorflow as tf
from freeeAPI import freeeAPI


graph = tf.get_default_graph()


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
                    emotion = self.recognize_posneg(small_frame, face_locations[i])
                    print(emotion)
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

    def demonstrate(self, tolerance):

        while True:
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

            for i, name in enumerate(face_names):
                emotion = self.recognize_emotion(small_frame, face_locations[i])
                frame = self.display(frame, face_locations[i], name, emotion)

            cv2.imshow('Demo', frame)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

    def recognize_emotion(self, frame, location):
        emotions = ['angry', 'disgust', 'scared', 'happy', 'sad', 'surprised', 'neutral']
        top, right, bottom, left = location
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        roi = gray[top:bottom, left:right]
        roi = cv2.resize(roi, (64, 64))
        roi = roi.astype("float") / 255.0
        roi = img_to_array(roi)
        roi = np.expand_dims(roi, axis=0)
        preds = self.emoclf.predict(roi)[0]
        label = emotions[preds.argmax()]
        return label

    def recognize_posneg(self, frame, location):
        top, right, bottom, left = location
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        roi = gray[top:bottom, left:right]
        roi = cv2.resize(roi, (64, 64))
        roi = roi.astype("float") / 255.0
        roi = img_to_array(roi)
        roi = np.expand_dims(roi, axis=0)
        global graph
        with graph.as_default():
            preds = self.emoclf.predict(roi)[0]
        if preds.argmax() in [3, 5]:
            emotion = 1
        else:
            emotion = -1
        return emotion

    def display(self, frame, location, name, emotion):
        if name != 'Unknown':
            name = name['last_name_kanji'] + ' ' + name['first_name_kanji']
        top, right, bottom, left = location
        top *= 4
        right *= 4
        bottom *= 4
        left *= 4
        cv2.rectangle(frame, (left, top), (right, bottom), (0, 0, 255), 2)
        cv2.rectangle(frame, (left, bottom - 35), (right, bottom), (0, 0, 255), cv2.FILLED)
        font_path = '/Users/ono-yu/Library/Fonts/rounded-mplus-1m-medium.ttf'
        info = name + ': {}'.format(emotion)
        frame = self.put_text(frame, info, (left + 6, bottom - 30), font_path, 26, (255, 255, 255))
        return frame

    def quit(self):
        self.video.release()
        cv2.destroyAllWindows()

    def fetch_known_faces(self):
        users_ref = self.db.collection(str(self.company_id))
        records = [doc.to_dict() for doc in users_ref.get()]
        face_imgs = [self.load_img_from_url(record['img_url']) for record in records]
        face_features = [face_recognition.face_encodings(img)[0] for img in face_imgs]
        return records, face_features

    def _init_emoclf(self):
        global graph
        model_path = 'models/mini_XCEPTION.hdf5'
        with graph.as_default():
            clf = load_model(model_path, compile=False)
        return clf

    @staticmethod
    def load_img_from_url(url):
        im = Image.open(io.BytesIO(requests.get(url).content)).convert('RGB')
        return np.array(im)

    @staticmethod
    def put_text(cv_image, text, point, font_path, font_size, color):
        font = ImageFont.truetype(font_path, font_size)
        cv_rgb_image = cv2.cvtColor(cv_image, cv2.COLOR_BGR2RGB)
        pil_image = Image.fromarray(cv_rgb_image)
        draw = ImageDraw.Draw(pil_image)
        draw.text(point, text, fill=color, font=font)
        cv_rgb_result_image = np.asarray(pil_image)
        cv_bgr_result_image = cv2.cvtColor(cv_rgb_result_image, cv2.COLOR_RGB2BGR)

        return cv_bgr_result_image

