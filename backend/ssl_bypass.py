import requests
import ssl
from urllib3.exceptions import InsecureRequestWarning

# Désactive les alertes de sécurité SSL
requests.packages.urllib3.disable_warnings(category=InsecureRequestWarning)

# Forcer contexte SSL non vérifié globalement (utile si une lib crée sa propre session)
ssl._create_default_https_context = ssl._create_unverified_context

# Patch bas niveau : requests.Session.request
original_session_request = requests.Session.request
def unsafe_session_request(self, method, url, **kwargs):
    kwargs["verify"] = False
    return original_session_request(self, method, url, **kwargs)
requests.Session.request = unsafe_session_request

# Patch haut niveau : requests.request
original_request_function = requests.request
def unsafe_request_function(method, url, **kwargs):
    kwargs["verify"] = False
    return original_request_function(method, url, **kwargs)
requests.request = unsafe_request_function

# Bonus : patch get/post
original_get = requests.get
original_post = requests.post
def safe_get(*args, **kwargs):
    kwargs["verify"] = False
    return original_get(*args, **kwargs)
def safe_post(*args, **kwargs):
    kwargs["verify"] = False
    return original_post(*args, **kwargs)
requests.get = safe_get
requests.post = safe_post
