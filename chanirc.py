#!/usr/bin/python

from chanirc import MainWin

if __name__ == '__main__':
	win = MainWin()
	s = win.add_server_tab()
	win.main()
	raise SystemExit, 0
