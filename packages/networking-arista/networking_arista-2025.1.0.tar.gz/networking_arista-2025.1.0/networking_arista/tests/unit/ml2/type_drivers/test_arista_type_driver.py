# Copyright (c) 2016 OpenStack Foundation
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or
# implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import mock
from mock import patch
from neutron_lib import context
from oslo_config import cfg

from neutron.tests.unit.plugins.ml2.drivers import test_helpers
from neutron.tests.unit import testlib_api

import networking_arista.common.exceptions as exc
from networking_arista.ml2.type_drivers.driver_helpers import VlanSyncService
from networking_arista.ml2.type_drivers.type_arista_vlan \
    import AristaVlanTypeDriver
import networking_arista.tests.unit.utils as utils


EAPI_SEND_FUNC = ('networking_arista.ml2.rpc.arista_eapi.AristaRPCWrapperEapi'
                  '._send_eapi_req')


class AristaTypeDriverTest(testlib_api.SqlTestCase):

    def setUp(self):
        super(AristaTypeDriverTest, self).setUp()
        utils.setup_arista_wrapper_config(cfg)

    @patch(EAPI_SEND_FUNC)
    def test_initialize_type_driver(self, mock_send_eapi_req):
        type_driver = AristaVlanTypeDriver()
        type_driver.sync_service._force_sync = False
        type_driver.sync_service._vlan_assignment_uuid = {'uuid': 1}
        type_driver.sync_service._rpc = mock.MagicMock()
        rpc = type_driver.sync_service._rpc
        rpc.get_vlan_assignment_uuid.return_value = {'uuid': 1}
        type_driver.initialize()

        cmds = ['show openstack agent uuid',
                'show openstack resource-pool vlan region RegionOne uuid']

        calls = [mock.call(cmds=[cmd], commands_to_log=[cmd])
                 for cmd in cmds]
        mock_send_eapi_req.assert_has_calls(calls)
        type_driver.timer.cancel()


class AristaTypeDriverHelpersTest(test_helpers.HelpersTest):

    def setUp(self):
        utils.setup_arista_wrapper_config(cfg)
        super(AristaTypeDriverHelpersTest, self).setUp()
        self.driver = AristaVlanTypeDriver()
        self.driver.network_vlan_ranges = test_helpers.NETWORK_VLAN_RANGES

    def test_allocate_specific_allocated_segment_outside_pools(self):
        # Invalid test case for Arista type driver because the first
        # allocate fails with VlanUnavailable
        pass

    def test_allocate_specific_unallocated_segment_outside_pools(self):
        expected = dict(physical_network=test_helpers.TENANT_NET,
                        vlan_id=test_helpers.VLAN_OUTSIDE)
        self.assertRaises(exc.VlanUnavailable,
                          self.driver.allocate_fully_specified_segment,
                          self.context, **expected)


class VlanSyncServiceTest(testlib_api.SqlTestCase):
    """Test that VLANs are synchronized between EOS and Neutron."""

    def setUp(self):
        super(VlanSyncServiceTest, self).setUp()
        self.rpc = mock.MagicMock()
        self.sync_service = VlanSyncService(self.rpc)
        self.ctx = context.get_admin_context()

    def tearDown(self):
        super(VlanSyncServiceTest, self).tearDown()
        # Cleanup the db
        utils.delete_vlan_allocation(self.ctx)

    def _ensure_in_db(self, assigned, allocated, available):
        vlans = utils.get_vlan_allocation(self.ctx)
        self.assertEqual(len(vlans), len(assigned))
        used_vlans = []
        available_vlans = []
        for vlan in vlans:
            self.assertIn(vlan.vlan_id, assigned)
            if vlan.vlan_id in available:
                self.assertFalse(vlan.allocated)
                available_vlans.append(vlan.vlan_id)
            elif vlan.vlan_id in allocated:
                self.assertTrue(vlan.allocated)
                used_vlans.append(vlan.vlan_id)
        self.assertEqual(set(used_vlans), set(allocated))
        self.assertEqual(set(available_vlans), set(available))

    def _get_vlan_allocations(self):
        vlan_allocations = {
            'available_vlans': [],
            'allocated_vlans': [],
        }
        vlans = utils.get_vlan_allocation(self.ctx)
        for vlan in vlans:
            if vlan.allocated:
                vlan_allocations['allocated_vlans'].append(vlan.vlan_id)
            else:
                vlan_allocations['available_vlans'].append(vlan.vlan_id)
        return vlan_allocations

    def test_synchronization_before_region_sync(self):
        """Test VLAN sync with empty data from CVX"""

        # Populated VlanAllocations before starting the sync
        for seg_id in range(2, 500):
            utils.create_vlan_allocation(self.ctx, segmentation_id=seg_id)

        self.rpc.get_vlan_allocation.return_value = {
            'assignedVlans': '10, 100',
            'availableVlans': '',
            'allocatedVlans': ''
        }
        self.sync_service.synchronize()

        self.assertTrue(self.sync_service._force_sync)

        # Verify only assignedVlans exist in the db
        vlans = self._get_vlan_allocations()
        assigned_vlans = [10, 100]
        allocated_vlans = []
        self.assertEqual(set(vlans['available_vlans']), set(assigned_vlans))
        self.assertEqual(set(vlans['allocated_vlans']), set(allocated_vlans))

    def test_synchronization_test(self):
        """Test VLAN sync based on allocated VLANs in db and CVX"""

        # Add entries to vlan allocation table
        VLAN_MIN = 100
        VLAN_MAX = 300
        for seg_id in range(VLAN_MIN, VLAN_MAX + 1):
            allocated = seg_id in [VLAN_MIN, VLAN_MAX]
            utils.create_vlan_allocation(self.ctx, segmentation_id=seg_id,
                                         allocated=allocated)

        # Test case that vlan resource pool does not have allocated vlans
        self.rpc.get_vlan_allocation.return_value = {
            'assignedVlans': '10-20, 50-60, %s, %s' % (VLAN_MIN, VLAN_MAX),
            'availableVlans': '10-20, 50-60',
            'allocatedVlans': ''
        }
        self.sync_service.synchronize()

        self.assertFalse(self.sync_service._force_sync)

        allocated_vlans = [VLAN_MIN, VLAN_MAX]
        available_vlans = list(set(range(10, 21)) | set(range(50, 61)))
        assigned_vlans = list(set(available_vlans) | set(allocated_vlans))
        self._ensure_in_db(assigned_vlans, allocated_vlans, available_vlans)

        # Test case that vlan resource pool has updated resources
        self.rpc.get_vlan_allocation.return_value = {
            'assignedVlans': '200-220, %s, %s' % (VLAN_MIN, VLAN_MAX),
            'availableVlans': '200-220',
            'allocatedVlans': '%s, %s' % (VLAN_MIN, VLAN_MAX)
        }
        available_vlans = list(set(range(200, 221)))
        assigned_vlans = list(set(available_vlans) | set(allocated_vlans))
        self.sync_service.synchronize()
        self._ensure_in_db(assigned_vlans, allocated_vlans, available_vlans)

    def test_synchronization_test_with_data_from_cvx(self):
        """Test VLAN sync based on data from CVX"""

        self.rpc.get_vlan_allocation.return_value = {
            'assignedVlans': '51-60,71-80',
            'availableVlans': '51-55,71,73,75,77,79',
            'allocatedVlans': '56-60,72,74,76,78,80'
        }
        assigned_vlans = list(set(range(51, 61)) | set(range(71, 81)))
        available_vlans = [51, 52, 53, 54, 55, 71, 73, 75, 77, 79]
        allocated_vlans = list(set(assigned_vlans) - set(available_vlans))
        self.sync_service.synchronize()

        self.assertFalse(self.sync_service._force_sync)

        self._ensure_in_db(assigned_vlans, allocated_vlans, available_vlans)
