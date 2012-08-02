import glib, gobject, gtk
from chanwin import ChanWin
from irc import IrcServer

class ServerTab(IrcServer):
	__gsignals__ = {
		'connected': (gobject.SIGNAL_RUN_LAST,
			gobject.TYPE_NONE, ()),
		'connecting': (gobject.SIGNAL_RUN_LAST,
			gobject.TYPE_NONE, ()),
		'disconnected': (gobject.SIGNAL_RUN_LAST,
			gobject.TYPE_NONE, ()),
	}

	STATE_DISCONNECTED = 0,
	STATE_CONNECTING = 1,
	STATE_CONNECTED = 2,

	def __init__(self):
		#self.__gobject_init__()
		IrcServer.__init__(self)
		self.title = '<None>'
		self.state = self.STATE_DISCONNECTED
		self.tab = ChanWin(self.title)
		self.__sid = None
		self.__waitf = None

	def server_msg(self, msg):
		self.tab.msg(msg, ['purple'])

	def info_msg(self, msg):
		self.tab.msg(msg, ['bold', 'purple'])

	def chan_msg(self, chan, msg):
		self.tab.msg(chan + ':' + msg)

	def _connected(self):
		self.state = self.STATE_CONNECTED
		self.emit('connected')
		self.join('#chanirc')

	def _connecting(self):
		self.state = self.STATE_CONNECTING
		self.emit('connecting')

	def _disconnected(self):
		self.state = self.STATE_DISCONNECTED
		self.info_msg('Disconnected.')
		self.emit('disconnected')

	def server(self, hostname, port = 6667):
		if port != 6667:
			self.title = '%s:%d'%(hostname, port)
		else:
			self.title = hostname

		IrcServer.server(self, hostname, port, 'scara')

	def __del__(self):
		print 'destroyed'
