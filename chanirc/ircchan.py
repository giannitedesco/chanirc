from chanwin import ChanWin

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
		self.usrlist.append(nick)
	def remove_nick(self, nick):
		if self.__nicks.has_key(nick):
			del self.__nicks[nick]
			self.usrlist.delete(nick)
	def __iter__(self):
		return iter(self.__nicks)
