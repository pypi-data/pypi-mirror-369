import hashlib


def passwrod2md5(password: str):
    '''
    Use the MD5 algorithm to encrypt user password

    Args:
        password:

    Returns:

    '''
    if password == None:
        return

    m = hashlib.md5(password.encode())
    return m.hexdigest().upper()


if __name__ == '__main__':
    ret = passwrod2md5('root')
    ret = passwrod2md5(ret)
    print(ret.upper())
