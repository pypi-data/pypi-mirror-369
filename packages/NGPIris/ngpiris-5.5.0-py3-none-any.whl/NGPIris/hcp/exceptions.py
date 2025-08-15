class VPNConnectionError(Exception):
    pass

class NoBucketMounted(Exception):
    pass

class BucketNotFound(Exception):
    pass

class BucketForbidden(Exception):
    pass

class ObjectAlreadyExist(Exception):
    pass

class ObjectDoesNotExist(Exception):
    pass

class DownloadLimitReached(Exception):
    pass

class NotADirectory(Exception):
    pass