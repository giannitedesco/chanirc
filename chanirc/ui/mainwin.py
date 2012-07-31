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
		if s[0] == '/':
			arr = s[1:].split(None, 1)
			if len(arr) < 2:
				arr.append(None)
			(cmd, args) = arr
			cb = self.__cmd.get(cmd.lower(), None)
			if cb is None:
				print 'unknown cmd:', cmd
				return
			else:
				cb(args)
		else:
			print 'chat: %s'%s

	def __send(self, _, s):
		self.send(s)

	def cmd_server(self, host):
		svr = self.serverlist.cur
		if svr is None or host is None:
			raise Exception('ugh...')
		svr.server(host)

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

		vp = gtk.HPaned()
		vb.pack_start(vp, True, True)

		self.entry = IrcEntry()
		self.entry.connect('send', self.__send)
		vb.pack_start(self.entry, False, False)

		self.serverlist = ServerList()
		vp.add1(self.serverlist)

		self.set_focus(self.entry)
		self.__cmd = {
			"server": self.cmd_server,
		}
