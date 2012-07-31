import gobject, gtk

class ServerList(gtk.TreeView):
	COL_ICON = 0
	COL_TEXT = 1
	COL_SEARCH = 2
	def __init__(self):
		#gtk.gdk.Pixbuf,
		self.__store = gtk.TreeStore(gobject.TYPE_STRING,
						gobject.TYPE_STRING,
						gobject.TYPE_STRING)
		gtk.TreeView.__init__(self, self.__store)

		self.set_headers_visible(True)
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

	def __svr_update(self, svr):
		self.__store.set_value(self.__map[svr],
					self.COL_TEXT, svr.title)

	def add_server(self, svr):
		i = self.__store.append(None, ('gtk-home', svr.title, None))
		self.__map[svr] = i
		svr.connect('status-update', self.__svr_update)
		self.cur = svr
		return
