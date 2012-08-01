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

	def __svr_update(self, svr):
		self.__store.set_value(self.__map[svr],
					self.COL_TEXT, svr.title)
		if svr.state == svr.STATE_DISCONNECTED:
			self.__store.set_value(self.__map[svr],
					self.COL_ICON, 'gtk-stop')
		elif svr.state == svr.STATE_CONNECTING:
			self.__store.set_value(self.__map[svr],
					self.COL_ICON, 'gtk-go-forward')
		elif svr.state == svr.STATE_CONNECTED:
			self.__store.set_value(self.__map[svr],
					self.COL_ICON, 'gtk-home')


	def __select_iter(self, i):
		self.__sel.select_iter(i)
		self.__tab = self.__store.get_value(i, self.COL_TAB)
		self.emit('selection-changed')

	def get_selection(self):
		return self.__tab

	def add_server(self, svr):
		obj = ('gtk-stop', svr.title, None, svr.tab)
		i = self.__store.append(None, obj)
		self.__map[svr] = i
		self.__select_iter(i)
		svr.connect('status-update', self.__svr_update)
		self.cur_svr = svr

gobject.type_register(ServerList)
gobject.signal_new('selection-changed', ServerList,
			gobject.SIGNAL_RUN_FIRST,
			gobject.TYPE_NONE, ())
