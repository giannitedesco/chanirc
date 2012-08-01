import gobject
from tcpsock import TCPSock

class IRC(gobject.GObject):
	__gsignals__ = {
		'connected': (gobject.SIGNAL_RUN_LAST,
			gobject.TYPE_NONE, ()),
		'disconnected': (gobject.SIGNAL_RUN_LAST,
			gobject.TYPE_NONE, ()),
		'info-msg': (gobject.SIGNAL_RUN_LAST,
			gobject.TYPE_NONE,
			(gobject.TYPE_STRING, )),
		'server-msg': (gobject.SIGNAL_RUN_LAST,
			gobject.TYPE_NONE,
			(gobject.TYPE_STRING, )),
		'chan-msg': (gobject.SIGNAL_RUN_LAST,
			gobject.TYPE_NONE,
			(gobject.TYPE_STRING, gobject.TYPE_STRING)),
	}

	def __001(self, prefix, args, extra):
		"connected"
		self.server_msg(extra)
		return True

	def __372(self, prefix, args, extra):
		"MOTD"
		self.server_msg(extra)
		return True

	def __376(self, prefix, args, extra):
		"end of MOTD"
		self.server_msg(extra)
		return True

	def __433(self, prefix, args, extra):
		"Nick already taken"
		self.info_msg('Nick already taken: '%extra)
		return True

	def __ping(self, prefix, args, extra):
		print 'PING', args
		self.send('PONG :%s'%extra)
		return True

	def __notice(self, prefix, args, extra):
		if extra is not None:
			self.server_msg('NOTICE %s'%(args))
		else:
			self.server_msg('NOTICE %s (%s)'%(args, extra))
		return True

	def connected(self):
		self.emit('connected')

	def disconnected(self):
		self.emit('disconnected')
		self.sock = None

	def info_msg(self, msg):
		self.emit('info-msg', msg)

	def server_msg(self, msg):
		self.emit('server-msg', msg)

	def chan_msg(self, chan, msg):
		self.emit('chan-msg', msg)

	def __sockerr(self, sock, op, msg):
		self.info_msg('*** %s: %s:%d: %s'%(op,
				sock.peer[0],
				sock.peer[1],
				msg))
		self.disconnected()

	def send(self, cmd):
		self.sock.send(cmd + '\r\n')

	def __connected(self, sock):
		self.info_msg('*** Connected: %s:%d'%(
				sock.peer[0],
				sock.peer[1]))
		self.send('USER %s * * :Description'%self.nick)
		self.send('NICK %s'%self.nick)

	def __disconnected(self, sock):
		self.info_msg('*** Disonnected: %s:%d'%(
				sock.peer[0],
				sock.peer[1]))
		self.disconnected()

	def __dispatch(self, prefix, cmd, args, extra):
		if isinstance(cmd, int):
			cb = self.__resp.get(cmd, None)
		else:
			cb = self.__cmds.get(cmd, None)

		if cb is None:
			return False

		return cb(prefix, args, extra)

	def __cmd(self, prefix, msg):
		arr = msg.split(None, 1)
		cmd = arr[0]
		if len(arr) > 1:
			args = arr[1]
			arr = args.split(':', 1)
			if len(arr) > 1:
				args = arr[0]
				extra = arr[1]
			else:
				extra = None
		else:
			args = None
			extra = None

		if cmd.isdigit():
			cmd = int(cmd)

		return self.__dispatch(prefix, cmd, args, extra)

	def __line(self, msg):
		if len(msg) == 0:
			return

		if msg[0] == ':':
			arr = msg.split(None, 1)
			prefix = arr[0][1:]
			if len(msg) > 1:
				cmd = arr[1]
			else:
				cmd = None
		else:
			prefix = None
			cmd = msg

		if cmd is None:
			return

		if not self.__cmd(prefix, cmd):
			self.info_msg('UNKNOWN COMMAND: %s'%msg)

	def __sock_in(self, sock, msg):
		map(self.__line,
			map(lambda x:x.rstrip('\r\n'), msg.split('\n')))

	def __init__(self):
		gobject.GObject.__init__(self)
		self.nick = None
		self.sock = TCPSock() 
		self.__resp = {
			001: self.__001,
			372: self.__372,
			376: self.__376,
			433: self.__433,
		}

		self.__cmds = {
			'PING': self.__ping,
			'NOTICE': self.__notice,
		}


	def reconnect(self, host, port, nick):
		self.nick = nick
		self.sock.connect('data-in', self.__sock_in)
		self.sock.connect('connected', self.__connected)
		self.sock.connect('disconnected', self.__disconnected)
		self.sock.connect('error', self.__sockerr)
		self.sock.connect_to(host, port)
