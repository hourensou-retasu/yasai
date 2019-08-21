#coding:utf-8

from datetime import datetime
from reserve_dakoku import reserve_dakoku
from execute_dakoku import execute_dakoku
from multiprocessing import Manager, Value, Process


def main():
    with Manager() as manager:
        RD = reserve_dakoku()
        ED = execute_dakoku()

        dakoku_queue = manager.list()
        reserve_process = Process(target=RD.reserve_dakoku, args=[dakoku_queue])
        execute_process = Process(target=ED.execute_dakoku, args=[dakoku_queue])

        reserve_process.start()
        execute_process.start()

        reserve_process.join()
        execute_process.join()


if __name__ == "__main__":
    main()
