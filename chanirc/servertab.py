import glib, gobject, gtk
from chanwin import ChanWin
from tcpsock import TCPSock

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

	def svr_msg(self, msg, tags = []):
		self.tab.msg(msg, tags)

	def sock_send(self, msg):
		self.__sock.send(msg + '\r\n')

	def __sockerr(self, sock, op, msg):
		self.svr_msg('*** %s: %s:%d: %s\n'%(op,
				sock.peer[0],
				sock.peer[1],
				msg),
				['bold', 'purple'])
		self.state = self.STATE_DISCONNECTED
		self.__sock = None
		self.emit('status-update')

	def __connected(self, sock):
		self.svr_msg('*** Connected: %s:%d\n'%(
				sock.peer[0],
				sock.peer[1]),
				['bold', 'purple'])
		self.state = self.STATE_CONNECTED
		self.emit('status-update')
		sock.send('NICK scaramanga\r\n')

	def __disconnected(self, sock):
		self.svr_msg('*** Disonnected: %s:%d\n'%(
				sock.peer[0],
				sock.peer[1]),
				['bold', 'purple'])
		self.state = self.STATE_DISCONNECTED
		self.emit('status-update')

	def __sock_in(self, sock, msg):
		self.svr_msg(msg)

	def server(self, hostname, port = 6667):
		if port != 6667:
			self.title = '%s:%d'%(hostname, port)
		else:
			self.title = hostname
		self.__sock = TCPSock()
		self.__sock.connect('data-in', self.__sock_in)
		self.__sock.connect('connected', self.__connected)
		self.__sock.connect('disconnected', self.__disconnected)
		self.__sock.connect('error', self.__sockerr)

		self.__sock.connect_to(hostname, port)
		self.state = self.STATE_CONNECTING
		self.emit('status-update')

	def __del__(self):
		print 'destroyed'

gobject.type_register(ServerTab)
gobject.signal_new('status-update', ServerTab,
			gobject.SIGNAL_RUN_FIRST,
			gobject.TYPE_NONE, ())
