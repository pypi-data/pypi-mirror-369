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

import glob
import logging
import os
import shutil
import subprocess
import sys
import tarfile
from importlib.metadata import PackageNotFoundError, distribution
from typing import List, Optional

import volcengine.bootstrap.envs as envs
from packaging.requirements import Requirement
from requests import ConnectionError, HTTPError, RequestException, Timeout, get
from volcengine.bootstrap.bootstrap_gen import install_packages, libraries
from volcengine.bootstrap.utils import get_agent_path, log_error, log_info, log_warning

# import tqdm
try:
    from tqdm import tqdm

    TQDM_AVAILABLE = True
except ImportError:
    TQDM_AVAILABLE = False


# 系统调用装饰器（增强类型提示）
def syscall(func):
    """系统调用异常处理装饰器"""

    def wrapper(self, package: Optional[List[str]] = None):
        try:
            return func(self, package) if package else func(self)
        except subprocess.CalledProcessError as exp:
            cmd = " ".join(exp.cmd) if exp.cmd else "unknown command"
            stderr_msg = exp.stderr.decode() if exp.stderr else "No stderr output"
            msg = f"Command failed: {cmd}, Error: {stderr_msg}"
            raise RuntimeError(msg) from exp
        except Exception as exp:
            raise RuntimeError(f"System call failed: {str(exp)}") from exp

    return wrapper


# 包管理模块（增加类型注释和文档字符串）
class PackageManager:
    """包管理工具类"""

    def __init__(self, pip_path: Optional[str] = None):
        self.pip_path = pip_path or os.getenv("PIPPATH")

    def _bulk_install(self, packages: List[str]) -> None:
        """批量安装包（带进度条）"""
        log_info(f"Installing {len(packages)} packages to {self.pip_path}")
        cmd = [
            sys.executable,
            "-m",
            "pip",
            "install",
            "--target",
            self.pip_path,
            "--no-cache-dir",
        ] + packages

        subprocess.run(cmd, check=True)

    @syscall
    def install(self, package: List[str]) -> None:
        """安装包（支持单包和批量安装）"""
        if self.pip_path:
            self._bulk_install(package)
        else:
            cmd = [
                sys.executable,
                "-m",
                "pip",
                "install",
                "-U",
                "--upgrade-strategy",
                "only-if-needed",
            ] + package
            self._handle_pip_install(cmd, package)

    def _handle_pip_install(self, cmd: List[str], packages: List[str]) -> None:
        """处理默认路径安装逻辑"""
        subprocess.run(cmd, check=True)

    @syscall
    def uninstall(self, package: str) -> None:
        """卸载包"""
        log_info(f"Uninstalling {package}")
        cmd = [sys.executable, "-m", "pip", "uninstall", "-y", package]
        subprocess.run(cmd, check=True)


# 文件处理模块（重构为类）
class FileHandler:
    """文件处理工具类"""

    def __init__(self):
        self.file_path = envs.AGENT_FILE_NAME
        self.whl_path = envs.WHL_PATH

    def is_local_file(self) -> bool:
        """检查本地安装文件是否存在"""
        return os.path.isfile(self.file_path)

    def download_agent(self, url: str) -> bool:
        """下载agent文件（带错误处理和进度条）"""
        log_info(f"Downloading agent from {url}")
        try:
            response = get(url, stream=True, timeout=30)
            response.raise_for_status()
            total_size = int(response.headers.get("content-length", 0))
            return self._save_with_progress(response, total_size)
        except Timeout:
            log_error(f"Download timed out")
            return False
        except ConnectionError:
            log_error(f"Network connection error")
            return False
        except HTTPError as err:
            log_error(f"HTTP error: {err}")
            return False
        except Exception as err:
            log_error(f"Download failed: {err}")
            return False

    def _save_with_progress(self, response, total_size: int) -> bool:
        """带进度条的文件保存"""
        try:
            if TQDM_AVAILABLE:
                with open(self.file_path, "wb") as f, tqdm(
                    desc="Downloading", total=total_size, unit="B", unit_scale=True
                ) as bar:
                    for data in response.iter_content(chunk_size=1024):
                        bar.update(len(data))
                        f.write(data)
            else:
                with open(self.file_path, "wb") as f:
                    for data in response.iter_content(chunk_size=1024):
                        f.write(data)
            return True
        except Exception as err:
            log_error(f"Failed to save file: {err}")
            return False

    def extract_whls(self) -> List[str]:
        """extract whl files"""
        os.makedirs(self.whl_path, exist_ok=True)
        log_info("Extracting wheel files")
        try:
            with tarfile.open(self.file_path, "r:gz") as tar:
                if TQDM_AVAILABLE:
                    members = tar.getmembers()
                    with tqdm(
                        total=len(members), desc="Extracting files", unit="file"
                    ) as pbar:
                        for member in members:
                            tar.extract(member, path=self.whl_path)
                            pbar.update(1)
                else:
                    tar.extractall(path=self.whl_path)
        except tarfile.TarError as e:
            log_error(f"Failed to extract package: {e}")
            raise RuntimeError("Invalid package format") from e

        # get all whl files
        whl_files = glob.glob(f"{self.whl_path}/*.whl")
        log_info(f"Found {len(whl_files)} wheel files")
        log_info(f"Found wheel files: {whl_files}")
        return whl_files

    def clean_temp_files(self) -> None:
        """清理临时文件"""
        try:
            os.remove(self.file_path)
            shutil.rmtree(self.whl_path, ignore_errors=True)
            log_info("Temporary files cleaned")
        except Exception as err:
            log_error(f"Failed to clean temp files: {err}")


# 依赖检测模块
class DependencyChecker:
    """依赖检测工具类"""

    logger = logging.getLogger(__name__)

    @staticmethod
    def check_conflicts() -> None:
        """检查依赖冲突"""
        result = subprocess.run(
            [sys.executable, "-m", "pip", "check"], capture_output=True, text=True
        )
        if result.returncode != 0:
            raise RuntimeError(f"Dependency conflicts found:\n{result.stdout}")

    @staticmethod
    def is_installed(req: str) -> bool:
        """检查包是否已安装"""
        try:
            distribution(req)
            return True
        except PackageNotFoundError:
            return False

    @staticmethod
    def _is_installed(req: str) -> bool:
        """检查包是否已安装且版本匹配"""
        req_obj = Requirement(req)
        try:
            dist_version = distribution(req_obj.name).version
        except PackageNotFoundError:
            return False
        if not req_obj.specifier.contains(dist_version):
            DependencyChecker.logger.warning(
                "instrumentation for package %s is available"
                " but version %s is installed. Skipping.",
                req,
                dist_version,
            )
            return False
        return True

    @staticmethod
    def _find_installed_libraries():
        """查找已安装的库"""
        for lib in install_packages:
            yield lib

        for lib in libraries:
            if DependencyChecker._is_installed(lib["library"]):
                yield lib["instrumentation"]


# 核心安装逻辑
class AgentInstaller:
    """Agent安装核心类"""

    def __init__(self):
        self.package_manager = PackageManager()
        self.file_handler = FileHandler()
        self.dependency_checker = DependencyChecker()
        self.agent_url = self._get_agent_url()

    def _get_agent_url(self) -> str:
        """获取agent下载URL"""
        # 首先尝试使用get_agent_path函数获取URL
        url = get_agent_path()
        if url is not None:
            return url
        # 如果get_agent_path返回None，则使用原来的逻辑
        return os.getenv("PYTHON_AGENT_PATH", envs.DEFAULT_AGENT_URL)

    def _prepare_installation(
        self, agent_url: str = None, package_path: str = None, is_local: bool = False
    ) -> bool:
        """安装前准备（网络检查和文件下载）"""
        # 如果指定了本地安装，直接检查固定路径文件
        if is_local:
            log_info("Using local installation mode")
            if not self.file_handler.is_local_file():
                log_error(f"Local package not found at: {self.file_handler.file_path}")
                return False
            log_info(f"Found local package: {self.file_handler.file_path}")
            return True

        # 如果指定了本地包路径，优先使用本地包
        if package_path and os.path.isfile(package_path):
            log_info(f"Using specified local package: {package_path}")
            try:
                shutil.copy(package_path, self.file_handler.file_path)
                return True
            except Exception as e:
                log_error(f"Failed to copy local package: {e}")
                return False

        # 如果指定了URL，使用指定URL
        download_url = agent_url or self.agent_url

        # 网络下载逻辑
        if not self._check_network(download_url):
            return False
        if not self.file_handler.download_agent(download_url):
            return False
        return True

    def _check_network(self, url: str) -> bool:
        """检查网络连通性"""
        try:
            response = get(url, timeout=5)
            response.raise_for_status()
            return True
        except RequestException:
            log_error(f"Network check failed for {url}")
            return False

    def install_agent(
        self,
        target: str = None,
        agent_url: str = None,
        package_path: str = None,
        version: str = None,
        is_local: bool = False,
    ) -> None:
        """执行安装流程

        Args:
            target: 安装目标目录
            agent_url: 自定义代理下载URL
            package_path: 本地包路径
            version: 指定版本号
            is_local: 是否从本地安装
        """
        log_info("Starting agent installation")

        # 如果指定了目标目录，更新包管理器
        if target:
            self.package_manager = PackageManager(target)
            log_info(f"Installing to target directory: {target}")

        # 检查本地安装模式下是否同时指定了版本号
        if is_local and version:
            log_warning("Version parameter is ignored in local installation mode")
            version = None

        # 如果指定了版本且不是本地安装，更新下载URL
        if version and not is_local:
            # 设置环境变量供get_agent_path使用
            os.environ["TLS_OTEL_AGENT_VERSION"] = version
            if agent_url:
                # 如果用户同时提供了URL和版本，尝试替换URL中的版本号
                if "/latest/" in agent_url:
                    agent_url = agent_url.replace("/latest/", f"/{version}/")
                else:
                    log_warning(
                        f"Cannot apply version {version} to custom URL. Using URL as-is."
                    )
            else:
                # 如果是默认URL，替换版本号
                if "/latest/" in self.agent_url:
                    agent_url = self.agent_url.replace("/latest/", f"/{version}/")
                else:
                    log_warning(
                        f"Cannot apply version {version} to default URL. Using default URL."
                    )

        # 确保传递正确的URL给_prepare_installation
        effective_agent_url = agent_url or self.agent_url

        log_info(f"Agent URL: {effective_agent_url}")
        log_info(f"Local package: {package_path or 'None'}")
        log_info(f"Version: {version or 'latest'}")
        log_info(f"Local installation mode: {is_local}")

        # 准备安装
        if not self._prepare_installation(effective_agent_url, package_path, is_local):
            log_error("Installation preparation failed")
            return

        # 提取并安装包
        whl_files = self.file_handler.extract_whls()
        if not whl_files:
            raise RuntimeError("No wheel files found in package")

        self.package_manager.install(whl_files)
        self._create_sitecustomize()
        self.dependency_checker.check_conflicts()
        self.file_handler.clean_temp_files()
        log_info("Installation completed successfully")

    def install_requirements(self) -> None:
        """执行requirements安装流程"""
        DependencyChecker.logger.setLevel(logging.ERROR)
        packages_to_install = list(DependencyChecker._find_installed_libraries())
        if packages_to_install:
            log_info(f"Requirements to install: {', '.join(packages_to_install)}")
        else:
            log_info("No requirements to install")
            # self.package_manager.install(packages_to_install)

    def _create_sitecustomize(self) -> None:
        """创建sitecustomize文件"""
        if self.package_manager.pip_path:
            site_path = os.path.join(self.package_manager.pip_path, "sitecustomize.py")
            with open(site_path, "w") as f:
                f.write(
                    "from volcengine.opentelemetry.instrumentation.auto_instrumentation import sitecustomize"
                )
            log_info(f"Created sitecustomize at {site_path}")

    def uninstall_agent(self) -> None:
        """执行卸载流程"""
        packages = install_packages
        log_info(f"Uninstalling {len(packages)} packages")
        failed = []
        for package in packages:
            try:
                self.package_manager.uninstall(package)
            except Exception as err:
                log_error(f"Failed to uninstall {package}: {err}")
                failed.append(package)
        if failed:
            log_error(f"Failed packages: {', '.join(failed)}")
        else:
            log_info("Uninstallation completed")
