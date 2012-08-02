from urlparse import urlparse
from collections import deque
import httplib
import threading

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
		self.reconnect()
	def reconnect(self):
		print 'conn:', self.scheme, self.hostname, self.port
		if self.scheme == 'https':
			self.conn = httplib.HTTPSConnection(self.hostname,
								self.port)
		else:
			self.conn = httplib.HTTPConnection(self.hostname,
								self.port)
	def pushreq(self, req):
		assert(req.url.hostname == self.hostname)
		assert(req.url.port == self.port)
		self.push(req)
	def _do_work(self, req):
		retry = 3
		while retry:
			try:
				self.conn.request(req.method, req.url.path,
						req.content, req.headers)
				r = self.conn.getresponse()
				d = r.read()
				retry = 0
			except Exception, e:
				self.reconnect()
				r = e
				d = None
				retry -= 1

		req.cb(r, d)

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
		try:
			u = urlparse(url)
		except:
			u = None
			pass
		if u is None or u.scheme == '':
			try:
				u = urlparse(url, scheme = 'http')
			except:
				return
		if u.hostname is None:
			return

		def Closure(r, data):
			if isinstance(r, Exception) or r.status != 200:
				if err:
					err(r)
				print r
				return
			cb(data)

		conn = self.get_conn(u)
		req = WebReq(Closure, u)
		conn.pushreq(req)
