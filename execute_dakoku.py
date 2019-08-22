# coding:utf-8

import time
from freeeAPI import freeeAPI


class execute_dakoku:

    def __init__(self):
        self.api = freeeAPI()

    def execute_dakoku(self, dakoku_queue, wait_for=15):
        while True:
            if len(dakoku_queue) == 0:
                time.sleep(0.1)
            else:
                oldest_time = dakoku_queue[0]['time']
                if time.time() - oldest_time > wait_for:
                    res = self._dakoku(dakoku_queue.popleft())
                    print(res)
                else:
                    time.sleep(0.1)

    def _dakoku(self, dakoku_dict):
        if dakoku_dict['dakoku_attr'] == 0:
            return self.api.clockIn(dakoku_dict['employee_id'])
        elif dakoku_dict['dakoku_attr'] == 1:
            return self.api.clockOut(dakoku_dict['employee_id'])
        elif dakoku_dict['dakoku_attr'] == 2:
            return self.api.breakBegin(dakoku_dict['employee_id'])
        elif dakoku_dict['dakoku_attr'] == 3:
            return self.api.breakEnd(dakoku_dict['employee_id'])
        else:
            return 'error'
