import gobject
from linesock import LineSock
from collections import deque

def begins_with(s, prefix):
	if len(s) < len(prefix):
		return False
	return s[:len(prefix)] == prefix
def ends_with(s, suffix):
	if len(s) < len(suffix):
		return False
	return s[-len(suffix):] == suffix

class IrcUser:
	def __init__(self, s):
		arr = s.split('!', 1)
		self.nick = arr[0]
		if len(arr) > 1:
			arr = arr[1].split('@', 1)
			self.user = arr[0]
			if len(arr) > 1:
				self.host = arr[1]
			else:
				self.host = ''
		else:
			self.user = ''
			self.host = ''
	def __str__(self):
		return '%s!%s@%s'%(self.nick, self.user, self.host)
	def __repr__(self):
		return 'IrcUser(%s!%s@%s)'%(self.nick, self.user, self.host)

class NickList:
	def __init__(self, nicks):
		self.__nicks = deque(nicks)
		self.reset()
	def reset(self):
		self.__next = deque(self.__nicks)
	def get(self):
		try:
			return self.__next.popleft()
		except IndexError:
			return None

class IrcServer(gobject.GObject):
	# to be overriddem
	def _connecting(self):
		pass
	def _connected(self):
		pass
	def _disconnected(self):
		pass
	def _set_topic(self, user, chan, topic):
		pass
	def _join(self, chan, user):
		pass
	def _part(self, chan, user):
		pass
	def _name_list(self, chan, name):
		pass
	def _privmsg(self, user, chan, msg):
		pass
	def _action(self, user, chan, msg):
		pass
	def _quit(self, chan, msg):
		pass
	def _nick_changed(self, user, nick, me):
		pass

	def __dispatch(self, prefix, cmd, args, extra):
		if len(prefix) == 0:
			prefix = None
		if len(args) == 0:
			args = None
		if len(extra) == 0:
			extra = None
		if isinstance(cmd, int):
			cb = self.resp_tbl.get(cmd, None)
		else:
			cb = self.__cmds.get(cmd, None)

		if cb is None:
			return False

		return cb(prefix, args, extra)

	def __cmd(self, prefix, msg):
		arr = msg.split(None, 1)
		cmd = arr[0].strip()
		if len(arr) > 1:
			args = arr[1].strip()
			arr = args.split(':', 1)
			if len(arr) > 1:
				args = arr[0].strip()
				extra = arr[1].strip()
			else:
				extra = ''
		else:
			args = ''
			extra = ''

		if cmd.isdigit():
			cmd = int(cmd)
		else:
			cmd = cmd.upper()

		return self.__dispatch(prefix, cmd, args, extra)

	def __init__(self, nicks = []): 
		gobject.GObject.__init__(self)
		self.nicklist = NickList(nicks)
		self.nick = None
		self.sock = None

		def r001(prefix, args, extra):
			"connected"
			self.server_msg(extra)
			self.nick = args
			return True

		def r332(prefix, args, extra):
			"Topic"
			arr = args.split(None, 1)
			if len(arr) > 1:
				chan = arr[1]
			else:
				chan = args
			self._set_topic(None, chan, extra)
			return True

		def r353(prefix, args, extra):
			"Names list"
			if '=' in args:
				arr = map(lambda x:x.strip(), args.split('='))
				args = arr[1]
			for x in extra.split():
				self._name_list(args, x)
			return True

		def r366(prefix, args, extra):
			"End of names list"
			return True

		def r371(prefix, args, extra):
			"Info"
			self.server_msg(extra)
			return True

		def r372(prefix, args, extra):
			"Info, cont."
			self.server_msg(extra)
			return True

		def r374(prefix, args, extra):
			"end of INFO"
			self.server_msg(extra)
			return True

		def r375(prefix, args, extra):
			"MOTD"
			self.server_msg(extra)
			return True

		def r376(prefix, args, extra):
			"end of MOTD"
			self.server_msg(extra)
			self._connected()
			return True

		def r433(prefix, args, extra):
			"Nick already taken"
			nxt = self.nicklist.get()
			if nxt is None:
				self.info_msg('Nick already taken: %s'%extra)
			else:
				self.info_msg('Nick already taken: %s, retrying with %s'%(extra, nxt))
				self.set_nick(nxt)
			return True

		self.resp_tbl = {
			001: r001,
			332: r332,
			353: r353,
			366: r366,
			372: r371,
			372: r372,
			374: r374,
			375: r375,
			376: r376,
			433: r433,
		}

		def ping(prefix, args, extra):
			self.send('PONG :%s'%extra)
			return True

		def notice(prefix, args, extra):
			if extra is not None:
				self.server_msg('NOTICE %s'%(args))
			else:
				self.server_msg('NOTICE %s (%s)'%(args, extra))
			return True

		def topic(prefix, args, extra):
			self._set_topic(IrcUser(prefix), args, extra)
			return True

		def join(prefix, args, extra):
			if args is None:
				args = extra
			self._join(args, IrcUser(prefix))
			return True

		def part(prefix, args, extra):
			if args is None:
				args = extra
			self._part(args, IrcUser(prefix))
			return True

		def privmsg(prefix, args, extra):
			if begins_with(extra, '\x01ACTION') and \
					ends_with(extra, '\x01'):
				extra = extra[7:-1].strip()
				self._action(IrcUser(prefix), args, extra)
				return True
			self._privmsg(IrcUser(prefix), args, extra)
			return True

		def quit(prefix, args, extra):
			self._quit(IrcUser(prefix), extra)
			return True

		def nick(prefix, args, extra):
			user = IrcUser(prefix)
			if user.nick == self.nick:
				self.nick = extra
				me = True
			else:
				me = False
			self._nick_changed(user, extra, me)
			return True

		self.__cmds = {
			'PING': ping,
			'NOTICE': notice,
			'JOIN': join,
			'PART': part,
			'TOPIC': topic,
			'PRIVMSG': privmsg,
			'QUIT': quit,
			'NICK': nick,
		}

	def send(self, cmd):
		self.sock.send(cmd + '\r\n')

	def join(self, chan):
		self.send('JOIN %s'%chan)

	def part(self, chan):
		self.send('PART %s'%(chan))

	def topic(self, chan, msg):
		self.send('TOPIC %s :%s'%(chan, msg))

	def privmsg(self, chan, msg):
		self.send('PRIVMSG %s :%s'%(chan, msg))

	def action(self, chan, msg):
		self.send('PRIVMSG %s :\x01ACTION %s\x01'%(chan, msg))

	def set_nick(self, nick):
		self.send('NICK %s'%nick)

	def server(self, host, port):
		def sockerr(sock, op, msg):
			self.info_msg('*** %s: %s:%d: %s'%(op,
					sock.peer[0],
					sock.peer[1],
					msg))
			self.sock = None
			self.nick = None
			self._disconnected()

		def connected(sock):
			self.info_msg('*** Connected: %s:%d'%(
					sock.peer[0],
					sock.peer[1]))

			nick = self.nicklist.get()
			self.send('USER %s * * :chanirc'%nick)
			self.set_nick(nick)

		def disconnected(sock):
			self.info_msg('*** Disonnected: %s:%d'%(
					sock.peer[0],
					sock.peer[1]))
			self.sock = None
			self.nick = None
			self._disconnected()

		def sock_in(sock, msg):
			if len(msg) == 0:
				return
			#print '<<', msg

			if msg[0] == ':':
				arr = msg.split(None, 1)
				prefix = arr[0][1:]
				if len(msg) > 1:
					cmd = arr[1]
				else:
					cmd = ''
			else:
				prefix = ''
				cmd = msg

			if len(cmd) == 0 or not self.__cmd(prefix, cmd):
				self.info_msg(msg)

		self.sock = LineSock() 
		self.nicklist.reset()
		self.sock.connect('data-in', sock_in)
		self.sock.connect('connected', connected)
		self.sock.connect('disconnected', disconnected)
		self.sock.connect('error', sockerr)
		self._connecting()
		self.sock.connect_to(host, port)

	def disconnect(self):
		if self.sock is not None:
			self.sock.close()
		self.sock = None
		self.nick = None
		self._disconnected()
