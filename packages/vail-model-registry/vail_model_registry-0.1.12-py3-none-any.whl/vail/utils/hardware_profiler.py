"""
Hardware Profiler Module

This module provides functionality for detecting and profiling hardware information
on the local machine, including CPU, memory, GPU, disk, and system information.
"""

import platform
import subprocess
from datetime import datetime
from typing import Dict, List, Optional

import psutil
import torch


class HardwareInfo:
    """
    Class representing hardware information with Pydantic-style serialization.
    """

    def __init__(
        self,
        cpu: Dict,
        memory: Dict,
        gpu: List[Dict],
        disk: Dict,
        system: Dict,
        last_updated: Optional[datetime] = None,
    ):
        """
        Initialize hardware information.

        Args:
            cpu: CPU information
            memory: Memory information
            gpu: GPU information
            disk: Disk information
            system: System information
            last_updated: When the hardware information was last updated
        """
        self.cpu = cpu
        self.memory = memory
        self.gpu = gpu
        self.disk = disk
        self.system = system
        self.last_updated = last_updated or datetime.now()

    def to_dict(self) -> Dict:
        """
        Convert the HardwareInfo object to a dictionary that can be serialized.

        Returns:
            Dictionary representation of the HardwareInfo object
        """
        return {
            "cpu": self.cpu,
            "memory": self.memory,
            "gpu": self.gpu,
            "disk": self.disk,
            "system": self.system,
            "last_updated": self.last_updated,
        }

    @classmethod
    def from_dict(cls, hardware_dict: Dict) -> "HardwareInfo":
        """
        Create a HardwareInfo object from a dictionary.

        Args:
            hardware_dict: Dictionary representation of a HardwareInfo object

        Returns:
            HardwareInfo object
        """
        return cls(
            cpu=hardware_dict.get("cpu", {}),
            memory=hardware_dict.get("memory", {}),
            gpu=hardware_dict.get("gpu", []),
            disk=hardware_dict.get("disk", {}),
            system=hardware_dict.get("system", {}),
            last_updated=hardware_dict.get("last_updated", datetime.now()),
        )


class HardwareProfiler:
    """
    Class for profiling hardware information on the local machine.
    """

    @staticmethod
    def get_local_hardware_info() -> HardwareInfo:
        """
        Gather information about the hardware available on the machine.

        Returns:
            HardwareInfo object containing hardware information
        """
        cpu_info = {
            "count": psutil.cpu_count(),
            "physical_count": psutil.cpu_count(logical=False),
            "model": platform.processor(),
            "frequency": psutil.cpu_freq()._asdict() if psutil.cpu_freq() else None,
        }

        memory_info = {
            "total": psutil.virtual_memory().total,
            "available": psutil.virtual_memory().available,
            "percent": psutil.virtual_memory().percent,
        }

        # Get GPU information
        gpu_info = HardwareProfiler._detect_gpus()

        # Get disk information
        disk_info = {
            "total": psutil.disk_usage("/").total,
            "available": psutil.disk_usage("/").free,
            "percent": psutil.disk_usage("/").percent,
        }

        # Get system information
        system_info = {
            "os": platform.system(),
            "os_version": platform.version(),
            "python_version": platform.python_version(),
            "torch_version": torch.__version__,
            "cuda_version": torch.version.cuda if torch.cuda.is_available() else None,
        }

        return HardwareInfo(
            cpu=cpu_info,
            memory=memory_info,
            gpu=gpu_info,
            disk=disk_info,
            system=system_info,
        )

    @staticmethod
    def _detect_gpus() -> List[Dict]:
        """
        Detect GPUs using multiple methods.

        Returns:
            List of dictionaries containing GPU information
        """
        gpu_info = []

        # Method 1: Try using torch.cuda
        if torch.cuda.is_available():
            for i in range(torch.cuda.device_count()):
                gpu = {
                    "name": torch.cuda.get_device_name(i),
                    "memory_total": torch.cuda.get_device_properties(i).total_memory,
                    "memory_allocated": torch.cuda.memory_allocated(i),
                    "memory_cached": torch.cuda.memory_reserved(i),
                    "detection_method": "torch.cuda",
                }
                gpu_info.append(gpu)

        # If we already found GPUs, return them
        if gpu_info:
            return gpu_info

        # Method 2: Try using nvidia-smi command
        try:
            result = subprocess.run(
                [
                    "nvidia-smi",
                    "--query-gpu=gpu_name,memory.total,memory.used,memory.free",
                    "--format=csv,noheader,nounits",
                ],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
            )
            if result.returncode == 0 and result.stdout.strip():
                for line in result.stdout.strip().split("\n"):
                    name, total, used, free = line.split(",")
                    gpu = {
                        "name": name.strip(),
                        "memory_total": int(total.strip()),
                        "memory_allocated": int(used.strip()),
                        "memory_cached": int(total.strip()) - int(free.strip()),
                        "detection_method": "nvidia-smi",
                    }
                    gpu_info.append(gpu)
        except (subprocess.SubprocessError, FileNotFoundError, ValueError):
            pass

        # Method 3: Try using GPUtil if available
        try:
            import GPUtil

            gpus = GPUtil.getGPUs()
            for gpu in gpus:
                gpu_info.append(
                    {
                        "name": gpu.name,
                        "memory_total": gpu.memoryTotal,
                        "memory_allocated": gpu.memoryUsed,
                        "memory_cached": gpu.memoryUtil * gpu.memoryTotal,
                        "detection_method": "GPUtil",
                    }
                )
        except (ImportError, Exception):
            pass

        # Method 4: Try using py3nvml if available
        try:
            import py3nvml

            py3nvml.nvmlInit()
            device_count = py3nvml.nvmlDeviceGetCount()

            for i in range(device_count):
                handle = py3nvml.nvmlDeviceGetHandleByIndex(i)
                info = py3nvml.nvmlDeviceGetMemoryInfo(handle)
                name = py3nvml.nvmlDeviceGetName(handle)

                gpu_info.append(
                    {
                        "name": name.decode("utf-8"),
                        "memory_total": info.total,
                        "memory_allocated": info.used,
                        "memory_cached": info.cached,
                        "detection_method": "py3nvml",
                    }
                )

            py3nvml.nvmlShutdown()
        except (ImportError, Exception):
            pass

        # Method 5: Try detecting Apple Silicon GPU
        try:
            if platform.system() == "Darwin" and platform.processor() == "arm":
                # Check if running on Apple Silicon
                result = subprocess.run(
                    ["sysctl", "-n", "hw.perflevel0.physicalcpu"],
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True,
                )
                if result.returncode == 0:
                    # Get GPU info using system_profiler
                    result = subprocess.run(
                        ["system_profiler", "SPDisplaysDataType"],
                        stdout=subprocess.PIPE,
                        stderr=subprocess.PIPE,
                        text=True,
                    )
                    if result.returncode == 0:
                        # Parse the output to find GPU information
                        output = result.stdout
                        if "Metal" in output and "Apple" in output:
                            # Extract GPU name
                            gpu_name = "Apple Silicon GPU"
                            for line in output.split("\n"):
                                if "Chipset Model" in line:
                                    gpu_name = line.split(":")[1].strip()
                                    break

                            # Get memory info using vm_stat
                            result = subprocess.run(
                                ["vm_stat"],
                                stdout=subprocess.PIPE,
                                stderr=subprocess.PIPE,
                                text=True,
                            )
                            if result.returncode == 0:
                                # Parse vm_stat output to estimate available memory
                                output = result.stdout
                                page_size = 4096  # Default page size
                                for line in output.split("\n"):
                                    if "page size of" in line:
                                        page_size = int(
                                            line.split("of")[1].strip().split()[0]
                                        )

                                # Get total memory
                                total_memory = 0
                                for line in output.split("\n"):
                                    if "Pages free" in line:
                                        free_pages = int(
                                            line.split(":")[1].strip().split(".")[0]
                                        )
                                        total_memory += free_pages * page_size

                                # Estimate GPU memory (typically 1/3 of total memory on Apple Silicon)
                                gpu_memory = total_memory // 3

                                gpu_info.append(
                                    {
                                        "name": gpu_name,
                                        "memory_total": gpu_memory,
                                        "memory_allocated": 0,  # We can't easily get this
                                        "memory_cached": 0,  # We can't easily get this
                                        "detection_method": "apple_silicon",
                                    }
                                )
        except (subprocess.SubprocessError, FileNotFoundError, ValueError, ImportError):
            pass

        return gpu_info
