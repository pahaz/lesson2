import collections
from io import BytesIO

import io

__author__ = 'pahaz'


class MultiValueDict(collections.UserDict):
    """
    >>> d = MultiValueDict()
    >>> d['foo'] = ['bar']
    >>> d['foo']
    'bar'
    >>> d = MultiValueDict({'foo': ['v1', 'v2']})
    >>> d['foo']
    'v1'
    >>> d.getlist('foo')
    ['v1', 'v2']
    >>> list(d.items())
    [('foo', 'v1')]
    >>> dict(MultiValueDict({'foo': ['v1', 'v2']}))
    {'foo': 'v1'}
    >>> dict(MultiValueDict({'foo': ['v1']}))
    {'foo': 'v1'}
    """

    def __iter__(self):
        a = super().__iter__()
        for x in a:
            yield x

    def __getitem__(self, key):
        val = super().__getitem__(key)
        if isinstance(val, (list, tuple)):
            val = val[0]
        else:
            raise RuntimeError('Invalid MultiValueDict inner state')
        return val

    def __setitem__(self, key, item):
        if not isinstance(item, (list, tuple)):
            raise TypeError("Can't set not a multi value")
        if not item:
            raise ValueError("Can't set empty multi value")
        self.data[key] = item

    def getlist(self, key, default=None):
        val = self.data.get(key, default)
        if not isinstance(val, (list, tuple)):
            raise RuntimeError('Invalid MultiValueDict inner state')
        return val


class LimitedStream(io.IOBase):
    """
    LimitedStream wraps another stream in order to not allow
    reading from it past specified amount of bytes.

    >>> import io
    >>> bio = io.BytesIO(b"some -- long -- byte string")
    >>> lbio = LimitedStream(bio, 4)
    >>> lbio.read()
    b'some'
    >>> lbio.read()
    b''

    >>> bio = io.BytesIO(b"s\\nome -- long -- byte string")
    >>> lbio = LimitedStream(bio, 4)
    >>> lbio.readline()
    b's\\n'
    >>> lbio.read()
    b'om'
    >>> lbio.read()
    b''

    """
    def __init__(self, stream, limit, buf_size=64 * 1024 * 1024):
        self.stream = stream
        self.remaining = limit
        self.buffer = b''
        self.buf_size = buf_size

    def _read_limited(self, size=None):
        if size is None or size > self.remaining:
            size = self.remaining
        if size == 0:
            return b''
        result = self.stream.read(size)
        self.remaining -= len(result)
        return result

    def read(self, size=None):
        if size is None:
            result = self.buffer + self._read_limited()
            self.buffer = b''
        elif size < len(self.buffer):
            result = self.buffer[:size]
            self.buffer = self.buffer[size:]
        else:  # size >= len(self.buffer)
            result = self.buffer + self._read_limited(size - len(self.buffer))
            self.buffer = b''
        return result

    def readline(self, size=None):
        while b'\n' not in self.buffer and \
              (size is None or len(self.buffer) < size):
            if size:
                # since size is not None here, len(self.buffer) < size
                chunk = self._read_limited(size - len(self.buffer))
            else:
                chunk = self._read_limited()
            if not chunk:
                break
            self.buffer += chunk
        sio = BytesIO(self.buffer)
        if size:
            line = sio.readline(size)
        else:
            line = sio.readline()
        self.buffer = sio.read()
        return line
