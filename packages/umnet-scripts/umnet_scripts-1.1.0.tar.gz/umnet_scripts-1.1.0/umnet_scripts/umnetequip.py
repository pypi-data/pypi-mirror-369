from sqlalchemy import create_engine
from .utils import get_env_vars
from .umnetdb import UMnetdb
import logging
from .utils import is_ip_address
from typing import Union

logger = logging.getLogger(__name__)

class UMnetequip(UMnetdb):
    '''
    This class wraps helpful equip db queries in python.
    The API is lame.
    '''
    def __init__(self, host='equipdb-prod.umnet.umich.edu', port=1521):

        eqdb_creds = get_env_vars(['EQUIP_DB_USERNAME','EQUIP_DB_PASSWORD'])
        self._url = f"oracle+oracledb://{eqdb_creds['EQUIP_DB_USERNAME']}:{eqdb_creds['EQUIP_DB_PASSWORD']}@(DESCRIPTION=(ADDRESS=(PROTOCOL=TCP)(HOST={host})(PORT={port}))(CONNECT_DATA=(SID=KANNADA)))"
        self._e = create_engine(self._url)
        
        logger.debug(f"Created DB engine {self._url}")


    def get_devices_by_category(self, category, active_only=False):
        '''
        Queries equip db for devices by category. You can also
        specify if you only want active devices.
        '''

        select = [ 'eq.monitored_device', 
                   'eq.rancid',
                   'eq.off_line',
                   'eq.dns_name',
                   'eq.ip_address',
                 ]
        table = 'ARADMIN1.UMNET_EQUIPMENT eq'

        where = [f"eq.category = '{category}'"]

        # Equipshim status numbers (see ARADMIN1.UMNET_EQUIPMENT_STATUS)
        # 1: RESERVE, 2:ACTIVE, 3:RETIRED
        if active_only:
            where.append("eq.status = 2")
        
        sql = self._build_select(select, table, where=where, distinct=True)
        return self._execute(sql)


    def get_device_type(self, ip):
        '''
        Queries equip db for a device by ip, returns the 'type' of the device.
        By type we mean the UMNET_EQUIPMENT_TYPE: ACCESS LAYER, DISTRIBUTION LAYER, UMD, etc
        '''
        select = [ 'types as type' ]
        table = 'ARADMIN1.UMNET_EQUIPMENT'
        where = [f"ip_address='{ip}'"]

        sql = self._build_select(select, table, where=where)
        return self._execute(sql)

    def get_devices_by_building_no(self, 
                    building_no:Union[int, list],
                    active_only:bool=False,
                    types:list=[],
                    location_info:bool=False,
                    ):
        """
        Queries equipdb for devices by building no. You can provide a single
        building number, or a list of numbers. You can specify if you want 'active only' devices
        (based on the 'status' field, defalut false) or you can limit to a certain device type (default all).
        You can also get the location info for each device via 'location_info' (default false)
        """
        select = [ 'dns_name',
                   'ip_address',
                   'model_no_ as model',
                   'types as device_type', 
                   'rancid',
                   'off_line',         
                 ]
        if location_info:
            select.extend([
                    'bldg as building_name',
                    'address as building_address',
                    'room as room_no',
                    'floor as floor',    
                    'bldg_code__ as building_no',     
            ])

        table = 'ARADMIN1.UMNET_EQUIPMENT eq'

        where = []
        if isinstance(building_no, int):
            where.append(f"eq.bldg_code__ = {building_no}")
        elif isinstance(building_no, list):
            bldgs_str = ",".join([str(bldg) for bldg in building_no])
            where.append(f"eq.bldg_code__ in ({bldgs_str})")
        else:
            raise ValueError(f"{building_no} must be int or list!")

        # Equipshim status numbers (see ARADMIN1.UMNET_EQUIPMENT_STATUS)
        # 1: RESERVE, 2:ACTIVE, 3:RETIRED
        if active_only:
            where.append("eq.status = 2")

        if types:
            types_str = ",".join([f"'{t}'" for t in types])
            where.append(f"eq.types in ({types_str})")

        sql = self._build_select(select, table, where=where)
        return self._execute(sql)

    def get_device(self, name_or_ip:str, location_info:bool=False):

        if is_ip_address(name_or_ip):
            where = [f"ip_address='{name_or_ip}'"]
        else:
            name_or_ip = name_or_ip.replace(".umnet.umich.edu","")
            where = [f"dns_name='{name_or_ip}'"]

        select = [ 'dns_name',
                   'ip_address',
                   'model_no_ as model',
                   'types as device_type', 
                   'rancid',
                   'off_line',          
                 ]
        if location_info:
            select.extend([
                    'bldg as building_name',
                    'address as building_address',
                    'room as room_no',
                    'floor as floor',    
                    'bldg_code__ as building_no',     
            ])
        table = 'ARADMIN1.UMNET_EQUIPMENT eq'

        sql = self._build_select(select, table, where=where)
        return self._execute(sql)

    def get_all_devices(self):
        select = [  "bldg_code__ as bldg_code",
                    "bldg",
                    "room",
                    "ip_address",
                    "dns_name",
                    "category",
                    "types",
                    "manufacturer",
                    "serial_number",
                    "billing_code_ as billing_code",
                    "warehouse_item__ as warehouse_item",
                    "st.descr as status",
                    "sla_network",
                    "address",
                    "floor",
                    "model_no_ as model_no",
                    "customer_name",
                    "mat_l_item_description",
                    "rancid",
                    "off_line",
                 ]
        table = 'ARADMIN1.UMNET_EQUIPMENT eq'
        joins = ["join ARADMIN1.UMNET_EQUIPMENT_STATUS st on st.idnum=eq.status"]
        where = ["eq.status != 3"]

        sql = self._build_select(select, table,where=where, joins=joins)
        return self._execute(sql)
