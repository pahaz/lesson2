import collections
import datetime
import re
import time
from datetime import timezone
from http.client import responses

from minidjango.conf import settings
from minidjango.http.cookie import SimpleCookie
from minidjango.utils.encoding import iri_to_uri
from minidjango.utils.http import cookie_date

_charset_from_content_type_re = re.compile(
    r';\s*charset=(?P<charset>[^\s;]+)',
    re.I)
_default = object()


class HttpCookiesMixin:
    def set_cookie(self, key, value='', max_age=None, expires=None, path='/',
                   domain=None, secure=False, httponly=False):
        """
        Sets a cookie.

        ``expires`` can be:
        - a string in the correct format,
        - a naive ``datetime.datetime`` object in UTC,
        - an aware ``datetime.datetime`` object in any time zone.
        If it is a ``datetime.datetime`` object then ``max_age`` will be calculated.
        """
        value = str(value)
        self.cookies[key] = value
        if expires is not None:
            if isinstance(expires, datetime.datetime):
                if timezone.is_aware(expires):
                    expires = timezone.make_naive(expires, timezone.utc)
                delta = expires - expires.utcnow()
                # Add one second so the date matches exactly (a fraction of
                # time gets lost between converting to a timedelta and
                # then the date string).
                delta = delta + datetime.timedelta(seconds=1)
                # Just set max_age - the max_age logic will set expires.
                expires = None
                max_age = max(0, delta.days * 86400 + delta.seconds)
            else:
                self.cookies[key]['expires'] = expires
        if max_age is not None:
            self.cookies[key]['max-age'] = max_age
            # IE requires expires, so set it if hasn't been already.
            if not expires:
                self.cookies[key]['expires'] = cookie_date(
                    time.time() + max_age)
        if path is not None:
            self.cookies[key]['path'] = path
        if domain is not None:
            self.cookies[key]['domain'] = domain
        if secure:
            self.cookies[key]['secure'] = True
        if httponly:
            self.cookies[key]['httponly'] = True

    def delete_cookie(self, key, path='/', domain=None):
        self.set_cookie(key, max_age=0, path=path, domain=domain,
                        expires='Thu, 01-Jan-1970 00:00:00 GMT')


class HttpResponse(HttpCookiesMixin, collections.Iterable):
    status_code = 200

    def __iter__(self):
        for x in self._content:
            if not isinstance(x, bytes):
                x = bytes(x, encoding=self.charset)
            yield x

    def get(self, *args, **kwargs):
        return self._headers.get(*args, **kwargs)

    def __getitem__(self, key):
        return self._headers[key.lower()]

    def __setitem__(self, key, item):
        self._headers[key.lower()] = item

    def __delitem__(self, key):
        try:
            del self._headers[key.lower()]
        except KeyError:
            pass

    def items(self):
        return self._headers.items()

    # The WSGI server must call this method upon completion
    # of the request.
    # See http://blog.dscpl.com.au/2012/10/
    # obligations-for-calling-close-on.html
    def close(self):
        pass

    def __init__(self, content=b'', content_type=None,
                 status=None, reason=None,
                 charset=None):
        self._content = [content]
        self._headers = {}

        self.cookies = SimpleCookie()
        if status is not None:
            self.status_code = status
        self._reason_phrase = reason
        self._charset = charset
        if content_type is None:
            content_type = '%s; charset=%s' % (
                settings.DEFAULT_CONTENT_TYPE,
                self.charset)
        self['Content-Type'] = content_type

    @property
    def reason_phrase(self):
        if self._reason_phrase is not None:
            return self._reason_phrase
        return responses.get(self.status_code, 'Unknown Status Code')

    @reason_phrase.setter
    def reason_phrase(self, value):
        self._reason_phrase = value

    @property
    def charset(self):
        if self._charset is not None:
            return self._charset
        content_type = self.get('Content-Type', '')
        matched = _charset_from_content_type_re.search(content_type)
        if matched:
            # Extract the charset and strip its double quotes
            return matched.group('charset').replace('"', '')
        return settings.DEFAULT_CHARSET

    @charset.setter
    def charset(self, value):
        self._charset = value

    def __repr__(self):
        return '<%(cls)s status_code=%(status_code)d, ' \
               '"%(content_type)s">' % {
            'cls': self.__class__.__name__,
            'status_code': self.status_code,
            'content_type': self['Content-Type'],
        }

    @property
    def content(self):
        return b''.join(iter(self))


class HttpResponseRedirectBase(HttpResponse):
    def __init__(self, redirect_to, *args, **kwargs):
        super(HttpResponseRedirectBase, self).__init__(*args, **kwargs)
        self['Location'] = iri_to_uri(redirect_to)

    url = property(lambda self: self['Location'])

    def __repr__(self):
        return '<%(cls)s status_code=%(status_code)d, ' \
               '"%(content_type)s", url="%(url)s">' % {
            'cls': self.__class__.__name__,
            'status_code': self.status_code,
            'content_type': self['Content-Type'],
            'url': self.url,
        }


class HttpResponseRedirect(HttpResponseRedirectBase):
    status_code = 302


class HttpResponsePermanentRedirect(HttpResponseRedirectBase):
    status_code = 301


class HttpResponseBadRequest(HttpResponse):
    status_code = 400


class HttpResponseNotFound(HttpResponse):
    status_code = 404


class HttpResponseForbidden(HttpResponse):
    status_code = 403


class HttpResponseGone(HttpResponse):
    status_code = 410


class HttpResponseServerError(HttpResponse):
    status_code = 500


class Http404(Exception):
    pass
