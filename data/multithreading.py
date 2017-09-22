import dota2api
from threading import Thread
from Queue import Queue, Empty, PriorityQueue
import time
import sys
import os
from data.api_helpers import api_call, get_match_history
from data.db_helpers import connect

def task(in_q, out_q, con):
    while True:
        args = in_q.get()
        api_call(args, out_q, con)
        in_q.task_done()

class Worker(object):
    def __init__(self, task, args=None):
        object.__init__(self)
        self.thread = Thread(target=task, args=args)
        self.thread.daemon = True
        self.thread.start()

class Scheduler(object):
    def __init__(self, task_queue, schedule):
        self.schedule = schedule
        self.task_queue = task_queue
        self.heap = PriorityQueue()
        self.thread = Thread(target=self.run_tasks)
        self.thread.start()
    def run_tasks(self):
        while True:
            priority, item = self.heap.get()
            self.task_queue.put(item)
            print('queued')
            time.sleep(self.schedule)

if __name__ == '__main__':
    try:
        db_name = sys.argv[2]
    except IndexError:
        db_name = 'dota2_draft'
    db_name = 'dota2_draft' # just for hydrogen
    with open(os.path.expanduser('~/.pgpass')) as f:
        for line in f:
            host, port, db, user, password = [x.strip() for x in line.split(':')]
            if db == db_name:
                con, meta = connect(user=user, password=password, db=db, host=host, port=port)
                break
    workers = []
    q = Queue()
    scheduler = Scheduler(q, 1)
    time0 = time.time()
    duration = 10
    for i in xrange(4):
        workers.append(Worker(task=task, args=(q, scheduler.heap, con)))
    scheduler.heap.put((3, (get_match_history, None, time0, duration)))