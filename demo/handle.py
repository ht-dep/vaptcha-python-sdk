# -*- coding: UTF-8 -*-
import os
import json
from vaptchasdk import vaptcha
VAPTCHAVID, VAPTHCHAKEY = 'xxxxxxxxxxxxxxxxxxxxxxxx', 'xxxxxxxxxxxxxxxxxxxxxxxx'
work_dir = os.path.dirname(os.path.abspath(__file__))
_vaptcha = vaptcha(VAPTCHAVID, VAPTHCHAKEY)

def application(environ, start_response):

    method = environ['REQUEST_METHOD']
    path = environ['PATH_INFO']
    stream = None
    if method == 'GET' and path == '/':
        start_response('200 OK', [('Content-Type', 'text/html')])
        with open(work_dir + '/templates/index.html', 'r') as f:
            # ascii to str
            fstr = f.read().decode('utf-8')
            stream = fstr.decode('utf-8').encode('utf-8')
        return [stream]
    elif method == 'GET' and path == '/getVaptcha':
        start_response('200 OK', [('Content-Type', 'application/json')])
        return _get_challenge()
    elif method == 'POST' and path == '/login':
        start_response('200 OK', [('Content-Type', 'application/json')])
        result = environ['wsgi.input'].read(
            int(environ['CONTENT_LENGTH'] or 0)).decode('utf-8')
        result = json.loads(str(result))
        return _validate(result['challenge'], result['token'])
    elif method == 'GET' and path == '/getDowTime':
        start_response('200 OK', [('Content-Type', 'application/json')])
        result = environ['QUERY_STRING']
        return _get_downtime(str(result).split('=')[1])
    else:
        try:
            _type = str(path).split('.')[1]
            if _type =='js':
                _type = 'javascript'
            start_response('200 OK', [('Content-Type', 'text/'+_type)])            
            with open(work_dir + '/templates'+path, 'r') as f:
                # ascii to str
                fstr = f.read().decode('utf-8')
                stream = fstr.encode('utf-8')
                return [stream]
        except:        
            return [b'<h1>404</h1>']


def _get_challenge():
    return [_vaptcha.get_challenge().encode('utf-8')]


def _validate(_challenge, _token):
    result = _vaptcha.validate(_challenge, _token)
    if(result):
        return ['{"msg":"success"}'.encode('utf-8')]
    else:
        return ['{"msg":"fail"}'.encode('utf-8')]


def _get_downtime(data):
    return [_vaptcha.downtime(data).encode('utf-8')]
