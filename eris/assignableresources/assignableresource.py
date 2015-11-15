from eris.owner import Owner
from eris.resource import Resource


class AssignableResource(Resource):
    def __init__(self):
        self.owners = []
        self.reserved = False
        self.suspended = False
        self.suspended_count = 0
        self.owners_count = 0
        self.total_owners_count = 0
        self.clean_at = None
        self.notified_at = None
        self.notified_count = 0
        self.deleted_at = None

    def set_assigned(self, ts, owner_id):
        owner = Owner(ts, owner_id)
        if owner in self.owners:
            assert self.reserved is False
            return False
        self.reserved = False
        self.owners.append(owner)
        self.owners_count = len(self.owners)
        self.total_owners_count = self.total_owners_count + 1
        return True

    def set_unassigned(self, ts, owner_id):
        owner = Owner(ts, owner_id)
        if owner not in self.owners:
            return False
        self.owners_count = len(self.owners)
        self.owners.remove(owner)
        return True

    def set_reserved(self, ts):
        if self.reserved:
            return False
        self.reserved = True
        self.suspended = False
        self.owners_count = 0
        self.owners = []
        return True

    def set_suspended(self, ts):
        if self.suspended:
            return False
        if self.reserved:
            return False
        if not self.owners:
            return False
        self.suspended = True
        self.suspended_count = self.suspended_count + 1
        return True

    def set_resumed(self, ts):
        if not self.suspended:
            return False
        if self.reserved:
            return False
        if not self.owners:
            return False
        self.suspended = False
        return True

    def set_clean(self, ts):
        self.clean_at = ts
        return True

    def set_notified(self, ts):
        if self.reserved:
            return False
        if not self.owners:
            return False
        self.notified_at = ts
        self.notified_count = self.notified_count + 1
        return True

    def set_cleaned(self, ts):
        self.clean_at = ts
        return True

    def set_deleted(self, ts):
        self.deleted_at = ts
        self.owners = []
        self.notified_count = 0
        self.reserved = False
        self.suspended = False
        self.suspended_count = 0
        self.owners_count = 0
        self.total_owners_count = 0
        self.clean_at = None
        self.notified_at = None
        return True
