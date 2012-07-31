import gobject, glib, gtk, pango

class ButtonBar(gtk.HBox):
	def __init__(self):
		gtk.HBox.__init__(self)
		self.set_size_request(-1, 32)

class ChanWin(gtk.HPaned):
	def __init__(self):
		gtk.HPaned.__init__(self)

		self.topic = gtk.Entry()
		self.text = gtk.TextView()
		self.entry = gtk.Entry()

		self.status = gtk.Label('32 ops, 38 total')
		self.usrlist = gtk.TreeView()

		u = gtk.VBox()
		u.pack_start(self.status, False, False)
		u.pack_start(self.usrlist, True, True)
		self.add1(u)

		chan = gtk.VBox()
		chan.pack_start(self.topic, False, False)
		chan.pack_start(self.text, True, True)
		chan.pack_start(self.entry, False, False)
		self.add2(chan)

class MainWin(gtk.Window):
	def destroy(self, *_):
		gtk.Window.destroy(self)
		if self.in_main:
			gtk.mainquit()

	def __accel(self, a, cb):
		agr = gtk.AccelGroup()
		(k, m) = gtk.accelerator_parse(a)
		agr.connect_group(k, m, gtk.ACCEL_VISIBLE, cb)
		self.add_accel_group(agr)

	def main(self):
		self.in_main = True
		self.show_all()
		gtk.main()
		self.in_main = False

	def __init__(self):
		gtk.Window.__init__(self, gtk.WINDOW_TOPLEVEL)

		self.in_main = False

		self.set_default_size(640, 480)
		self.set_title('chanirc')

		self.connect('destroy', self.destroy)

		self.__accel('<Control>Q', self.destroy)
		self.__accel('<Control>W', self.destroy)

		vb = gtk.VBox()
		self.add(vb)

		self.buttonbar = ButtonBar()
		vb.pack_start(self.buttonbar, False, False)
		vb.pack_start(ChanWin(), True, True)
