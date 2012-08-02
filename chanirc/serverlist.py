import gobject, gtk

class ServerList(gtk.TreeView):
	COL_ICON = 0
	COL_TEXT = 1
	COL_SEARCH = 2
	COL_TAB = 3
	def __init__(self):
		#gtk.gdk.Pixbuf,
		self.__store = gtk.TreeStore(gobject.TYPE_STRING,
						gobject.TYPE_STRING,
						gobject.TYPE_STRING,
						gobject.TYPE_OBJECT)
		gtk.TreeView.__init__(self, self.__store)
		self.__sel = gtk.TreeView.get_selection(self)

		self.set_headers_visible(False)
		self.set_headers_clickable(False)
		self.set_enable_search(True)
		self.set_search_column(self.COL_SEARCH)

		r = gtk.CellRendererText()
		i = gtk.CellRendererPixbuf()
		col = gtk.TreeViewColumn('Servers / Channels')
		col.pack_start(i, False)
		#col.add_attribute(i, 'pixbuf', self.COL_ICON)
		col.add_attribute(i, 'stock-id', self.COL_ICON)
		col.pack_start(r, True)
		col.add_attribute(r, 'text', self.COL_TEXT)
		col.set_resizable(True)
		self.append_column(col)
		self.__map = {}
		self.cur = None

		self.__sel.connect('changed', self.__sel_change)

	def __sel_change(self, sel):
		(model, i) = sel.get_selected()
		self.cur = self.__store.get_value(i, self.COL_TAB)
		self.emit('selection-changed')

	def __select_iter(self, i):
		self.__sel.select_iter(i)

	def add_chan(self, svr, chan):
		ch = ('gtk-edit', chan.chan, None, chan)
		itr = self.__map[svr]
		chanitr = self.__store.append(itr, ch)

		self.__map[chan] = chanitr

		self.expand_to_path(self.__store.get_path(chanitr))
		self.__select_iter(chanitr)

	def remove_chan(self, svr, chan):
		chanitr = self.__map[chan]
		itr = self.__map[svr]
		self.__select_iter(itr)
		self.__store.remove(chanitr)
		del self.__map[chan]

	def add_server(self, svr):
		obj = ('gtk-stop', svr.title, None, svr.tab)
		itr = self.__store.append(None, obj)
		self.__map[svr] = itr
		self.__select_iter(itr)

		def connected(svr):
			self.__store.set_value(itr,
					self.COL_TEXT, svr.title)
			self.__store.set_value(itr,
					self.COL_ICON, 'gtk-home')
		def connecting(svr):
			self.__store.set_value(itr,
					self.COL_TEXT, svr.title)
			self.__store.set_value(itr,
					self.COL_ICON, 'gtk-go-forward')
		def disconnected(svr):
			self.__store.set_value(itr,
					self.COL_TEXT, svr.title)
			self.__store.set_value(itr,
					self.COL_ICON, 'gtk-stop')

		svr.connect('connected', connected)
		svr.connect('connecting', connecting)
		svr.connect('disconnected', disconnected)
		svr.connect('add-channel', self.add_chan)
		svr.connect('remove-channel', self.remove_chan)

gobject.type_register(ServerList)
gobject.signal_new('selection-changed', ServerList,
			gobject.SIGNAL_RUN_FIRST,
			gobject.TYPE_NONE, ())
