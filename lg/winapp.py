import win32gui

from win32con import *

from win32gui import ShowWindow, SetWindowPos, GetWindowLong, SetWindowLong, SetLayeredWindowAttributes

from common.window import BaseWindow
from common.message import subscriber, subscribe

from timer import set_timer, kill_timer
from utils import get_message_name

@subscriber
class OverlayWindow(BaseWindow):

    def __init__(self):
        BaseWindow.__init__(self)

    @subscribe
    def onmessage(self, hwnd, message, wparam, lparam):
        print("[%d] message=%-24s wparam=0x%-10x lparam=0x%-10x" % (hwnd, get_message_name(message), wparam, lparam))

    @subscribe(WM_CREATE)
    def oncreate(self, hwnd, message, wparam, lparam):
        SetWindowLong(hwnd, GWL_STYLE, WS_POPUP | WS_CHILD)
        SetWindowLong(hwnd, GWL_EXSTYLE, WS_EX_LAYERED | WS_EX_TOPMOST | WS_EX_TOOLWINDOW)
        SetWindowPos(hwnd, HWND_TOPMOST, 0, 0, 64, 64, SWP_NOMOVE)
        ShowWindow(hwnd, SW_SHOW)
        set_timer(5000, self.ontimer)

    @subscribe(WM_STYLECHANGED)
    def onstyled(self, hwnd, message, wparam, lparam):
        if GetWindowLong(hwnd, GWL_EXSTYLE) & WS_EX_LAYERED:
            SetLayeredWindowAttributes(hwnd, 0, (255 * 70) / 100, LWA_ALPHA);

    @subscribe(WM_DESTROY)
    def ondestroy(self, hwnd, message, wparam, lparam):
        self.application.quit()

    def ontimer(self, timer_id, time):
        kill_timer(timer_id)
        self.destroyWindow()