# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

import sys
from ansible_collections.community.sap.tests.unit.compat.mock import patch, MagicMock
from ansible_collections.community.sap.tests.unit.plugins.modules.utils import AnsibleExitJson, AnsibleFailJson, ModuleTestCase, set_module_args

sys.modules['pyrfc'] = MagicMock()
sys.modules['pyrfc.Connection'] = MagicMock()

from ansible_collections.community.sap.plugins.modules.identity import sap_user


class TestSAPRfcModule(ModuleTestCase):

    def setUp(self):
        super(TestSAPRfcModule, self).setUp()
        self.module = sap_user

    def tearDown(self):
        super(TestSAPRfcModule, self).tearDown()

    def define_rfc_connect(self, mocker):
        return mocker.patch(self.module.call_rfc_method)

    def test_without_required_parameters(self):
        """Failure must occurs when all parameters are missing"""
        with self.assertRaises(AnsibleFailJson):
            set_module_args({})
            self.module.main()

    def test_error_user_create(self):
        """test fail to create user"""

        set_module_args({
            "conn_username": "DDIC",
            "conn_password": "Test1234",
            "host": "10.1.8.9",
            "username": "ADMIN",
            "firstname": "first_admin",
            "lastname": "last_admin",
            "email": "admin@test.de",
            "password": "Test123456",
            "useralias": "ADMIN",
            "company": "DEFAULT_COMPANY"
        })

        with patch.object(self.module, 'check_user') as check:
            check.return_value = False

            with patch.object(self.module, 'call_rfc_method') as RAW:
                RAW.return_value = {'RETURN': [{'FIELD': 'BNAME', 'ID': '01', 'LOG_MSG_NO': '000000',
                                                'LOG_NO': '', 'MESSAGE': 'Something went wrong', 'MESSAGE_V1': 'ADMIN',
                                                'MESSAGE_V2': '', 'MESSAGE_V3': '', 'MESSAGE_V4': '', 'NUMBER': '199',
                                                'PARAMETER': '', 'ROW': 0, 'SYSTEM': '', 'TYPE': 'E'}]}

                with patch.object(self.module, 'return_analysis') as RET:
                    RET.return_value = [{"change": False}, {"failed": True}]

                    with self.assertRaises(AnsibleFailJson) as result:
                        sap_user.main()
        self.assertEqual(result.exception.args[0]['msg'], 'Something went wrong')

    def test_success(self):
        """test execute user create success"""

        set_module_args({
            "conn_username": "DDIC",
            "conn_password": "Test1234",
            "host": "10.1.8.9",
            "username": "ADMIN",
            "firstname": "first_admin",
            "lastname": "last_admin",
            "email": "admin@test.de",
            "password": "Test123456",
            "useralias": "ADMIN",
            "company": "DEFAULT_COMPANY"
        })
        with patch.object(self.module, 'check_user') as check:
            check.return_value = False

            with patch.object(self.module, 'call_rfc_method') as RAW:
                RAW.return_value = {'RETURN': [{'FIELD': 'BNAME', 'ID': '01', 'LOG_MSG_NO': '000000',
                                                'LOG_NO': '', 'MESSAGE': 'User ADMIN created', 'MESSAGE_V1': 'ADMIN',
                                                'MESSAGE_V2': '', 'MESSAGE_V3': '', 'MESSAGE_V4': '', 'NUMBER': '102',
                                                'PARAMETER': '', 'ROW': 0, 'SYSTEM': '', 'TYPE': 'S'}]}

                with patch.object(self.module, 'return_analysis') as RET:
                    RET.return_value = [{"change": True}, {"failed": False}]

                    with self.assertRaises(AnsibleExitJson) as result:
                        sap_user.main()
        self.assertEqual(result.exception.args[0]['msg'], 'User ADMIN created')
