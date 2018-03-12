import win32gui
import win32con
import functools

class _WrapperFn:
    def __init__(self, message, fn):
        self.message = message
        self.fn = fn
    def __call__(self, *args, **kwargs):
        if (self.message == None or self.message == args[2]):
            return self.fn(*args, **kwargs)
    def __get__(self, instance):
        return functools.partial(self.__call__, instance)

def subscribe(message):
    def wrapper(fn):
        return _WrapperFn(message, fn)
    if isinstance(message, int):
        return wrapper
    else:
        return _WrapperFn(None, message)

def subscriber(clz):
    class WndMessageSubscriber(clz):
        def __init__(self, *args, **kwargs):
            clz.__init__(self, *args, **kwargs)
            self.subscriptions = []
            for key in dir(self):
                fn = self.__getattribute__(key)
                if isinstance(fn, _WrapperFn):
                    self.subscriptions.append(fn)
                    if fn.message == win32con.WM_CREATE:
                        self._wm_create_subscriptions.append(fn)
        def get_wnd_proc(self):
            def wnd_proc(*args):
                for fn in self.subscriptions:
                    if fn(self, *args):
                        break
                else:
                    win32gui.DefWindowProc(*args)
            return wnd_proc
    return WndMessageSubscriber
