import socket
import netifaces


def is_connected():
    try:
        host = socket.gethostbyname('google.com')
        s = socket.create_connection((host, 80), 2)
        return True
    except:
        return False


def get_ips():
    ifaces = netifaces.interfaces()
    to_return = []
    for iface in ifaces:
        addrs = netifaces.ifaddresses(iface)
        if netifaces.AF_INET in addrs:
            for a in addrs[netifaces.AF_INET]:
                to_return.append(a['addr'])
    return to_return