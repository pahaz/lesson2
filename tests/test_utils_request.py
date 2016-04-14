import unittest
from io import BytesIO
from wsgiref.util import setup_testing_defaults
from minidjango.http.request import HttpRequest, RequestParseError
from minidjango.utils.rand import get_random_string

__author__ = 'pahaz'


class RequestTestCase(unittest.TestCase):
    def test_httprequest(self):
        path = '/' + get_random_string()
        request = self.request({'PATH_INFO': path})
        self.assertEqual(list(request.GET.keys()), [])
        self.assertEqual(list(request.POST.keys()), [])
        self.assertEqual(list(request.COOKIES.keys()), [])
        self.assertFalse(
            {'PATH_INFO', 'REQUEST_METHOD', 'CONTENT_TYPE',
             'wsgi.input'} - set(request.META.keys())
        )
        self.assertEqual(request.META['PATH_INFO'], path)
        self.assertEqual(request.META['REQUEST_METHOD'], 'GET')

    def test_path(self):
        path = '/' + get_random_string()
        request = self.request({'PATH_INFO': path})
        self.assertEqual(request.path, path)

    def test_path_with_script_name(self):
        request = self.request({
            'PATH_INFO': '/somepath/',
            'SCRIPT_NAME': '/PREFIX/',
            'REQUEST_METHOD': 'get',
            'wsgi.input': BytesIO(b''),
        })
        self.assertEqual(request.path, '/PREFIX/somepath/')

        # Without trailing slash
        request = self.request({
            'PATH_INFO': '/somepath/',
            'SCRIPT_NAME': '/PREFIX',
            'REQUEST_METHOD': 'get',
            'wsgi.input': BytesIO(b''),
        })
        self.assertEqual(request.path, '/PREFIX/somepath/')

    def test_stream(self):
        data = b'name=value'
        request = self.request({
            'REQUEST_METHOD': 'POST',
            'CONTENT_TYPE': 'application/x-www-form-urlencoded',
            'CONTENT_LENGTH': len(data),
            'wsgi.input': BytesIO(data)})
        self.assertEqual(request.read(), b'name=value')

    def test_read_after_value(self):
        data = b'name=value'
        request = self.request({
            'REQUEST_METHOD': 'POST',
            'CONTENT_TYPE': 'application/x-www-form-urlencoded',
            'CONTENT_LENGTH': len(data),
            'wsgi.input': BytesIO(data)})
        self.assertEqual(request.POST['name'], 'value')
        self.assertEqual(request.body, b'name=value')
        self.assertEqual(request.read(), b'name=value')

    def test_value_after_read(self):
        """
        Construction of POST or body is not allowed after reading
        from request.
        """
        data = b'name=value'
        request = self.request({
            'REQUEST_METHOD': 'POST',
            'CONTENT_TYPE': 'application/x-www-form-urlencoded',
            'CONTENT_LENGTH': len(data),
            'wsgi.input': BytesIO(data)})
        self.assertEqual(request.read(2), b'na')
        with self.assertRaises(RequestParseError):
            request.body
        self.assertEqual(request.POST, {})

    def request(self, environ):
        setup_testing_defaults(environ)
        return HttpRequest(environ)

    # https://github.com/django/django/blob/master/
    # tests/requests/tests.py#L390
