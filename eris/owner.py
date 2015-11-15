
class Owner(object):
    def __init__(self, since, id):
        self.id = id
        self.since = since

    def __eq__(self, other):
        return self.id == other.id
