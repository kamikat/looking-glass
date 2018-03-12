import win32gui

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
        def get_wnd_proc(self):
            fns = []
            for key in dir(self):
                fn = self.__getattribute__(key)
                if isinstance(fn, _WrapperFn):
                    fns.append(fn)
            def wnd_proc(*args):
                for fn in fns:
                    if fn(self, *args):
                        break
                else:
                    win32gui.DefWindowProc(*args)
            return wnd_proc
    return WndMessageSubscriber
