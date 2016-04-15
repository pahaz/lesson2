from __future__ import unicode_literals
import logging
import sys
import types
from minidjango.conf import settings
from minidjango.core.exceptions import PermissionDenied
from minidjango.http import Http404, HttpResponse
from minidjango.http.request import RequestParseError
from minidjango.utils.module_loading import import_string

logger = logging.getLogger('minidjango.request')


class BaseHandler(object):
    def __init__(self):
        self._middleware = None

    def load_middleware(self):
        self._middleware = []

        for middleware_path in settings.MIDDLEWARE_CLASSES:
            mw_class = import_string(middleware_path)
            mw_instance = mw_class()
            self._middleware.append(mw_instance)

    def resolve(self, request_path):
        # TODO: write code here
        args = tuple()
        kwargs = {}
        from minidjango.conf import settings

        if request_path in settings.ROUTER:
            return settings.ROUTER[request_path], args, kwargs

        def index(request):
            return HttpResponse(b'HI!')

        return index, args, kwargs

    def get_response(self, request):
        "Returns an HttpResponse object for the given HttpRequest"

        try:
            response = None
            for middleware in self._middleware:
                response = middleware.process_request(request)
                if response:
                    break

            if response is None:
                resolver_match = self.resolve(request.path_info)
                callback, callback_args, callback_kwargs = resolver_match
                request.resolver_match = resolver_match

                # Apply view middleware
                for middleware in self._middleware:
                    response = middleware.process_view(
                        request, callback, callback_args, callback_kwargs
                    )
                    if response:
                        break

            if response is None:
                try:
                    response = callback(
                        request, *callback_args, **callback_kwargs
                    )
                except Exception as e:
                    response = self.process_exception_by_middleware(
                        e, request
                    )

            if response is None:
                if isinstance(callback, types.FunctionType):  # FBV
                    view_name = callback.__name__
                else:  # CBV
                    view_name = callback.__class__.__name__ + '.__call__'
                raise ValueError("The view %s.%s didn't return an HttpResponse"
                                 " object. It returned None instead."
                                 % (callback.__module__, view_name))

            # If the response supports deferred rendering, apply template
            # response middleware and then render the response
            if hasattr(response, 'render') and callable(response.render):
                try:
                    response = response.render()
                except Exception as e:
                    response = self.process_exception_by_middleware(e, request)

                response_is_rendered = True

        except Http404 as exc:
            logger.warning('Not Found: %s', request.path,
                           extra={
                               'status_code': 404,
                               'request': request
                           })
            response = self.get_exception_response(
                request, 404, exc)

        except PermissionDenied as exc:
            logger.warning(
                'Forbidden (Permission denied): %s', request.path,
                extra={
                    'status_code': 403,
                    'request': request
                })
            response = self.get_exception_response(
                request, 403, exc)

        except RequestParseError as exc:
            logger.warning(
                'Bad request (Unable to parse request body): %s', request.path,
                extra={
                    'status_code': 400,
                    'request': request
                })
            response = self.get_exception_response(
                request, 400, exc)

        except SystemExit:
            # Allow sys.exit() to actually exit. See tickets #1023 and #4701
            raise

        except:  # Handle everything else.
            # Get the exception info now, in case another exception is thrown later.
            response = self.handle_uncaught_exception(
                request, sys.exc_info())

        return response

    def process_exception_by_middleware(self, exception, request):
        raise

    def handle_uncaught_exception(self, request, exc_info):
        raise

    def get_exception_response(self, request, param, exc):
        pass
