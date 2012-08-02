from tcpsock import TCPSock

class LineSock(TCPSock):
	def __init__(self):
		TCPSock.__init__(self)
		self.__buf = ''

	def _read(self):
		try:
			self.__buf += self._sock.recv(4096)
		except SockError, e:
			if e.errno == EINPROGRESS or e.errno == EAGAIN:
				return
			else:
				self.emit('error', 'recv', e.strerror)
				return
		except:
			raise

		while '\n' in self.__buf:
			(msg, rest) = self.__buf.split('\n', 1)
			msg = msg.rstrip('\r')
			self.emit('data-in', msg)
			self.__buf = rest
