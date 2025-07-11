from flick.router import basehandler

from flick.common import utils
from flick.core import node


class Info(basehandler.BaseRequestHandler):

    def get(self):
        self.finish({"info": node.SERVICE.platform()})


class Cpu(basehandler.BaseRequestHandler):

    def get(self):
        self.finish({"cpu": node.SERVICE.cpu()})


class Memory(basehandler.BaseRequestHandler):

    def get(self):
        self.finish({"memory": node.SERVICE.memory()})


class Partitions(basehandler.BaseRequestHandler):

    def get(self):
        all_device = utils.strtobool(self.get_query_argument("all_device", ''))
        self.finish({"partitions": node.SERVICE.partitions(all_device=all_device)})


class NetInterfaces(basehandler.BaseRequestHandler):

    def get(self):
        return self.finish({"net_interfaces": node.SERVICE.net_interfaces()})
