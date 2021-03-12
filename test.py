from util import EmailClient
import unittest
import logging
from scheduler import Scheduler
from job import WebMonitorJob

class EmailClientTest(unittest.TestCase):
    def test_send(self):
        emailClient = EmailClient()
        emailClient.send('testuser@gmail.com', 'hi', 'how are you')
        logging.info('test sending email successful')

class SchedulerTest(unittest.TestCase):
    def test_scheduler(self):
        scheduler1 = Scheduler()
        scheduler1.addJob(WebMonitorJob('http://192.168.0.101', 3))
        scheduler1.addJob(WebMonitorJob('http://192.168.0.101?a=1', 5))
        scheduler1.addJob(WebMonitorJob('http://192.168.0.101?b=2', 7))
        scheduler1.start()
        scheduler1.join()
        logging.info('test scheduler successful')

if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s: %(message)s')
    unittest.main()
