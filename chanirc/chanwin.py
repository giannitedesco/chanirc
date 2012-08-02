import gobject, gtk, pango
from webthread import WebPool

class ChanWin(gtk.HPaned):
	def __setup_tags(self, buf):
		tag = buf.create_tag('font')
		tag.set_property('font', 'Lucida Console 8')

		tag = buf.create_tag('bold')
		tag.set_property('weight', pango.WEIGHT_BOLD)

		for x in ['red', 'blue', 'green',
				'cyan', 'magenta', 'yellow',
				'purple', 'black',
				'dark blue', 'dark green']:
			tag = buf.create_tag(x)
			tag.set_property('foreground', x)
			tag.set_property('foreground-set', True)

	def __init__(self, servertab, userlist = True):
		gtk.HPaned.__init__(self)
		self.web = WebPool()

		self.servertab = servertab

		self.img_max_height = 192

		self.topic = gtk.Entry()

		self.text = gtk.TextView()
		#self.text.set_border_window_size(gtk.TEXT_WINDOW_LEFT, 8)
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

		if userlist:
			chan.pack_start(self.topic, False, False)
		chan.pack_start(scr, True, True)
		self.pack1(chan, True, True)

		if userlist:
			u = gtk.VBox()
			u.pack_start(self.status, False, False)
			u.pack_start(self.usrlist, True, True)
			self.pack2(u, False, False)

	def scale_image(self, pic):
		def got_size(ldr, width, height):

			if height < self.img_max_height:
				return

			ratio = float(width) / float(height)
			scale = self.img_max_height / float(height)

			ldr.set_size(int(scale * float(width)),
					int(scale * float(height)))

		ldr = gtk.gdk.PixbufLoader()
		ldr.connect('size-prepared', got_size)
		ldr.write(pic)
		ldr.close()
		pixbuf = ldr.get_pixbuf()
		img = gtk.image_new_from_pixbuf(pixbuf)
		img.show_all()
		return img

	def msg(self, msg, tags = []):
		tags.append('font')
		buf = self.text.get_buffer()
		i = buf.get_iter_at_offset(buf.get_char_count())
		buf.place_cursor(i)
		buf.insert_with_tags_by_name(i, msg, *tags)
		i = buf.get_iter_at_offset(buf.get_char_count())
		buf.place_cursor(i)

		if not '\n' in msg:
			return

		self.text.scroll_to_iter(i, 0.0)

		def is_url(s):
			def begins_with(s, prefix):
				if len(s) < len(prefix):
					return False
				return s[:len(prefix)] == prefix
			if begins_with(s, 'http://'):
				return True
			if begins_with(s, 'https://'):
				return True
			if begins_with(s, 'www'):
				return True
			return False

		for x in msg.split():
			if not is_url(x):
				continue
			def Closure(pic):
				img = self.scale_image(pic)
				anchor = buf.create_child_anchor(i)
				self.text.add_child_at_anchor(img, anchor)
				buf.insert(i, '\n')
				return
			self.web.get_image(x, Closure)
