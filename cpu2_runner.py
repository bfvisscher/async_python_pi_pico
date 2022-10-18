# MIT License (MIT)
# Copyright (c) 2022 Bart-Floris Visscher
# https://opensource.org/licenses/MIT


import _thread
import time


class __CPU2:
    """
    As micropython uses a GIL, there is no CPU advantage that multi threaded gives v.s. async
    """
    _instance = None

    def __new__(cls, *args, **kwargs):  # ensures only a single instance is created
        if not cls._instance:
            cls._instance = super().__new__(
                cls, *args, **kwargs)

        return cls._instance

    has_instance = False

    def __init__(self):  # as its a singleton, this is run only once
        self.id = 0
        self.completed = -1
        self.tasks = []
        self.task_lock = _thread.allocate_lock()

        _thread.start_new_thread(self.monitor, ())
        print('CPU2 ready to process tasks..')

    def monitor(self):
        while True:
            with self.task_lock:
                if len(self.tasks) == 0:
                    task = None
                else:
                    task = self.tasks.pop()
            if task is not None:
                task[1](*task[2], **task[3])
                with self.task_lock:
                    self.completed = task[0]
            time.sleep_us(100)

    def add_task(self, task_fcn, *nargs, **kwargs):
        with self.task_lock:
            self.id += 1
            self.tasks.append((self.id, task_fcn, nargs, kwargs))
            id = self.id
        return id

    def is_complete(self, task_id):
        return task_id <= self.completed


CPU2 = __CPU2()
