import subprocess
from datetime import datetime
from pydub import AudioSegment

def jtalk(t):
    open_jtalk = ['open_jtalk']
    mech = ['-x', '/usr/local/Cellar/open-jtalk/1.11/dic']
    htsvoice = ['-m', '/usr/local/Cellar/open-jtalk/1.11/voice/mei/mei_normal.htsvoice']
    speed = ['-r', '1.0']
    outwav = ['-ow', 'out.wav']
    cmd = open_jtalk + mech + htsvoice + speed + outwav
    c = subprocess.Popen(cmd, stdin=subprocess.PIPE)
    c.stdin.write(t.encode('utf-8'))
    c.stdin.close()
    c.wait()
    aplay = ['afplay', 'out.wav']
    wr = subprocess.Popen(aplay)

    # 音声ファイルの読み込み
    sound = AudioSegment.from_file("out.wav", "wav")

    # 情報の取得
    return sound.duration_seconds  # 再生時間(秒)
    
def say_datetime():
    d = datetime.now()
    text = '%s月%s日、%s時%s分%s秒' % (d.month, d.day, d.hour, d.minute, d.second)
    jtalk(text)

if __name__ == '__main__':
    say_datetime()
