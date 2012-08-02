import gobject
from linesock import LineSock

class IrcServer(gobject.GObject):
	def join(self, chan):
		self.send('JOIN %s'%chan)

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

	def __init__(self):
		gobject.GObject.__init__(self)
		self.nick = None
		self.sock = LineSock() 

		def r001(prefix, args, extra):
			"connected"
			self.server_msg(extra)
			return True

		def r353(prefix, args, extra):
			"Names list"
			print 'names', prefix, args, extra
			return True

		def r366(prefix, args, extra):
			"End of names list"
			print 'end of names', prefix, args, extra
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
			self.info_msg('Nick already taken: '%extra)
			return True

		self.resp_tbl = {
			001: r001,
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
			print 'PING', args
			self.send('PONG :%s'%extra)
			return True

		def notice(prefix, args, extra):
			if extra is not None:
				self.server_msg('NOTICE %s'%(args))
			else:
				self.server_msg('NOTICE %s (%s)'%(args, extra))
			return True

		def topic(prefix, args, extra):
			print 'topic in', args, 'is', extra
			return True

		def join(prefix, args, extra):
			if args is None:
				args = extra
			print prefix, 'joined', args
			return True

		self.__cmds = {
			'PING': ping,
			'NOTICE': notice,
			'JOIN': join,
			'TOPIC': topic,
		}

	def send(self, cmd):
		self.sock.send(cmd + '\r\n')

	def server(self, host, port, nick):
		def sockerr(sock, op, msg):
			self.info_msg('*** %s: %s:%d: %s'%(op,
					sock.peer[0],
					sock.peer[1],
					msg))
			self._disconnected()

		def connected(sock):
			self.info_msg('*** Connected: %s:%d'%(
					sock.peer[0],
					sock.peer[1]))
			self.send('USER %s * * :Description'%self.nick)
			self.send('NICK %s'%self.nick)

		def disconnected(sock):
			self.info_msg('*** Disonnected: %s:%d'%(
					sock.peer[0],
					sock.peer[1]))
			self._disconnected()

		def sock_in(sock, msg):
			if len(msg) == 0:
				return

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


		self.nick = nick
		self.sock.connect('data-in', sock_in)
		self.sock.connect('connected', connected)
		self.sock.connect('disconnected', disconnected)
		self.sock.connect('error', sockerr)
		self.sock.connect_to(host, port)
		self._connecting()
