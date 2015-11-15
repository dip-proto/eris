#! /usr/bin/env python

import ujson
import random
import time
import netaddr
from random import randrange, sample, getrandbits
from pyblake2 import blake2b
from pprint import pprint

TRANSITIONS = {
  None: {
    "assigned": (100, 0), "reserved": (1, 0)
  },
  "assigned": {
    "assigned": (100, 10), "unassigned": (100, 20), "clean": (1, 90),
    "cleaned": (10, 60), "notified": (10, 60)
  },
  "reserved": {
    "assigned": (80, 100), "deleted": (1, 100), "clean": (25, 100)
  },
  "unassigned": {
    "assigned": (100, 50), "reserved": (2, 100)
  },
  "suspended": {
    "unassigned": (100, 10), "notified": (100, 10), "resumed": (80, 10),
    "cleaned": (75, 10)
  },
  "resumed": {
    "unassigned": (1, 80), "suspended": (1, 100), "clean": (3, 10),
    "notified": (2, 60), "cleaned": (10, 10)
  },
  "clean": {
    "assigned": (30, 40), "unassigned": (40, 70), "suspended": (1, 100),
    "notified": (1, 100)
  },
  "notified": {
    "unassigned": (100, 30), "suspended": (100, 30), "clean": (50, 80),
    "cleaned": (100, 50)
  },
  "cleaned": {
    "unassigned": (80, 80), "suspended": (80, 80), "assigned": (100, 80)
  },
  "deleted": {

  }
}


class ResourceState(object):
    def __init__(self):
        self.assigned = []
        self.reserved = False
        self.suspended = False
        self.clean = False
        self.notified = False
        self.cleaned = False
        self.deleted = False
        self.dedicated = randrange(0, 3) == 0

    def set_assigned(self, owner):
        if owner in self.assigned:
            return False
        if self.reserved or self.suspended or self.deleted:
            return False
        if self.dedicated and self.assigned:
            return False
        self.assigned.append(owner)
        return True

    def set_unassigned(self, owner):
        if owner not in self.assigned:
            return False
        if self.reserved or self.suspended or self.deleted:
            return False
        self.assigned.remove(owner)
        return True

    def set_reserved(self):
        if self.assigned:
            return False
        if self.reserved:
            return False
        if self.suspended or self.deleted:
            return False
        self.assigned = []
        self.reserved = True
        self.suspended = False
        self.clean = False
        self.notified = False
        self.cleaned = True
        self.deleted = False
        return True

    def set_suspended(self):
        if (not self.assigned) or self.reserved or self.deleted:
            return False
        if self.suspended:
            return False
        if self.cleaned:
            return False
        self.suspended = True
        return True

    def set_resumed(self):
        if (not self.assigned) or self.reserved or self.deleted:
            return False
        if not self.suspended:
            return False
        self.suspended = False
        return True

    def set_clean(self):
        if (not self.assigned) and (not self.reserved):
            return False
        if self.suspended or self.deleted:
            return False
        if self.cleaned:
            return False
        self.clean = True
        return True

    def set_notified(self):
        if (not self.assigned):
            return False
        if self.reserved or self.deleted:
            return False
        if self.clean or self.cleaned:
            return False
        self.notified = True
        return True

    def set_cleaned(self):
        if (not self.assigned) or self.reserved or self.deleted:
            return False
        if self.clean:
            return False
        if self.cleaned:
            return False
        self.cleaned = True
        return True

    def set_deleted(self):
        if self.deleted:
            return False
        self.deleted = True
        return True

    def apply_transition(self, transition):
        switcher = {
          "assigned": self.set_assigned,
          "reserved": self.set_reserved,
          "unassigned": self.set_unassigned,
          "suspended": self.set_suspended,
          "resumed": self.set_resumed,
          "clean": self.set_clean,
          "notified": self.set_notified,
          "cleaned": self.set_cleaned,
          "deleted": self.set_deleted
        }
        switcher[transition]()


class Resource(object):
    def __init__(self, type, resource):
        self.last_event = None
        self.type = type
        self.resource = resource
        self.state = ResourceState()

    def pick_transition(self):
        if self.last_event:
            options = TRANSITIONS[self.last_event.event['state']]
        else:
            options = TRANSITIONS[None]
        tw = sum([w for (w, t) in options.values()])
        if tw <= 0:
            return (None, 0)
        point = randrange(tw)
        pos = 0
        chosen = None
        delay = 0
        for k, v in options.iteritems():
            w, t = v
            if point >= pos and point < pos + w:
                chosen = k
                delay = t
                break
            pos = pos + w
        delay = delay * 32000 + 1
        delay = randrange(delay - delay / 2, delay + delay * 2)
        return (chosen, delay)

    def transition(self):
        pass


class Resources(object):
    def __init__(self, type):
        self.type = type
        self.resources = []

    def pick(self):
        resource = None
        if (not self.resources) or randrange(0, 17) == 0:
            if self.type == "ip":
                ip = "%u.%u.%u.%u" % (randrange(0, 255), randrange(0, 255),
                                      randrange(0, 255), randrange(0, 255))
                resource = Resource(self.type, ip)
            elif self.type == "nsrec":
                nsrec = "{}.com".format(blake2b(str(getrandbits(128)), 4).
                                        hexdigest())
                resource = Resource(self.type, nsrec)
            elif self.type == "email":
                nsrec = "x@{}.com".format(blake2b(str(getrandbits(128)), 4).
                                          hexdigest())
                resource = Resource(self.type, nsrec)
            elif self.type == "domain":
                nsrec = "{}.com".format(blake2b(str(getrandbits(128)), 4).
                                        hexdigest())
                resource = Resource(self.type, nsrec)
            elif self.type == "vhost":
                vhost = "vh-{}.com".format(blake2b(str(getrandbits(128)), 1).
                                           hexdigest())
                resource = Resource(self.type, vhost)
            elif self.type == "uri":
                uri = "http://vh-{}.com/{}.html". \
                    format(blake2b(str(getrandbits(128)), 1).hexdigest(),
                           blake2b(str(getrandbits(128)), 16).hexdigest())
                resource = Resource(self.type, uri)
            else:
                abort()

            for r in self.resources:
                if r.type == resource.type and r.resource == resource.resource:
                    return r
            self.resources.append(resource)
        else:
            resource = sample(self.resources, 1)[0]
        return resource

    def delete(self, resource):
        del self.resources[self.resources.index(resource)]


class Owners(object):
    def __init__(self):
        self.owners = set()

    def pick(self):
        owner = None
        if self.owners and randrange(0, 1000) == 0:
            owner = sample(self.owners, 1)[0]
        else:
            owner = blake2b(str(getrandbits(128)), 16).hexdigest()
            self.owners.add(owner)
        return owner


class Event(object):
    def __init__(self, resource, transition, ts, **kwargs):
        event = {}
        event['id'] = blake2b(str(getrandbits(128)), 16).hexdigest()
        event['time'] = ts
        event['type'] = resource.type
        event['resource'] = resource.resource
        event['state'] = transition
        event['source'] = 'OVH'
        event['depth'] = 0
        if resource.type == "ip":
            event['ip_packed'] = netaddr.IPAddress(event['resource']).value
        self.event = event
        self.id = event['id']
        self.ts = event['time']
        for k, v in kwargs.iteritems():
            event[k] = v
        print(ujson.dumps(event))


owners = Owners()
resources_all = [Resources("ip"), Resources("nsrec"), Resources("email"),
                 Resources("domain"), Resources("vhost"), Resources("uri")]
owner = None
base_ts = int(time.time() - 86400 * 365)

for _ in range(0, 100000 * 4):
    while True:
        resources = random.choice(resources_all)
        resource = resources.pick()
        if resource:
            break

    transition, delay = resource.pick_transition()
    if transition == "assigned":
        owner = owners.pick()
        if resource.state.set_assigned(owner) == True:
            if resource.last_event:
                ts = resource.last_event.ts + delay
            else:
                ts = base_ts + delay
            event = Event(resource, transition, ts, owner=owner)
            resource.last_event = event
    elif transition == "clean":
        if resource.state.set_clean() == True:
            if resource.last_event:
                ts = resource.last_event.ts + delay
            else:
                ts = base_ts + delay
            event = Event(resource, transition, ts)
            resource.last_event = event
    elif transition == "unassigned":
        if resource.state.assigned:
            owner = sample(resource.state.assigned, 1)[0]
            if resource.state.set_unassigned(owner) == True:
                if resource.last_event:
                    ts = resource.last_event.ts + delay
                else:
                    ts = base_ts + delay
                event = Event(resource, transition, ts, owner=owner)
                resource.last_event = event
    elif transition == "reserved":
        if resource.state.set_reserved() == True:
            if resource.last_event:
                ts = resource.last_event.ts + delay
            else:
                ts = base_ts + delay
            event = Event(resource, transition, ts)
            resource.last_event = event
    elif transition == "notified":
        if resource.state.set_notified() == True:
            if resource.last_event:
                ts = resource.last_event.ts + delay
            else:
                ts = base_ts + delay
            event = Event(resource, transition, ts)
            resource.last_event = event
    elif transition == "suspended":
        if resource.state.set_suspended() == True:
            if resource.last_event:
                ts = resource.last_event.ts + delay
            else:
                ts = base_ts + delay
            event = Event(resource, transition, ts)
            resource.last_event = event
    elif transition == "cleaned":
        if resource.state.set_cleaned() == True:
            if resource.last_event:
                ts = resource.last_event.ts + delay
            else:
                ts = base_ts + delay
            event = Event(resource, transition, ts)
            resource.last_event = event
    elif transition == "deleted":
        if resource.state.set_deleted() == True:
            if resource.last_event:
                ts = resource.last_event.ts + delay
            else:
                ts = base_ts + delay
            event = Event(resource, transition, ts)
            resource.last_event = event
    elif transition == "resumed":
        if resource.state.set_resumed() == True:
            if resource.last_event:
                ts = resource.last_event.ts + delay
            else:
                ts = base_ts + delay
            event = Event(resource, transition, ts)
            resource.last_event = event
    elif transition is None:
        pass
    else:
        die()

    now = int(time.time())
    if resource.last_event.ts > now:
        resources.delete(resource)
