from socket import gethostbyname, socket, AF_INET, SOCK_STREAM, IPPROTO_TCP, \
			SOL_SOCKET, SO_ERROR, error as SockError
from errno import EINPROGRESS, EAGAIN
import glib, gobject, gtk
from os import strerror
from collections import deque
from chanwin import ChanWin

class ServerTab(gobject.GObject):
	STATE_DISCONNECTED = 0,
	STATE_CONNECTING = 1,
	STATE_CONNECTED = 2,

	def __init__(self):
		#self.__gobject_init__()
		gobject.GObject.__init__(self)
		self.title = '<None>'
		self.state = self.STATE_DISCONNECTED
		self.tab = ChanWin(self.title)
		self.__sid = None
		self.__sock = None
		self.__waitf = None
		self.msgs = deque()

	def svr_msg(self, msg, tags = []):
		self.tab.msg(msg, tags)

	def sock_send(self, msg):
		self.__sock.send(msg + '\r\n')

	def __connected(self):
		self.state = self.STATE_CONNECTED
		self.emit('status-update')
		self.__waitf = glib.IO_IN
		self.sock_send('NICK scaramanga')

	def __read(self):
		if self.state == self.STATE_CONNECTING:
			return
		msg = self.__sock.recv(4096)
		self.svr_msg(msg)
		return

	def __write(self):
		if self.state == self.STATE_CONNECTING:
			ret = self.__sock.getsockopt(SOL_SOCKET, SO_ERROR)
			if ret:
				self.svr_msg('*** Connect: %s:%d: %s\n'%(
						self.peer[0],
						self.peer[1],
						strerror(ret)),
						['bold', 'purple'])
				self.__sock = None
				self.state = self.STATE_DISCONNECTED
				return
			self.svr_msg('*** Connected to %s:%d\n'%(
					self.peer[0],
					self.peer[1]),
					['bold', 'purple'])
			self.__connected()
			return
		print 'write'
		raise Exception()
		return

	def __callback(self, fd, flags):
		if flags & (glib.IO_IN|glib.IO_HUP|glib.IO_ERR):
			self.__read()
		if flags & (glib.IO_OUT):
			self.__write()
		if self.__sid is not None:
			glib.source_remove(self.__sid)
		if self.__sock is not None:
			self.__sid = glib.io_add_watch(
				self.__sock.fileno(),
				self.__waitf | glib.IO_HUP | glib.IO_ERR,
				self.__callback)
		return False

	def server(self, hostname, port = 6667):
		if port != 6667:
			self.title = '%s:%d'%(hostname, port)
		else:
			self.title = hostname
		self.state = self.STATE_CONNECTING
		self.emit('status-update')

		ip = gethostbyname(hostname)
		self.__sock = socket(AF_INET, SOCK_STREAM, IPPROTO_TCP)
		self.__sock.setblocking(0)
		try:
			self.peer = (hostname, port)
			self.__sock.connect(self.peer)
		except SockError, e:
			if e.errno == EINPROGRESS:
				self.__waitf = glib.IO_OUT
				self.__callback(-1, 0)
			else:
				self.svr_msg('*** Connect: %s:%d: %s\n'%(
						self.peer[0],
						self.peer[1],
						e.strerror),
						['bold', 'purple'])
				self.__sock = None
			return

		self.__connected()

	def __del__(self):
		print 'destroyed'

gobject.type_register(ServerTab)
gobject.signal_new('status-update', ServerTab,
			gobject.SIGNAL_RUN_FIRST,
			gobject.TYPE_NONE, ())
