import requests

_original_request = requests.Session.request

def _patched_request(self, method, url, *args, **kwargs):
    kwargs['verify'] = False  # Отключаем проверку SSL
    return _original_request(self, method, url, *args, **kwargs)

requests.Session.request = _patched_request
