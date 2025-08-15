
from base64 import b64encode
from hashlib import md5

def base64_hashing(string : str) -> str:
    return (b64encode(string.encode('ascii'))).decode('UTF-8')

def md5_hashing(string : str) -> str:
    return md5(string.encode('ascii')).hexdigest()