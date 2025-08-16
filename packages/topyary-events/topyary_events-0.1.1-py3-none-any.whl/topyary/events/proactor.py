from .loop import EventLoop
from .inotify import inotify_init, inotify_add_watch, inotify_rm_watch
from typing import Callable, Tuple, Dict, Optional
from datetime import datetime, timedelta
from socket import socket
from io import FileIO
import os
import struct

_inotify_hdr = struct.Struct('iIII') # wd, mask, cookie, len
_inotify_hdr_size = _inotify_hdr.size
_inotify_hdr_unpack_from = _inotify_hdr.unpack_from


class SocketIoPolicy:
    def on_event(self, socket: socket, events: int) -> bool:
        raise NotImplementedError()


class FileIoPolicy:
    def on_event(self, file: FileIO, events: int) -> bool:
        raise NotImplementedError()


class ReadStreamSocketIoPolicy(SocketIoPolicy):
    def __init__(self, buf: bytearray, on_data: Callable[[bytes], bool]) -> None:
        self._buf = buf
        self._on_data = on_data

    def on_event(self, socket: socket, events: int) -> bool:
        if events & EventLoop.OUT:
            num_bytes_read = socket.recv_into(self._buf)
            # TODO: memoryview
            return self._on_data(self._buf[:num_bytes_read])
        return True


class ReadFileIoPolicy(FileIoPolicy):
    def __init__(self, buf: bytearray, on_data: Callable[[bytes], bool]) -> None:
        self._buf = buf
        self._on_data = on_data

    def on_event(self, file: FileIO, events: int) -> bool:
        if events & EventLoop.OUT:
            num_bytes_read = file.readinto(self._buf)
            return self._on_data(self._buf[:num_bytes_read])
        return True


class EventLoopProactor:
    IN = EventLoop.IN
    OUT = EventLoop.OUT
    ERROR = EventLoop.ERROR
    HANGUP = EventLoop.HANGUP

    def __init__(self) -> None:
        self._el = EventLoop()
        self._el_poll = self._el.poll
        self._inotify = FileIO(inotify_init())
        self._wds : Dict[int, Tuple[FileIO, FileIoPolicy]] = {}
        self._el.add_fd(self._inotify.fileno(), EventLoop.IN, self._on_inotify)
        self._inotify_buf = bytearray(1024)

    def _on_inotify(self, events: int) -> bool:
        _inotify_buf = self._inotify_buf
        _inotify_readinto = self._inotify.readinto
        _get_wd = self._wds.get
        bytes_read = _inotify_readinto(self._inotify_buf)

        i = 0
        while i < bytes_read:
            wd, mask, cookie, name_len = _inotify_hdr_unpack_from(_inotify_buf, i)
            i += _inotify_hdr_size + name_len
            
            wd_tuple = _get_wd(wd)
            if wd_tuple:
                io, policy = wd_tuple
                policy.on_event(io, EventLoop.OUT)
        return True

    def __del__(self) -> None:
        self.close()

    def close(self) -> None:
        self._inotify.close()

    def add_timer(self, interval: timedelta, on_elapsed: Callable[[datetime], bool]) -> None:
        self._el.add_looping_timer(interval, lambda e=on_elapsed: e(datetime.now()))

    def add_socket(self, s: socket, events: int, policy: SocketIoPolicy) -> None:
        self._el.add_socket(s, events, lambda e, s=s, policy=policy: policy.on_event(s, e))

    def add_file_tailer(self, filename: str, policy: FileIoPolicy) -> None:
        wd = inotify_add_watch(self._inotify.fileno(), filename.encode('utf-8'), 2)
        if wd == -1: raise IOError("invalid filename specified")
        io = FileIO(os.open(filename, 400))
        self._wds[wd] = (io, policy)

    def poll(self, timeout: Optional[timedelta] = None) -> int:
        return self._el_poll(timeout)
