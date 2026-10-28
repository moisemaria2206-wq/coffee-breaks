def get_ip(request):
    str_lista_ip = request.META.get('HTTP_X_FORWARDED_FOR')
    if str_lista_ip:
        return str_lista_ip.split(',')[-1].strip()
    return request.META.get('REMOTE_ADDR')


class IPMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        request.ip_client = get_ip(request)
        return self.get_response(request)