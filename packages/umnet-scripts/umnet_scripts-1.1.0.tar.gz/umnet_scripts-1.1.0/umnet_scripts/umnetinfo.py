from sqlalchemy import create_engine
from .utils import get_env_vars, is_ip_address, is_mac_address, is_ip_network
from .umnetdb import UMnetdb
import logging
import ipaddress
import re

logger = logging.getLogger(__name__)
logger.setLevel("DEBUG")


class UMnetinfo(UMnetdb):
    """
    This class wraps helpful netinfo db queries in python.
    """

    def __init__(self, host="kannada.web.itd.umich.edu", port=1521):

        eqdb_creds = get_env_vars(["NETINFO_USERNAME", "NETINFO_PASSWORD"])
        self._url = f"oracle+oracledb://{eqdb_creds['NETINFO_USERNAME']}:{eqdb_creds['NETINFO_PASSWORD']}@(DESCRIPTION=(ADDRESS=(PROTOCOL=TCP)(HOST={host})(PORT={port}))(CONNECT_DATA=(SID=KANNADA)))"
        self._e = create_engine(self._url)

    def get_network_by_name(self, netname, active_only=False):
        """
        Looks up a network by netname.
        """
        select = [
            "p.itemname as netname",
            "i.itemname as ipv4_subnet",
            "six_i.itemname as ipv6_subnet",
            "NVL(n.vlanid,n.local_vlanid) as vlan_id",
            "s.statusdes as status",
        ]
        table = "UMNET_ONLINE.ITEM p"
        joins = [
            "join UMNET_ONLINE.NETWORK n on p.itemidnum = n.itemidnum",
            "join UMNET_ONLINE.STATUS_CODE s on p.statuscd = s.statuscd",
            "left outer join UMNET_ONLINE.ITEM i on i.parentitemidnum = p.itemidnum",
            "left outer join UMNET_ONLINE.IP_SUBNET ip on i.itemidnum = ip.itemidnum",
            "left outer join UMNET_ONLINE.RELATED_ITEM r on p.itemidnum = r.relitemidnum",
            "left outer join UMNET_ONLINE.IP6NET six on r.itemidnum = six.itemidnum",
            "left outer join UMNET_ONLINE.ITEM six_i on six.itemidnum = six_i.itemidnum",
        ]
        where = [
            f"p.itemname = '{netname}'",
        ]

        sql = self._build_select(select, table, joins=joins, where=where)
        results = self._execute(sql)

        # there are also IPv4 subnets that are "pending removal" or "pending activation"
        # tied to the network in the RELATED_ITEM table, we need to find those too.
        # doing it as a separate query to maintain existing results row structure
        select = [
            "p.itemname as netname",
            "r_i.itemname as ipv4_subnet",
            "'' as ipv6_subnet",
            "NVL(n.vlanid,n.local_vlanid) as vlan_id",
            "r.itemreltypcd as status",
        ]
        joins = [
            "join UMNET_ONLINE.NETWORK n on p.itemidnum = n.itemidnum",
            "left outer join UMNET_ONLINE.ITEM i on i.parentitemidnum = p.itemidnum",
            "left outer join UMNET_ONLINE.RELATED_ITEM r on p.itemidnum = r.relitemidnum",
            "left outer join UMNET_ONLINE.ITEM r_i on r.itemidnum = r_i.itemidnum",
        ]
        where = [
            f"p.itemname = '{netname}'",
            "r_i.itemcatcd = 'IP'",
        ]
        # if we're doing active only, we only want "pending removal"
        if active_only:
            where.append("r.itemreltypcd = 'IP-PRNET'")

        sql = self._build_select(select, table, joins=joins, where=where)
        more_results = self._execute(sql)

        if more_results:
            results.extend(more_results)

        return results

    def get_network_by_ip(self, ip, active_only=False):
        """
        Looks up a network based on an IPv4 or IPv6 address. Returns the netname,
        vlan id, as well as *all active subnets* (IPv4 and IPv6) tied to the netname.
        """

        ip = ipaddress.ip_address(ip)

        # to make our lives simpler we're breaking this up into two steps.
        # first let's find the network entry in the 'item' table
        if ip.version == 4:
            select = ["NVL(p.itemidnum, r.relitemidnum) as id"]
            table = "UMNET_ONLINE.IP_SUBNET ip"
            joins = [
                "join UMNET_ONLINE.ITEM i on ip.itemidnum = i.itemidnum",
                "left outer join UMNET_ONLINE.RELATED_ITEM r on r.itemidnum = ip.itemidnum",
                "left outer join UMNET_ONLINE.ITEM p on i.parentitemidnum = p.itemidnum",
            ]
            where = [
                f"{int(ip)} >= ip.ADDRESS32BIT",
                f"{int(ip)} <= ip.ENDADDRESS32BIT",
                "NVL(p.itemidnum, r.relitemidnum) is not null",
            ]

        # IPv6 table is related to the 'item' table via the RELATED_ITEM table
        elif ip.version == 6:
            select = ["p.itemidnum as id"]
            table = "UMNET_ONLINE.IP6NET ip"
            joins = [
                "join UMNET_ONLINE.RELATED_iTEM r on r.itemidnum = ip.itemidnum",
                "join UMNET_ONLINE.ITEM p on p.itemidnum = r.relitemidnum",
            ]
            # and the start/end addresses are stored as hex strings
            addr_str = ip.exploded.replace(":", "")
            where = [
                f"'{addr_str}' >= ip.ADDRESS128BIT",
                f"'{addr_str}' <= ip.ENDADDRESS128BIT",
            ]

        sql = self._build_select(select, table, joins=joins, where=where)
        network = self._execute(sql)

        if not (network):
            return False
        net_id = network[0]["id"]

        # Now let's use the network itemidnum to find all associated subnets
        # with that network, as well as the netname and VLAN ID
        select = [
            "p.itemname as netname",
            "i.itemname as ipv4_subnet",
            "six_i.itemname as ipv6_subnet",
            "NVL(n.vlanid,n.local_vlanid) AS vlan_id",
            "i.itemcatcd as ITEMCAT",
            "p.itemcatcd as PCAT",
            "r.itemreltypcd as RELCAT",
        ]
        table = "UMNET_ONLINE.ITEM p"
        joins = [
            "join UMNET_ONLINE.NETWORK n on p.itemidnum = n.itemidnum",
            "join UMNET_ONLINE.ITEM i on i.parentitemidnum = p.itemidnum",
            "left outer join UMNET_ONLINE.RELATED_ITEM r on p.itemidnum = r.relitemidnum",
            "left outer join UMNET_ONLINE.IP6NET six on r.itemidnum = six.itemidnum",
            "left outer join UMNET_ONLINE.ITEM six_i on six.itemidnum = six_i.itemidnum",
        ]
        where = [
            f"p.itemidnum = {net_id}",
        ]

        sql = self._build_select(select, table, joins=joins, where=where)
        results = self._execute(sql)

        # there are also IPv4 subnets that are "pending removal" or "pending activation"
        # tied to the network in the RELATED_ITEM table, we need to find those too.
        # doing it as a separate query to maintain existing results row structure
        select = [
            "p.itemname as netname",
            "r_i.itemname as ipv4_subnet",
            "'' as ipv6_subnet",
            "NVL(n.vlanid,n.local_vlanid) AS vlan_id",
            "r.itemreltypcd as RELTYPCD",
        ]
        joins = [
            "join UMNET_ONLINE.NETWORK n on p.itemidnum = n.itemidnum",
            "left outer join UMNET_ONLINE.ITEM i on i.parentitemidnum = p.itemidnum",
            "left outer join UMNET_ONLINE.RELATED_ITEM r on p.itemidnum = r.relitemidnum",
            "left outer join UMNET_ONLINE.ITEM r_i on r.itemidnum = r_i.itemidnum",
        ]
        where = [
            f"p.itemidnum = {net_id}",
            "r_i.itemcatcd = 'IP'",
        ]
        # if we're doing active only, we only want "pending removal"
        if active_only:
            where.append("r.itemreltypcd = 'IP-PRNET'")

        sql = self._build_select(select, table, joins=joins, where=where)
        more_results = self._execute(sql)

        if more_results:
            results.extend(more_results)

        return results

    def get_vrfs(self, vrf_name=None, rd=None):
        """
        Pulls data from the vrf table on netinfo. If you supply a name and/or rd, it filters only
        for that vrf. Otherwise it returns all VRFs
        """

        select = [
            "shortname",
            "route_distinguisher",
            "default_vrf",
            "inside_vrf",
        ]
        table = "UMNET_ONLINE.VRF"

        where = []
        if vrf_name:
            where.append(f"shortname = '{vrf_name}'")
        if rd:
            where.append(f"route_distinguisher = '{rd}'")

        sql = self._build_select(select, table, where=where)
        results = self._execute(sql)

        return results

    def get_special_acl(self, netname: str):
        """
        Looks for a special ACL assignment by netname
        """
        select = ["acl.itemname"]
        table = "UMNET_ONLINE.ITEM net"
        joins = [
            "join UMNET_ONLINE.FILTER_NETWORK fn on fn.net_itemidnum = net.itemidnum",
            "join UMNET_ONLINE.ITEM acl on fn.filter_itemidnum = acl.itemidnum",
        ]
        where = [f"net.itemname='{netname}'"]

        sql = self._build_select(select, table, joins=joins, where=where)
        results = self._execute(sql)

        return results

    def get_asns(self, name_filter: str = ""):
        """
        Pulls all the ASNs from the AUTONOMOUS_SYSTEM
        table, optionally filtering by asname
        """
        select = ["ASNAME", "ASN"]
        table = "UMNET_ONLINE.AUTONOMOUS_SYSTEM"

        where = []
        if name_filter:
            where = [f"ASNAME like '%{name_filter}%'"]

        sql = self._build_select(select, table, where=where)
        results = self._execute(sql)

        return results

    def get_dlzone_buildings(self, zone: str):
        """
        given a dlzone shortname, returns a list of building numbers tied
        to that zone.
        """

        select = ["BUILDINGNUM as building_no"]
        table = "UMNET_ONLINE.AUTONOMOUS_SYSTEM asn"
        joins = [
            "join UMNET_ONLINE.BUILDING_AS b_asn on b_asn.ASID = asn.ASID",
        ]
        where = [f"asn.ASNAME = '{zone}'"]

        sql = self._build_select(select, table, joins=joins, where=where)
        results = self._execute(sql)

        return results

    def get_dlzone_by_building(self, bldg_num: int):
        """
        given a seven-digit building number, return the name of the
        distribution-zone to which it is assigned
        """

        select = ["ASNAME"]
        table = "UMNET_ONLINE.AUTONOMOUS_SYSTEM asn"
        joins = [
            "join UMNET_ONLINE.BUILDING_AS b_asn on b_asn.ASID = asn.ASID",
        ]
        where = [f"b_asn.BUILDINGNUM = '{bldg_num}'"]

        sql = self._build_select(select, table, joins=joins, where=where)
        results = self._execute(sql)

        return results

    def get_user_groups(self, username: str):
        """
        Looks up a user in netinfo and returns the groups they're in
        """

        select = ["e_grp.name"]
        table = "UMNET_ONLINE.PERSON p"
        joins = [
            "join UMNET_ONLINE.PERSON_GROUP p_grp on p_grp.PERSON_ENTITYIDNUM = p.ENTITYIDNUM",
            "join UMNET_ONLINE.ENTITY_GROUP e_grp on e_grp.ENTITYIDNUM = p_grp.GROUP_ENTITYIDNUM",
        ]
        where = [f"UNIQNAME='{username}'"]

        sql = self._build_select(select, table, joins=joins, where=where)
        results = self._execute(sql)

        return results

    def get_network_admins(
        self, netname: str, entity_types: list = [], rel_types: list = []
    ):
        """
        Looks up the users and user groups that are tied to this network.
        You can fiter by entity types (see UMNET_ONLINE.ENTITY_TYPE_CODE), these are:
          group, organization, person
        You can also filter by relationship type (UMNET_ONLINE.ENTITEM_RELATIONSHIP_TYPE_CODE):
          Owner, Worker, Business, Admin, Security
        """

        select = [
            "NVL(NVL(e_g.name, p.uniqname), o.NAME) as name",
            "e_t_c.ENTITYTYPDES as entity_type",
            "i_a.ENTITYITEMRELTYPCD as rel_type",
        ]

        table = "UMNET_ONLINE.ITEM i"
        joins = [
            "join UMNET_ONLINE.ITEM_ADMIN i_a on i_a.ITEMIDNUM=i.ITEMIDNUM",
            "join UMNET_ONLINE.ENTITY e on i_a.ENTITYIDNUM=e.ENTITYIDNUM",
            "join UMNET_ONLINE.ENTITY_TYPE_CODE e_t_c on e_t_c.ENTITYTYPCD=e.ENTITYTYPCD",
            "left outer join UMNET_ONLINE.ENTITY_GROUP e_g on e_g.ENTITYIDNUM=e.ENTITYIDNUM",
            "left outer join UMNET_ONLINE.PERSON p on p.ENTITYIDNUM=e.ENTITYIDNUM",
            "left outer join UMNET_ONLINE.ORGANIZATION o on o.ENTITYIDNUM=e.ENTITYIDNUM",
        ]

        where = [f"i.ITEMNAME='{netname}'"]

        if entity_types:
            e_where = " or ".join([f"e_t_c.ENTITYTYPDES='{e}'" for e in entity_types])
            where.append(f"({e_where})")
        if rel_types:
            rel_where = " or ".join(
                [f"i_a.ENTITYITEMRELTYPCD='{rel}'" for rel in rel_types]
            )
            where.append(f"({rel_where})")

        sql = self._build_select(select, table, joins=joins, where=where)
        results = self._execute(sql)

        return results

    def get_device_admins(
        self, name_or_ip: str, entity_types: list = [], rel_types: list = []
    ):
        """
        Looks up the users and user groups that are tied to this device.
        You can fiter by entity types (see UMNET_ONLINE.ENTITY_TYPE_CODE), these are:
          group, organization, person
        You can also filter by relationship type (UMNET_ONLINE.ENTITEM_RELATIONSHIP_TYPE_CODE):
          Owner, Worker, Business, Admin, Security
        """

        select = [
            "NVL(NVL(e_g.name, p.uniqname), o.NAME) as name",
            "e_t_c.ENTITYTYPDES as entity_type",
            "i_a.ENTITYITEMRELTYPCD as rel_type",
        ]

        table = "UMNET_ONLINE.DEVICE d"
        joins = [
            "join UMNET_ONLINE.ITEM i on i.itemidnum=d.ITEMIDNUM",
            "join UMNET_ONLINE.ITEM_ADMIN i_a on i_a.ITEMIDNUM=i.ITEMIDNUM",
            "join UMNET_ONLINE.ENTITY e on i_a.ENTITYIDNUM=e.ENTITYIDNUM",
            "join UMNET_ONLINE.ENTITY_TYPE_CODE e_t_c on e_t_c.ENTITYTYPCD=e.ENTITYTYPCD",
            "left outer join UMNET_ONLINE.ENTITY_GROUP e_g on e_g.ENTITYIDNUM=e.ENTITYIDNUM",
            "left outer join UMNET_ONLINE.PERSON p on p.ENTITYIDNUM=e.ENTITYIDNUM",
            "left outer join UMNET_ONLINE.ORGANIZATION o on o.ENTITYIDNUM=e.ENTITYIDNUM",
        ]

        # netinfo IPv4 addresses are always stored as integers
        if is_ip_address(name_or_ip):
            where = [f"d.ADDRESS32={int(ipaddress.ip_address(name_or_ip))}"]

        # dns names in the device table are fqdn and end in a dot (eg 'dl-arbl-1.umnet.umich.edu.')
        else:

            name_or_ip = name_or_ip.lower()
            if "." not in name_or_ip:
                name_or_ip += ".umnet.umich.edu"
            if not (name_or_ip.endswith(".")):
                name_or_ip += "."

            where = [f"d.DNS_NAME='{name_or_ip}'"]

        if entity_types:
            e_where = " or ".join([f"e_t_c.ENTITYTYPDES='{e}'" for e in entity_types])
            where.append(f"({e_where})")
        if rel_types:
            rel_where = " or ".join(
                [f"i_a.ENTITYITEMRELTYPCD='{rel}'" for rel in rel_types]
            )
            where.append(f"({rel_where})")

        sql = self._build_select(select, table, joins=joins, where=where)
        results = self._execute(sql)

        return results

    def get_arphist(
        self, query: str, device=None, interface=None, no_hist=False, no_device=False
    ):
        """
        Given either a MAC address, IP address, or subnet, query UMNET.ARPHIST
        and return the results.

        If you don't care about history, set "no_hist"
        If you don't care about which device the entries are routed on,
        set "no_device"

        Optionally limit the query by device and/or by interface
        with the "device" and "interface" fields
        """

        # for 'no_hist' 'no_device' we are just straight up pulling ip->mac
        # mappings
        select = ["address32bit, mac_addr"]
        if not no_hist:
            select.extend(["first_seen", "last_seen"])
        if not no_device:
            select.extend(["device_name as device", "ifdescr as interface"])

        table = "UMNET.ARPHIST arp"
        where = []

        # UMNET.ARPHIST stores MACs as strings without separators .:-, ie
        # 0010.abcd.1010 => '0010abcd1010'
        if is_mac_address(query):

            arphist_mac = re.sub(r"[\.\:\-]", "", query)
            where.append(f"arp.mac_addr = '{arphist_mac}'")

        # UMNET.ARPHIST stores IPs as integers, ie
        # 10.233.0.10 => 183042058. Also - only supports IPv4
        # IPv6 is stored in IP6NEIGHBOR
        elif is_ip_address(query, version=4):
            ip = ipaddress.ip_address(query)
            where.append(f"arp.address32bit = {int(ip)}")

        elif is_ip_network(query, version=4):
            net = ipaddress.ip_network(query)
            where.extend(
                [
                    f"arp.address32bit >= {int(net[0])}",
                    f"arp.address32bit <= {int(net[-1])}",
                ]
            )

        else:
            raise ValueError(
                f"Unsupported input {query}, must be a MAC, a subnet, or an IP"
            )

        if device:
            where.append(f"arp.device = '{device}'")
        if interface:
            where.append(f"arp.interface = '{interface}'")

        sql = self._build_select(select, table, where=where, distinct=True)
        results = self._execute(sql)

        # normally we like to return the results unprocessed. But the IPs and
        # MACs really need to get converted to make the ouptut useful.
        # hopefully the type different (Sqlalchemy result object vs list[dict])
        # isn't throwing anyone :-/
        processed_results = []
        for r in results:

            processed = {
                "ip": ipaddress.ip_address(r["address32bit"]),
                "mac": f"{r['mac_addr'][0:4]}.{r['mac_addr'][4:8]}.{r['mac_addr'][8:12]}",
            }
            for col in ["device", "interface", "first_seen", "last_seen"]:
                if col in r:
                    processed[col] = r[col]

            processed_results.append(processed)

        return processed_results

    def get_prefix_lists(self, prefix_lists: list = None):
        """
        Queries UMNET_ONLINE.PREFIX_LISTS for a list of prefix list names (as defined in the database).
        If you don't provide a list of names it will return all of them
        """

        select = ["name", "prefix"]
        table = "UMNET_ONLINE.PREFIX_LIST"

        where = []
        if prefix_lists:
            in_query = "(" + ",".join([f"'{p}'" for p in prefix_lists]) + ")"
            where.append(f"name in {in_query}")

        sql = self._build_select(select, table, where=where, order_by="1,2")
        results = self._execute(sql)

        return results
