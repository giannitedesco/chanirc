from socket import gethostbyname, socket, AF_INET, SOCK_STREAM, IPPROTO_TCP, \
			SOL_SOCKET, SO_ERROR, error as SockError
from errno import EINPROGRESS, EAGAIN
from os import strerror
from collections import deque
import gobject, glib

class TCPSock(gobject.GObject):
	__gsignals__ = {
		'data-in': (gobject.SIGNAL_RUN_LAST,
			gobject.TYPE_NONE, (gobject.TYPE_STRING,)),
		'connected': (gobject.SIGNAL_RUN_LAST,
			gobject.TYPE_NONE, ()),
		'disconnected': (gobject.SIGNAL_RUN_LAST,
			gobject.TYPE_NONE, ()),
		'error': (gobject.SIGNAL_RUN_LAST,
			gobject.TYPE_NONE,
			(gobject.TYPE_STRING, gobject.TYPE_STRING))
	}
	def __init__(self):
		gobject.GObject.__init__(self)
		self.__sock = socket(AF_INET, SOCK_STREAM, IPPROTO_TCP)
		self.__sock.setblocking(0)
		self.__waitf = 0
		self.__sid = None
		self.__wait = False
		self.peer = (None, None)
		self.connected = False

	def send(self, msg):
		# FIXME: handle write-buffer full
		self.__sock.send(msg)

	def __read(self):
		msg = self.__sock.recv(4096)
		self.emit('data-in', msg)

	def do_error(self, op, msg):
		print 'TCPSock.do_error'
		self.__sock = None

	def do_connected(self):
		return

	def __write(self):
		if not self.connected:
			ret = self.__sock.getsockopt(SOL_SOCKET, SO_ERROR)
			if ret:
				self.emit('error', 'connect', strerror(ret))
			else:
				self.emit('connected')
				self.connected = True
				self.set_wait_write(False)
				self.set_wait_read()

		else:
			return

	def __cb(self, fd, flags):
		if flags & (glib.IO_IN|glib.IO_HUP|glib.IO_ERR):
			self.__read()
		if flags & (glib.IO_OUT):
			self.__write()
		self.wait()
		return False

	def unwait(self):
		if self.__sid is not None:
			glib.source_remove(self.__sid)
			self.__sid = None

	def wait(self):
		self.unwait()
		if self.__sock:
			self.__sid = glib.io_add_watch(self.__sock.fileno(),
				self.__waitf | glib.IO_HUP | glib.IO_ERR,
				self.__cb)

	def set_wait_read(self, flag = True):
		if bool(flag):
			self.__waitf |= glib.IO_IN
		else:
			self.__waitf &= ~glib.IO_IN

	def set_wait_write(self, flag = True):
		if bool(flag):
			self.__waitf |= glib.IO_OUT
		else:
			self.__waitf &= ~glib.IO_OUT

	def connect_to(self, host, port):
		self.peer = (host, port)
		try:
			self.__sock.connect(self.peer)
		except SockError, e:
			if e.errno == EINPROGRESS:
				self.set_wait_write()
				self.__cb(-1, 0)
			else:
				self.emit('error', 'connect', e.strerror)
			return

		self.__connected()

gobject.type_register(TCPSock)
