#from w3lib.http import basic_auth_header


class CustomProxyMiddleware(object):
    def process_request(self, request, spider):
        request.meta['proxy'] = "https://12.183.155.185:49001"
        #request.headers['Proxy-Authorization'] = basic_auth_header(
        #    '<PROXY_USERNAME>', '<PROXY_PASSWORD>')