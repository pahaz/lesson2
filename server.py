from wsgiref.validate import validator
from wsgiref.simple_server import make_server
from app import application

httpd = make_server('', 8002, validator(application))
print("Listening on port 8002....")
httpd.serve_forever()
