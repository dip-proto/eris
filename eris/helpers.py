from validate_email import validate_email
from urlparse import urlparse
import netaddr
import re


def is_ip(resource):
    try:
        netaddr.IPAddress(resource)
        return True
    except netaddr.AddrFormatError:
        return False


def is_hostname(resource):
    if re.match("^([a-zA-Z\d-]{,63})+\.[a-zA-Z\d-]{1,63}$", resource):
        return True
    return False


def is_email(resource):
    if validate_email(resource):
        return True
    return False


def is_uri(resource):
    try:
        parsed = urlparse(resource, allow_fragments=False)
    except BaseException:
        return False
    if parsed.scheme and parsed.netloc:
        return True
    return False
