from util import EmailClient
import unittest
import logging
from scheduler import Scheduler
from job import WebMonitorJob
import time
from dbutil import Database


class EmailClientTest(unittest.TestCase):
    def test_send(self):
        emailClient = EmailClient()
        emailClient.send('testuser@gmail.com', 'hi', 'how are you')
        logging.info('test sending email successful')



class DatabaseTest(unittest.TestCase):
    def test_db(self):
        db = Database('tmp.db')
        db.init()
        db.insertUser('1', '123456', 'testuser@gmail.com')
        db.insertJob('1', '1', 10, 'http://localhost:8081')
        db.insertJob('2', '1', 100, 'http://localhost:8081')
        logging.info('jobs for one user: {}'.format(db.queryJobsForUser('1')))
        logging.info('jobs for all users: {}'.format(db.getAllJobs()))

        # TODO: purge data after tests
        db.removeJob('1')
        db.removeJob('2')

        logging.info('after removal. jobs for all users: {}'.format(db.getAllJobs()))

class SchedulerTest(unittest.TestCase):
    def test_scheduler(self):
        scheduler1 = Scheduler()
        scheduler1.db.init()
        job1 = WebMonitorJob('http://192.168.0.101', 3)
        job2 = WebMonitorJob('http://192.168.0.101?a=1', 5)
        job3 = WebMonitorJob('http://192.168.0.101?b=2', 7)
        scheduler1.addJob(job1)
        scheduler1.addJob(job2)
        scheduler1.addJob(job3)
        scheduler1.start()
        time.sleep(10)
        logging.info("jobs are removed")
        scheduler1.removeJob(job1.jobid)
        scheduler1.removeJob(job2.jobid)
        scheduler1.removeJob(job3.jobid)
        time.sleep(3)
        logging.info("stop scheduler")
        scheduler1.stop()
        logging.info('test scheduler successful')
        scheduler1.join()


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s: %(message)s')
    unittest.main()
