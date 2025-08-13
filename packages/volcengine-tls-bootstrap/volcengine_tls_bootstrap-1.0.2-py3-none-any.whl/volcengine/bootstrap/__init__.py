# Copyright (c) 2024 Bytedance Ltd. and/or its affiliates
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import argparse
import logging

import volcengine.bootstrap.bootstrap as bootstrap
from volcengine.bootstrap.utils import log_error, log_info
from volcengine.bootstrap.version import __version__


def run() -> None:
    """
    Unified entry point. Handles command-line arguments and executes corresponding operations.
    Can be called directly or used as a library function.
    """
    log_info(f"start python agent version: {__version__}")
    cli = CLI()
    cli.execute()


class CLI:
    """
    Command-line interface class (optimized argument parsing and process control).
    """

    def __init__(self):
        self.parser = argparse.ArgumentParser(
            description="Volcengine Opentelemetry Python Agent Installation Bootstrapper",
            formatter_class=argparse.RawTextHelpFormatter,
        )
        self._configure_arguments()
        self.args = self.parser.parse_args()

    def _configure_arguments(self) -> None:
        """Configure command-line arguments (extract common parameter logic)."""
        self.parser.add_argument(
            "-a",
            "--action",
            choices=["install", "uninstall", "requirements"],
            default="install",
            help="Operation type:\n"
            "install - Install the agent (default)\n"
            "uninstall - Uninstall the agent\n"
            "requirements - Install requirements",
        )
        self.parser.add_argument(
            "--local",
            help="Install from local directory instead of downloading from remote source",
            action="store_true",
        )
        self.parser.add_argument(
            "-t",
            "--target",
            help="Specify the installation target directory (default: system path)",
            metavar="PATH",
        )
        self.parser.add_argument(
            "-u",
            "--agent-url",
            help="Specify the agent download URL (override default address)",
            metavar="URL",
        )
        self.parser.add_argument(
            "-v",
            "--version",
            help="Specify the agent version to install (e.g., 1.0.0). If not provided, the latest version will be used.",
            metavar="VERSION",
        )

    def execute(self) -> None:
        """Execute specific operations (separate parameter processing from business logic)."""
        installer = bootstrap.AgentInstaller()

        try:
            if self.args.action == "install":
                installer.install_agent(
                    is_local=self.args.local,
                    target=self.args.target,
                    agent_url=self.args.agent_url,
                    version=self.args.version,
                )
            elif self.args.action == "uninstall":
                installer.uninstall_agent()
            elif self.args.action == "requirements":
                installer.install_requirements()
        except Exception as e:
            log_error(f"!!! ERROR: Operation failed - {str(e)} !!!")
            raise SystemExit(1)
