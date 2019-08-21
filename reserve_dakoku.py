#coding:utf-8

import speech_recognition as sr
import re
import numpy as np
from jtalk import jtalk

def reserve_dakoku():

    r = sr.Recognizer()
    mic = sr.Microphone()

    dakoku_patterns = [
        '.*?(おはよう).*', 
        '.*?(おつかれ|さき|しつれい|さようなら).*',
        '.*?(きゅうけい)(はいり|いただきます).*',
        '.*?(きゅうけい)(あがり|いただきました).*'
    ]

    dakoku_message_dict = {
        0: 'おはようございます',
        1: 'おつかれさまでした',
        2: 'きゅうけいどうぞ',
        3: 'がんばってください'
    }

    while True:
        print("Say something ...")

        with mic as source:
            r.adjust_for_ambient_noise(source) #雑音対策
            audio = r.listen(source)

        print ("Now to recognize it...")

        try:
            recog_text = r.recognize_google(audio, language='ja-JP')
            print(recog_text)

            dakoku_results = [re.match(dakoku_pattern, recog_text) for dakoku_pattern in dakoku_patterns]
        
            # 打刻WORDにマッチ
            if any(dakoku_results):
                name = face_recog()

                # マッチした打刻種類の最初のindexを取得 0:出勤 1:退勤 2:休憩始 3:休憩終
                
            # マッチした打刻種類の最初のindexを取得 0:出勤 1:退勤 2:休憩始 3:休憩終
            dakoku_attr = None
            for index, dakoku_result in enumerate(dakoku_results):
                if dakoku_result is None:
                    continue
                else:
                    dakoku_attr = index
                    break
            message = dakoku_message_dict[dakoku_attr] + ('、どちらさまですか' if name is None else '、' + name + 'さん')
            jtalk(message)

            if name is None:
                name = detect_unknown_visitor()

                # また失敗したとき
                if name is None or name not in names:
                    jtalk('登録されたユーザを認識できませんでした')

            dakoku_queue.append(name, dakoku_attr)            

        # 以下は認識できなかったときに止まらないように。
        except sr.UnknownValueError:
            print("could not understand audio")
        except sr.RequestError as e:
            print("Could not request results from Google Speech Recognition service; {0}".format(e))


def main():
    reserve_dakoku()


if __name__ == "__main__":
    main()