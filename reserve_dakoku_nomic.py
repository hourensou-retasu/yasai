#coding:utf-8

import re
import numpy as np

def reserve_dakoku():

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
        print("Input something ...")

        recog_text = input()

        dakoku_results = [re.match(dakoku_pattern, recog_text) for dakoku_pattern in dakoku_patterns]
        print(dakoku_results)

        # 打刻WORDにマッチ
        if any(dakoku_results):
            name = "[名前]"

            # マッチした打刻種類の最初のindexを取得 0:出勤 1:退勤 2:休憩始 3:休憩終
            dakoku_attr = None
            for index, dakoku_result in enumerate(dakoku_results):
                if dakoku_result is None:
                    continue
                else:
                    dakoku_attr = index
                    break
            
            message = dakoku_message_dict[dakoku_attr] + ('、どちらさまですか' if name is None else '、' + name + 'さん')
            print('reply: {}'.format(message))
        else:
            pass


def main():
    reserve_dakoku()


if __name__ == "__main__":
    main()