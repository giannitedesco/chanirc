import glib, gobject, gtk
from chanwin import ChanWin
from irc import IrcServer

class IrcChan(ChanWin):
	def __init__(self, servertab, name):
		ChanWin.__init__(self, servertab)
		self.chan = name
		self.__nicks = {}
	def __str__(self):
		return self.chan
	def __repr__(self):
		return 'IrcChan(%s)'%(self.chan)
	def add_nick(self, nick):
		self.__nicks[nick] = None
	def remove_nick(self, nick):
		if self.__nicks.has_key(nick):
			del self.__nicks[nick]
	def __iter__(self):
		return iter(self.__nicks)

class ServerTab(IrcServer):
	__gsignals__ = {
		'connected': (gobject.SIGNAL_RUN_LAST,
			gobject.TYPE_NONE, ()),
		'connecting': (gobject.SIGNAL_RUN_LAST,
			gobject.TYPE_NONE, ()),
		'disconnected': (gobject.SIGNAL_RUN_LAST,
			gobject.TYPE_NONE, ()),
		'add-channel': (gobject.SIGNAL_RUN_LAST,
			gobject.TYPE_NONE, (gobject.TYPE_OBJECT, )),
		'remove-channel': (gobject.SIGNAL_RUN_LAST,
			gobject.TYPE_NONE, (gobject.TYPE_OBJECT, )),
	}

	STATE_DISCONNECTED = 0,
	STATE_CONNECTING = 1,
	STATE_CONNECTED = 2,

	def __init__(self):
		#self.__gobject_init__()
		IrcServer.__init__(self)
		self.title = '<None>'
		self.state = self.STATE_DISCONNECTED
		self.tab = ChanWin(self, userlist = False)
		self.__sid = None
		self.__waitf = None
		self.channels = {}

		def server(chan, args):
			self.server(args)

		def privmsg(chan, args):
			tab = self.get_chan(chan)
			tab.msg('<%s> %s'%(self.nick, args))
			self.privmsg(chan, args)

		self.__cmd = {
			'server': server,
			'privmsg': privmsg,
		}

	def get_chan(self, chan):
		if chan in self.channels:
			return self.channels[chan]
		else:
			ret = IrcChan(self, chan)
			self.channels[chan] = ret
			self.emit('add-channel', ret)
			return ret

	def server_msg(self, msg):
		self.tab.msg(msg)

	def info_msg(self, msg):
		self.tab.msg(msg, ['bold', 'purple'])

	def chan_msg(self, chan, msg):
		tab = self.get_chan(chan)
		tab.msg(msg)

	def _connected(self):
		self.state = self.STATE_CONNECTED
		self.emit('connected')
		self.join('#webdev')

	def _connecting(self):
		self.state = self.STATE_CONNECTING
		self.emit('connecting')

	def _disconnected(self):
		self.state = self.STATE_DISCONNECTED
		self.info_msg('Disconnected.')
		self.emit('disconnected')

	def _set_topic(self, chan, topic):
		tab = self.get_chan(chan)
		tab.topic.set_text(topic)
		tab.msg('topic in %s is %s'%(chan, topic),
						['bold', 'purple'])

	def _join(self, chan, user):
		tab = self.get_chan(chan)
		tab.msg('%s (%s@%s) joined %s'%(user.nick,
						user.user,
						user.host,
						chan),
						['bold', 'purple'])

	def _part(self, chan, user):
		tab = self.get_chan(chan)
		tab.msg('%s left %s'%(user, chan))

	def _name_list(self, chan, name):
		pass

	def _privmsg(self, user, chan, msg):
		tab = self.get_chan(chan)
		tab.msg('<%s> %s'%(user.nick, msg))

	def _quit(self, user, chan, msg):
		tab = self.get_chan(chan)
		tab.msg('*** %s QUIT (%s)'%(user, msg), ['purple', 'bold'])

	def server(self, hostname, port = 6667):
		if port != 6667:
			self.title = '%s:%d'%(hostname, port)
		else:
			self.title = hostname

		self.disconnect()
		IrcServer.server(self, hostname, port, 'scara')

	def disconnect(self):
		for x in self.channels.values():
			self.emit('remove-channel', x)
		IrcServer.disconnect(self)

	def send_chat(self, win, s):
		if isinstance(win, IrcChan):
			chan = win.chan
		else:
			chan = None

		if s[0] == '/':
			arr = s[1:].split(None, 1)
			if len(arr) < 2:
				arr.append(None)
			(cmd, args) = arr
		else:
			(cmd, args) = ('privmsg', s)

		cb = self.__cmd.get(cmd.lower(), None)
		if cb is None:
			print 'unknown cmd:', cmd
			return
		else:
			cb(chan, args)
