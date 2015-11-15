from app_exceptions import *
import re
import ujson


def build_limit_rules_aql(limit_rules_str):
    limit_rules_str = limit_rules_str.strip()
    if not re.match("^[1-9][0-9]*$", limit_rules_str):
        raise LimitRuleException("Invalid limit")
    aql = "LIMIT {}".format(limit_rules_str)
    return aql


def is_instant_time_rules(time_rules_str):
    if not re.match("^=?[1-9][0-9]*$", time_rules_str.strip()):
        return False
    return True


def build_instant_time_rules_aql(time_rules_str):
    if is_instant_time_rules(time_rules_str) is False:
        return None
    time_rules_str = time_rules_str.strip()
    aql = "event.time<=" + time_rules_str.replace("=", "")
    return aql


def build_state_rules_aql(state_rules_str):
    aql = None
    states = set()
    for state_str in state_rules_str.split("|"):
        state_str = state_str.replace(" ", "").strip()
        if state_str not in ["assigned", "unassigned", "reserved",
                             "suspended", "resumed", "clean", "notified",
                             "cleaned", "deleted"]:
            raise stateRuleException("Invalid state rule")
        states.add(state_str)

    aql = "event.state IN {}".format(ujson.dumps(states))
    return aql
