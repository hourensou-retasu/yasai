#coding:utf-8

import speech_recognition as sr
import re
import numpy as np
from jtalk import jtalk
import face_recognizer
import time
from firestoreAPI import FireStoreDB
from pykakasi import kakasi

class reserve_dakoku:
    def __init__(self):
        self.r = sr.Recognizer()
        self.mic = sr.Microphone()

        self.user_db = FireStoreDB().db

        self.fr = face_recognizer.FaceRecognizer(self.user_db)
        
        kakasi = kakasi()
        kakasi.setMode('J', 'H')  # J(Kanji) to H(Hiragana)
        self.conv = kakasi.getConverter()

        self.dakoku_patterns = [
            '.*?(おはよう).*', 
            '.*?(おつかれ|さき|しつれい|さようなら).*',
            '.*?(きゅうけい)(はいり|いただきます).*',
            '.*?(きゅうけい)(あがり|いただきました).*'
        ]

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

    def reserve_dakoku(self, dakoku_queue):

        while True:
            print("Say something ...")

            with self.mic as source:
                self.r.adjust_for_ambient_noise(source) #雑音対策
                audio = self.r.listen(source)

            print ("Now to recognize it...")

            try:
                recog_text = conv.do(self.r.recognize_google(audio, language='ja-JP'))
                print(recog_text)

                dakoku_results = [re.match(dakoku_pattern, recog_text) for dakoku_pattern in self.dakoku_patterns]
            
                # 打刻WORDにマッチ
                if any(dakoku_results):
                    user = self.fr.authorize()
                    
                    # マッチした打刻種類の最初のindexを取得 0:出勤 1:退勤 2:休憩始 3:休憩終
                    dakoku_attr = None
                    for index, dakoku_result in enumerate(dakoku_results):
                        if dakoku_result is None:
                            continue
                        else:
                            dakoku_attr = index
                            break
                            
                    message = self.dakoku_message_dict[dakoku_attr] + ('、どちらさまですか' if user is None else '、' + user['last_name_kana'] + 'さん')
                    jtalk(message)

                    if user is None:
                        user = self.detect_unknown_visitor()

                        # また失敗したとき
                        if user is None:
                            jtalk('登録されたユーザを認識できませんでした')
                            continue

                    dakoku_queue.append({'employee_id':user['employee_id'], 'dakoku_attr':dakoku_attr, 'time':time.time()})

                # 前回打刻されたユーザを除き、登録ユーザ名が発話に含まれるか否か
                else:
                    users_ref = self.user_db.collection('users')
                    users = [doc.to_dict() for doc in users_ref.get()]

                    for user in users:
                        if len(dakoku_queue):
                            if user['employee_id'] != dakoku_queue[-1]['employee_id'] and name_in_text(user, recog_text) in recog_text:
                                dakoku_queue[-1] = {{'employee_id': user['employee_id'],
                                                     'dakoku_attr': dakoku_queue[-1]['dakoku_attr'],
                                                      'time': time.time()}}
                                          
                                message = '{}さんの{}を打刻しました'.format(
                                    user['last_name_kana'], self.dakoku_attr_str[dakoku_queue[-1]['dakoku_attr']])
                                jtalk(message)

            # 以下は認識できなかったときに止まらないように。
            except sr.UnknownValueError:
                print("could not understand audio")
            except sr.RequestError as e:
                print("Could not request results from Google Speech Recognition service; {0}".format(e))


    # 顔認証で失敗したユーザに対して、名前をもとに判別
    def detect_unknown_visitor(self):
        print("Say your name ...")

        with self.mic as source:
            self.r.adjust_for_ambient_noise(source)  # 雑音対策
            audio = self.r.listen(source)

        print("Now to recognize it...")

        try:
            recog_text = conv.do(self.r.recognize_google(audio, language='ja-JP'))
            print(recog_text)
            
            users_ref = self.user_db.collection('users')
            users = [doc.to_dict() for doc in users_ref.get()]

            for user in users:
                if name_in_text(user, recog_text):
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
    return user['last_name_kana'] in text or user['first_name_kana'] in text


def main():
    reserve_dakoku()


if __name__ == "__main__":
    main()
