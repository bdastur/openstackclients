#!/usr/bin/env python
# -*- coding: utf-8 -*-

'''
Openstack Client Test code.
'''

import unittest
import credentials
import osnetwork_client as neutronclient


class OSTest(unittest.TestCase):
    '''
    Test Openstack client handlers.
    '''
    def get_openstack_credentials(self, rcfile):
        '''
        Get OpenStack cloud credentials
        '''
        if rcfile is None:
            return None

        creds = credentials.Credentials(rcfile, None, None)
        credict = creds.get_credentials()

        return credict

    def test_credentials(self):
        '''
        Test reading credentials
        '''

        credict = self.get_openstack_credentials("./openrc")
        self.failUnless(credict['username'] == 'admin')
        self.failUnless(credict['tenant_name'] == 'admin')
        self.failUnless(credict['password'] == 'password')
        self.failUnless(
            credict['auth_url'] == 'http://172.22.191.163:5000/v2.0')

    def test_ext_network_create(self):
        '''
        Test network creation and list.
        '''
        credict = self.get_openstack_credentials("./openrc")

        neutron_handle = neutronclient.NeutronManage(credict)
        self.failUnless(neutron_handle is not None)

        # Create external network.
        network = {
            'network': {
                'name': 'ext-net',
                'admin_state_up': True,
                'shared': True,
                'router:external': True,
                'provider:network_type': 'flat',
                'provider:physical_network': 'physnet1'
            }
        }

        subnet = {
            'subnet': {
                'name': 'subnet-ext',
                'enable_dhcp': False,
                'cidr': '172.22.191.160/25',
                'allocation_pools': [{'start': '172.22.191.164',
                                      'end': '172.22.191.169'}],
                'dns_nameservers': ['171.70.168.183'],
                'gateway_ip': '172.22.191.131',
                'ip_version': 4
            }
        }

        # Create network and subnet.
        new_nw = neutron_handle.neutron_create_network(net_dict=network,
                                                       subnet_dict=subnet)

        self.failUnless(new_nw is not None)

        # Get network based on network name
        new_nw = neutron_handle.neutron_get_networks(network_name="ext-net")
        self.failUnless(new_nw[0]['router:external'] is True)

        # Get subnet based on network id.
        subnet_list = neutron_handle.neutron_get_subnets(
            network_id=new_nw[0]['id'])
        self.failUnless(subnet_list[0]['enable_dhcp'] is False)
        self.failUnless(subnet_list[0]['cidr'] == '172.22.191.128/25')

        # Delete network
        newlist = neutron_handle.neutron_delete_networks(
            network_name="ext-net")
        self.failUnless(len(newlist) == 0)





