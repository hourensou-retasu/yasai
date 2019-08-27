#coding:utf-8

import speech_recognition as sr
import re
from jtalk import jtalk
import face_emotion_recognizer
import time
from firestoreAPI import FireStoreDB
from jaconv import kata2hira
from freeeAPI import freeeAPI
from collections import deque
from threading import Thread

MAX_NUM = 100

class reserve_dakoku:
    def __init__(self):
        self.r = sr.Recognizer()
        self.mic = sr.Microphone()

        self.user_db = FireStoreDB().db

        self.fr = face_emotion_recognizer.FaceEmotionRecognizer(self.user_db)

        self.sound_queue = deque([])
        self.listening_speaking_flg = False
        
        self.dakoku_patterns = [
            '.*?(おはよう).*',
            '.*?(お疲れ|先|失礼|さようなら).*',
            '.*?(休憩).*?(入り|いただきます).*',
            '.*?(休憩).*?(上がり|いただきました).*'
        ]

        self.cancel_pattern = '.*?(キャンセル).*'

        self.dakoku_message_dict = {
            0: 'おはようございます',
            1: 'おつかれさまでした',
            2: 'きゅうけいいってらっしゃい',
            3: 'がんばってください'
        }

        self.dakoku_attr_str = {
            0: '出勤',
            1: '退勤',
            2: '休憩開始',
            3: '休憩終了'
        }

        self.company_id = freeeAPI().getCompanyID()

    def record(self):
        print("Recording start")

        while True:
            print('record: sound_queue_size is {}'.format(len(self.sound_queue)))

            with self.mic as source:
                self.r.adjust_for_ambient_noise(source)  # 雑音対策

                while self.listening_speaking_flg:
                    time.sleep(0.1)

                self.listening_speaking_flg = True
                audio = self.r.listen(source, phrase_time_limit=3)
                self.listening_speaking_flg = False

                self.sound_queue.append(audio)

            # 録音キューが溢れそうなとき
            if len(self.sound_queue) > MAX_NUM:
                print('record(): too big sound queue... sleep...')
                time.sleep(1)

    def recognize(self, dakoku_queue):
        print("Recognize start")

        while True:
            if len(self.sound_queue) == 0:
                continue
            
            audio = self.sound_queue.popleft()

            try:
                recog_result = self.r.recognize_google(
                    audio, language='ja-JP', show_all=True)
                print(recog_result)

                # 音声認識がうまくいってないとき
                if not isinstance(recog_result, dict) or len(recog_result.get("alternative", [])) == 0:
                    continue;

                sorted_result = sorted(recog_result['alternative'], key=lambda x: x['confidence']
                                       ) if "confidence" in recog_result["alternative"] else recog_result['alternative']
                recog_texts = [recog_elem['transcript']
                               for recog_elem in sorted_result]
                recog_text = recog_texts[0]
                print(recog_text)

                dakoku_results = [re.match(dakoku_pattern, recog_text) for dakoku_pattern in self.dakoku_patterns]
            
                # 打刻WORDにマッチ
                if any(dakoku_results):
                    user = self.fr.authorize(num_trial=20)
                    
                    # マッチした打刻種類の最初のindexを取得 0:出勤 1:退勤 2:休憩始 3:休憩終
                    dakoku_attr = None
                    for index, dakoku_result in enumerate(dakoku_results):
                        if dakoku_result is None:
                            continue
                        else:
                            dakoku_attr = index
                            break
                            
                    message = self.dakoku_message_dict[dakoku_attr] + ('、どちらさまですか' if user is None else '、' + user['last_name_kana'] + 'さん')

                    if user is not None:
                        message += '、' + mercy_message(dakoku_attr, user['emotion'])

                    self.speak(message)

                    if user is None:
                        user = self.detect_unknown_visitor()

                        # また失敗したとき
                        if user is None:
                            self.speak('登録されたユーザを認識できませんでした')
                            continue

                        message = '{}さんの{}を打刻します'.format(
                            user['last_name_kana'], self.dakoku_attr_str[dakoku_attr])
                        self.speak(message)

                    dakoku_queue.append({'employee_id':user['employee_id'], 'dakoku_attr':dakoku_attr, 'time':time.time()})

                # 削除フロー
                elif re.match(self.cancel_pattern, recog_text):
                    if len(dakoku_queue) != 0:
                        self.speak('打刻をキャンセルします')
                        dakoku_queue.pop()
                        continue
                    else:
                        continue

                # 訂正フロー
                else:
                    users_ref = self.user_db.collection(str(self.company_id))
                    users = [doc.to_dict() for doc in users_ref.get()]

                    # 前回打刻されたユーザを除き、登録ユーザ名が発話に含まれるか否か
                    if len(dakoku_queue):
                        detect_flg = False

                        for user in users:
                            if user['employee_id'] != dakoku_queue[-1]['employee_id'] and name_in_texts(user, recog_texts):
                                dakoku_queue[-1] = {'employee_id': user['employee_id'],
                                                    'dakoku_attr': dakoku_queue[-1]['dakoku_attr'],
                                                    'time': time.time()}

                                message = '{}さんの{}を打刻します'.format(
                                    user['last_name_kana'], self.dakoku_attr_str[dakoku_queue[-1]['dakoku_attr']])

                                detect_flg = True
                                self.speak(message)
                                break

                        if not detect_flg:
                            continue
                    
                    else:
                        continue


            # 以下は認識できなかったときに止まらないように。
            except sr.UnknownValueError:
                print("could not understand audio")
            except sr.RequestError as e:
                print(
                    "Could not request results from Google Speech Recognition service; {0}".format(e))
            except ValueError as e:
                print(e)


    def reserve_dakoku(self, dakoku_queue):

        record_thread = Thread(target=self.record)
        recognize_thread = Thread(target=self.recognize, args=(dakoku_queue,))
        record_thread.daemon = True
        recognize_thread.daemon = True

        record_thread.start()
        recognize_thread.start()

        while True:
            time.sleep(10)

    def speak(self, message):
        # 録音終了まで待機
        while self.listening_speaking_flg:
            time.sleep(0.1)

        self.listening_speaking_flg = True
        sec = jtalk(message)

        # システム発話終了まで待機
        time.sleep(sec)
        self.listening_speaking_flg = False

        

    # 顔認証で失敗したユーザに対して、名前をもとに判別
    def detect_unknown_visitor(self):
        start = time.time()

        print('say your name...')

        while time.time() - start < 20:
            if len(self.sound_queue) == 0:
                time.sleep(0.1)
                continue

            audio = self.sound_queue.popleft()

            print("Now to recognize it...")

            try:
                recog_result = self.r.recognize_google(audio, language='ja-JP', show_all=True)
                print(recog_result)

                # 音声認識がうまくいってないとき
                if not isinstance(recog_result, dict) or len(recog_result.get("alternative", [])) == 0:
                    print("could not understand audio")
                    continue

                sorted_result = sorted(recog_result['alternative'], key=lambda x: x['confidence']) if "confidence" in recog_result["alternative"] else recog_result['alternative']
                recog_texts = [recog_elem['transcript'] for recog_elem in sorted_result]
                
                users_ref = self.user_db.collection(str(self.company_id))
                users = [doc.to_dict() for doc in users_ref.get()]

                for user in users:
                    if name_in_texts(user, recog_texts):
                        return user

            # 以下は認識できなかったときに止まらないように。
            except sr.UnknownValueError:
                print("could not understand audio")
            except sr.RequestError as e:
                print(
                    "Could not request results from Google Speech Recognition service; {0}".format(e))

        return None


# userの姓名がtextに含まれるか否か
def name_in_text(user, text):
    return user['last_name_kanji'] in text or user['first_name_kanji'] in text or kata2hira(user['last_name_kana']) in text or kata2hira(user['first_name_kana']) in text or user['last_name_kana'] in text or user['first_name_kana'] in text

# userの姓名がtextsに含まれるか否か
def name_in_texts(user, texts):
    return any([name_in_text(user, text) for text in texts])

# 慈悲深い声掛けを追加
def mercy_message(attr, emotion):
    if attr == 0:
        return '今日も頑張りましょう' if emotion == 1 else '無理しないで下さい'
    elif attr == 1:
        return '次も頑張ってください' if emotion == 1 else 'ゆっくり休んでください'
    elif attr == 2:
        return '' if emotion == 1 else 'ゆっくり休んでください'
    elif attr == 3:
        return '' if emotion == 1 else '無理しないで下さい'
    else:
        raise ValueError('error: attr is invalid')
        


def main():
    reserve_dakoku([])


if __name__ == "__main__":
    main()
