import psutil

# 获取所有网络接口信息
net_io = psutil.net_io_counters(pernic=True)
print("所有网络接口:")
for interface, stats in net_io.items():
    print(f"接口名: {interface}")
    print(f"  发送字节数: {stats.bytes_sent}")
    print(f"  接收字节数: {stats.bytes_recv}")
    print(f"  发送包数: {stats.packets_sent}")
    print(f"  接收包数: {stats.packets_recv}")


# 获取网络接口地址信息
addrs = psutil.net_if_addrs()
print("\n网络接口地址信息:")
for interface, addresses in addrs.items():
    print(f"接口名: {interface}")
    for addr in addresses:
        print(f"  地址族: {addr.family.name}")
        print(f"  地址: {addr.address}")
        print(f"  网络掩码: {addr.netmask}")
        print(f"  广播地址: {addr.broadcast}")
        print("  ----------")
