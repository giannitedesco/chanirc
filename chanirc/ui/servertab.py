import glib, gobject, gtk
from socket import gethostbyname, socket, AF_INET, SOCK_STREAM, IPPROTO_TCP, \
			SOL_SOCKET, SO_ERROR, error as SockError
from errno import EINPROGRESS, EAGAIN
from os import strerror
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

	def __connected(self):
		self.__state = self.STATE_CONNECTED
		self.emit('status-update')

	def __read(self):
		if self.state == self.STATE_CONNECTING:
			return
		return

	def __write(self):
		if self.state == self.STATE_CONNECTING:
			ret = self.__sock.getsockopt(SOL_SOCKET, SO_ERROR)
			if ret:
				self.__sock = None
				print strerror(ret)
				self.state = self.STATE_DISCONNECTED
				return
			self.__connected()
			return
		return

	def __callback(self, fd, flags):
		if flags & (glib.IO_IN|glib.IO_HUP|glib.IO_ERR):
			self.__read()
		if flags & (glib.IO_OUT):
			self.__write()
		return False

	def setwait(self, recv = False, send = False):
		if self.__sid is not None:
			glib.source_remove(self.__sid)
		assert(recv or send)
		f = glib.IO_HUP | glib.IO_ERR
		if recv:
			f |= glib.IO_IN
		if send:
			f |= glib.IO_OUT
		self.__sid = glib.io_add_watch(self.__sock.fileno(), f,
						self.__callback)

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
			self.__sock.connect((hostname, port))
		except SockError, e:
			if e.errno == EINPROGRESS:
				self.setwait(send = True)
			else:
				print e.strerror
				self.__sock = None
			return

		self.__connected()

	def __del__(self):
		print 'destroyed'

gobject.type_register(ServerTab)
gobject.signal_new('status-update', ServerTab,
			gobject.SIGNAL_RUN_FIRST,
			gobject.TYPE_NONE, ())
