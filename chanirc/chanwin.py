import gobject, gtk, pango

class ChanWin(gtk.HPaned):
	def __setup_tags(self, buf):
		tag = buf.create_tag('bold')
		tag.set_property('weight', pango.WEIGHT_BOLD)

		for x in ['red', 'blue', 'green',
				'cyan', 'magenta', 'yellow',
				'purple', 'black']:
			tag = buf.create_tag(x)
			tag.set_property('foreground', x)
			tag.set_property('foreground-set', True)

	def __init__(self, title, userlist = False):
		gtk.HPaned.__init__(self)

		self.topic = gtk.Entry()

		self.text = gtk.TextView()
		self.text.set_border_window_size(gtk.TEXT_WINDOW_LEFT, 8)
		self.text.set_editable(False)
		self.text.set_cursor_visible(False)
		self.text.set_wrap_mode(gtk.WRAP_WORD)
		self.__setup_tags(self.text.get_buffer())
		scr = gtk.ScrolledWindow()
		scr.set_policy(gtk.POLICY_NEVER, gtk.POLICY_AUTOMATIC)
		scr.add(self.text)

		self.status = gtk.Label('32 ops, 38 total')
		self.usrlist = gtk.TreeView()

		chan = gtk.VBox()
		chan.pack_start(self.topic, False, False)
		chan.pack_start(scr, True, True)
		self.pack1(chan, True, True)

		if userlist:
			u = gtk.VBox()
			u.pack_start(self.status, False, False)
			u.pack_start(self.usrlist, True, True)
			self.pack2(u, False, False)

	def msg(self, msg, tags = []):
		buf = self.text.get_buffer()
		i = buf.get_iter_at_offset(buf.get_char_count())
		buf.place_cursor(i)
		buf.insert_with_tags_by_name(i, msg + '\n', *tags)
		i = buf.get_iter_at_offset(buf.get_char_count())
		buf.place_cursor(i)
		self.text.scroll_to_iter(i, 0.0)
		


gobject.signal_new('title-changed', ChanWin,
			gobject.SIGNAL_RUN_FIRST,
			gobject.TYPE_NONE, (gobject.TYPE_STRING,))
