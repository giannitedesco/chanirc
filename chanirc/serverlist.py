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
		self.cur_svr = None
		self.__tab = None

	def __select_iter(self, i):
		self.__sel.select_iter(i)
		self.__tab = self.__store.get_value(i, self.COL_TAB)
		self.emit('selection-changed')

	def get_selection(self):
		return self.__tab

	def add_server(self, svr):
		obj = ('gtk-stop', svr.title, None, svr.tab)
		itr = self.__store.append(None, obj)
		self.__map[svr] = itr
		self.__select_iter(itr)
		self.cur_svr = svr

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

gobject.type_register(ServerList)
gobject.signal_new('selection-changed', ServerList,
			gobject.SIGNAL_RUN_FIRST,
			gobject.TYPE_NONE, ())
