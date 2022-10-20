import threading

__LogLevel = 0

def set_level(level_char):
    global __LogLevel

    if level_char == 'e':
        __LogLevel = 0
    elif level_char == 'w':
        __LogLevel = 1
    elif level_char == 'i':
        __LogLevel = 2
    elif level_char == 'd':
        __LogLevel = 3

def e(msg):
    _log(0, msg)

def w(msg):
    _log(1, msg)

def i(msg):
    _log(2, msg)

def d(msg):
    _log(3, msg)

__ValToLevel = {
    0: 'E',
    1: 'W',
    2: 'I',
    3: 'D',
}

def _log(level, msg):
    global __LogLevel

    this_thread = threading.current_thread()
    thread_name = this_thread.name
    if this_thread.ident == threading.main_thread().ident:
        thread_name = 'MAIN'

    if level <= __LogLevel:
        print('[{}][{}] - {}'.format(
            __ValToLevel[level], thread_name, msg))
