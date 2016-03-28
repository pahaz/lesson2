from utils import parse_http_get_data, get_first_element
import gitdata.local as db
db.load(['messages'])


def application(environ, start_response):
    status = '200 OK'
    with open('index.html', encoding='utf-8') as f:
        response_template = f.read()

    GET = parse_http_get_data(environ)
    name = get_first_element(GET, "name", '')
    message = get_first_element(GET, "message", '')

    if message:
        db.messages.append({'name': name, 'message': message})
        start_response('302 Found', [
            ('Content-Type', 'text/html'),
            ('Location', '/')])
        return [b'']

    response_body = response_template.format(
        name=name,
        messages=db.messages)

    response_headers = [
        ('Content-Type', 'text/html'),
        ('Content-Length', str(len(response_body)))
    ]

    start_response(status, response_headers)
    return [response_body.encode('utf-8')]
