import requests


def checkHost(host: str) -> bool:
    if host is not None and host.startswith('http'):
        raise ValueError(f'Invalid url: {host}')
    try:
        response = requests.get(f'https://{host}', timeout=5)
        if response.status_code < 400:
            return True
    except requests.RequestException:
        return False
    return False
