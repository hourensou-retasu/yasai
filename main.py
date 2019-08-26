#coding:utf-8

import time
from reserve_dakoku import reserve_dakoku
from execute_dakoku import execute_dakoku
from threading import Thread
from collections import deque


def main():
    RD = reserve_dakoku()
    ED = execute_dakoku()

    dakoku_queue = deque([])
    reserve_thread = Thread(target=RD.reserve_dakoku, args=(dakoku_queue,))
    execute_thread = Thread(target=ED.execute_dakoku, args=(dakoku_queue,))
    reserve_thread.daemon = True
    execute_thread.daemon = True

    reserve_thread.start()
    execute_thread.start()

    while True:
        time.sleep(10)


if __name__ == "__main__":
    main()
