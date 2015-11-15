from assignableresource import AssignableResource
from eris.app_exceptions import *
from eris.helpers import *
import time


def ensure_notempty(dict, property, expected_type):
    if property not in dict:
        raise IncompleteException("{} property missing".format(property))
    val = dict[property]
    if isinstance(val, unicode):
        val = val.strip()
        if not val:
            raise IncompleteException("{} property is empty".format(property))
    if type(val).__name__ != expected_type:
        raise IncompleteException("{} property should be of type {}, found {}".
                                  format(property, expected_type,
                                         type(val).__name__))


def ensure_base_properties(dict):
    BASE_PROPERTIES = [("time", "int"), ("id", "unicode"),
                       ("source", "unicode"), ("depth", "int"),
                       ("state", "unicode"), ("resource", "unicode"),
                       ("type", "unicode")]
    STATES = ["assigned", "unassigned", "reserved", "suspended", "resumed",
              "clean", "notified", "cleaned", "deleted"]
    TYPES = ["ip", "subnet", "nsrec", "email", "domain", "vhost", "uri"]
    for (property, type) in BASE_PROPERTIES:
        ensure_notempty(dict, property, type)

    now = time.time()
    ts = dict["time"]
    if False and (ts > now or ts <= 0):
        raise TimeException()
    depth = dict["depth"]
    if depth < 0:
        raise DepthException()
    state = dict["state"]
    if state not in STATES:
        raise StateException()
    type = dict["type"]
    if type not in TYPES:
        raise TypeException()
    if type == "subnet":
        raise NotImplementedException()


class IPResource(AssignableResource):
    def __init__(self):
        super(IPResource, self).__init__()
        self.type = "ip"

    @staticmethod
    def inject_from_dict(dict):
        ensure_base_properties(dict)
        if not is_ip(dict["resource"]):
            raise IPException()


class NSRecResource(AssignableResource):
    def __init__(self):
        super(NSRecResource, self).__init__()
        self.type = "nsrec"

    @staticmethod
    def inject_from_dict(dict):
        ensure_base_properties(dict)
        if not is_hostname(dict["resource"]):
            raise NSRecException()


class EmailResource(AssignableResource):
    def __init__(self):
        super(EmailResource, self).__init__()
        self.type = "email"

    @staticmethod
    def inject_from_dict(dict):
        ensure_base_properties(dict)
        if not is_email(dict["resource"]):
            raise EmailException()


class DomainResource(AssignableResource):
    def __init__(self):
        super(DomainResource, self).__init__()
        self.type = "domain"

    @staticmethod
    def inject_from_dict(dict):
        ensure_base_properties(dict)
        if not is_hostname(dict["resource"]):
            raise DomainException()


class VhostResource(AssignableResource):
    def __init__(self):
        super(VhostResource, self).__init__()
        self.type = "vhost"

    @staticmethod
    def inject_from_dict(dict):
        ensure_base_properties(dict)
        if not is_hostname(dict["resource"]):
            raise VhostException()


class UriResource(AssignableResource):
    def __init__(self):
        super(UriResource, self).__init__()
        self.type = "uri"

    @staticmethod
    def inject_from_dict(dict):
        ensure_base_properties(dict)
        if not is_uri(dict["resource"]):
            raise UriException()
