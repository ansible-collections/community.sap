#!/usr/bin/python
# -*- coding: utf-8 -*-
 
# Copyright: (c) 2021, Rainer Leber <rainerleber@gmail.com>
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)
from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

DOCUMENTATION = r'''
---
module: community.sap.sap_company

short_description: This module will manage a company entities in a SAP S4/HANA environment.

version_added: "1.1.0"

description:
    - The C(sap_user) module depends on C(pyrfc) Python library (version 2.4.0 and upwards).
        Depending on distribution you are using, you may need to install additional packages to
        have these available.
    - This module will use the company BAPIs c(BAPI_COMPANY_CLONE) and c(BAPI_COMPANY_DELETE) to manage company entities.

options:
    state:
        description:
        - The decission what to do with the company.
        - Could be c('present'), c('absent')
        default: 'present'
        required: true
        type: str
    conn_username:
        description: The required username for the SAP system.
        required: true
        type: str
    conn_password:
        description: The required password for the SAP system.
        required: true
        type: str
    host:
        description: The required host for the SAP system. Can be either an FQDN or IP Address.
        required: true
        type: str
    sysnr:
        description:
        - The system number of the SAP system.
        - You must quote the value to ensure retaining the leading zeros.
        default: '00'
        type: str
    client:
        description:
        - The client number to connect to.
        - You must quote the value to ensure retaining the leading zeros.
        default: '000'
        type: str

requirements:
    - pyrfc >= 2.4.0

author:
    - Rainer Leber (@rainerleber)
'''

EXAMPLES = r'''
# Pass in a message
- name: Test with a message
  my_namespace.my_collection.my_test:
    name: hello world

# pass in a message and have changed true
- name: Test with a message and changed output
  my_namespace.my_collection.my_test:
    name: hello world
    new: true

# fail the module
- name: Test failure of the module
  my_namespace.my_collection.my_test:
    name: fail me
'''

RETURN = r'''
# These are examples of possible return values, and in general should use other names for return values.
original_message:
    description: The original name param that was passed in.
    type: str
    returned: always
    sample: 'hello world'
message:
    description: The output message that the test module generates.
    type: str
    returned: always
    sample: 'goodbye'
'''

from ansible.module_utils.basic import AnsibleModule, missing_required_lib
import traceback
try:
    from pyrfc import Connection
except ImportError:
    HAS_PYRFC_LIBRARY = False
    ANOTHER_LIBRARY_IMPORT_ERROR = traceback.format_exc()
else:
    HAS_PYRFC_LIBRARY = True



def call_rfc_method(connection, method_name, kwargs):
    # PyRFC call function
    return connection.call(method_name, **kwargs)


def build_company_params(name, name_2, country, time_zone, city, post_code, street, street_no, e_mail):
    """Creates RFC parameters for creating organizations"""
    # define dicts in batch
    params = dict()
    # define company name
    params['NAME'] = name
    params['NAME_2'] = name_2
    # define location
    params['COUNTRY'] = country
    params['TIME_ZONE'] = time_zone
    params['CITY'] = city
    params['POSTL_COD1'] = post_code
    params['STREET'] = street
    params['STREET_NO'] = street_no
    # define communication
    params['E_MAIL'] = e_mail
    #return dict
    return params


def run_module():
    # define available arguments/parameters a user can pass to the module
    module = AnsibleModule(
        argument_spec=dict(
            # logical values
            state = dict(default='present', choices=['absent', 'present']),
            # values for connection
            conn_username=dict(type='str', required=True, default="DDIC"),
            conn_password=dict(type='str', required=True, no_log=True),
            host=dict(type='str', required=True),
            sysnr=dict(type='str', default="01"),
            client=dict(type='str', default="000"),
            # values for the new or exsisting organization
            company_id = dict(type='str', required=True),
            name = dict(type='str', required=True),
            name_2 = dict(type='str', required=False),
            country = dict(type='str', required=True),
            time_zone = dict(type='str', required=True),
            city = dict(type='str', required=False),
            post_code = dict(type='str', required=False),
            street = dict(type='str', required=False),
            street_no = dict(type='str', required=False),
            e_mail = dict(type='str', required=False),
        ),
        supports_check_mode=False,
    )
    result = dict(changed=False, msg='', out={})
    raw = ""

    params = module.params

    state = params['state']
    conn_username = (params['conn_username']).upper()
    conn_password = params['conn_password']
    host = params['host']
    sysnr = params['sysnr']
    client = params['client']

    company_id = (params['company_id']).upper()
    name = params['name']
    name_2 = params['name_2']
    country = params['country']
    time_zone = params['time_zone']
    city = params['city']
    post_code = params['post_code']
    street = params['street']
    street_no = params['street_no']
    e_mail = params['e_mail']

    if not HAS_PYRFC_LIBRARY:
        module.fail_json(
            msg=missing_required_lib('pyrfc'),
            exception=ANOTHER_LIBRARY_IMPORT_ERROR)    

    # basic RFC connection with pyrfc
    try:
        conn = Connection(user=conn_username, passwd=conn_password, ashost=host, sysnr=sysnr, client=client)
    except Exception as err:
        result['error'] = str(err)
        result['msg'] = 'Something went wrong connecting to the SAP system.'
        module.fail_json(**result)

    # build parameter dict of dict
    company_params = build_company_params(name, name_2, country, time_zone, city, post_code, street, street_no, e_mail)

    if state == "absent":
        raw = call_rfc_method(conn,'BAPI_COMPANY_DELETE', {'COMPANY': company_id})

    if state == "present":
        raw = call_rfc_method(conn,'BAPI_COMPANY_CLONE',
                                       {'METHOD': {'USMETHOD':'COMPANY_CLONE'},'COMPANY': company_id, 'COMP_DATA': company_params })
    
    result['out'] = raw
    result['msg'] = raw['RETURN'][0]['MESSAGE']

    if raw['RETURN'][0]['TYPE'] == 'E':
        module.fail_json(**result)
        
    module.exit_json(**result)


def main():
    run_module()


if __name__ == '__main__':
    main()
