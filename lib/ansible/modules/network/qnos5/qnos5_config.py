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
    'status': ['preview'],
    'supported_by': 'community',
    'version': '1.0'
}

DOCUMENTATION = """
---
module: qnos5_config
version_added: "2.3"
author: "Mark Yang (@QCT)"
short_description: Manage Quanta QNOS5 configuration sections
description:
  - Quanta QNOS5 configurations use a simple block indent file syntax
    for segmenting configuration into sections.  This module provides
    an implementation for working with QNOS5 configuration sections in
    a deterministic way.
extends_documentation_fragment: qnos5
options:
  lines:
    description:
      - The ordered set of commands that should be configured in the
        section.  The commands must be the exact same commands as found
        in the device running-config.  Be sure to note the configuration
        command syntax as some commands are automatically modified by the
        device config parser.
    required: false
    default: null
    aliases: ['commands']
  parents:
    description:
      - The ordered set of parents that uniquely identify the section
        the commands should be checked against.  If the parents argument
        is omitted, the commands are checked against the set of top
        level or global commands.
    required: false
    default: null
  src:
    description:
      - Specifies the source path to the file that contains the configuration
        or configuration template to load.  The path to the source file can
        either be the full path on the Ansible control host or a relative
        path from the playbook or role root directory.  This argument is mutually
        exclusive with I(lines).
    required: false
    default: null
    version_added: "2.2"
  before:
    description:
      - The ordered set of commands to push on to the command stack if
        a change needs to be made.  This allows the playbook designer
        the opportunity to perform configuration commands prior to pushing
        any changes without affecting how the set of commands are matched
        against the system.
    required: false
    default: null
  after:
    description:
      - The ordered set of commands to append to the end of the command
        stack if a change needs to be made.  Just like with I(before) this
        allows the playbook designer to append a set of commands to be
        executed after the command set.
    required: false
    default: null
  match:
    description:
      - Instructs the module on the way to perform the matching of
        the set of commands against the current device config.  If
        match is set to I(line), commands are matched line by line.  If
        match is set to I(strict), command lines are matched with respect
        to position.  If match is set to I(exact), command lines
        must be an equal match.  Finally, if match is set to I(none), the
        module will not attempt to compare the source configuration with
        the running configuration on the remote device.
    required: false
    default: line
    choices: ['line', 'strict', 'exact', 'none']
  replace:
    description:
      - Instructs the module on the way to perform the configuration
        on the device.  If the replace argument is set to I(line) then
        the modified lines are pushed to the device in configuration
        mode.  If the replace argument is set to I(block) then the entire
        command block is pushed to the device in configuration mode if any
        line is not correct.
    required: false
    default: line
    choices: ['line', 'block']
  multiline_delimiter:
    description:
      - This argument is used when pushing a multiline configuration
        element to the QNOS5 device.  It specifies the character to use
        as the delimiting character.  This only applies to the
        configuration action.
    required: false
    default: "@"
    version_added: "2.3"
  force:
    description:
      - The force argument instructs the module to not consider the
        current devices running-config.  When set to true, this will
        cause the module to push the contents of I(src) into the device
        without first checking if already configured.
      - Note this argument should be considered deprecated.  To achieve
        the equivalent, set the C(match=none) which is idempotent.  This argument
        will be removed in a future release.
    required: false
    default: false
    choices: ["true", "false"]
  backup:
    description:
      - This argument will cause the module to create a full backup of
        the current C(running-config) from the remote device before any
        changes are made.  The backup file is written to the C(backup)
        folder in the playbook root directory.  If the directory does not
        exist, it is created.
    required: false
    default: no
    choices: ['yes', 'no']
    version_added: "2.2"
  config:
    description:
      - The C(config) argument allows the playbook designer to supply
        the base configuration to be used to validate configuration
        changes necessary.  If this argument is provided, the module
        will not download the running-config from the remote node.
    required: false
    default: null
    version_added: "2.2"
  defaults:
    description:
      - This argument specifies whether or not to collect all defaults
        when getting the remote device running config.  When enabled,
        the module will get the current config by issuing the command
        C(show running-config).
    required: false
    default: no
    choices: ['yes', 'no']
    version_added: "2.2"
  save:
    description:
      - The C(save) argument instructs the module to save the running-
        config to the startup-config at the conclusion of the module
        running.  If check mode is specified, this argument is ignored.
    required: false
    default: no
    choices: ['yes', 'no']
    version_added: "2.2"
"""

EXAMPLES = """
- name: configure top level configuration
  qnos5_config:
    lines: hostname {{ inventory_hostname }}

- name: configure interface settings
  qnos5_config:
    lines:
      - description test interface
      - ip address 172.31.1.1 255.255.255.0
    parents: interface 0/1

- name: load new acl into device
  qnos5_config:
    lines:
      - 10 permit ip host 1.1.1.1 any log
      - 20 permit ip host 2.2.2.2 any log
      - 30 permit ip host 3.3.3.3 any log
      - 40 permit ip host 4.4.4.4 any log
      - 50 permit ip host 5.5.5.5 any log
    parents: ip access-list test
    before: no ip access-list test
    match: exact
"""

RETURN = """
updates:
  description: The set of commands that will be pushed to the remote device
  returned: Only when lines is specified.
  type: list
  sample: ['...', '...']
backup_path:
  description: The full path to the backup file
  returned: when backup is yes
  type: path
  sample: /playbooks/ansible/backup/qnos5_config.2016-07-16@22:28:34
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
import re
import time

from functools import partial

from ansible.module_utils import qnos5
from ansible.module_utils import qnos5_cli
from ansible.module_utils.basic import AnsibleModule
from ansible.module_utils.local import LocalAnsibleModule
from ansible.module_utils.network_common import ComplexList
from ansible.module_utils.netcli import Conditional
from ansible.module_utils.six import string_types
from ansible.module_utils.netcfg import NetworkConfig, dumps
from ansible.module_utils.six import iteritems


SHARED_LIB = 'qnos5'

def get_ansible_module():
    if SHARED_LIB == 'qnos5':
        return LocalAnsibleModule
    return AnsibleModule

def invoke(name, *args, **kwargs):
    obj = globals().get(SHARED_LIB)
    func = getattr(obj, name)
    return func(*args, **kwargs)

run_commands = partial(invoke, 'run_commands')
load_config = partial(invoke, 'load_config')
get_config = partial(invoke, 'get_config')

def check_args(module, warnings):
    if SHARED_LIB == 'qnos5_cli':
        qnos5_cli.check_args(module)

    if module.params['multiline_delimiter']:
        if len(module.params['multiline_delimiter']) != 1:
            module.fail_json(msg='multiline_delimiter value can only be a '
                                 'single character')
    if module.params['force']:
        warnings.append('The force argument is deprecated as of Ansible 2.2, '
                        'please use match=none instead.  This argument will '
                        'be removed in the future')

def get_running_config(module):
    contents = module.params['config']
    if not contents:
        flags = []
        if module.params['defaults']:
            flags.append('all')
        contents = get_config(module, flags=flags)
    return NetworkConfig(indent=1, contents=contents)

def get_candidate(module):
    candidate = NetworkConfig(indent=1)

    if module.params['src']:
        src = module.params['src']
        candidate.load(src)

    elif module.params['lines']:
        parents = module.params['parents'] or list()
        candidate.add(module.params['lines'], parents=parents)

    return candidate

def main():
    """ main entry point for module execution
    """
    argument_spec = dict(
        src=dict(type='path'),

        lines=dict(aliases=['commands'], type='list'),
        parents=dict(type='list'),

        before=dict(type='list'),
        after=dict(type='list'),

        match=dict(default='line', choices=['line', 'strict', 'exact', 'none']),
        replace=dict(default='line', choices=['line', 'block']),
        multiline_delimiter=dict(default='@'),

        # this argument is deprecated (2.2) in favor of setting match: none
        # it will be removed in a future version
        force=dict(default=False, type='bool'),

        config=dict(),
        defaults=dict(type='bool', default=False),

        backup=dict(type='bool', default=False),
        save=dict(type='bool', default=False),
    )

    argument_spec.update(qnos5_cli.qnos5_cli_argument_spec)

    mutually_exclusive = [('lines', 'src')]

    required_if = [('match', 'strict', ['lines']),
                   ('match', 'exact', ['lines']),
                   ('replace', 'block', ['lines'])]

    cls = get_ansible_module()
    module = cls(argument_spec=argument_spec,
                mutually_exclusive=mutually_exclusive,
                required_if=required_if,
                supports_check_mode=True)

    warnings = list()
    check_args(module, warnings)

    if module.params['force'] is True:
        module.params['match'] = 'none'

    warnings = list()
    check_args(module, warnings)

    result = {'changed': False, 'warnings': warnings}

    if any((module.params['lines'], module.params['src'])):
        match = module.params['match']
        replace = module.params['replace']
        path = module.params['parents']

        candidate = get_candidate(module)

        if match != 'none':
            config = get_running_config(module)
            path = module.params['parents']
            configobjs = candidate.difference(config, path=path, match=match,
                                              replace=replace)
        else:
            configobjs = candidate.items

        if configobjs:
            commands = dumps(configobjs, 'commands').split('\n')

            if module.params['lines']:
                if module.params['before']:
                    commands[:0] = module.params['before']

                if module.params['after']:
                    commands.extend(module.params['after'])

            result['updates'] = commands

            # send the configuration commands to the device and merge
            # them with the current running config
            if not module.check_mode:
                if commands:
                    load_config(module, commands)

            result['changed'] = True

    if module.params['backup']:
        result['__backup__'] = get_config(module=module)

    if module.params['save']:
        if not module.check_mode:
            run_commands(module, ['write memory confirm'])
        result['changed'] = True

    module.exit_json(**result)


if __name__ == '__main__':
    SHARED_LIB = 'qnos5_cli'
    main()
