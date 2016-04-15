import minidjango
from minidjango.core.handlers.wsgi import WSGIHandler


def get_wsgi_application():
    minidjango.setup()
    return WSGIHandler()
