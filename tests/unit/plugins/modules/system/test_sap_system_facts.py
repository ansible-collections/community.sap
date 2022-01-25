# -*- coding: utf-8 -*-

# Copyright: (c) 2021, Rainer Leber (@rainerleber) <rainerleber@gmail.com>
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function
__metaclass__ = type

from ansible_collections.community.sap.plugins.modules.system import sap_system_facts
from ansible_collections.community.sap.tests.unit.plugins.modules.utils import AnsibleExitJson, AnsibleFailJson, ModuleTestCase
from ansible_collections.community.sap.tests.unit.compat.mock import patch
from ansible.module_utils import basic


def get_bin_path(*args, **kwargs):
    """Function to return path of SAPCAR"""
    return "/usr/sap/hostctrl/exe/sapcontrol"


class Testsap_system_facts(ModuleTestCase):
    """Main class for testing sap_system_facts module."""

    def setUp(self):
        """Setup."""
        super(Testsap_system_facts, self).setUp()
        self.module = sap_system_facts

    def tearDown(self):
        """Teardown."""
        super(Testsap_system_facts, self).tearDown()

    def test_no_systems_available(self):
        """Failure must occurs when all parameters are missing."""
        with patch.object(basic.AnsibleModule, 'run_command') as run_command:
            run_command.return_value = 1, '', ''
            with self.assertRaises(AnsibleExitJson) as result:
                self.module.main()
        self.assertEqual(result.exception.args[0]['ansible_facts'], {})

    def test_sap_system_facts_hana(self):
        """Check that result is changed when HANA system."""
        with patch.object(self.module, 'get_all_hana_sid') as get_all_hana_sid:
            get_all_hana_sid.return_value = ['HDB']
            with patch.object(self.module, 'get_hana_nr') as get_hana_nr:
                get_hana_nr.return_value = [{"InstanceType": "HANA", "NR": "01", "SID": "HDB", "TYPE": "HDB"}]
                with self.assertRaises(AnsibleExitJson) as result:
                    self.module.main()
                    self.assertTrue(result.exception.args[0]['changed'])
        self.assertEqual(result.exception.args[0]['ansible_facts'], {'sap': [{"InstanceType": "HANA", "NR": "01", "SID": "HDB", "TYPE": "HDB"}]})

    def test_sap_system_facts_nw(self):
        """Check that result is changed when NW system."""
        with patch.object(self.module, 'get_all_nw_sid') as get_all_nw_sid:
            get_all_nw_sid.return_value = ['ABC']
            with patch.object(self.module, 'get_nw_nr') as get_nw_nr:
                get_nw_nr.return_value = [{"InstanceType": "NW", "NR": "00", "SID": "ABC", "TYPE": "ASCS"},
                                          {"InstanceType": "NW", "NR": "01", "SID": "ABC", "TYPE": "PAS"}]
                with self.assertRaises(AnsibleExitJson) as result:
                    self.module.main()
                    self.assertTrue(result.exception.args[0]['changed'])
        self.assertEqual(result.exception.args[0]['ansible_facts'], {'sap': [{"InstanceType": "NW", "NR": "00", "SID": "ABC", "TYPE": "ASCS"},
                                                                             {"InstanceType": "NW", "NR": "01", "SID": "ABC", "TYPE": "PAS"}]})

    def test_sap_system_facts_all(self):
        """Check that result is changed when NW system."""
        with patch.object(self.module, 'get_all_hana_sid') as get_all_hana_sid:
            get_all_hana_sid.return_value = ['HDB']
            with patch.object(self.module, 'get_hana_nr') as get_hana_nr:
                get_hana_nr.return_value = [{"InstanceType": "HANA", "NR": "01", "SID": "HDB", "TYPE": "HDB"}]
                with patch.object(self.module, 'get_all_nw_sid') as get_all_nw_sid:
                    get_all_nw_sid.return_value = ['ABC']
                    with patch.object(self.module, 'get_nw_nr') as get_nw_nr:
                        get_nw_nr.return_value = [{"InstanceType": "NW", "NR": "00", "SID": "ABC", "TYPE": "ASCS"},
                                                  {"InstanceType": "NW", "NR": "01", "SID": "ABC", "TYPE": "PAS"}]
                        with self.assertRaises(AnsibleExitJson) as result:
                            self.module.main()
                            self.assertTrue(result.exception.args[0]['changed'])
        self.assertEqual(result.exception.args[0]['ansible_facts'], {'sap': [{"InstanceType": "HANA", "NR": "01", "SID": "HDB", "TYPE": "HDB"},
                                                                             {"InstanceType": "NW", "NR": "00", "SID": "ABC", "TYPE": "ASCS"},
                                                                             {"InstanceType": "NW", "NR": "01", "SID": "ABC", "TYPE": "PAS"}]})
