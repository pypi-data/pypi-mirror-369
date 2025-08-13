# Copyright (c) 2016 OpenStack Foundation
# All Rights Reserved.
#
#    Licensed under the Apache License, Version 2.0 (the "License"); you may
#    not use this file except in compliance with the License. You may obtain
#    a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#    License for the specific language governing permissions and limitations
#    under the License.

import collections

from neutron_lib import constants as n_const
from neutron_lib import context
from neutron_lib.db import api as db_api
from oslo_log import log
from six import moves

from neutron.objects import network as network_obj
from neutron.objects.plugins.ml2 import vlanallocation as vlanalloc

from networking_arista._i18n import _LI
from networking_arista.common.constants import EOS_UNREACHABLE_MSG
from networking_arista.common import exceptions as arista_exc

LOG = log.getLogger(__name__)


class VlanSyncService(object):
    """Sync vlan assignment from CVX into the OpenStack db."""

    def __init__(self, rpc_wrapper):
        self._rpc = rpc_wrapper
        self._force_sync = True
        self._vlan_assignment_uuid = None
        self._assigned_vlans = dict()

    def force_sync(self):
        self._force_sync = True

    def _parse_vlan_ranges(self, vlan_pool, return_as_ranges=False):
        vlan_ids = set()
        if return_as_ranges:
            vlan_ids = list()
        if not vlan_pool:
            return vlan_ids
        vlan_ranges = vlan_pool.split(',')
        for vlan_range in vlan_ranges:
            endpoints = vlan_range.split('-')
            if len(endpoints) == 2:
                vlan_min = int(endpoints[0])
                vlan_max = int(endpoints[1])
                if return_as_ranges:
                    vlan_ids.append((vlan_min, vlan_max))
                else:
                    vlan_ids |= set(moves.range(vlan_min, vlan_max + 1))
            elif len(endpoints) == 1:
                single_vlan = int(endpoints[0])
                if return_as_ranges:
                    vlan_ids.append((single_vlan, single_vlan))
                else:
                    vlan_ids.add(single_vlan)
        return vlan_ids

    def get_network_vlan_ranges(self):
        return self._assigned_vlans

    def _sync_required(self):
        try:
            if not self._force_sync and self._region_in_sync():
                LOG.info(_LI('VLANs are in sync!'))
                return False
        except arista_exc.AristaRpcError:
            LOG.warning(EOS_UNREACHABLE_MSG)
            self._force_sync = True
        return True

    def _region_in_sync(self):
        eos_vlan_assignment_uuid = self._rpc.get_vlan_assignment_uuid()
        return (self._vlan_assignment_uuid and
                (self._vlan_assignment_uuid['uuid'] ==
                 eos_vlan_assignment_uuid['uuid']))

    def _set_vlan_assignment_uuid(self):
        try:
            self._vlan_assignment_uuid = self._rpc.get_vlan_assignment_uuid()
        except arista_exc.AristaRpcError:
            self._force_sync = True

    def do_synchronize(self):
        if not self._sync_required():
            return

        self.synchronize()
        self._set_vlan_assignment_uuid()

    def synchronize(self):
        LOG.info(_LI('Syncing VLANs with EOS'))
        try:
            self._rpc.check_vlan_type_driver_commands()
            vlan_pool = self._rpc.get_vlan_allocation()
        except arista_exc.AristaRpcError:
            LOG.warning(EOS_UNREACHABLE_MSG)
            self._force_sync = True
            return

        LOG.debug('vlan_pool %(vlan)s', {'vlan': vlan_pool})
        self._assigned_vlans = {
            'default': self._parse_vlan_ranges(vlan_pool['assignedVlans']),
        }
        cvx_available_vlans = frozenset(
            self._parse_vlan_ranges(vlan_pool['availableVlans']))
        cvx_used_vlans = frozenset(
            self._parse_vlan_ranges(vlan_pool['allocatedVlans']))
        # Force vlan sync if assignedVlans is empty or availableVlans and
        # allocatedVlans both are empty in the vlan_pool
        if not(self._assigned_vlans['default'] and
               (cvx_available_vlans or cvx_used_vlans)):
            LOG.info(_LI('Force sync, vlan pool is empty'))
            self.force_sync()
        else:
            self._force_sync = False

        allocated_vlans = {}
        ctx = context.get_admin_context()
        with db_api.CONTEXT_READER.using(ctx):
            for physical_network in self._assigned_vlans:
                filter = {
                    'network_type': n_const.TYPE_VLAN,
                    'physical_network': physical_network,
                }
                objs = network_obj.NetworkSegment.get_objects(ctx, **filter)
                allocated_vlans.update(
                    {physical_network: [obj.segmentation_id for obj in objs]})
            LOG.debug('allocated vlans %(vlan)s', {'vlan': allocated_vlans})

        with db_api.CONTEXT_WRITER.using(ctx):
            physnets = vlanalloc.VlanAllocation.get_physical_networks(ctx)
            physnets_unconfigured = physnets - set(self._assigned_vlans)
            if physnets_unconfigured:
                vlanalloc.VlanAllocation.delete_physical_networks(
                        ctx, physnets_unconfigured)

            allocations = collections.defaultdict(list)
            for alloc in vlanalloc.VlanAllocation.get_objects(ctx):
                allocations[alloc.physical_network].append(alloc)

            for physical_network, vlan_ranges in self._assigned_vlans.items():
                if physical_network in allocations:
                    for alloc in allocations[physical_network]:
                        try:
                            vlan_ranges.remove(alloc.vlan_id)
                        except KeyError:
                            alloc.delete()
                vlanalloc.VlanAllocation.bulk_create(ctx, physical_network,
                                                     vlan_ranges)
                LOG.debug('vlan_ranges: %(vlan)s', {'vlan': vlan_ranges})
                for vlan_id in vlan_ranges:
                    allocated = (vlan_id not in cvx_available_vlans and
                                 (vlan_id in cvx_used_vlans or vlan_id in
                                 allocated_vlans[physical_network]))
                    LOG.debug('Updating %(phys)s %(vlan)s %(alloc)s',
                              {'phys': physical_network, 'vlan': vlan_id,
                               'alloc': allocated})
                    vlanalloc.VlanAllocation.update_objects(ctx,
                                values={'allocated': allocated,
                                        'vlan_id': vlan_id,
                                        'physical_network': physical_network},
                                physical_network=physical_network,
                                vlan_id=vlan_id)
