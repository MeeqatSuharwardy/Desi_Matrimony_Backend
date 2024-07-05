try:
    from .common import *
except ModuleNotFoundError:
    raise Exception('No common.py file found')

DEBUG = True
