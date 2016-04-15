import unittest
from io import BytesIO
from wsgiref.util import setup_testing_defaults

from minidjango.core.wsgi import get_wsgi_application
from minidjango.http import HttpResponse

__author__ = 'pahaz'


class ApplicationTestCase(unittest.TestCase):
    def setUp(self):
        self.app = get_wsgi_application()

    def request(self, environ):
        self.callback = lambda *a, **aa: 1
        setup_testing_defaults(environ)
        return self.app(environ, self.callback)

    def test_index(self):
        data = b'name=value'
        request = self.request({
            'REQUEST_METHOD': 'GET',
            'CONTENT_TYPE': 'application/x-www-form-urlencoded',
            'CONTENT_LENGTH': len(data),
            'wsgi.input': BytesIO(data)})
        self.assertIsInstance(request, HttpResponse)
        self.assertEqual(request.content, b'HI!')
