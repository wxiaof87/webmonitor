import threading
import time
import logging
import dbutil
from queue import PriorityQueue
from concurrent.futures import ThreadPoolExecutor
from threading import Thread
from job import WebMonitorJob
from job import RepeatJob
from job import Job


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
        self.logger.info("scheduling all jobs from database")
        jsonJobs = self.db.getAllJobs()
        for curJsonJob in jsonJobs:
            # url = curJsonJob['params']
            interval = float(curJsonJob['interval'])
            jobid = curJsonJob['jobid']
            email = curJsonJob['email']
            params = curJsonJob['params']
            job_type = 'WebMonitorJob'  # TODO: curJsonJob['job_type']
            if job_type == 'WebMonitorJob':
                url = params
                if url is not None and url.startswith('http'):
                    job = WebMonitorJob(url, interval, jobid=jobid, email=email)
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

            # exit job
            if job.jobid == '-1':
                self.logger.info("========exit job encountered. exit now!========")
                self.executor.shutdown()
                return

            if job.jobid in self.removedJobs:
                self.removedJobs.remove(job.jobid)
                self.logger.info('jobid {} is removed!'.format(job.jobid))
                continue
            # TODO: which is the better way to handle this ?
            # job.waitTillReady()
            if job.isReady():
                self.executor.submit(job.execute)
                if job.hasNext():
                    self.scheduleJob(job)
            else:
                self.scheduleJob(job)
                self.logger.info("current job {} is not ready. sleep for a while".format(job.jobid))
                time.sleep(3)

    def scheduleJob(self, job):
        self.logger.info('schedule one job: {} at {}'.format(job.params, job.getExecTime()))
        self.waitQueue.put(job)

    # create a new job: schedule job and put into db
    def addJob(self, job):
        self.scheduleJob(job)
        self.db.insertJob(job.jobid, job.userid, job.email, job.interval, job.params)
        return job.jobid

    def removeJob(self, jobid):
        self.removedJobs.add(jobid)
        self.db.removeJob(jobid)

    def jobRefresherThread(self):
        # read config file and update jobs
        pass

    def stop(self):
        exitJob = Job(1, '-1')
        self.scheduleJob(exitJob)
