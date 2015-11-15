from assignableresources import *
from context import Context
from app_exceptions import *
from flask import Flask, request, Response, abort
from flask_arango import Arango
import ujson


app = Flask(__name__)
app.config.from_object('config.default_settings')
app.config.from_pyfile('eris.cfg', silent=True)
arango = Arango(app)
context = Context(app=app, arango=arango)


def inject_from_dict(event):
    if "type" not in event:
        return False
    event_type = event["type"]
    if event_type == "ip":
        IPResource.inject_from_dict(event)
    elif event_type == "subnet":
        raise NotImplementedException
    elif event_type == "nsrec":
        NSRecResource.inject_from_dict(event)
    elif event_type == "email":
        EmailResource.inject_from_dict(event)
    elif event_type == "domain":
        DomainResource.inject_from_dict(event)
    elif event_type == "vhost":
        VhostResource.inject_from_dict(event)
    elif event_type == "uri":
        UriResource.inject_from_dict(event)
    else:
        raise TypeException

    return True


@app.route('/ping')
def ping():
    return Response("Pong", mimetype="text/plain")


@app.route('/upload', methods=['POST'])
def upload():
    lines = request.get_data()
    content = None
    for line in lines.splitlines():
        event = None
        try:
            event = ujson.loads(line.strip())
        except ValueError:
            continue
        inject_from_dict(event)
        content = ujson.dumps(event)
    return "content"


def run():
    app.run(host=app.config.get("HOST", "localhost"),
            port=app.config.get("PORT", 4999))
