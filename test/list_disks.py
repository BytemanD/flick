import psutil

# 获取所有磁盘分区信息
partitions = psutil.disk_partitions(all=True)

print("磁盘分区信息:")
for partition in partitions:
    print(partition)
    print(f"设备: {partition.device}")
    print(f"挂载点: {partition.mountpoint}")
    print(f"文件系统类型: {partition.fstype}")
    print(f"选项: {partition.opts}")

    # 获取磁盘使用情况
    try:
        usage = psutil.disk_usage(partition.mountpoint)
        print(f"总空间: {usage.total / (1024**3):.2f} GB")
        print(f"已用空间: {usage.used / (1024**3):.2f} GB")
        print(f"可用空间: {usage.free / (1024**3):.2f} GB")
        print(f"使用百分比: {usage.percent}%")
    except PermissionError:
        print("无权限访问此分区")
    
    print("-" * 40)
