import platform

import psutil


class NodeManager:

    def platform(self) -> dict:
        return {
            "system": platform.system(),
            "release": platform.release(),
            "version": platform.version(),
            "machine": platform.machine(),
            "processor": platform.processor(),
        }
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


SERVICE = NodeManager()
