#!/usr/bin/env python

"""
Thin wrapper around the "az" command line interface (CLI) for use
with LocalStack.

The "azlocal" CLI allows you to easily interact with your local Azure services
without having to configure anything.

Example:
Instead of the following command ...
HTTPS_PROXY=... REQUESTS_CA_BUNDLE=... az storage account list
... you can simply use this:
azlocal storage account list

Options:
  Run "azlocal help" for more details on the Azure CLI subcommands.
"""

import os
import sys
from pathlib import Path

from .constants import AZURE_CONFIG_DIR_ENV
from .shared import prepare_environment, get_proxy_endpoint, get_proxy_env_vars, AZURE_CONFIG_DIR, run_in_background


def usage():
    print(__doc__.strip())


def run(cmd, env):
    """
    Replaces this process with the AZ CLI process, with the given command and environment
    """
    os.execvpe(cmd[0], cmd, env)


def main():
    if len(sys.argv) > 1 and sys.argv[1] == '-h':
        return usage()
    run_as_separate_process()


def run_as_separate_process():
    """
    Constructs a command line string and calls "az" as an external process.
    """

    cmd_args = list(sys.argv)
    cmd_args[0] = 'az'
    if ("--help" in cmd_args) or ("--version" in cmd_args):
        # Early exit - if we only want to know the version/help, we don't need LS to be running
        run(cmd_args, None)
        return

    proxy_endpoint = get_proxy_endpoint()

    env_dict = prepare_environment(proxy_endpoint)

    env_dict[AZURE_CONFIG_DIR_ENV] = AZURE_CONFIG_DIR
    if not os.path.exists(AZURE_CONFIG_DIR):
        # Create the config directory
        Path(AZURE_CONFIG_DIR).mkdir(parents=True, exist_ok=True)

        # Prepare necessary arguments to ensure `az ..` commands are run against this config directory
        az_args_list = [f"{key}={val}" for key, val in get_proxy_env_vars(proxy_endpoint).items()]
        az_args_list.append(f"{AZURE_CONFIG_DIR_ENV}={AZURE_CONFIG_DIR}")
        az_arg = " ".join(az_args_list)

        # Turn off telemetry
        survey_command = f"{az_arg} az config set output.show_survey_link=no"
        run_in_background(survey_command)
        telemetry_command = f"{az_arg} az config set core.collect_telemetry=false"
        run_in_background(telemetry_command)

        # Login to ensure the config directory has credentials
        login_command = f"{az_arg} az login --service-principal -u any-app -p any-pass --tenant any-tenant"
        run_in_background(login_command)

    # Hijack the login command
    # When creating our custom config dir, we automatically log in - so this is not necessary anymore
    if len(cmd_args) == 2 and cmd_args[1] == "login":
        print("Login Succeeded")
        return

    # Hijack the ACR login command
    if len(cmd_args) > 1 and cmd_args[1] == "acr" and "login" in cmd_args:
        print("Login Succeeded")
        return

    # run the command
    run(cmd_args, env_dict)


if __name__ == '__main__':
    main()
