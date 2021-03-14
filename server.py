import logging
import json
import sys
import scheduler
from job import WebMonitorJob
from http.server import HTTPServer, ThreadingHTTPServer, BaseHTTPRequestHandler
import urllib.parse


# TODO: add path handler, add request parameters parser, add html template
class EndPoints:
    ADD_JOB = '/addjob'
    REMOVE_JOB = '/removejob'
    QUERY_JOB = '/queryjob'


class MyHTTPRequestHandler(BaseHTTPRequestHandler):
    _scheduler = scheduler.Scheduler()

    def do_GET(self):
        # path include request parameters, e.g. /index.html?p1=1&p2=2
        logging.info('path: ' + self.path)
        path = self.path

        # TODO: what if the watched url has query parameters itself ?
        # qs = dict([qs.split('=') for qs in path[path.index('?')+1:].split('&')])
        # TODO: add change job interval
        # TODO: use a map to handle endpoint to handler
        contentType = 'application/json'  # default content type: json
        # TODO: have a nicer method to parse parameters
        # e.g. http://127.0.0.1:8000/addjob?interval=10&url=http://192.168.0.101?a=101
        if path.startswith(EndPoints.ADD_JOB):
            # TODO: add try-catch to handle illegal params
            idxForIntervalStart = len(EndPoints.ADD_JOB) + len('?interval=')
            idxForIntervalEnd = path.find('&', idxForIntervalStart)
            interval = float(path[idxForIntervalStart: idxForIntervalEnd])

            idxForEmailStart = idxForIntervalEnd + len('&email=')
            idxForEmailEnd = path.find('&', idxForEmailStart)
            email = urllib.parse.unquote(path[idxForEmailStart:idxForEmailEnd])

            idxForUrlStart = idxForEmailEnd + len('&url=')
            urlEncoded = path[idxForUrlStart:]
            url = urllib.parse.unquote(urlEncoded)
            response = self.addJob(interval, url, email)

        # e.g. http://127.0.0.1:8000/removejob?jobid=1615164987341_1276
        elif path.startswith(EndPoints.REMOVE_JOB):
            idxStart = len(EndPoints.REMOVE_JOB) + len('?jobid=')
            idxEnd = path.find('&', idxStart)
            if idxEnd < 0:
                idxEnd = len(path)
            # logging.info('idxEnd: {}'.format(idxEnd))
            jobid = path[idxStart:idxEnd]
            response = self.removeJob(jobid)

        # e.g. http://127.0.0.1:8000/queryjob?userid=1
        elif path.startswith(EndPoints.QUERY_JOB):
            idxStart = len(EndPoints.QUERY_JOB) + len('?email=')
            idxEnd = path.find('&', idxStart)
            if idxEnd < 0:
                idxEnd = len(path)
            logging.info('idxStart: {}, idxEnd: {}'.format(idxStart, idxEnd))
            email = urllib.parse.unquote(path[idxStart:idxEnd])
            response = self.queryJob(email)
        # regular html file, e.g. http://127.0.0.1:8000/index.html
        else:
            contentType = 'text/html; charset=utf-8'  # overwrite content type
            fileName = ""
            if path == "/":
                fileName = "index.html"
            elif path.endswith('.html'):
                fileName = path[1:]  # '/xxx.html', skip '/'
            if len(fileName) > 0:
                response = self.getHtmlFromFile(fileName)  # index.html
            else:
                response = 'ERROR: NOT IMPLEMENTED!'

        self.sendResponse(response, contentType)

    def sendResponse(self, response, contentType):
        self.send_response(200)
        self.send_header('Content-Type', contentType)
        self.end_headers()
        self.wfile.write(response.encode('utf-8'))

    def getHtmlFromFile(self, fileName):
        # TODO: add memory cache here
        with open(fileName) as f:
            html = f.read()
            return html

    def addJob(self, interval, url, email):
        logging.info('adding job. interval: {}, url: {}, email'.format(interval, url, email))
        job = WebMonitorJob(url, interval, email=email)
        MyHTTPRequestHandler._scheduler.addJob(job)
        return json.dumps({'jobid': job.jobid})

    def removeJob(self, jobid):
        logging.info('remove job: {}'.format(jobid))

        MyHTTPRequestHandler._scheduler.removeJob(jobid)
        return json.dumps({'success': True})

    def queryJob(self, email):
        logging.info('query job for email {}'.format(email))
        # TODO: change this
        jobs = MyHTTPRequestHandler._scheduler.db.queryJobsForEmail(email)
        return json.dumps(jobs)

    def getEndpoint(self, path):
        idx = path.find('?')
        return path[1:idx]

if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s: %(message)s')
    MyHTTPRequestHandler._scheduler.start()

    handler_class = MyHTTPRequestHandler
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 8000
    server_address = ('', port)
    # httpd = HTTPServer(server_address, handler_class)
    httpd = ThreadingHTTPServer(server_address, handler_class)
    # TODO: add another thread to print all status regularly
    logging.info('Starting HTTPServer at port {}'.format(port))
    httpd.serve_forever()
    MyHTTPRequestHandler._scheduler.join()
    logging.info('exit!')
