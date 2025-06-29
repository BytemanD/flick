import dataclasses
import platform
from typing import Dict, List, Optional

import distro
import psutil


@dataclasses.dataclass
class DiskUsage:
    total: int
    used: int
    free: int
    percent: float


@dataclasses.dataclass
class Disk:
    device: str
    mountpoint: str
    fstype: str
    opts: str = ""
    usage: Optional[DiskUsage] = None


@dataclasses.dataclass
class NetInterface:
    name: str
    mac_address: str = ""
    addresses: List[str] = dataclasses.field(default_factory=list)
    bytes_sent: int = 0
    bytes_recv: int = 0
    packets_sent: int = 0
    packets_recv: int = 0


class NodeManager:

    def platform(self) -> dict:
        info = {
            "system": platform.system(),
            "release": platform.release(),
            "version": platform.version(),
            "machine": platform.machine(),
            "processor": platform.processor(),
        }
        if platform.system().lower() == 'linux':
            info['name'] = distro.name()
            info['dist_version'] = distro.version()

        return info
        # boot_time = psutil.boot_time()
        # info['boot_time'] = datetime.datetime.fromtimestamp(
        #        boot_time).strftime("%Y-%m-%d %H:%M:%S")

    def cpu(self) -> dict:
        return {
            "count": psutil.cpu_count(logical=False),
            "count_logical": psutil.cpu_count(),
            "percent": psutil.cpu_percent(interval=1),
        }

    def memory(self) -> dict:
        mem = psutil.virtual_memory()
        return {
            "total": mem.total,
            "available": mem.available,
            "used": mem.used,
            "percent": mem.percent,
        }

    def disk(self) -> dict:
        disk = psutil.disk_usage("/")
        return {
            "total": disk.total,
            "used": disk.used,
            "free": disk.free,
            "percent": disk.percent,
        }

    def partitions(self, all_device=False) -> List[Disk]:
        """获取所有磁盘分区信息

        如果 all_device=False, 仅物理设备
        """
        partitions = psutil.disk_partitions(all=all_device)
        return [
            Disk(
                device=part.device,
                mountpoint=part.mountpoint,
                fstype=part.fstype,
                opts=part.opts,
                usage=self.get_disk_usage(part.mountpoint),
            )
            for part in partitions
            if part.device and part.fstype not in ["cgroup", "cgroup2", "tmpfs"]
        ]

    def get_disk_usage(self, path):
        usage = psutil.disk_usage(path)
        return DiskUsage(total=usage.total, used=usage.used, free=usage.free, percent=usage.percent)

    def net_interfaces(self) -> List[NetInterface]:
        """获取网络接口地址信息"""
        net_ifs: Dict[str, NetInterface] = {}
        addrs = psutil.net_if_addrs()
        for interface, addresses in addrs.items():
            if interface == "lo":
                continue
            net_ifs[interface] = NetInterface(name=interface)
            for addr in addresses:
                if addr.family.name in ["AF_LINK", "AF_PACKET"]:
                    net_ifs[interface].mac_address = addr.address
                else:
                    net_ifs[interface].addresses.append(addr.address)

        net_io = psutil.net_io_counters(pernic=True)
        for interface, stats in net_io.items():
            if interface not in net_ifs:
                continue
            net_ifs[interface].bytes_sent = stats.bytes_sent
            net_ifs[interface].bytes_recv = stats.bytes_recv
            net_ifs[interface].packets_sent = stats.packets_sent
            net_ifs[interface].packets_recv = stats.packets_recv

        return list(net_ifs.values())


SERVICE = NodeManager()
