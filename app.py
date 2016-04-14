from wsgiref.util import setup_testing_defaults

from utils import parse_http_get_data, get_first_element, \
    parse_http_content_type, parse_http_headers, parse_http_path, \
    parse_http_x_www_form_urlencoded_post_data
import gitdata.local as db
db.load(['messages'])


class Request:
    def __init__(self, environ):
        self.method = environ['REQUEST_METHOD'].upper()
        self.headers = parse_http_headers(environ)
        self.path_info = environ['PATH_INFO']
        self.path = parse_http_path(environ)
        self.POST = parse_http_x_www_form_urlencoded_post_data(environ)
        self.GET = parse_http_get_data(environ)


def application(environ, start_response):
    # https://www.python.org/dev/peps/pep-3333/#environ-variables

    req = Request(environ  )
    response_headers = [('Content-type', 'text/html; charset=utf-8')]
    response_status = '200 OK'
    response_body = ''

    start_response(response_status, response_headers)
    return [response_body.encode('utf-8')]
