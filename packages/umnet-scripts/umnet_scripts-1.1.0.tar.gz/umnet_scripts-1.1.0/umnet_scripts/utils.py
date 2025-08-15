import os
import ipaddress
from .constants import I_ABBR
import re
from dns import resolver, reversename

INTERFACE_SPEEDS = {
    'et-': 40,
    'xe-': 10,
    'ge-': 1,

    'Fo': 40,
    'Twe': 25,
    'Te': 10,
    'Two': 2,
    'Gi': 1,
    'Fa': .1,
}

def interface_sort(input):
    """
    Meant to be passed as a sort function for a list of interface names, or a list
    of dictionaries representing interface data

    If you're dealing with a list of dictionaries, the port name must be keyed as "port"
    or "name". If it's not, the function will throw an error.

    It is assumed that all ports have at least a mod/port component (eg GiX/Y), and it will also
    handle a slot/mod/number (eg GiX/Y/Z). "X" is weighted by 1000, "Y" by 100, and Z by 1.

    """
    if isinstance(input, dict):
        if "port" in input:
            port = input["port"]
        elif "name" in input:
            port = input["name"]
        else:
            raise KeyError(f"Unknown key for port list of dicts sort")
    elif isinstance(input, str):
        port = input

    prefix_value = 0
    for prefix, weight in INTERFACE_SPEEDS.items():
        if port.startswith(prefix):
            prefix_value = int(weight * 10000)

    m = re.match(r'.+(\d+)/(\d+)/(\d+)$', port)
    if m:
        return(prefix_value + int(m.group(1))*1000 + int(m.group(2))*100 + int(m.group(3)))
    
    m = re.match(r'.+(\d+)/(\d+)$', port)
    if m:
        return(prefix_value + int(m.group(1))*100 + int(m.group(2)))

    m = re.match(r'.+(\d+)$', port)
    if m:
        return(prefix_value + int(m.group(1)))
    
    return 0


def get_env_vars(vars_list):
    '''
    Pull list of variables from the environment,
    store in dict
    '''
    results = {}
    for var in vars_list:
        val = os.getenv(var)
        if val:
            results[var] = val
        else:
            raise Exception(f"Environment variable '{var}' is unset")

    return results

def is_ip_network(input_str, version=None):
 
    # First check that this is a valid IP or network
    try:
        net = ipaddress.ip_network(input_str)
    except:
        return False

    if version and version != net.version:
        return False
    
    return True

def is_ip_address(input_str, version=None):
    try:
        ip = ipaddress.ip_address(input_str)
    except:
        return False

    if version and version != ip.version:
        return False

    return True

def is_mac_address(input_str):
    '''
    Validates the input string as a mac address. Valid formats are
    XX:XX:XX:XX:XX:XX, XX-XX-XX-XX-XX-XX, XXXX.XXXX.XXXX
    where 'X' is a hexadecimal digit (upper or lowercase).
    '''
    mac = input_str.lower()
    if re.match(r'[0-9a-f]{2}([-:])[0-9a-f]{2}(\1[0-9a-f]{2}){4}$', mac):
        return True
    if re.match(r'[0-9a-f]{4}\.[0-9a-f]{4}\.[0-9a-f]{4}$', mac):
        return True

    return False

def forward_resolve(name):
    '''
    Looks for an A record for an inputted DNS name
    '''
    try:
        resolve = resolver.resolve(name, 'A')
    except:
        return False

    return resolve[0].to_text()


def reverse_resolve(ip):
    '''
    looks for a PTR record for an inputted IPv4 address
    '''
    try:
        resolve = resolver.resolve(reversename.from_address(ip),'PTR')
    except:
        return False
    return resolve[0].to_text()

def resolve_name_or_ip(input_str):
    '''
    Resolves a DNS name or an IPv4 address.
    Returns {'name':<hostname>, 'ip':<ip>}
    If a lookup didn't get an answer, returns None
    as that value
    '''

    result = {'name':None, 'ip': None}

    # if it's an IP, do a reverse lookup
    if is_ip_address(input_str):

        result['ip'] = input_str
        result_type = 'name'
        q_str = reversename.from_address(input_str)
        q_type = 'PTR'

    # otherwise just assume its a hostname
    else:
        result['name'] = input_str
        result_type = 'ip'

        # if no domain name was provided, tack on our standard domain
        if "." not in input_str:
            input_str += ".umnet.umich.edu"

        q_str = input_str
        q_type = 'A'

    resolve = resolver.resolve(q_str, q_type)
    try:
        resolve = resolver.resolve(q_str, q_type)
        print(resolve[0].to_text())
    except resolver.NXDOMAIN:
        resolve = False
        pass

    if resolve:
        result[result_type] = resolve[0].to_text()

    return result

def expand_interface(input_str):
    '''
    Expands a cisco interface to its full name.
    If no match is found, the string is returned
    unchanged
    '''
    for short, long in I_ABBR.items():
        if re.search(f'{short}\d',input_str):
            return input_str.replace(short, long)
    return input_str


def get_ncs_interface_name(port):
    '''
    Shortens a cisco interface from its full name
    to an abbreviation. Also removes '.0' from juniper interfaces
    '''
    # I_ABBR maps cisco short names to long ones
    for short, long in I_ABBR.items():
        if port.startswith(long):
            port = port.replace(long, short)

    # also need to remove ".0" from junos ports
    port = re.sub(r'\.0$','', port)
    return port
