import gobject, gtk

class UserList(gtk.TreeView):
	def __init__(self):
		self.store = gtk.ListStore(gobject.TYPE_STRING)
		gtk.TreeView.__init__(self, self.store)

		self.set_headers_visible(False)
		self.set_headers_clickable(False)
		self.set_enable_search(False)
		self.set_search_column(0)
		self.store.set_sort_column_id(0, gtk.SORT_ASCENDING)

		r = gtk.CellRendererText()
		col = gtk.TreeViewColumn('Users', None)
		col.pack_start(r, True)
		col.add_attribute(r, 'text', 0)
		col.set_sort_column_id(0)
		col.set_resizable(True)
		self.append_column(col)
		self.set_size_request(120, -1)

		self.m = {}

	def append(self, nick):
		itr = self.m.get(nick, None)
		if itr is None:
			itr = self.store.append((nick, ))
			self.m[nick] = itr

	def delete(self, nick):
		itr = self.m.get(nick, None)
		if itr is None:
			return
		self.store.remove(itr)
		del self.m[nick]
