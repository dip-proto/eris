from assignableresources import *
from context import Context
from event import Event
from flask import Response, abort
import ujson


def retrieve(context, type, resource, time_rules_str):
    arango = context.arango
    time_rules_aql = ""
    if time_rules_str:
        time_rules_aql = "AND ({})".format(
          build_instant_time_rules_aql(time_rules_str))
    aql = """
FOR event IN events
FILTER event.resource == @resource {}
SORT event.time RETURN event
    """.format(time_rules_aql)
    events = arango.db.AQLQuery(aql, bindVars={"resource": resource},
                                batchSize=1000)
    resource = None
    if type == "ip":
        resource = IPResource()
    elif type == "nsrec":
        resource = NSRecResource()
    elif type == "email":
        resource = EmailResource()
    elif type == "domain":
        resource = DomainResource()
    elif type == "vhost":
        resource = VhostResource()
    elif type == "uri":
        uri = UriResource()
    else:
        abort(404)

    for event in events:
        state = event["state"]
        ts = event["time"]
        if state == "assigned":
            owner = event["owner"]
            resource.set_assigned(ts, owner)
        elif state == "unassigned":
            owner = event["owner"]
            resource.set_unassigned(ts, owner)
        elif state == "reserved":
            resource.set_reserved(ts)
        elif state == "suspended":
            resource.set_suspended(ts)
        elif state == "resumed":
            resource.set_resumed(ts)
        elif state == "clean":
            resource.set_clean(ts)
        elif state == "notified":
            resource.set_notified(ts)
        elif state == "cleaned":
            resource.set_cleaned(ts)
        elif state == "deleted":
            resource.set_deleted(ts)

    return Response(ujson.dumps(resource.__dict__, ensure_ascii=False),
                    mimetype="application/json")
