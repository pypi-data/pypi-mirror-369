from ctypes import CDLL, c_int, c_char_p, c_uint32

_libc = CDLL('libc.so.6')

inotify_init = _libc.inotify_init
inotify_add_watch = _libc.inotify_add_watch
inotify_add_watch.argtypes = [c_int, c_char_p, c_uint32]
inotify_rm_watch = _libc.inotify_rm_watch
