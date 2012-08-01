import gobject, gtk

class IrcEntry(gtk.Entry):
	def send(self, s):
		self.emit('send', s)

	def __activate(self, _):
		s = self.get_text()
		self.set_text('')
		if len(s):
			self.send(s)

	def __init__(self):
		gtk.Entry.__init__(self)
		self.connect('activate', self.__activate)

gobject.type_register(IrcEntry)
gobject.signal_new('send', IrcEntry,
			gobject.SIGNAL_RUN_FIRST,
			gobject.TYPE_NONE, (gobject.TYPE_STRING,))
