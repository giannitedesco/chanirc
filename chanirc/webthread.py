from collections import deque
import httplib2
import threading
from os import environ, path

class WorkQueue(threading.Thread):
	def __init__(self):
		threading.Thread.__init__(self)
		self.daemon = True
		self.queue = deque()
		self.lock = threading.Lock()
		self.wait = threading.Event(1)
		self.start()
	def push(self, thing):
		self.lock.acquire()
		self.queue.append(thing)
		self.lock.release()
		self.wait.set()
	def run(self):
		while True:
			self.wait.wait()

			self.lock.acquire()
			work = self.queue.popleft()
			if not len(self.queue):
				self.wait.clear()
			self.lock.release()

			if work is not None:
				self._do_work(work)

class WebReq:
	def __init__(self, cb, url,
			method = 'GET', content = None, headers = {}):
		self.url = url
		self.method = method
		self.content = content
		self.headers = headers
		self.cb = cb

class WebConn(WorkQueue):
	def __init__(self, u):
		WorkQueue.__init__(self)
		self.hostname = u.hostname
		self.port = u.port
		self.scheme = u.scheme
		p = environ.get('HOME')
		if p is None:
			p = environ.get('APPDATA')
		self.cache_dir = path.join(p, ".chanirc/cache")
		self.conn = httplib2.Http(cache = self.cache_dir)
	def pushreq(self, req):
		assert(req.url.hostname == self.hostname)
		assert(req.url.port == self.port)
		self.push(req)
	def _do_work(self, req):
		url = req.url.geturl()
		try:
			while True:
				(r, d) = self.conn.request(url)
				if r.status == 404 and url[-1:] == ')':
					url = url[:-1]
					continue
				else:
					break
		except Exception, e:
			(r, d) = (e, None)

		req.cb(r, d)

def begins_with(s, prefix):
	if len(s) < len(prefix):
		return False
	return s[:len(prefix)] == prefix

class WebPool:
	def __init__(self, login = None, pwd = None):
		self.login = login
		self.pwd = pwd
		self.conn = {}

	def get_conn(self, url):
		conn = self.conn.get((url.scheme, url.hostname, url.port), None)
		if conn is None:
			conn = WebConn(url)
			self.conn[(url.scheme, url.hostname, url.port)] = conn
		return conn

	def get_image(self, url, cb, err = None):
		def Closure(r, data):
			if isinstance(r, Exception) or \
				r.status != 200 or \
				not begins_with(r['content-type'], 'image/'):
				if err:
					err(r)
				else:
					return
			else:
				cb(data)

		conn = self.get_conn(url)
		req = WebReq(Closure, url)
		conn.pushreq(req)
