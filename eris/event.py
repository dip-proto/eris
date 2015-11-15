class Event(object):
    def __init__(self, adb_res):
        self.time = adb_res["time"]
        self.id = adb_res["_key"]
        self.type = adb_res["type"]
        self.resource = adb_res["resource"]
        self.state = adb_res["state"]
        self.source = adb_res["source"]
        self.depth = adb_res["depth"]
        if "owner" in adb_res:
            self.owner = adb_res["owner"]
        if "related" in adb_res:
            self.related = adb_res["related"]
