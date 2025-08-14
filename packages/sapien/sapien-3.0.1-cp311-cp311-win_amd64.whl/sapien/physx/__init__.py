#
# Copyright 2025 Hillbot Inc.
# Copyright 2020-2024 UCSD SU Lab
# 
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at:
# 
#     http://www.apache.org/licenses/LICENSE-2.0
# 
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
import io
import platform
from pathlib import Path
from zipfile import ZipFile

import requests

from ..pysapien.physx import *
from ..pysapien.physx import _enable_gpu


def enable_gpu():
    if is_gpu_enabled():
        return

    physx_version = version()
    parent = Path.home() / ".sapien" / "physx" / physx_version
    parent.mkdir(exist_ok=True, parents=True)

    if platform.system() == "Windows":
        dll = parent / "PhysXGpu_64.dll"
        url = f"https://github.com/sapien-sim/physx-precompiled/releases/download/{physx_version}/windows-dll.zip"
    elif platform.system() == "Linux" and platform.machine() in ("x86_64", "AMD64"):
        dll = parent / "libPhysXGpu_64.so"
        url = f"https://github.com/sapien-sim/physx-precompiled/releases/download/{physx_version}/linux-so.zip"
    elif platform.system() == "Linux" and platform.machine() in ("aarch64", "arm64"):
        dll = parent / "libPhysXGpu_64.so"
        url = f"https://github.com/sapien-sim/physx-precompiled/releases/download/{physx_version}/linux-aarch64-so.zip"
    else:
        raise RuntimeError("Unsupported platform")

    if not dll.exists():
        print(
            f"Downloading PhysX GPU library to {parent} from Github. This can take several minutes."
            f" If it fails to download, please manually download f{url} and unzip at {parent}."
        )
        res = requests.get(url)
        z = ZipFile(io.BytesIO(res.content))
        z.extractall(parent)
        print("Download complete.")

    import ctypes

    if platform.system() == "Windows":
        ctypes.CDLL("cuda.dll", ctypes.RTLD_GLOBAL)
        ctypes.CDLL(str(dll), ctypes.RTLD_LOCAL)
    elif platform.system() == "Linux":
        ctypes.CDLL("libcuda.so", ctypes.RTLD_GLOBAL)
        ctypes.CDLL(str(dll), ctypes.RTLD_LOCAL)

    _enable_gpu()
