import kazoo
from kazoo.client import KazooClient


def test_kazoo():
    x = KazooClient(hosts='10.8.0.1:2181')
    x.start()
    x.ensure_path("/heptet/myapp")
    x.create("/heptet/myapp/1", b"test")
