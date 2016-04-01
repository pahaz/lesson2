# Short overview #

	$ python3 -m http.server

 - server.py - simple pure python web server
 - app.py - simple pure python application
 - utils.py - wsgi helpers

## Run example ##

	$ python3 server.py  # open http://127.0.0.1:8001/

## server0.py

	import http.server
	import socketserver

	PORT = 8000

	Handler = http.server.SimpleHTTPRequestHandler

	httpd = socketserver.TCPServer(("", PORT), Handler)

	print("serving at port", PORT)
	httpd.serve_forever()

## app1.py

	# The application interface is a callable object
	def application ( # It accepts two arguments:
	    # environ points to a dictionary containing CGI like environment
	    # variables which is populated by the server for each
	    # received request from the client
	    environ,
	    # start_response is a callback function supplied by the server
	    # which takes the HTTP status and headers as arguments
	    start_response
	):

	    # Build the response body possibly
	    # using the supplied environ dictionary
	    response_body = 'Request method: %s' % environ['REQUEST_METHOD']

	    # HTTP response code and message
	    status = '200 OK'

	    # HTTP headers expected by the client
	    # They must be wrapped as a list of tupled pairs:
	    # [(Header name, Header value)].
	    response_headers = [
	        ('Content-Type', 'text/plain'),
	        ('Content-Length', str(len(response_body)))
	    ]

	    # Send them to the server using the supplied function
	    start_response(status, response_headers)

	    # Return the response body. Notice it is wrapped
	    # in a list although it could be any iterable.
	    return [response_body.encode('utf-8')]

## server1.py

	from wsgiref.validate import validator
	from wsgiref.simple_server import make_server, demo_app

	# This is the application wrapped in a validator
	validator_app = validator(demo_app)

	httpd = make_server('', 8000, validator_app)
	print("Listening on port 8000....")
	httpd.serve_forever()

## server2.py

	from wsgiref.validate import validator
	from wsgiref.simple_server import make_server
	from app import application

	# This is the application wrapped in a validator
	validator_app = validator(application)

	httpd = make_server('', 8000, validator_app)
	print("Listening on port 8000....")
	httpd.serve_forever()

## app2.py

	def application(environ, start_response):

	    # Sorting and stringifying the environment key, value pairs
	    response_body = [
	        '%s: %s' % (key, value) for key, value in sorted(environ.items())
	    ]
	    response_body = '\n'.join(response_body)

	    status = '200 OK'
	    response_headers = [
	        ('Content-Type', 'text/plain'),
	        ('Content-Length', str(len(response_body)))
	    ]
	    start_response(status, response_headers)

	    return [response_body.decode('utf-8')]

## utils.py

	import cgi
	from urllib.parse import parse_qs
	from warnings import warn
	from wsgiref.headers import Headers
	from wsgiref.util import request_uri


	def parse_http_get_data(environ):
	    qs = environ.get("QUERY_STRING", "")
	    if isinstance(qs, bytes):
	        qs = qs.decode('utf-8')
	    return parse_qs(qs)


	def parse_http_x_www_form_urlencoded_post_data(environ):
	    """
	    Parse HTTP 'application/x-www-form-urlencoded' post data.
	    """
	    try:
	        request_body_size = int(environ.get("CONTENT_LENGTH", 0))
	    except ValueError:
	        request_body_size = 0

	    CONTENT_TYPE, CONTENT_TYPE_KWARGS = parse_http_content_type(environ)
	    if CONTENT_TYPE != 'application/x-www-form-urlencoded':
	        warn(" * WARNING * Used parse_http_x_www_form_urlencoded_post_data "
	             "when CONTENT_TYPE != 'application/x-www-form-urlencoded'")
	        return {}

	    request_body_bytes = environ["wsgi.input"].read(request_body_size)
	    request_body_text = request_body_bytes.decode('utf-8')
	    body_query_dict = parse_qs(request_body_text)
	    return body_query_dict


	def parse_http_content_type(environ):
	    return cgi.parse_header(environ.get('CONTENT_TYPE', ''))


	def parse_http_headers(environ):
	    h = Headers([])
	    for k, v in environ.items():
	        if k.startswith('HTTP_'):
	            name = k[5:]
	            h.add_header(name, v)
	    return h


	def parse_http_uri(environ):
	    return request_uri(environ)


	def get_first_element(dict_, key, default=None):
	    """
	    Take one value by key from dict or return None.
	        >>> d = {"foo":[1,2,3], "baz":7}
	        >>> get_first_element(d, "foo")
	        1
	        >>> get_first_element(d, "bar") is None
	        True
	        >>> get_first_element(d, "bar", "") == ""
	        True
	        >>> get_first_element(d, "baz")
	        7
	    """
	    val = dict_.get(key, default)
	    if type(val) in (list, tuple) and len(val) > 0:
	        val = val[0]
	    return val

# GIT HELP

    git remote set-url origin https://github.com/USERNAME/OTHERREPOSITORY.git
    git remote add origin2 https://github.com/USERNAME/OTHERREPOSITORY.git
