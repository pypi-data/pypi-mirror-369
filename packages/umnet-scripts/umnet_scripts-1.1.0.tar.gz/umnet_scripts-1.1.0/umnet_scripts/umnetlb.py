from f5.bigip import ManagementRoot

VALID_HOSTS = [

'lb-macc-vltm-1',
'lb-macc-vltm-2',
'lb-macc-vltm-3',
'lb-macc-vltm-4',
'lb-macc-vltm-active',
'lb-asbdc-vltm-3',
'lb-asbdc-vltm-4',
'lb-asbdc-vltm-active',


]

class UMnetLB(ManagementRoot):

    def __init__(self, host:str, username:str, password:str):
        '''
        Validate lb hostname before attempting to connect
        '''

        host = host.replace(".umnet.umich.edu","")
        host = host.lower()
        if host not in VALID_HOSTS:
            raise LookupError(f'Invalid LB name, must be one of: {VALID_HOSTS}')
        
        super().__init__(host, username, password)

    def get_pool_member_state(self, pool:str=None, partition:str=None) -> list:
        '''
        Returns a list of pool members and their status. If a pool is provided,
        only that pool is returned. If a context is provided, only pools in that
        context are returned.
        '''
        pool_list = []

        # if we know the exact pool (pool name AND partition), it's faster for
        # us to just pull that one pool
        if pool and partition:
            all_pools = [ self.tm.ltm.pools.load(name=pool, partition=partition) ]

        # otherwise just get all the pools from all the partitions (you can't)
        # apparently filter 'get collection' by partition :/
        else:
            all_pools = self.tm.ltm.pools.get_collection()
        
        # pull members from the pools and their state.
        for p in all_pools:

            # filter out results the user didn't want
            if partition and p.partition != partition:
                continue
            if pool and p.name != pool:
                continue

            for m in p.members_s.get_collection():
                pool_list.append(
                    {'pool':p.name,
                     'partition':p.partition,
                     'member':m.name,
                     'state':m.state,
                    }
                )

        return pool_list
    
    def get_vip_status(self, vip:str=None, partition:str=None) -> list:
        """
        Queries the F5 for VIP status. If you provide the vip and the partition,
        only that VIP is requested. Otherwise all VIPs from all partitions are retrieved
        and filtered based on input.

        Output for each vip includes the name, ip:port, 
            partition, pool, status, and reason status
        """

        v_list = []

        if vip and partition:
            all_vips = [ self.tm.ltm.virtuals.virtual.load(name=vip, partition=partition) ]
        else:
            all_vips = self.tm.ltm.virtuals.get_collection()

        for v in all_vips:

            if partition and v.partition != partition:
                continue
            if vip and v.name != vip:
                continue

            # VIP stats are nested in an ugly way - this article helped me:
            # https://community.f5.com/t5/technical-forum/f5-python-sdk-how-to-get-virtual-server-availability/td-p/203317
            stats = v.stats.load()
            s_entries = stats.entries[list(stats.entries.keys())[0]]['nestedStats']['entries']

            pool = getattr(v, 'pool', None)
            if pool:
                pool.replace(f'/{v.partition}/','')

            v_list.append(
                {'vip':v.name,
                 'ip_port': v.destination.replace(f'/{v.partition}/',''),
                 'partiion':v.partition,
                 'pool': pool,
                 'status': s_entries['status.availabilityState']['description'],
                 'status_reason': s_entries['status.statusReason']['description'],
                }
            )

        return v_list