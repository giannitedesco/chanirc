import glib, gobject, gtk
from ircchan import IrcChan
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
			tab.msg('<%s> '%self.nick, ['dark green'])
			tab.msg(args + '\n')
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
		self.tab.msg(msg + '\n')

	def info_msg(self, msg):
		self.tab.msg(msg + '\n', ['bold', 'purple'])

	def chan_msg(self, chan, msg):
		tab = self.get_chan(chan)
		tab.msg(msg + '\n')

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
		tab.msg('topic in %s is %s\n'%(chan, topic),
						['bold', 'purple'])

	def _join(self, chan, user):
		tab = self.get_chan(chan)
		tab.msg('%s (%s@%s) joined %s\n'%(user.nick,
						user.user,
						user.host,
						chan),
						['bold', 'purple'])

	def _part(self, chan, user):
		tab = self.get_chan(chan)
		tab.msg('%s left %s\n'%(user, chan))
		tab.remove_nick(name)

	def _name_list(self, chan, name):
		tab = self.get_chan(chan)
		tab.add_nick(name)

	def _privmsg(self, user, chan, msg):
		tab = self.get_chan(chan)
		tab.msg('<%s> '%user.nick, ['dark blue'])
		tab.msg(msg + '\n')

	def _quit(self, user, msg):
		for x in self.channels.values():
			x.remove_nick(user.nick)
			x.msg('*** %s QUIT (%s)\n'%(user, msg),
				['purple', 'bold'])

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
