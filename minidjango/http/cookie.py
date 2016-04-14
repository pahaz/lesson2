from http.cookies import SimpleCookie, BaseCookie, CookieError


def parse_cookie(cookie):
    """
    >>> parse_cookie('')
    {}
    >>> parse_cookie('foo=bar;')
    {'foo': 'bar'}
    >>> parse_cookie('foo=bar;foo=baz')
    {'foo': 'baz'}
    >>> parse_cookie('f1=v1;f2=v2') == {'f1': 'v1', 'f2': 'v2'}
    True
    """
    if not cookie:
        return {}
    if not isinstance(cookie, BaseCookie):
        try:
            c = SimpleCookie()
            c.load(cookie)
        except CookieError:
            # Invalid cookie
            return {}
    else:
        c = cookie
    return {k: c.get(k).value for k in c.keys()}
