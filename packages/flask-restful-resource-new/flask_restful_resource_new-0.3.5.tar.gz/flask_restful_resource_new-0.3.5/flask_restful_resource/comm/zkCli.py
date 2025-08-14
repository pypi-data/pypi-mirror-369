#!usr/bin/env python
# coding=utf-8
"""
@author: holens
@time: 2018/09/02
@desc:
"""
import json
import logging

from kazoo.client import KazooClient


class ZKClient:
    def __init__(self, zk_servers, service_name, host):
        self.config = None
        self.zk = KazooClient(zk_servers)
        self.zk.start()

        self.service_name = service_name
        self.serve_path = "/entry/service/{}/node".format(service_name)
        self.zk.ensure_path(self.serve_path)
        self.zk.create(self.serve_path + "/server", host.encode(), ephemeral=True, sequence=True)
        self.config_path = "/entry/config/service/{}".format(self.service_name)
        self.zk.DataWatch(self.config_path, self.read_config)

    def read_config(self, *args):
        logging.info("ZKClient: Parameter configuration updated")
        self.zk.ensure_path("/entry/config/service")
        if not self.zk.exists(self.config_path):
            self.zk.create(self.config_path, json.dumps({}).encode())
        self.config = json.loads(self.zk.get(self.config_path)[0].decode())

    def update_config(self, config):
        self.zk.set(self.config_path, json.dumps(config).encode())
