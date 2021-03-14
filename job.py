import time
import random
import logging
import traceback
import difflib
import urllib.request
import util
from threading import Lock


class Job:
    def __init__(self, interval, jobid=None, delay_start=True, userid=1, params=None, email=None):
        # create job id for new job. use existing job id for existing job
        if jobid is None:
            self.jobid = str(int(1000*time.time())) + "_" + str(random.randint(1000, 2000-1))
        else:
            self.jobid = jobid

        self.userid = userid
        self.email = email
        self.params = params  # job specific params. e.g. URL
        self.interval = interval
        self.execTime = time.time()
        if delay_start:
            self.execTime += interval
        self.lock = Lock()  # create a new lock for this job object
        self.numExecuted = 0
        self.logger = logging.getLogger(self.__class__.__name__)

    def execute(self):
        # the job may be repeating job.
        # if a job has not finished and a same new job is submitted to ThreadPoolExecutor
        # the run method may be executed by different threads in ThreadPoolExecutor at the same time
        # the lock here is to avoid such situation
        with self.lock:
            self.logger.info('job started: ' + self.jobid)
            # catch exception from subclass. otherwise it would be swallowed silently
            # https://stackoverflow.com/questions/49322477/concurrent-futures-threadpoolexecutor-swallowing-exceptions-python-3-6
            try:
                self.run()
            except Exception as e:
                self.logger.error("job {} execution error:\n".format(job.jobid) + traceback.format_exc())
            self.numExecuted += 1
            self.logger.info('job done: ' + self.jobid + '. this job has been executed ' + str(self.numExecuted) + ' number of times')

    # method to be overrided in subclass (concrete job)
    def run(self):
        pass

    # override this if it is not repeating job
    def hasNext(self):
        self.updateExecTime()
        return True

    def updateExecTime(self):
        self.execTime = time.time() + self.interval

    def getExecTime(self):
        return self.execTime

    # used in priority queue
    def __lt__(self, other):
        return self.execTime < other.execTime

    def isReady(self):
        return self.execTime < time.time()

    def waitTillReady(self):
        gap = self.execTime-time.time()
        if gap > 0.5:
            self.logger.info("waiting for job " + self.jobid + " to be ready...sleep " + format(gap, '.1f') + " seconds")
            time.sleep(gap)


class RepeatJob(Job):
    def run(self):
        self.logger.info('i am job ' + self.jobid + " running")
        time.sleep(1)


class WebMonitorJob(Job):
    def __init__(self, url, interval, jobid=None, email=None):
        Job.__init__(self, interval, jobid=jobid, email=email)
        self.url = url
        self.params = self.url
        self.html = ""
        self.emailClient = util.EmailClient()
        self.headers = {
            'Referer': 'https://www.google.com',
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/79.0.3945.130 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
            'Accept-Language': 'en-US,en;q=0.9,zh-CN;q=0.8,zh;q=0.7'
        }

    def diff(self, oldHtml, newHtml):
        result = difflib.context_diff(oldHtml.splitlines(), newHtml.splitlines())
        return '\n'.join(result)

    def run(self):
        self.logger.info("fetching {}".format(self.url))
        # TODO: handle exception below ?
        req = urllib.request.Request(self.url, data=None, headers=self.headers)
        # self.logger.info("req created")
        with urllib.request.urlopen(req) as response:
            # self.logger.info("fetch done")
            html = response.read().decode()
            # self.logger.info("decode done: ".format(html))
            if self.html is None or len(self.html) < 1:
                self.logger.info("first time fetch, skip comparison")
                self.html = html
                return
            diff = self.diff(self.html, html)
            if len(diff) > 0:
                self.logger.debug("change found:\n" + diff)
                self.emailClient.send(self.email, 'updated ' + self.url, diff)
            else:
                self.logger.info("Nothing change")
            self.html = html
