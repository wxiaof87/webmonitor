import sqlite3
import logging


class Database:
    def __init__(self, location='test.db'):
        self.logger = logging.getLogger(self.__class__.__name__)
        self.location = location
        self.logger.info("Successfully Connected to SQLite.")

    def execute(self, query):
        sqliteConnection = sqlite3.connect(self.location)
        cursor = sqliteConnection.cursor()

        self.logger.info("executing query\n{}".format(query))
        cursor.execute(query)
        sqliteConnection.commit()
        self.logger.info("query is executed Successfully")
        cursor.close()

    def insertUser(self, userid, password, email):
        query = """INSERT INTO users
                    (userid, password, email) 
                    VALUES 
                    ('{}', '{}', '{}')""".format(userid, password, email)
        self.execute(query)

    def insertJob(self, jobid, userid, interval, url):
        job_type = 'WebMonitorJob'  # TODO: fix this!
        params = url
        query = """INSERT INTO jobs
                    (jobid, userid, job_type, interval, params) 
                    VALUES 
                    ('{}', '{}', '{}', {}, '{}')""".format(jobid, userid, job_type, interval, params)
        self.execute(query)

    def queryJobsForUser(self, userid):
        query = """SELECT jobid, interval, params FROM jobs WHERE userid = '{}'""".format(userid)
        rows = self.executeSelectQuery(query)
        return self.rowsToJobs(rows)

    def getAllJobs(self):
        query = """SELECT jobid, interval, params FROM jobs"""
        rows = self.executeSelectQuery(query)
        return self.rowsToJobs(rows)

    def executeSelectQuery(self, query):
        sqliteConnection = sqlite3.connect(self.location)
        cur = sqliteConnection.cursor()
        self.logger.info('Execute Select Query:\n{}'.format(query))
        cur.execute(query)
        rows = cur.fetchall()
        return rows

    def rowsToJobs(self, rows):
        allJobs = []
        for row in rows:
            curJob = {'jobid': row[0],
                      'interval': row[1],
                      'params': row[2]
                    }

            allJobs.append(curJob)
        return allJobs

    def removeJob(self, jobid):
        query = """DELETE FROM jobs WHERE jobid = '{}'""".format(jobid)
        self.execute(query)
    # TODO: check user and job relation before create/update/delete a job
    # TODO: add delete user and all its jobs
    def deleteUser(self, userid):
        pass

    def init(self):
        # Create all tables, only called once (e.g. during test).
        with open('tables.sql', 'r') as f:
            queries = f.read()

        sqliteConnection = sqlite3.connect(self.location)
        cur = sqliteConnection.cursor()
        cur.executescript(queries)


