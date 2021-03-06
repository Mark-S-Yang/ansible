#!/usr/bin/python
#
# This file is part of Ansible
#
# Ansible is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Ansible is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Ansible.  If not, see <http://www.gnu.org/licenses/>.
#
ANSIBLE_METADATA = {
    'status': ['deprecated'],
    'supported_by': 'community',
    'version': '1.0'
}

DOCUMENTATION = """
---
module: qnos5_template
version_added: "2.3"
author: "Mark Yang(@QCT)"
short_description: Manage Quanta QNOS5 device configurations over SSH
description:
  - Manages Quanta QNOS5 network device configurations over SSH.  This module
    allows implementers to work with the device running-config.  It
    provides a way to push a set of commands onto a network device
    by evaluating the current running-config and only pushing configuration
    commands that are not already configured.  The config source can
    be a set of commands or a template.
deprecated: Deprecated in 2.2. Use M(qnos5_config) instead.
extends_documentation_fragment: qnos5
options:
  src:
    description:
      - The path to the config source.  The source can be either a
        file with config or a template that will be merged during
        runtime.  By default the task will first search for the source
        file in role or playbook root folder in templates unless a full
        path to the file is given.
    required: true
  force:
    description:
      - The force argument instructs the module not to consider the
        current device running-config.  When set to true, this will
        cause the module to push the contents of I(src) into the device
        without first checking if already configured.
    required: false
    default: false
    choices: [ "true", "false" ]
  include_defaults:
    description:
      - The module, by default, will collect the current device
        running-config to use as a base for comparison to the commands
        in I(src).  Setting this value to true will cause the command
        issued to add any necessary flags to collect all defaults as
        well as the device configuration.  If the destination device
        does not support such a flag, this argument is silently ignored.
    required: true
    choices: [ "true", "false" ]
  backup:
    description:
      - When this argument is configured true, the module will backup
        the running-config from the node prior to making any changes.
        The backup file will be written to backup_{{ hostname }} in
        the root of the playbook directory.
    required: false
    default: false
    choices: [ "true", "false" ]
  config:
    description:
      - The module, by default, will connect to the remote device and
        retrieve the current running-config to use as a base for comparing
        against the contents of source.  There are times when it is not
        desirable to have the task get the current running-config for
        every task.  The I(config) argument allows the implementer to
        pass in the configuration to use as the base config for
        comparison.
    required: false
    default: null
"""

EXAMPLES = """
- name: push a configuration onto the device
  qnos5_template:
    src: config.j2

- name: forceable push a configuration onto the device
  qnos5_template:
    src: config.j2
    force: yes

- name: provide the base configuration for comparison
  qnos5_template:
    src: candidate_config.txt
    config: current_config.txt
"""

RETURN = """
updates:
  description: The set of commands that will be pushed to the remote device
  returned: always
  type: list
  sample: ['...', '...']
start:
  description: The time the job started
  returned: always
  type: str
  sample: "2016-11-16 10:38:15.126146"
end:
  description: The time the job ended
  returned: always
  type: str
  sample: "2016-11-16 10:38:25.595612"
delta:
  description: The time elapsed to perform all operations
  returned: always
  type: str
  sample: "0:00:10.469466"
"""
from functools import partial

from ansible.module_utils import qnos5
from ansible.module_utils import qnos5_cli
from ansible.module_utils.basic import AnsibleModule
from ansible.module_utils.local import LocalAnsibleModule
from ansible.module_utils.network_common import ComplexList
from ansible.module_utils.netcli import Conditional
from ansible.module_utils.six import string_types
from ansible.module_utils.netcfg import NetworkConfig, dumps

SHARED_LIB = 'qnos5'

def get_ansible_module():
    if SHARED_LIB == 'qnos5':
        return LocalAnsibleModule
    return AnsibleModule

def invoke(name, *args, **kwargs):
    obj = globals().get(SHARED_LIB)
    func = getattr(obj, name)
    return func(*args, **kwargs)

load_config = partial(invoke, 'load_config')
get_config = partial(invoke, 'get_config')

def check_args(module, warnings):
    if SHARED_LIB == 'qnos5_cli':
        qnos5_cli.check_args(module)

def get_current_config(module):
    if module.params['config']:
        return module.params['config']
    if module.params['include_defaults']:
        flags = ['all']
    else:
        flags = []
    return get_config(module=module, flags=flags)

def main():
    """ main entry point for module execution
    """
    argument_spec = dict(
        src=dict(),
        force=dict(default=False, type='bool'),
        include_defaults=dict(default=True, type='bool'),
        backup=dict(default=False, type='bool'),
        config=dict(),
    )

    argument_spec.update(qnos5_cli.qnos5_cli_argument_spec)

    mutually_exclusive = [('config', 'backup'), ('config', 'force')]

    cls = get_ansible_module()
    module = cls(argument_spec=argument_spec,
                 mutually_exclusive=mutually_exclusive,
                 supports_check_mode=True)

    warnings = list()
    check_args(module, warnings)

    candidate = NetworkConfig(contents=module.params['src'], indent=1)

    result = {'changed': False}
    if warnings:
        result['warnings'] = warnings

    if module.params['backup']:
        result['__backup__'] = get_config(module=module)

    if not module.params['force']:
        contents = get_current_config(module)
        configobj = NetworkConfig(contents=contents, indent=1)
        commands = candidate.difference(configobj)
        commands = dumps(commands, 'commands').split('\n')
        commands = [str(c).strip() for c in commands if c]
    else:
        commands = [c.strip() for c in str(candidate).split('\n')]

    if commands:
        if not module.check_mode:
            load_config(module, commands)
        result['changed'] = True

    result['updates'] = commands

    module.exit_json(**result)

if __name__ == '__main__':
    SHARED_LIB = 'qnos5_cli'
    main()
