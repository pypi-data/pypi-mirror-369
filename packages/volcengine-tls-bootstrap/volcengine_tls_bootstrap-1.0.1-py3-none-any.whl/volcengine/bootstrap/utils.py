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

import logging
import os
import sys

import requests
from volcengine.bootstrap import envs

logger = logging.getLogger(__name__)


def log_error(message):
    """Log an error message to stdout."""
    print(f"Error: {message}", file=sys.stderr)


def log_info(message):
    """Log an info message to stdout."""
    print(f"Info: {message}", file=sys.stdout)


def log_warning(message):
    """Log an info message to stdout."""
    print(f"Warn: {message}", file=sys.stdout)


"""
获取agent 下载地址。
"""


def get_agent_path():
    url = os.getenv(envs.PYTHON_AGENT_PATH, None)
    if url is not None:
        return url
    region_id = os.getenv(envs.REGION_ID, None)
    if region_id is None:
        region_id = envs.DEFAULT_REGION_ID
    bucket_name = envs.TOS_BUCKET_LIST[region_id]
    if bucket_name is None:
        return None
    tos_prefix = envs.TOS_PREFIX[region_id]
    if tos_prefix is None:
        return None

    # Check if version is specified
    version = os.getenv("TLS_OTEL_AGENT_VERSION", None)
    if version:
        # Use version-specific path
        path_segment = f"{version}/{envs.AGENT_FILE_NAME}"
    else:
        # Use default path
        path_segment = f"{envs.DEFAULT_VERSION}/{envs.AGENT_FILE_NAME}"

    # Try internal URL first
    url = f"https://{bucket_name}.{tos_prefix}.{envs.INTERNAL}.{envs.TOS_URL}/{path_segment}"
    internal_connect = check_network(url=url)
    if internal_connect:
        logger.info(f"use internal region url {url}")
        return url

    # Fallback to public URL
    url = f"https://{bucket_name}.{tos_prefix}.{envs.TOS_URL}/{path_segment}"
    public_connect = check_network(url=url)
    if public_connect:
        logger.info(f"use public region url {url}")
        return url
    return None


"""
判断网络是否通
"""


def check_network(url, timeout=1):
    try:
        response = requests.request("GET", url, timeout=timeout)
        if response.status_code == 200:
            return True
    except Exception:
        return False
