import win32con

_MESSAGE_NAME = {}

for k in dir(win32con):
    v = win32con.__dict__.get(k)
    if isinstance(v, int) and k[:3] == 'WM_':
        _MESSAGE_NAME[v] = k

def get_message_name(message):
    return _MESSAGE_NAME[message]
