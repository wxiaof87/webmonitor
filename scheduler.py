from queue import PriorityQueue
from concurrent.futures import ThreadPoolExecutor
import threading
from threading import Thread
from threading import Lock
import time
import random
import logging
import traceback
import dbutil
from job import WebMonitorJob
from job import RepeatJob

class Scheduler(Thread):
    def __init__(self):
        Thread.__init__(self)
        self.db = dbutil.Database()
        self.waitQueue = PriorityQueue()
        self.executor = ThreadPoolExecutor(4)
        self.logger = logging.getLogger(self.__class__.__name__)

        self.removedJobs = set([])
        self.scheduleAllJobsFromDB()

    def scheduleAllJobsFromDB(self):
        jsonJobs = self.db.getAllJobs()
        for curJsonJob in jsonJobs:
            url = curJsonJob['params']
            interval = float(curJsonJob['interval'])
            jobid = curJsonJob['jobid']
            params = curJsonJob['params']
            job_type = 'WebMonitorJob' # TODO: curJsonJob['job_type']
            if job_type == 'WebMonitorJob':
                url = params
                if url is not None and url.startswith('http'):
                    job = WebMonitorJob(url, interval, jobid)
                    self.scheduleJob(job)
                else:
                    self.logger.warning('skip one WebMonitorJob, because invalid url: {}'.format(url))
            else:
                # Simple repeat job. for testing purpose
                job = RepeatJob(interval, jobid)
                self.scheduleJob(job)

    def reportStatus(self):
        self.logger.info('qsize in waitQueue: ' + str(self.waitQueue.qsize()) + ', qsize in executor: ' + str(self.executor._work_queue.qsize()) + ', active threads: ' + str(threading.activeCount()))

    def run(self):
        self.logger.info('Scheduler started')
        while True:
            self.reportStatus()
            job = self.waitQueue.get()  # block
            if job.jobid in self.removedJobs:
                self.removedJobs.remove(job.jobid)
                self.logger.info('jobid {} is removed!'.format(job.jobid))
                continue
            # job.waitTillReady()
            if job.isReady():
                self.executor.submit(job.execute)
                if job.hasNext():
                    self.scheduleJob(job)
            else:
                self.scheduleJob(job)
                time.sleep(1)

    def scheduleJob(self, job):
        self.logger.info('schedule one job: {} at {}'.format(job.params, job.getExecTime()))
        self.waitQueue.put(job)

    # create a new job: schedule job and put into db
    def addJob(self, job):
        self.scheduleJob(job)
        self.db.insertJob(job.jobid, job.userid, job.interval, job.params)

    def removeJob(self, jobid):
        self.removedJobs.add(jobid)
        self.db.removeJob(jobid)

    def jobRefresherThread(self):
        # read config file and update jobs
        pass

if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s: %(message)s')
    logging.info('start')
    scheduler1 = Scheduler()
    scheduler1.addJob(WebMonitorJob('http://192.168.0.101', 3))
    scheduler1.addJob(WebMonitorJob('http://192.168.0.101?a=1', 5))
    scheduler1.addJob(WebMonitorJob('http://192.168.0.101?b=2', 7))
    scheduler1.start()
    scheduler1.join()
    logging.info('exit')


