#coding:utf-8

import speech_recognition as sr
import re
import numpy as np
from jtalk import jtalk
import face_recognizer
import time

class reserve_dakoku:
    def __init__(self):
        self.r = sr.Recognizer()
        self.mic = sr.Microphone()

        self.fr = face_recognizer.FaceRecognizer()

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
                recog_text = self.r.recognize_google(audio, language='ja-JP')
                print(recog_text)

                dakoku_results = [re.match(dakoku_pattern, recog_text) for dakoku_pattern in self.dakoku_patterns]
            
                # 打刻WORDにマッチ
                if any(dakoku_results):
                    user = fr.authorize()
                    
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
                        
                        # 名前が登録ユーザーでないとき

                    dakoku_queue.append({'employee_id':user['employee_id'], 'dakoku_attr':dakoku_attr, 'time':time.time()})

                # 前回打刻されたユーザを除き、登録ユーザ名が発話に含まれるか否か
                else:
                    for user in users:
                        if user['employee_id'] != dakoku_queue[-1]['employee_id'] and user['last_name_kana'] in recog_text:
                            dakoku_queue[-1] = {{'employee_id': user['employee_id'],
                                                 'dakoku_attr': dakoku_queue[-1]['dakoku_attr'], 'time': time.time()}}
                                          
                            message = '{}さんの{}を打刻しました'.format(
                                user['last_name_kana'], self.dakoku_attr_str[dakoku_queue[-1]['dakoku_attr']])
                            jtalk(message)


            # 以下は認識できなかったときに止まらないように。
            except sr.UnknownValueError:
                print("could not understand audio")
            except sr.RequestError as e:
                print("Could not request results from Google Speech Recognition service; {0}".format(e))

    def detect_unknown_visitor(self):
        print("Say your name ...")

        with self.mic as source:
            self.r.adjust_for_ambient_noise(source)  # 雑音対策
            audio = self.r.listen(source)

        print("Now to recognize it...")

        try:
            recog_text = self.r.recognize_google(audio, language='ja-JP')
            print(recog_text)
            return recog_text

        # 以下は認識できなかったときに止まらないように。
        except sr.UnknownValueError:
            print("could not understand audio")
        except sr.RequestError as e:
            print(
                "Could not request results from Google Speech Recognition service; {0}".format(e))

def main():
    reserve_dakoku()


if __name__ == "__main__":
    main()
