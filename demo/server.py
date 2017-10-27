# -*- coding: UTF-8 -*-
from  wsgiref.simple_server import make_server
from handle import application
HOST, PORT = '', 9999
httpd = make_server(HOST,PORT,application)
print('Serving HTTP on port %s ...' % PORT)
httpd.serve_forever()