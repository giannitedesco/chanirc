import glib, gobject, gtk
from chanwin import ChanWin
from irc import IRC

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
		self.conn = None
		self.__waitf = None

	def server_msg(self, msg):
		self.tab.msg(msg, ['purple'])

	def info_msg(self, msg):
		self.tab.msg(msg, ['bold', 'purple'])

	def chan_msg(self, chan, msg):
		self.tab.msg(chan + ':' + msg)

	def __server_msg(self, irc, msg):
		self.server_msg(msg)
	def __info_msg(self, irc, msg):
		self.info_msg(msg)
	def __chan_msg(self, irc, chan, msg):
		self.chan_msg(chan, msg)

	def __connected(self, conn):
		self.state = self.STATE_CONNECTED
		self.emit('status-update')
		conn.join('#chanirc')

	def __disconnected(self, conn):
		self.state = self.STATE_DISCONNECTED
		self.info_msg('Disconnected.')
		self.emit('status-update')

	def server(self, hostname, port = 6667):
		if port != 6667:
			self.title = '%s:%d'%(hostname, port)
		else:
			self.title = hostname
		self.conn = IRC()

		self.conn.connect('connected', self.__connected)
		self.conn.connect('disconnected', self.__disconnected)
		self.conn.connect('info-msg', self.__info_msg)
		self.conn.connect('server-msg', self.__server_msg)
		self.conn.connect('chan-msg', self.__chan_msg)

		self.conn.reconnect(hostname, port, 'scara')
		self.state = self.STATE_CONNECTING
		self.emit('status-update')

	def __del__(self):
		print 'destroyed'

gobject.type_register(ServerTab)
gobject.signal_new('status-update', ServerTab,
			gobject.SIGNAL_RUN_FIRST,
			gobject.TYPE_NONE, ())
