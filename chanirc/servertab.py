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
		IrcServer.__init__(self, ['scaramanga', 'scara', 'scara-tzu'])
		self.title = '<None>'
		self.state = self.STATE_DISCONNECTED
		self.tab = ChanWin(self, userlist = False)
		self.__sid = None
		self.__waitf = None
		self.channels = {}

		def server(win, chan, args):
			self.server(args)

		def part(win, chan, args):
			if chan is None:
				chan = args
			if self.state != self.STATE_CONNECTED:
				return
			self.part(chan)

		def join(win, chan, args):
			if not len(args):
				win.msg('Must specify a channel to join\n')
				return
			if self.state != self.STATE_CONNECTED:
				return
			self.join(args)

		def topic(win, chan, args):
			if chan is None:
				arr = args.split(None, 1)
				if len(arr) > 1:
					(chan, msg) = arr
				else:
					(chan, msg) = arr[0], None
			if not len(chan):
				win.msg('Must specify a channel for topic\n')
				return
			self.topic(chan, args)

		def privmsg(win, chan, args):
			tab = self.get_chan(chan)
			if tab is None:
				return
			tab.msg('<%s> '%self.nick, ['dark green'])
			tab.msg(args + '\n')
			self.privmsg(chan, args)

		def action(win, chan, args):
			tab = self.get_chan(chan)
			if tab is None:
				return
			tab.msg('*** %s %s\n'%(self.nick, args), ['dark green'])
			self.action(chan, args)

		def nick(win, chan, args):
			self.set_nick(args)

		def reconnect(win, chan, args):
			if self.sock is None:
				return
			self.server(self.sock.peer[0], self.sock.peer[1])

		def disconnect(win, chan, args):
			self.disconnect()

		self.__cmd = {
			'server': server,
			'topic': topic,
			'part': part,
			'join': join,
			'reconnect': reconnect,
			'disconnect': disconnect,
			'j': join,
			'privmsg': privmsg,
			'nick': nick,
			'me': action,
		}

	def get_chan(self, chan):
		if self.state != self.STATE_CONNECTED:
			return None
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

	def chan_msg(self, chan, msg, tags = []):
		tab = self.get_chan(chan)
		if tab is None:
			return
		tab.msg(msg + '\n', tags)

	def nick_msg(self, nick, msg, tags = []):
		for tab in self.channels.values():
			if nick not in tab:
				continue
			tab.msg(msg + '\n', tags)

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

	def _set_topic(self, user, chan, topic):
		tab = self.get_chan(chan)
		if tab is None:
			return
		tab.topic.set_text(topic)
		if user is None:
			tab.msg('topic in %s is %s\n'%(chan, topic),
						['bold', 'purple'])
		else:
			tab.msg('%s set topic to: %s\n'%(user.nick, topic),
						['bold', 'purple'])

	def _join(self, chan, user):
		tab = self.get_chan(chan)
		if tab is None:
			return
		tab.msg('%s (%s@%s) joined %s\n'%(user.nick,
						user.user,
						user.host,
						chan),
						['bold', 'purple'])
		tab.add_nick(user.nick)

	def _part(self, chan, user):
		tab = self.get_chan(chan)
		if tab is None:
			return
		tab.msg('%s left %s\n'%(user, chan))
		tab.remove_nick(user.nick)
		if user.nick == self.nick:
			self.emit('remove-channel', tab)

	def _name_list(self, chan, name):
		tab = self.get_chan(chan)
		if tab is None:
			return
		tab.add_nick(name)

	def _privmsg(self, user, chan, msg):
		tab = self.get_chan(chan)
		if tab is None:
			return
		tab.msg('<%s> '%user.nick, ['dark blue'])
		tab.msg(msg + '\n')

	def _action(self, user, chan, msg):
		tab = self.get_chan(chan)
		if tab is None:
			return
		tab.msg('*** %s %s\n'%(user.nick, msg), ['dark bluet'])

	def _quit(self, user, msg):
		for x in self.channels.values():
			x.remove_nick(user.nick)
		self.nick_msg('*** %s QUIT (%s)\n'%(user, msg),
			['purple', 'bold'])

	def _nick_changed(self, user, nick, me):
		if me:
			# changed my nick
			self.nick_msg(user.nick,
				'*** you (%s) are now known as %s'%(user,
								nick),
				['purple'])
		else:
			self.nick_msg(user.nick,
				'*** %s is now known as %s'%(user, nick),
				['purple'])
		for tab in self.channels.values():
			if user.nick not in tab:
				continue
			tab.rename_nick(user.nick, nick)

	def server(self, hostname, port = 6667):
		if port != 6667:
			self.title = '%s:%d'%(hostname, port)
		else:
			self.title = hostname

		self.disconnect()
		IrcServer.server(self, hostname, port)

	def disconnect(self):
		for x in self.channels.values():
			self.emit('remove-channel', x)
		self.channels = {}
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
			cb(win, chan, args)
