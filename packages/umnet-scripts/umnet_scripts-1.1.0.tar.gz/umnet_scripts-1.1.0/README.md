# umnet-scripts
A set of python modules/classes for interacting with UMnet tools.

This package is hosted on pypi - you can install it with `pip install umnet-scripts` and use it in your own code.

# Database Helper Classes
As of Dec 2021 this repo defines db wrapper classes for Equipdb, Netinfo, and Netdisco.
To use these classes you need to set specific environment variables with the credentials
for each db respectively:
* Netinfo: `NETINFO_USERNAME`, `NETINFO_PASSSWORD`
* Netdisco: `NETDISCO_DB_USER`, `NETDISCO_DB_PASSWORD`
* Equipdb: `EQUIP_DB_USER`, `EQUIP_DB_PASSWORD`

Queries for specific things are added as they're needed. As of Dec 2021 there are only a few methods defined for netdisco and equipdb.
Each class inherits a super basic sql query builder method as well as an 'execute' method from a base class (see `umnetdb.py`).

# Rancid Helper Class
The rancid helper class currently parses the router.db files in `/home/rancid/` as well as the `/home/rancid/Topology`
into a list of `Device` objects with rancid-related data as attributes, particularly the following:
* `rancid_name`: The name of the device as rancid knows it (the name of the config file). IP address for AL, DNS name for everything else.
* `rancid_type`: The rancid perl script that is used to back up the device (eg `juniper` or `Cat3750`)
* `rancid_role`: This is the folder the device config lives in, eg `accesslayer` or `core`. Maps 1:1 to the equipdb device `type`.
* `model`: Device model as populated in equipdb, eg 'EX2200-24T-4G'
* `cfg_file`: Full path to the config file, eg `/home/rancid/accesslayer/10.233.0.10`
* `status`: Up or down per the equipdb `offline` flag (offline is down).
* `neighbors`: A dict of the device's neighbors as reported by TopologyWalker.

There are also two attributes that look like attributes but are actually 'property' functions: `hostname` and `ip` that return the device's hostname
or IP respectively. If you call 'hostname' for a device whose rancid name is an IP, a dns reverse lookup is done. Similarly,
if you call 'ip' on a device whose rancid name is a DNS name, a forward dns lookup is done.

Note that if you're only focusing on one rancid config folder (eg datacenter, accesslayer, etc),
to speed your code up you can limit which folders are processed when you instantiate the Rancid class.
Note that if you want to get devices by dl_zone you *must* include the distlayer folder at minimum.

