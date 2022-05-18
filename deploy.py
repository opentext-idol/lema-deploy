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
                   help='path to a configuration file with values that override all other '
                        'configuration files')
    p.add_argument('--skip-pull', action='store_const', const=True, default=False,
                   help='skip pulling Docker images; allows running against a custom set of images')
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


def run_compose(components, options, detach=True, remove=False, log_level='info'):
    # base should be first
    components = ['base'] + list(components)

    compose_args = ['docker-compose']
    compose_args.extend(['--log-level', log_level])
    if options.docker_host is not None:
        compose_args.extend(['--host', options.docker_host])
    env_paths = (list(get_env_paths(components)) +
                 ([] if options.config_file is None else [options.config_file]))
    compose_args.extend(['--env-file', build_env_file(env_paths)])
    for compose_path in get_compose_paths(components):
        compose_args.extend(['--file', compose_path])

    if not options.skip_pull:
        subprocess.check_call(compose_args + ['pull'])

    up_args = ['up']
    if detach:
        up_args.append('--detach')
    if remove:
        up_args.append('--remove-orphans')
    subprocess.check_call(compose_args + up_args)


def deploy(components, options):
    components = list(components)
    if options.disable_encryption:
        # should be last
        components.append('unencrypted')

    run_compose(components, options, remove=True)


def initialise(options):
    components = ['auth-setup']
    if options.disable_encryption:
        # should be last
        components.append('unencrypted')

    run_compose(components, options, detach=False, log_level='error')


def main():
    program_args = parse_args()
    # workaround for argparse bug: https://bugs.python.org/issue27227
    # we set COMPONENT_DEFAULT to a unique object, set it as valid, and set it as the default
    # then if no values are specified, argparse gives us COMPONENT_DEFAULT instead of a list
    components = [] if program_args.component is COMPONENT_DEFAULT else program_args.component
    deploy(components, program_args)
    if program_args.init:
        initialise(program_args)


main()
