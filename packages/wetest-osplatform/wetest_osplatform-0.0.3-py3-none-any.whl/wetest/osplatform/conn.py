import socket
from typing import Union

import tidevice
from adbutils import Network, adb


def make_android_connection(
    serial: str = "", network: Network = Network.TCP, addr: Union[int, str] = 8000
) -> socket.socket:
    """
    Get Android inner connection's socket.

    Args:
        serial (str): Android device serial. If not specified, default to current connected.
        network (Network): network type.
        addr (Union[int, str]): device port or localabstract name.

    Returns:
        socket.socket: raw inner socket.
    """
    device = adb.device(serial) if serial else adb.device()
    return device.create_connection(network, addr)


def make_ios_connection(udid: str = "", port: int = 21343) -> socket.socket:
    """
    Get Android inner connection's socket.

    Args:
        udid (str): iOS device udid. If not specified, default to current connected.
        port (int): the port to connect.

    Returns:
        socket.socket: raw inner socket.
    """
    device = tidevice.Device(udid) if udid else tidevice.Device()
    conn = device.create_inner_connection(port)
    """
    tidevice的create_inner_connection在创建连接时，实现了一个清理操作
    tidevice/_safe_socket.py:247
    self._finalizer = weakref.finalize(self, self._psock.close)

    weakref.finalize用于在自动垃圾回收销毁对象时进行清理操作，
    释放资源关闭文件，避免内存泄露

    ios_connection函数的返回值为连接的socket对象，但在返回后conn的引用归零，
    触发python的垃圾回收机制，对conn进行回收销毁，调用self._psock.close方法，
    该方法会关闭socket。
    后续的screenshot函数试图从一个已经被关闭的socket中读取数据，导致截图失败。

    detach方法取消在finalize中注册的回调清理函数，在对象生命周期结束时不执行特定的清理操作

    具体分析过程见issue #4
    https://git.woa.com/CloudTesting/automation/scrcpy-python-client/issues/4

    将取消conn的finalizer，修改为取消conn.psock的finalizer，避免在thread中使用sock时触发finalizer的清理操作，与线程清理相冲突
    ref: https://git.woa.com/CloudTesting/CTArchive/GA-Python/issues/18
    """
    conn.psock._finalizer.detach()
    return conn.psock.get_socket()


def make_local_connection(host: str, port: int) -> socket.socket:
    """
    通过adb forward或tidevice将设备端口映射到本地端口，连接本地端口实现与设备的联通。

    Args:
        host (str): ip address or "localhost".
        port (str): local port.

    Returns:
        socket.socket: raw socket.
    """
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect((host, port))
    return sock
