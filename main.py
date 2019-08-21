#coding:utf-8

from datetime import datetime
from reserve_dakoku import reserve_dakoku
from execute_dakoku import execute_dakoku
from concurrent.futures import ThreadPoolExecutor

def main():
    executor = ThreadPoolExecutor(max_workers=2)
    executor.submit(reserve_dakoku)
    executor.submit(execute_dakoku)

if __name__ == "__main__":
    main()