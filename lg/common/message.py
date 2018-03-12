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
            self.__bind_events = False
            self.subscriptions = []
            for key in dir(self):
                fn = self.__getattribute__(key)
                if isinstance(fn, _WrapperFn):
                    bound_fn = functools.partial(fn, self)
                    self.subscriptions.append(bound_fn)
                    if fn.message == win32con.WM_CREATE:
                        self._wm_create_subscriptions.append(bound_fn)
            self.__bind_events = True
        def __getattribute__(self, name):
            v = clz.__getattribute__(self, name)
            if isinstance(v, _WrapperFn) and self.__bind_events:
                return functools.partial(v, self)
            else:
                return v
        def get_wnd_proc(self):
            def wnd_proc(*args):
                for fn in self.subscriptions:
                    if fn(*args):
                        break
                else:
                    win32gui.DefWindowProc(*args)
            return wnd_proc
    return WndMessageSubscriber
