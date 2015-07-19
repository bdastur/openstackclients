#!/usr/bin/env python
# -*- coding: utf-8 -*-

'''
Neutron Client.
'''

from neutronclient.v2_0 import client as neutron_client
from neutronclient.common.exceptions import NeutronException


class NeutronManage(object):
    '''
    Class to manage Neutron
    '''
    def __init__(self, creds):
        self.neutronclient = neutron_client.Client(**creds)

        self.networks = None  # List of available networks.

    #######################################################
    # neutron_get_networks:
    #
    # Params:
    # external: Flag to indicate search for external
    #           networks only [OPTIONAL]
    # ext_netname: Specific network name to look for. [OPTIONAL]
    #
    # Returns: A list of networks (empty list if none found)
    #######################################################
    def neutron_get_networks(self, external=True, network_name=None):
        '''
        Retrieve all neutron networks
        '''
        netlist = []
        self.networks = self.neutronclient.list_networks()['networks']
        for network in self.networks:
            if external is True:
                # Only get external networks.
                if not network['router:external']:
                    continue

            if network_name is not None:
                # Return a specific network
                if network['name'] == network_name:
                    netlist.append(network)
                    break
            else:
                netlist.append(network)

        return netlist

    #######################################################
    # neutron_create_network:
    #
    # Params:
    # network_name:
    # network_type:     'flat', 'vxlan', 'vlan'
    # physical_network: Name of physical network
    #                   (required if network type is vlan)
    # shared:           True or False
    # external:         True or False
    #
    # Returns: new network (dict) if successful, None if
    #          failure.
    #######################################################
    def neutron_create_network(self,
                               net_dict=None,
                               subnet_dict=None):
        '''
        Create a new neutron network.
        '''
        if net_dict is None:
            print "Invalid arguments"
            return None

        nw_list = self.neutron_get_networks(
            external=False,
            network_name=net_dict['network']['name'])
        if len(nw_list) > 0:
            print "Network exist [%s] [%d] " % \
                (nw_list[0]['name'], len(nw_list))
            return nw_list[0]

        try:
            new_nw = self.neutronclient.create_network(net_dict)
        except NeutronException as exp:
            print "[NeutronException]: ", exp
            return None

        if subnet_dict is None:
            return new_nw

        subnet_dict['subnet']['network_id'] = new_nw['network']['id']

        try:
            subnet = self.neutronclient.create_subnet(subnet_dict)['subnet']
        except NeutronException as exp:
            print "[NW CREATE NeutronException]: ", exp
            return new_nw

        new_nw['network']['subnets'].append(subnet['id'])

        return new_nw

    #######################################################
    # neutron_get_subnets:
    #
    # Params:
    # subnet_name:    Filter by subnet name
    # network_id:     Filter by network_id
    #
    # Returns:  list of subnets
    #######################################################
    def neutron_get_subnets(self,
                            subnet_name=None,
                            network_id=None):
        '''
        Get neutron subnets.
        '''
        snet_list = []
        subnet_list = self.neutronclient.list_subnets()['subnets']
        for subnet in subnet_list:
            # Put filters
            if subnet_name is not None:
                if subnet['name'] != subnet_name:
                    continue

            if network_id is not None:
                if subnet['network_id'] != network_id:
                    continue

            snet_list.append(subnet)

        return snet_list

    #######################################################
    # neutron_delete_network
    #
    #
    #
    #
    #
    #######################################################
    def neutron_delete_networks(self,
                                network_name=None):
        '''
        Delete neutron networks
        '''
        newnetlist = []
        netlist = self.neutron_get_networks(network_name=network_name)
        if len(netlist) == 0:
            print "No networks with name %s found" % network_name
            return newnetlist

        for network in netlist:
            try:
                ret = self.neutronclient.delete_network(network['id'])
                print "ret: ", ret
            except NeutronException as exp:
                print "[NW DEL NeutronException]: ", exp

        netlist = self.neutron_get_networks(network_name=network_name)

        return netlist

