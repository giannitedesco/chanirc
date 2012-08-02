import gobject, glib, gtk, pango
from chanwin import ChanWin
from servertab import ServerTab
from serverlist import ServerList
from ircentry import IrcEntry

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

	def __add_tab(self, *a):
		print a

	def add_server_tab(self):
		svr = ServerTab()
		self.serverlist.add_server(svr)
		return svr

	def main(self):
		self.in_main = True
		self.show_all()
		gtk.main()
		self.in_main = False

	def send(self, s):
		win = self.serverlist.cur
		if win is None:
			raise Exception('ugh...')
		win.servertab.send_chat(win, s)

	def __send(self, _, s):
		self.send(s)

	def __sel(self, serverlist):
		old = self.__vp.get_child2()
		new = serverlist.cur
		if old == new:
			return
		if old is not None:
			self.__vp.remove(old)
		self.__vp.add2(new)
		self.__vp.show_all()

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

		self.__vp = gtk.HPaned()
		vb.pack_start(self.__vp, True, True)

		self.entry = IrcEntry()
		self.entry.connect('send', self.__send)
		vb.pack_start(self.entry, False, False)

		self.serverlist = ServerList()
		self.serverlist.connect('selection-changed', self.__sel)
		self.__vp.add1(self.serverlist)

		self.set_focus(self.entry)
