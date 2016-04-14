from __future__ import unicode_literals

import logging
import sys
from threading import Lock

from django import http
from django.core import signals

from minidjango.core.handlers.base import BaseHandler
from minidjango.http.request import HttpRequest

logger = logging.getLogger('minidjango.request')


class WSGIHandler(BaseHandler):
    init_lock = Lock()
    request_class = HttpRequest

    def __call__(self, environ, start_response):
        # Set up middleware if needed. We couldn't do this earlier, because
        # settings weren't available.
        if self._middleware is None:
            with self.init_lock:
                try:
                    # Check that middleware is still uninitialized.
                    if self._middleware is None:
                        self.load_middleware()
                except:
                    # Unload whatever middleware we got
                    self._middleware = None
                    raise

        signals.request_started.send(sender=self.__class__, environ=environ)
        try:
            request = self.request_class(environ)
        except UnicodeDecodeError:
            logger.warning('Bad Request (UnicodeDecodeError)',
                exc_info=sys.exc_info(),
                extra={
                    'status_code': 400,
                }
            )
            response = http.HttpResponseBadRequest()
        else:
            response = self.get_response(request)

        response._handler_class = self.__class__

        status = '%s %s' % (response.status_code, response.reason_phrase)

        response_headers = [(str(k), str(v)) for k, v in response.items()]
        for c in response.cookies.values():
            response_headers.append(
                ('Set-Cookie', str(c.output(header='')))
            )

        start_response(status, response_headers)

        # some optimization
        response_file_to_stream = getattr(response, 'file_to_stream', None)
        file_wrapper = environ.get('wsgi.file_wrapper')
        if response_file_to_stream is not None and file_wrapper:
            response = file_wrapper(response.file_to_stream)
        return response
