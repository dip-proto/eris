from context import Context
from event import Event
from filters import *
from flask import Response, abort
from helpers import *
from urlparse import urlparse
import netaddr
import re
import ujson


def build_time_rules_aql(time_rules_str):
    or_idx = time_rules_str.find("|")
    and_idx = time_rules_str.find("&")
    if or_idx != -1 and and_idx != -1:
        raise TimeRuleException("| and & cannot be mixed")
        op_char = None
    if or_idx != -1:
        op_char = "|"
        op_aql = "OR"
    else:
        op_char = "&"
        op_aql = "AND"
    aql = None
    for rule_str in time_rules_str.split(op_char):
        rule_str = rule_str.replace(" ", "").strip()
        if not re.match("^(=|<|<=|>|>=)?[1-9][0-9]*$", rule_str):
            raise TimeRuleException("Invalid time matching rule")
        if rule_str[0] == "=":
            rule_str = "=" + rule_str
        elif rule_str[0] != "<" and rule_str[0] != ">":
            rule_str = "==" + rule_str
        if aql is None:
            aql = "event.time" + rule_str
        else:
            aql = "{} {} event.time{}".format(aql, op_aql, rule_str)
    return aql


def retrieve(context, type, resource, time_rules_str, state_rules_str,
             limit_rules_str, owners_count):
    app = context.app
    arango = context.arango
    time_rules_aql = ""
    if time_rules_str:
        time_rules_aql = "AND ({})". \
          format(build_time_rules_aql(time_rules_str))
    state_rules_aql = ""
    if state_rules_str:
        state_rules_aql = "AND ({})". \
          format(build_state_rules_aql(state_rules_str))
    limit_rules_aql = ""
    if limit_rules_str:
        limit_rules_aql = build_limit_rules_aql(limit_rules_str)

    if type == "ip":
        if not is_ip(resource):
            abort(400)
        filter_aql = "event.type == 'ip' AND event.resource == @resource"
        bind_vars = {"resource": resource}
    elif type == "subnet":
        filter_aql = \
          "event.type == 'ip' AND " + \
          "event.ip_packed >= @ip_low AND event.ip_packed <= @ip_high"
        subnet = None
        try:
            subnet = netaddr.IPNetwork(resource)
        except netaddr.AddrFormatError:
            raise SubnetException("Invalid subnet input")
        ip_low = subnet.network.value
        ip_high = subnet.broadcast.value
        if ip_high - ip_low > app.config["MAX_SUBNET_SIZE"]:
            raise SubnetException("Subnet too large")
        bind_vars = {"ip_low": ip_low, "ip_high": ip_high}
    elif type == "nsrec":
        if not is_hostname(resource):
            abort(400)
        filter_aql = "event.type == 'nsrec' AND event.resource == @resource"
        bind_vars = {"resource": resource}
    elif type == "domain":
        if not is_hostname(resource):
            abort(400)
        filter_aql = "event.type == 'domain' AND event.resource == @resource"
        bind_vars = {"resource": resource}
    elif type == "email":
        if not is_email(resource):
            abort(400)
        filter_aql = "event.type == 'email' AND event.resource == @resource"
        bind_vars = {"resource": resource}
    elif type == "vhost":
        if not is_hostname(resource):
            abort(400)
        filter_aql = "event.type == 'vhost' AND event.resource == @resource"
        bind_vars = {"resource": resource}
    elif type == "uri":
        parsed = urlparse(resource, allow_fragments=False)
        if not (parsed.scheme and parsed.netloc):
            abort(400)
        uri = "{}://{}{}".format(parsed.scheme, parsed.netloc, parsed.path)
        filter_aql = "event.type == 'uri' AND event.resource == @resource"
        bind_vars = {"resource": resource}
    else:
        abort(404)

    if owners_count:
        aql = """
LET res = (
FOR event IN events
FILTER """ + filter_aql + """ {time} {state}
RETURN DISTINCT event.owner
)
RETURN {{ owners_count: LENGTH(res) }}
        """.format(time=time_rules_aql, state=state_rules_aql)
        events = arango.db.AQLQuery(aql, bindVars=bind_vars,
                                    batchSize=1000, rawResults=True)
        return Response(ujson.dumps(events.result[0]),
                        mimetype="application/json")
    else:
        aql = """
FOR event IN events
FILTER """ + filter_aql + """ {time} {state}
SORT event.time {limit} RETURN event
    """.format(time=time_rules_aql, state=state_rules_aql,
               limit=limit_rules_aql)
        events = arango.db.AQLQuery(aql, bindVars=bind_vars,
                                    batchSize=1000, rawResults=True)
        events = [Event(event).__dict__ for event in events.result]
        return Response(ujson.dumps(events, ensure_ascii=False),
                        mimetype="application/json")
