from urllib.parse import urlparse, urlunparse


def clean_url(url, remove_query_params=True, remove_fragment=True):
    parsed = urlparse(url)
    query = '' if remove_query_params else parsed.query
    fragment = '' if remove_fragment else parsed.fragment

    return urlunparse((
        parsed.scheme,
        parsed.netloc,
        parsed.path,
        parsed.params,
        query,
        fragment,
    ))


def get_available_ports_host(start_port=8900, end_port=8990):
    import nmap

    nm = nmap.PortScanner()

    scan_range = f'{start_port}-{end_port}'
    nm.scan(hosts='host.docker.internal', arguments=f'-p {scan_range}')

    try:
        open_ports = nm['host.docker.internal']['tcp'].keys()
        open_ports = [int(port) for port in open_ports]
    except KeyError:
        open_ports = []

    for port in range(start_port, end_port + 1):
        if port not in open_ports:
            return port

    raise IOError(f'No free ports available in range {start_port}-{end_port}')
