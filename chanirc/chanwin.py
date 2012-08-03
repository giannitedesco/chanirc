import gobject, gtk, pango
from webthread import WebPool
from urlparse import urlparse, parse_qs
from userlist import UserList
import webkit

def begins_with(s, prefix):
	if len(s) < len(prefix):
		return False
	return s[:len(prefix)] == prefix

def parse_url(url):
		try:
			u = urlparse(url)
		except:
			u = None
			pass
		if u is None or u.scheme == '':
			try:
				u = urlparse(url, scheme = 'http')
			except:
				return None
		if u.hostname is None:
			return None
		return u

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
		self.usrlist = UserList();

		chan = gtk.VBox()

		if userlist:
			chan.pack_start(self.topic, False, False)
		chan.pack_start(scr, True, True)
		self.pack1(chan, True, True)

		if userlist:
			u = gtk.VBox()
			u.pack_start(self.status, False, False)
			scr = gtk.ScrolledWindow()
			scr.set_policy(gtk.POLICY_NEVER, gtk.POLICY_AUTOMATIC)
			scr.add(self.usrlist)
			u.pack_start(scr, True, True)
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
		try:
			ldr.write(pic)
		except:
			return None
		ldr.close()
		pixbuf = ldr.get_pixbuf()
		img = gtk.image_new_from_pixbuf(pixbuf)
		img.show_all()
		return img

	def embed_web(self, url, mark):
		buf = self.text.get_buffer()
		gtk.gdk.threads_enter()
		view = webkit.WebView()
		view.set_usize(400, 256)
		view.set_full_content_zoom(True)
		view.set_zoom_level(0.25)
		view.show_all()
		view.open(url)
		itr = buf.get_iter_at_mark(mark)
		anchor = buf.create_child_anchor(itr)
		self.text.add_child_at_anchor(view, anchor)
		buf.insert(itr, '\n')
		gtk.gdk.threads_leave()

	def embed_image(self, url, mark):
		buf = self.text.get_buffer()
		def Closure(pic):
			gtk.gdk.threads_enter()
			img = self.scale_image(pic)
			if img is None:
				gtk.gdk.threads_leave()
				return
			itr = buf.get_iter_at_mark(mark)
			anchor = buf.create_child_anchor(itr)
			self.text.add_child_at_anchor(img, anchor)
			buf.insert(itr, '\n')
			gtk.gdk.threads_leave()

		self.web.get_image(url, Closure)

	def embed_url(self, url, mark):
		url = parse_url(url)
		if url is None:
			return

		if url.query is not None and len(url.query):
			q = parse_qs(url.query)
			if 'youtube' in url.hostname.lower() and q.has_key('v'):
				yt = 'http://youtube.googleapis.com/v/'
				self.embed_web(yt + q['v'][0], mark)
				return
		elif url.hostname.lower() == 'youtube.googleapis.com' and \
				begins_with(url.path, '/v/'):
			self.embed_web(yt + q['v'][0], mark)
			return

		return self.embed_image(url, mark)

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
			if begins_with(s, 'http://'):
				return True
			if begins_with(s, 'https://'):
				return True
			if begins_with(s, 'www.'):
				return True
			return False

		mark = buf.create_mark(None, i, left_gravity = True)
		for x in msg.split():
			if not is_url(x):
				continue

			self.embed_url(x, mark)
