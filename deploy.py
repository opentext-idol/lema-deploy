#
# (c) Copyright 2021 Micro Focus or one of its affiliates.
#
# Licensed under the MIT License (the "License"); you may not use this file
# except in compliance with the License.
#
# The only warranties for products and services of Micro Focus and its affiliates
# and licensors ("Micro Focus") are as may be set forth in the express warranty
# statements accompanying such products and services. Nothing herein should be
# construed as constituting an additional warranty. Micro Focus shall not be
# liable for technical or editorial errors or omissions contained herein. The
# information contained herein is subject to change without notice.
#

import textwrap
import sys
import os
import shutil
import subprocess
import argparse

COMPONENT_DEFAULT = object()
COMPONENTS = [
    COMPONENT_DEFAULT,
    'auth',
    'entity',
    'filestore',
    'analysis',
    'audit',
    'api',
    'ui',
]
BASE_PATH = os.path.dirname(os.path.abspath(sys.argv[0]))
OUTPUT_WIDTH = min(100, shutil.get_terminal_size()[0])


def wrap(text):
    return textwrap.fill(text, OUTPUT_WIDTH)


DESCRIPTION = '''
Deploy IDOL LEMA.

''' + wrap('''\
This program deploys components of the LEMA system, or resumes a stopped system, or reconfigures an
existing system.  Before running, check and update the configuration in `config/base.env`.
''') + '''

''' + wrap('''\
By default, nothing is deployed; for a working system, all components are required, but you may
deploy them on different hosts.  For each component you deploy using this program, check and update
its individual configuration file - for example, to configure the 'auth' component, you can edit
`config/auth.env`.
''') + '''

''' + wrap('''\
The components that can only be deployed using this script are:
''') + '''

- entity: storage for application data
- analysis: media analysis system
- api: user-facing web server
- ui: user-facing web server

''' + wrap('''\
The components that may be deployed using this script, or may be deployed manually using suitable
replacements, are:
''') + '''

- auth: user-facing web server - Keycloak authentication server
- filestore: storage for files - Amazon S3-compatible object storage
- audit: storage for audit logs - PostgreSQL database server
'''


def parse_args():
    p = argparse.ArgumentParser(description=DESCRIPTION,
                                formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument('component', nargs='*', default=COMPONENT_DEFAULT, choices=COMPONENTS,
                   metavar='COMPONENT', help='components to deploy')
    p.add_argument('--docker-host', metavar='HOST',
                   help='Docker host to run containers on (default: use Docker running locally)')
    p.add_argument('--init', action='store_const', const=True, default=False,
                   help='after the system is running, perform one-time initialisation tasks')
    p.add_argument('--disable-encryption', action='store_const', const=True, default=False,
                   help='configure user-facing servers to accept HTTP connections (by default, '
                        'user-facing servers accept HTTPS connections)')
    p.add_argument('--config-file', metavar='FILE',
                   help='Path to a configuration file with values that override all other '
                        'configuration files')
    return p.parse_args()


def get_env_paths(components):
    for component in components:
        for source in ('config-fixed', 'config'):
            path = os.path.join(BASE_PATH, source, f'{component}.env')
            if os.path.exists(path):
                yield path


def build_env_file(env_paths):
    target_path = os.path.join(BASE_PATH, '.env')
    with open(target_path, 'w') as target_f:
        for source_path in env_paths:
            with open(source_path) as source_f:
                target_f.write(f'\n\n# source: {source_path}\n\n')
                target_f.write(source_f.read())
    return target_path


def get_compose_paths(components):
    for component in components:
        path = os.path.join(BASE_PATH, 'docker-compose', f'docker-compose.{component}.yml')
        if os.path.exists(path):
            yield path


def run_compose(docker_host, components, config_path, detach=True, remove=False, log_level='info'):
    # base should be first
    components = ['base'] + list(components)

    compose_args = ['docker-compose']
    compose_args.extend(['--log-level', log_level])
    if docker_host is not None:
        compose_args.extend(['--host', docker_host])
    env_paths = list(get_env_paths(components)) + ([] if config_path is None else [config_path])
    compose_args.extend(['--env-file', build_env_file(env_paths)])
    for compose_path in get_compose_paths(components):
        compose_args.extend(['--file', compose_path])
    compose_args.extend(['up'])
    if detach:
        compose_args.append('--detach')
    if remove:
        compose_args.append('--remove-orphans')

    subprocess.check_call(compose_args)


def deploy(docker_host, components, config_path, disable_encryption):
    components = list(components)
    if disable_encryption:
        # should be last
        components.append('unencrypted')

    run_compose(docker_host, components, config_path, remove=True)


def initialise(docker_host, config_path, disable_encryption):
    components = ['auth-setup']
    if disable_encryption:
        # should be last
        components.append('unencrypted')

    run_compose(docker_host, components, config_path, detach=False, log_level='error')


def main():
    program_args = parse_args()
    # workaround for argparse bug: https://bugs.python.org/issue27227
    # we set COMPONENT_DEFAULT to a unique object, set it as valid, and set it as the default
    # then if no values are specified, argparse gives us COMPONENT_DEFAULT instead of a list
    components = [] if program_args.component is COMPONENT_DEFAULT else program_args.component
    deploy(program_args.docker_host, components, program_args.config_file,
           program_args.disable_encryption)
    if program_args.init:
        initialise(program_args.docker_host, program_args.config_file,
                   program_args.disable_encryption)


main()
