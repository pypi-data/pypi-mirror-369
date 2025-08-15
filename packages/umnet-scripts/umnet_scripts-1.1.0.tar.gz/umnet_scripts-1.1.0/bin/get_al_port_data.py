#!venv/bin/python

from umnet_scripts.constants import VALID_PORT
from umnet_scripts import Umnetdisco, Rancid, UMGoogleSheet
from umnet_scripts.utils import resolve_name_or_ip, interface_sort
import argparse
import logging
from datetime import datetime

def process_device(input_device):

    # we need the device's name and IP for this script to work properly
    device = resolve_name_or_ip(input_device)
    print(f"Processing device {device['name']}")
    if not(device['ip']):
        raise ValueError(f"Could not resolve {input_device} in DNS")
    
    # for now we're going to set the hostname to the IP if that didn't resolve
    if not(device['name']):
        logging.error(f"Couldn't figure out DNS name of {input_device}, referring to device by {device['ip']}")
        device['name'] = device['ip']
    
    # pulling netdisco and rancid data
    nd_results = nd.get_port_and_host_data(device['ip'])
    r_device = rancid_data.get_device(device['ip'])

    if not(r_device):
        raise LookupError(f"Could not find {r_device} in rancid")
    device_neighbors = r_device.neighbors

    # process results
    results = {}
    nonels_port_desc = {}

    for port in nd_results:

        new_port = port['port']

        # non-els to els munging
        if r_device.model.startswith("EX") and r_device.os_version.startswith('12'):

            # the 'logical' non-els port is where everything but the port desc lives.
            # if this is that port, just rename it to be the base port and keep going
            if port['port'].endswith(".0"):
                new_port = new_port.replace(".0", "")
            
            # if this is the physical port, save the description in a hash that maps port
            # names to descriptions and move on to the next port
            else:
                nonels_port_desc[port['port']] = port['description']
                continue
        elif new_port.endswith(".0"):
            continue

        # Skipping all non-physical ports
        if not(VALID_PORT.match(new_port)):
            logging.debug(f"{new_port} doesn't match valid port regex {VALID_PORT}, skipping")
            continue

        # skipping ports with neighbors - netdisco doesn't work great for neighbors
        # on the new network because of nxos snmp limitations
        if new_port in device_neighbors.keys():
            logging.info(f"{new_port} has a neighbor in topowalker, skipping")
            continue

        # We need to do things slightly differently if this is a voip
        # or non-voip host
        voip_host = True if port['vlan'] == '2' else False

        # looking at timeframe to decide if port is active or not
        if port['time_last']:
            active_port = True
            last_seen = (datetime.today() - port['time_last']).days

            # if the user provided a time range to check for, set a port to
            # non-active if the last MAC was seen before the time frame
            if(args.time_range) and last_seen > args.time_range:
                active_port = False

            # if we already found this port, update the existing entry
            # and continue
            if new_port in results:
                found_port = results[new_port]

                # Update the host if there isn't an existing entry last seen
                # more recently than this one
                if voip_host:
                    if not(found_port['voip_days_since_seen']) or (found_port['voip_days_since_seen'] < last_seen):
                        found_port['voip_days_since_seen'] = last_seen
                        found_port['voip_mac'] = port['mac']
                
                elif not(found_port['days_since_seen']) or (found_port['days_since_seen'] < last_seen):
                    found_port['days_since_seen'] = last_seen
                    found_port['mac'] = port['mac']
                    found_port['vlan'] = port['vlan']

                continue
       
        # if we've never seen a MAC on the port, it is not active
        else:
            last_seen = "Never"
            active_port = False

        # create new port entry
        results[new_port] = {
             'port':new_port,
             'description':port['description'],
             'admin_status':port['admin_status'],
             'oper_status':port['oper_status'],
             'speed':port['speed'],
             'vlan':port['vlan'] if not(voip_host) else '',
             'mac':port['mac'] if not(voip_host) else '',
             'ip': port['ip'] if not(voip_host) else '',
             'days_since_seen': last_seen if not(voip_host) else '',
             'voip_mac': port['mac'] if voip_host else '',
             'voip_ip': port['ip'] if voip_host else '',
             'voip_days_since_seen': last_seen if voip_host else '',
             'active_port': active_port
        }


    # post processing steps, where we also convert our dict to a list    
    results_list = []
    for row in results.values():

        # add ports to port counts
        if row['mac']:
            if row['vlan'] not in vlan_data:
                vlan_data[row['vlan']] = 0
            vlan_data[row['vlan']]+=1

        if row['voip_mac']:
            if '2' not in vlan_data:
                vlan_data['2'] = 0
            vlan_data['2'] +=1

        # for non-els devices go back and update the descriptions
        if nonels_port_desc:
            if row['port'] in nonels_port_desc:
                row['description'] = nonels_port_desc[row['port']]

        results_list.append(row)

    results_list.sort(key=interface_sort)
    gs.create_or_overwrite_worksheet(device['name'].replace(".umnet.umich.edu.",""), results_list)


if __name__ == '__main__':

    parser = argparse.ArgumentParser(description="Populate a spreadsheet with AL port info.")
    parser.add_argument('ss', help="URL of the google sheet")
    parser.add_argument('-l', '--log-level', dest='log_level', default="error",
            help='Set logging level (default=error)')
    parser.add_argument('--dev', dest='dev', action='store_true',
            help='Run query against dev server (default=false)')
    parser.add_argument('-t', '--time-range', dest='time_range', default=None, type=int, 
            help='A time in days to restrict historical queries to (default=all time)')
    group = parser.add_mutually_exclusive_group()
    group.add_argument('--device', help="A device's DNS name or primary IP")
    group.add_argument('--device-list', help="A list of devices to populate", nargs='+')
    group.add_argument('--zone', help="A list of devices to populate")
    args = parser.parse_args()

    logging.basicConfig(
        format='%(asctime)s %(levelname)s %(name)s %(message)s',
        datefmt='%Y-%m-%dT%H:%M:%S%z',
        level=args.log_level.upper(),
    )

    nd_server = ( 'netdisco-lab-vm.umnet.umich.edu' if args.dev else 'netdisco.umnet.umich.edu' )
    nd = Umnetdisco(host=nd_server)
    rancid_data = Rancid(cfg_dirs = ['distlayer', 'accesslayer'])
    gs = UMGoogleSheet(args.ss)
    now = datetime.now()

    vlan_data = {}

    if args.device:
        process_device(args.device)
    elif args.device_list:
        [process_device(d) for d in args.device_list]
    elif args.zone:
        devices = rancid_data.get_dlzone(args.zone)
        if not(devices):
            raise LookupError(f"No devices found in Rancid for DL zone {devices}")
        [process_device(d.rancid_name) for d in devices if d.rancid_role=="accesslayer"]
    else:
        print(f"Provide a device, list of devices, or zone name")
        parser.print_help()

    vlan_data_list = [{'vlan':k, 'active host count':v} for k,v in vlan_data.items()]
    gs.create_or_overwrite_worksheet("Per-Vlan Counts", vlan_data_list)
    



