from assignableresources import *
from context import Context
from app_exceptions import *
from filters import is_instant_time_rules
from flask import Flask, request, Response, abort, send_from_directory, jsonify
from flask_arango import Arango
from flask_swagger import swagger
import instant
import os
import timeframe


app = Flask(__name__)
app.config.from_object('config.default_settings')
app.config.from_pyfile('eris.cfg', silent=True)
arango = Arango(app)
context = Context(app=app, arango=arango)


@app.route('/ping')
def ping():
    """
Send a ping query
---
tags:
  - ping
parameters:
  - in: query
    name: time
    description: timestamp
    required: false
    type: integer
  - in: states
    name: states
    description: states
    required: false
    type: string
responses:
  200:
    description: pong received
    """
    return Response("Pong", mimetype="text/plain")


@app.route("/ip/<path:ip>")
def query_ip(ip):
    """
Retrieve DIP data about an IP address
---
tags:
  - ip
parameters:
  - in: path
    name: ip
    description: IP address
    required: true
    type: string
  - in: query
    name: time
    description: timestamp
    required: false
    type: integer
  - in: query
    name: state
    description: state
    required: false
    type: string
  - in: query
    name: limit
    description: limit
    required: false
    type: integer
  - in: query
    name: owners_count
    description: compute the number of owners
    required: false
    type: boolean
responses:
  200:
    description: response
    """
    return query_any("ip", ip)


@app.route("/subnet/<path:subnet>")
def query_subnet(subnet):
    """
Retrieve DIP data about a subnet
---
tags:
  - subnet
parameters:
  - in: path
    name: subnet
    description: subnet/mask
    required: true
    type: string
  - in: query
    name: time
    description: timestamp
    required: false
    type: integer
  - in: query
    name: state
    description: state
    required: false
    type: string
  - in: query
    name: limit
    description: limit
    required: false
    type: integer
  - in: query
    name: owners_count
    description: compute the number of owners
    required: false
    type: boolean
responses:
  200:
    description: response
    """
    return query_any("subnet", subnet)


@app.route("/nsrec/<path:nsrec>")
def query_nsrec(nsrec):
    """
Retrieve DIP data about a name server record
---
tags:
  - nsrec
parameters:
  - in: path
    name: nsrec
    description: name server record
    required: true
    type: string
  - in: query
    name: time
    description: timestamp
    required: false
    type: integer
  - in: query
    name: state
    description: state
    required: false
    type: string
  - in: query
    name: limit
    description: limit
    required: false
    type: integer
  - in: query
    name: owners_count
    description: compute the number of owners
    required: false
    type: boolean
responses:
  200:
    description: response
    """
    return query_any("nsrec", nsrec)


@app.route("/email/<path:email>")
def query_email(email):
    """
Retrieve DIP data about an email address
---
tags:
  - email
parameters:
  - in: path
    name: email
    description: email address
    required: true
    type: string
  - in: query
    name: time
    description: timestamp
    required: false
    type: integer
  - in: query
    name: state
    description: state
    required: false
    type: string
  - in: query
    name: limit
    description: limit
    required: false
    type: integer
  - in: query
    name: owners_count
    description: compute the number of owners
    required: false
    type: boolean
responses:
  200:
    description: response
    """
    return query_any("email", email)


@app.route("/domain/<path:domain>")
def query_domain(domain):
    """
Retrieve DIP data about a domain
---
tags:
  - domain
parameters:
  - in: path
    name: domain
    description: domain name
    required: true
    type: string
  - in: query
    name: time
    description: timestamp
    required: false
    type: integer
  - in: query
    name: state
    description: state
    required: false
    type: string
  - in: query
    name: limit
    description: limit
    required: false
    type: integer
  - in: query
    name: owners_count
    description: compute the number of owners
    required: false
    type: boolean
responses:
  200:
    description: response
    """
    return query_any("domain", domain)


@app.route("/vhost/<path:vhost>")
def query_vhost(vhost):
    """
Retrieve DIP data about a website
---
tags:
  - vhost
parameters:
  - in: path
    name: vhost
    description: vhost of a website
    required: true
    type: string
  - in: query
    name: time
    description: timestamp
    required: false
    type: integer
  - in: query
    name: state
    description: state
    required: false
    type: string
  - in: query
    name: limit
    description: limit
    required: false
    type: integer
  - in: query
    name: owners_count
    description: compute the number of owners
    required: false
    type: boolean
responses:
  200:
    description: response
    """
    return query_any("vhost", vhost)


@app.route("/uri/<path:uri>")
def query_uri(uri):
    """
Retrieve DIP data about a URI
---
tags:
  - vhost
parameters:
  - in: path
    name: uri
    description: URI
    required: true
    type: string
  - in: query
    name: time
    description: timestamp
    required: false
    type: integer
  - in: query
    name: state
    description: state
    required: false
    type: string
  - in: query
    name: limit
    description: limit
    required: false
    type: integer
  - in: query
    name: owners_count
    description: compute the number of owners
    required: false
    type: boolean
responses:
  200:
    description: response
    """
    return query_any("uri", uri)


@app.route("/<string:type>/<path:resource>")
def query_any(type, resource):
    """
Retrieve DIP data
---
tags:
  - any
parameters:
  - in: path
    name: type
    description: type
    required: true
    type: string
  - in: path
    name: resource
    description: resource
    required: true
    type: string
  - in: query
    name: time
    description: timestamp
    required: false
    type: integer
  - in: query
    name: state
    description: state
    required: false
    type: string
  - in: query
    name: limit
    description: limit
    required: false
    type: integer
  - in: query
    name: owners_count
    description: compute the number of owners
    required: false
    type: boolean
responses:
  200:
    description: response
    """
    time_rules_str = request.args.get("time")
    state_rules_str = request.args.get("state")
    limit_rules_str = request.args.get("limit")
    owners_count_str = request.args.get("owners_count")
    owners_count = owners_count_str is not None
    if (time_rules_str is None) or is_instant_time_rules(time_rules_str):
        return instant.retrieve(context, type, resource, time_rules_str)
    else:
        return timeframe.retrieve(context, type, resource, time_rules_str,
                                  state_rules_str, limit_rules_str,
                                  owners_count)


@app.route("/swagger/<path:path>")
def send(path):
    f_path = os.path.dirname(os.path.abspath(__file__))
    swui_path = os.path.join(os.path.dirname(f_path), "swagger-ui")
    print swui_path
    return send_from_directory(swui_path, path)


@app.route("/spec")
def spec():
    swag = swagger(app)
    swag['info']['version'] = "0.1"
    swag['info']['title'] = "ERIS"
    return jsonify(swag)


def run():
    app.run(host=app.config.get("HOST", "localhost"),
            port=app.config.get("PORT", 5000))
