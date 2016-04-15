import gitdata.local as db

db.load(['messages'])

from minidjango.core.wsgi import get_wsgi_application
application = get_wsgi_application()
