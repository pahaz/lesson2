from wsgiref.simple_server import make_server, demo_app

httpd = make_server('', 8001, demo_app)
print("Listening on port 8001....")
httpd.serve_forever()
