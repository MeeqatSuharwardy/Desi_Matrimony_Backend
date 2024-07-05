try:
    from .common import *
except ModuleNotFoundError:
    raise Exception('No common.py file found')

DEBUG = False
# ALLOWED_HOSTS = ['localhost', '127.0.0.1', '0.0.0.0']
