import gitdata.local as db
from minidjango.http import HttpResponse
db.load(['messages'])

from minidjango.core.wsgi import get_wsgi_application
from minidjango.conf import settings

settings.ROUTER['/'] = lambda r: HttpResponse('helllo!')
application = get_wsgi_application()
