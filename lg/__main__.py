#!/usr/bin/env python2
#-*- coding: utf-8 -*-

import os
import sys
import winxpgui as win32gui
import win32gui_struct
import win32api
import winerror
import win32con

from win32con import *

from common.window import BaseWindow
from common.message import subscriber, subscribe

MESSAGE_NAME = {}

for k in dir(win32con):
    v = win32con.__dict__.get(k)
    if isinstance(v, int) and k[:3] == 'WM_':
        MESSAGE_NAME[v] = k

class Application:

    def __init__(self, window):
        win32gui.InitCommonControls()
        self.window = window

    def start(self):
        self.window.application = self
        win32gui.PumpMessages()

    def quit(self):
        win32gui.PostQuitMessage(0)

@subscriber
class OverlayWindow(BaseWindow):

    @subscribe
    def onmessage(self, hwnd, message, wparam, lparam):
        print "[%d] message=%-24s wparam=0x%-10x lparam=0x%-10x" % (hwnd, MESSAGE_NAME[message], wparam, lparam)

    @subscribe(WM_CREATE)
    def oncreate(self):
        print self.setWindowLong(GWL_EXSTYLE, WS_EX_LAYERED | WS_EX_TOPMOST)
        print self.setWindowPos(z=HWND_TOPMOST, x=100, y=100, flags=SWP_NOSIZE)
        self.show()

    @subscribe(WM_DESTROY)
    def ondestroy(self, hwnd, message, wparam, lparam):
        self.application.quit()

if __name__ == '__main__':
    wnd = OverlayWindow()
    wnd.prepareClass()
    wnd.createWindow(title='Demo Project', w=200, h=200)
    app = Application(wnd)
    app.start()

