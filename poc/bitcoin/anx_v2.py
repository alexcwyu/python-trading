# http://docs.anxv2.apiary.io/#reference/authentication

import base64, hashlib, hmac, urllib, time, urllib, json
base = 'https://anxpro.com/api/2/'


def post_request(key, secret, path, data):
    hmac_obj = hmac.new(secret, path + chr(0) + data, hashlib.sha512)
    hmac_sign = base64.b64encode(hmac_obj.digest())

    header = {
        'Content-Type': 'application/x-www-form-urlencoded',
        'User-Agent': 'anxv2 based client',
        'Rest-Key': key,
        'Rest-Sign': hmac_sign,
    }

    request = urllib.Request(base + path, data, header)
    response = urllib.urlopen(request, data)
    return json.load(response)


def gen_tonce():
    return str(int(time.time() * 1e6))


class ANX:

    def __init__(self, key, secret):
        self.key = key
        self.secret = base64.b64decode(secret)

    def request(self, path, params={}):
        params = dict(params)
        params['tonce'] = gen_tonce()
        data = urllib.urlencode(params)

        result = post_request(self.key, self.secret, path, data)
        if result['result'] == 'success':
            return result['data']
        else:
            raise Exception(result['result'])

x = ANX('<key>', '<secret>')
result = x.request('money/info')
print(result)
