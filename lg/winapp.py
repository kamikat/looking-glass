import win32gui

from win32con import *

from win32gui import ShowWindow, SetWindowPos, GetWindowLong, SetWindowLong, SetLayeredWindowAttributes
from win32gui import SendMessage, PostMessage, GetWindowRect, SetCapture, ReleaseCapture, GetCursorPos
from win32api import GetAsyncKeyState

from common.window import BaseWindow
from common.message import subscriber, subscribe

from timer import set_timer, kill_timer
from utils import get_message_name

@subscriber
class OverlayWindow(BaseWindow):

    def __init__(self):
        BaseWindow.__init__(self)
        self._modifier = 0

    def check_button_state(self, modifier, mask):
        if (modifier & mask) == (self._modifier & mask):
            return 0
        elif modifier & mask != 0:
            return 1
        else:
            return 2

    @subscribe
    def on_message(self, hwnd, message, wparam, lparam):
        print("[%d] message=%-24s wparam=0x%-10x lparam=0x%-10x" % (hwnd, get_message_name(message), wparam, lparam))

    @subscribe(WM_CREATE)
    def on_create(self, hwnd, message, wparam, lparam):
        set_timer(30000, self.on_timer)
        SetWindowLong(hwnd, GWL_STYLE, WS_POPUP | WS_CHILD)
        SetWindowLong(hwnd, GWL_EXSTYLE, WS_EX_LAYERED | WS_EX_TOPMOST | WS_EX_TOOLWINDOW)
        SetWindowPos(self.hwnd, 0, 0, 0, 200, 200, SWP_NOMOVE | SWP_NOZORDER)
        SetWindowPos(self.hwnd, HWND_TOPMOST, 0, 0, 0, 0, SWP_NOMOVE | SWP_NOSIZE)
        SetWindowPos(self.hwnd, 0, 0, 0, 0, 0, SWP_NOSIZE | SWP_NOZORDER)
        ShowWindow(self.hwnd, SW_SHOW)

    @subscribe(WM_STYLECHANGED)
    def on_styled(self, hwnd, message, wparam, lparam):
        if GetWindowLong(hwnd, GWL_EXSTYLE) & WS_EX_LAYERED:
            SetLayeredWindowAttributes(hwnd, 0, 255 * 90 / 100, LWA_ALPHA);

    @subscribe(WM_NCHITTEST)
    def on_hit(self, hwnd, message, wparam, lparam):
        x, y = (lparam & 0xFFFF, lparam >> 16)
        left, top, right, bottom = GetWindowRect(hwnd)
        dx, dy = (x - left, y - top)
        a = dx | (dy << 16)
        modifier = reduce(lambda x, y: x << 1 | (1 if GetAsyncKeyState(y) != 0 else 0), reversed([
            VK_LBUTTON,
            VK_RBUTTON,
            VK_SHIFT,
            VK_CONTROL,
            VK_MBUTTON ]), 0)
        button_spec = [
                (0x0001, (WM_MOUSEMOVE, WM_LBUTTONDOWN, WM_LBUTTONUP)),
                (0x0002, (WM_MOUSEMOVE, WM_RBUTTONDOWN, WM_RBUTTONUP)),
                (0x0010, (WM_MOUSEMOVE, WM_MBUTTONDOWN, WM_MBUTTONUP))]
        for mask, message in button_spec:
            p = self.check_button_state(modifier, mask)
            if p:
                SendMessage(hwnd, message[p], modifier, a)
                break
        else:
            SendMessage(hwnd, WM_MOUSEMOVE, modifier, a)
        print "{0:b} => {1:b}".format(self._modifier, modifier)
        self._modifier = modifier
        print("[%d] Hit (%d, %d)" % (hwnd, x, y))

    @subscribe(WM_LBUTTONDOWN)
    def on_mousedown(self, hwnd, message, wparam, lparam):
        self._dx, self._dy = (lparam & 0xFFFF, lparam >> 16)
        SetCapture(hwnd)

    @subscribe(WM_LBUTTONUP)
    def on_mouseup(self, hwnd, message, wparam, lparam):
        self._modifier = 0
        ReleaseCapture()

    @subscribe(WM_MOUSEMOVE)
    def on_mousemove(self, hwnd, message, wparam, lparam):
        if wparam & 0x1:
            x0, y0 = GetCursorPos()
            SetWindowPos(hwnd, 0, x0 - self._dx, y0 - self._dy, 0, 0, SWP_NOSIZE | SWP_NOZORDER | SWP_NOSENDCHANGING)

    @subscribe(WM_PAINT)
    def do_paint(self, hwnd, message, wparam, lparam):
        pass

    @subscribe(WM_DESTROY)
    def on_destroy(self, hwnd, message, wparam, lparam):
        self.application.quit()

    def on_timer(self, timer_id, time):
        kill_timer(timer_id)
        self.destroyWindow()
