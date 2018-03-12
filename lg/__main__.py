#!/usr/bin/env python2
#-*- coding: utf-8 -*-

import winxpgui as win32gui
import winapp

class Application:

    def __init__(self, window):
        win32gui.InitCommonControls()
        self.window = window

    def start(self):
        self.window.application = self
        win32gui.PumpMessages()

    def quit(self):
        win32gui.PostQuitMessage(0)

if __name__ == '__main__':
    wnd = winapp.OverlayWindow()
    wnd.prepareClass()
    wnd.createWindow()
    app = Application(wnd)
    app.start()

