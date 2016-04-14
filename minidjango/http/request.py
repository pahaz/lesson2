import cgi
import codecs
import io
from urllib.parse import quote, parse_qs, urlparse, urljoin
from wsgiref.util import request_uri

from minidjango.conf import settings
from minidjango.core.exceptions import ImproperlyConfigured
from minidjango.http.cookie import parse_cookie
from minidjango.utils.encoding import escape_uri_path
from minidjango.utils.encoding import iri_to_uri
from minidjango.utils.functional import cached_property
from minidjango.utils.types import MultiValueDict, LimitedStream


class RequestParseError(Exception):
    pass


class HttpRequest(object):
    def __init__(self, environ):
        self.environ = environ
        self.META = environ

        raw_script_name = environ.get('SCRIPT_NAME') or '/'
        raw_path_info = environ.get('PATH_INFO') or '/'
        script_name = quote(raw_script_name, encoding='latin1')
        path_info = quote(raw_path_info, safe='/;=,', encoding='latin1')

        self.path = script_name.rstrip('/') + path_info
        self.path_info = path_info
        self.method = environ['REQUEST_METHOD'].upper()
        self.encoding = _detect_encoding(environ) or 'utf-8'
        self._stream = LimitedStream(
            self.environ['wsgi.input'],
            _content_length(environ)
        )
        self._read_started = False

    def get_host(self):
        """Return the HTTP host using the environment or request
        headers. So may return an insecure host."""
        if 'HTTP_HOST' in self.META:
            host = self.META['HTTP_HOST']
        else:
            # Reconstruct the host using the algorithm from PEP 333.
            host = self.META['SERVER_NAME']
            server_port = self.get_port()
            if server_port != ('443' if self.is_secure() else '80'):
                host = '%s:%s' % (host, server_port)
        return host

    def get_port(self):
        """Return the port number for the request as a string."""
        forwarded_in_meta = 'HTTP_X_FORWARDED_PORT' in self.META
        if settings.USE_X_FORWARDED_PORT and forwarded_in_meta:
            port = self.META['HTTP_X_FORWARDED_PORT']
        else:
            port = self.META['SERVER_PORT']
        return str(port)

    def get_full_path(self, force_append_slash=False):
        # RFC 3986 requires query string arguments to be in
        # the ASCII range. Rather than crash if this doesn't
        # happen, we encode defensively.
        qs = self.META.get('QUERY_STRING', '')
        sep = '/' if force_append_slash and not self.path.endswith('/') \
            else ''
        return '%s%s%s' % (
            escape_uri_path(self.path),
            sep,
            ('?' + iri_to_uri(qs)) if qs else ''
        )

    def get_raw_uri(self):
        return '{scheme}://{host}{path}'.format(
            scheme=self.scheme,
            host=self.get_host(),
            path=self.get_full_path(),
        )

    @property
    def scheme(self):
        if settings.SECURE_PROXY_SSL_HEADER:
            try:
                header, value = settings.SECURE_PROXY_SSL_HEADER
            except ValueError:
                raise ImproperlyConfigured(
                    'The SECURE_PROXY_SSL_HEADER setting must be '
                    'a tuple containing two values.'
                )
            if self.META.get(header) == value:
                return 'https'
        return self.environ.get('wsgi.url_scheme') or 'http'

    def is_secure(self):
        return self.scheme == 'https'

    @cached_property
    def GET(self):
        qs = self.environ.get("QUERY_STRING", "")
        if isinstance(qs, bytes):
            qs = qs.decode(self.encoding)
        return MultiValueDict(parse_qs(qs))

    @cached_property
    def COOKIES(self):
        raw_cookie = self.environ.get('HTTP_COOKIE', '')
        return parse_cookie(raw_cookie)

    def _get_post(self):
        if not hasattr(self, '_post'):
            self._load_post_and_files()
        return self._post

    def _get_files(self):
        if not hasattr(self, '_files'):
            self._load_post_and_files()
        return self._files

    POST = property(_get_post)
    FILES = property(_get_files)

    @property
    def body(self):
        if not hasattr(self, '_body'):
            if self._read_started:
                raise RequestParseError(
                    "You cannot access body after reading "
                    "from request's data stream")
            try:
                self._body = self.read()
            except IOError as e:
                raise RequestParseError() from e
            self._stream = io.BytesIO(self._body)
        return self._body

    def _load_post_and_files(self):
        """Populate self._post and self._files if the content-type
        is a form type"""
        if self.method != 'POST':
            self._post, self._files = MultiValueDict(), MultiValueDict()
            return

        content_type = self.META.get('CONTENT_TYPE', '')
        is_multipart = content_type.startswith('multipart/form-data')
        is_www_form = content_type.startswith(
            'application/x-www-form-urlencoded')
        if is_multipart:
            self._post, self._files = self.parse_file_upload(self.META, self)

        elif is_www_form:
            request_body_bytes = self.body
            request_body_text = request_body_bytes.decode(self.encoding)
            body_query_dict = parse_qs(request_body_text)
            self._post = MultiValueDict(body_query_dict)
            self._files = MultiValueDict()

        else:
            raise RequestParseError(
                "unknown request content type"
            )

    def close(self):
        if hasattr(self, '_files'):
            for f in self._files:
                if hasattr(f, 'close'):
                    f.close()

    # File-like and iterator interface.

    def read(self, *args, **kwargs):
        self._read_started = True
        try:
            return self._stream.read(*args, **kwargs)
        except IOError as e:
            raise RequestParseError() from e

    def readline(self, *args, **kwargs):
        self._read_started = True
        try:
            return self._stream.readline(*args, **kwargs)
        except IOError as e:
            raise RequestParseError() from e

    __iter__ = readline

    def parse_file_upload(self, META, filelike):
        raise RequestParseError("How to parse multipart data?? "
                                "Not implemented!")


def _detect_encoding(environ):
    encoding = None
    _, content_params = cgi.parse_header(environ.get('CONTENT_TYPE', ''))
    if 'charset' in content_params:
        try:
            codecs.lookup(content_params['charset'])
        except LookupError:
            pass
        else:
            encoding = content_params['charset']
    return encoding


def _content_length(environ):
    try:
        content_length = int(environ.get('CONTENT_LENGTH'))
    except (ValueError, TypeError):
        content_length = 0
    return content_length
