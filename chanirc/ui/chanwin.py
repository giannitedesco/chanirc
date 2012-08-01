import gobject, gtk

class ChanWin(gtk.HPaned):
	def __init__(self, title, userlist = False):
		gtk.HPaned.__init__(self)

		self.topic = gtk.Entry()
		self.text = gtk.TextView()

		self.status = gtk.Label('32 ops, 38 total')
		self.usrlist = gtk.TreeView()

		chan = gtk.VBox()
		chan.pack_start(self.topic, False, False)
		chan.pack_start(self.text, True, True)
		self.pack1(chan, True, True)

		if userlist:
			u = gtk.VBox()
			u.pack_start(self.status, False, False)
			u.pack_start(self.usrlist, True, True)
			self.pack2(u, False, False)


gobject.signal_new('title-changed', ChanWin,
			gobject.SIGNAL_RUN_FIRST,
			gobject.TYPE_NONE, (gobject.TYPE_STRING,))
