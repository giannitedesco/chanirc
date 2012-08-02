#!/usr/bin/python

from chanirc import MainWin
import gobject
import gtk

if __name__ == '__main__':
#	gobject.threads_init()
#	gtk.gdk.threads_init()
	win = MainWin()
	s = win.add_server_tab()
	win.main()
	raise SystemExit, 0
