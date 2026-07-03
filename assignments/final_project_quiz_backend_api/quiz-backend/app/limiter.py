"""Shared rate limiter instance, imported by main.py and the routers.

Kept in its own module (rather than defined in main.py) so routers can
import it without a circular import back to main.py.
"""
from slowapi import Limiter
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)
