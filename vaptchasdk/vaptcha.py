# -*- coding: UTF-8 -*-
import base64
import hmac
import time
try:
    import urllib2 as _request
except ImportError:
    import urllib.request as _request
from hashlib import sha1
from hashlib import md5


class config(object):
    # SDK版本号
    VERSION = '1.0.0'
    # SDK语言
    SDK_LANG = 'python'
    # VaptchaAPI Url
    API_URL = 'http://api.vaptcha.com'
    # 获取流水号 Url
    GET_CHALLENGE_URL = '/challenge'
    # 验证 Url
    VALIDATE_URL = '/validate'
    # 验证数量使用完
    REQUEST_UESD_UP = '0209'

    # 宕机模式检验恢复时间=ms
    DOWNTIME_CHECK_TIME = 185000
    # 宕机模式二次验证失效时间=ms
    VALIDATE_PASS_TIME = 600000
    # 宕机模式请求失效的时间=ms
    REQUEST_ABATE_TIME = 250000
    # 宕机模式验证等待时间=ms
    VALIDATE_WAIT_TIME = 2000

    # 宕机模式保存通过数量最大值=50000
    MAX_LENGTH = 50000
    # 验证图的后缀
    PIC_POST_FIX = ".png"
    # 宕机模式key路径
    PUBLIC_KEY_PATH = "http://down.vaptcha.com/publickey"
    # 是否宕机路径
    IS_DOWN_PATH = "http://static.vaptcha.com/isdown"
    # 宕机模式图片路径
    DOWN_TIME_PATH = "downtime/"


class vaptcha(object):
    def __init__(self, id, key):
        self.__id = id
        self.__key = key
        self.__isDown = False
        self.__publicKey = None
        self.__lastCheckDownTime = 0
        self.__passedSignatures = []
        self.get_challenge = self.__get_challenge
        self.validate = self.__validate
        self.downtime = self.__downtime

    def __get_challenge(self, scene_id=''):
        url = config.API_URL + config.GET_CHALLENGE_URL
        now = self.__to_unix_time(time.time())
        query = 'id=' + self.__id + '&scene=' + scene_id + '&time=' + str(now)
        signature = self.__hmac_sha1(self.__key, query)
        if not self.__isDown:
            _url = url + "?" + query + "&signature=" + signature
            challenge = self.__get_request(_url)
            predicate_one = challenge == config.REQUEST_UESD_UP
            predicate_two = not bool(challenge) and self.__get_isdown()
            if predicate_one or predicate_two:
                self.__lastCheckDownTime = now
                self.__isDown = True
                self.__lastCheckDownTime = []
                return self.__get_downtim_captcha()
            return '{' + '"vid":"{0}","challenge":"{1}"'.format(str(self.__id), str(challenge)) + '}'
        else:
            if now - self.__lastCheckDownTime > config.DOWNTIME_CHECK_TIME:
                self.__lastCheckDownTime = now
                challenge = self.__get_request(url)
                if bool(challenge) and (challenge != config.REQUEST_UESD_UP):
                    self.__isDown = False
                    self.__passedSignatures = []
                    return '{' + '"vid":"{0}","challenge":"{1}"'.format(str(self.__id), str(challenge)) + '}'
            return self.__get_downtim_captcha()

    def __validate(self, challenge, token, scene_id=''):
        if not self.__isDown and bool(challenge):
            return self.__normal_validate(challenge, token, scene_id)
        else:
            return self.__downtime_validate(token)

    def __downtime(self, data):
        if not bool(data):
            return '{"error":"parms error"}'
        datas = str(data).split(',')
        if datas[0] == "request":
            return self.__get_downtim_captcha()
        elif datas[0] == "getsignature":
            if datas.__len__() < 2:
                return '{"error":"parms error"}'
            else:
                try:
                    _time = int(datas[1])
                    return self.__get_signature(_time)
                except :
                    return '{"error":"parms error"}'
        elif datas[0] == "check":
            if datas.__len__() < 5:
                return '{"error":"parms error"}'
            else:
                try:
                    time1 = int(datas[1])
                    time2 = int(datas[2])
                    signature = datas[3]
                    captcha = datas[4]
                    return self.__down_time_check(time1, time2, signature, captcha)
                except:
                    return '{"error":"parms error"}'
        else:
            return '{"error":"parms error"}'

    def __normal_validate(self, challenge, token, scene_id):
        if not bool(token) or not bool(challenge) or token != self.__md5_encode(self.__key + "vaptcha" + challenge):
            return False
        url = config.API_URL + config.VALIDATE_URL
        query = "id={0}&scene={1}&token={2}&time={3}".format(
            self.__id, scene_id, token, self.__to_unix_time(time.time()))
        signature = self.__hmac_sha1(self.__key, query)
        response = self.__post_request(url, query + "&signature=" + signature)
        return response == "success"

    def __downtime_validate(self, token):
        if not bool(token):
            return False
        strs = str(token).split(',')
        if strs.__len__() < 2:
            return False
        else:
            _time = int(strs[0])
            signature = strs[1]
            now = self.__to_unix_time(time.time())
            if now - _time > config.VALIDATE_PASS_TIME:
                return False
            else:
                signatureTrue = self.__md5_encode(
                    str(_time) + self.__key + "vaptcha")
                if signature == signatureTrue:
                    if(self.__passedSignatures.count(signature) != 0):
                        return False
                    else:
                        self.__passedSignatures.append(signature)
                        length = self.__passedSignatures.__len__()
                        if length >= config.MAX_LENGTH:
                            del self.__passedSignatures[0:length -
                                                        config.MAX_LENGTH + 1]
                        return True
                else:
                    return False

    def __get_signature(self, _time):
        now = self.__to_unix_time(time.time())
        if (now - _time) > config.REQUEST_ABATE_TIME:
            return None
        signature = self.__md5_encode(str(now) + self.__key)
        return '{' + '"time":"{0}","signature":"{1}"'.format(now, signature) + '}'

    def __down_time_check(self, time1, time2, signature, captcha):
        now = self.__to_unix_time(time.time())
        if now - time1 > config.REQUEST_ABATE_TIME or signature != self.__md5_encode(str(time2) + self.__key) or now - time2 < config.VALIDATE_WAIT_TIME:
            return '{"result":false}'
        trueCaptcha = self.__md5_encode(str(time1) + self.__key)[0:3]
        if trueCaptcha == str(captcha).lower():
            return '{' + '"result":true,"token":"{0}"'.format(str(now) + ',' + self.__md5_encode(str(now) + self.__key + 'vaptcha')) + '}'
        else:
            return '{"result":false}'

    def __hmac_sha1(self, key, text):
        encrypts = hmac.new(key.encode(), text.encode(), sha1).digest()
        signature = base64.b64encode(encrypts)
        result = signature.decode('utf-8').replace('=', '').replace('/', '').replace('+', '')
        return result

    def __get_request(self, url):
        try:
            req = _request.urlopen(url, timeout=2)         
            res = req.read()
            if res:
                return res.decode('utf-8')
            return ''
        except:
            return ''

    def __post_request(self, url, data):
        try:
            req = _request.urlopen(
                url, data=data.encode('utf-8'), timeout=2)
            res = req.read()
            if res:
                return res.decode('utf-8')
            return ''
        except:
            return ''

    def __get_isdown(self):
        result = self.__get_request(config.IS_DOWN_PATH)
        return bool(result)

    def __get_downtim_captcha(self):
        now = self.__to_unix_time(time.time())
        md5 = self.__md5_encode(str(now) + self.__key)
        captcha = md5[0:3]
        verificationKey = md5[30:]
        if not bool(self.__publicKey):
            self.__publicKey = self.__get_public_key()
        url = self.__md5_encode(
            captcha + verificationKey + self.__publicKey) + config.PIC_POST_FIX
        url = config.DOWN_TIME_PATH + url
        return '{' + '"time":"{0}","url":"{1}"'.format(str(now), str(url)) + '}'

    def __get_public_key(self):
        return self.__get_request(config.PUBLIC_KEY_PATH)

    def __to_unix_time(self, time_param):
        return int(time_param * 1000)

    def __md5_encode(self, text):
        _md5 = md5()
        _md5.update(text.encode())
        return _md5.hexdigest()