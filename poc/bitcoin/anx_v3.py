# http://docs.anxv3.apiary.io/#
# http://docs.anxv3.apiary.io/#reference/quick-start

import base64, hashlib, hmac, urllib, time, urllib, json
base = 'https://anxpro.com/'


def post_request(key, secret, path, data):
    hmac_obj = hmac.new(secret, path + chr(0) + data, hashlib.sha512)
    hmac_sign = base64.b64encode(hmac_obj.digest())

    header = {
        'Content-Type': 'application/json',
        'User-Agent': 'anxv2 based client',
        'Rest-Key': key,
        'Rest-Sign': hmac_sign,
    }

    proxy = urllib.ProxyHandler({'http': '127.0.0.1:8888'})
    opener = urllib.build_opener(proxy)
    urllib.install_opener(opener)

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
        # data = urllib.urlencode(params)
        data = json.dumps(params)

        result = post_request(self.key, self.secret, path, data)
        if result['result'] == 'success':
            return result['data']
        else:
            raise Exception(result['result'])

x = ANX('<key>', '<secret>')
result = x.request('api/3/order/list')