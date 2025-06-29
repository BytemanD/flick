import docker


def get_docker_system_info():
    # 创建Docker客户端
    client = docker.from_env()

    try:
        # 获取Docker系统信息
        info = client.info()

        print("=== Docker系统信息 ===")
        print(f"Docker版本: {info['ServerVersion']}")
        print(
            f"容器数量: {info['Containers']} (运行中: {info['ContainersRunning']}, 停止: {info['ContainersStopped']}, 暂停: {info['ContainersPaused']})"
        )
        print(f"镜像数量: {info['Images']}")
        print(f"操作系统: {info['OperatingSystem']}")
        print(f"内核版本: {info['KernelVersion']}")
        print(f"Docker根目录: {info['DockerRootDir']}")
        print(f"CPU数量: {info['NCPU']}")
        print(f"总内存: {round(info['MemTotal'] / (1024*1024*1024), 2)} GB")
        print(f"存储驱动: {info['Driver']}")
        print(f"是否支持GPU: {'是' if info.get('Runtimes', {}).get('nvidia') else '否'}")

        # 返回完整信息字典
        return info

    except Exception as e:
        print(f"获取Docker信息时出错: {e}")
        return None


def list_containers():
    # 列出所有容器（包括停止的）
    client = docker.from_env()
    items = client.containers.list(all=True)
    print("========== 所有容器 ===========")
    for container in items:
        print(f"ID: {container.short_id}, 名称: {container.name}, 状态: {container.status}")


def list_volumes():
    client = docker.from_env()
    items = client.volumes.list()
    print("========== 所有卷 ===========")
    for volume in items:
        print(f"ID: {volume.short_id}, 名称: {volume.name}, 状态: {volume.attrs}")


if __name__ == "__main__":
    get_docker_system_info()
    list_containers()
    list_volumes()
