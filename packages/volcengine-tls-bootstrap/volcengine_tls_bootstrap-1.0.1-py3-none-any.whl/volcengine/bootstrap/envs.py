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

import os

DEFAULT_AGENT_URL = "https://volcengine-opentelemetry-python-agent.tos-cn-beijing.volces.com/latest/volcengine-opentelemetry-python-agent.tar.gz"
AGENT_FILE_NAME = "volcengine-opentelemetry-python-agent.tar.gz"
WHL_PATH = "./volcengine-opentelemetry-python-agent"

# 在utils.py中使用的环境变量
PYTHON_AGENT_PATH = "PYTHON_AGENT_PATH"
REGION_ID = "REGION_ID"
DEFAULT_REGION_ID = "cn-beijing"
DEFAULT_VERSION = "latest"

TOS_BUCKET_LIST = {
    "cn-beijing": "volcengine-opentelemetry-python-agent",
    "cn-shanghai": "volcengine-opentelemetry-python-agent",
    "cn-guangzhou": "volcengine-opentelemetry-python-agent",
}
TOS_PREFIX = {
    "cn-beijing": "tos-cn-beijing",
    "cn-shanghai": "tos-cn-shanghai",
    "cn-guangzhou": "tos-cn-guangzhou",
}

TOS_PATH = "agents"
INTERNAL = "internal"
TOS_URL = "volces.com"
