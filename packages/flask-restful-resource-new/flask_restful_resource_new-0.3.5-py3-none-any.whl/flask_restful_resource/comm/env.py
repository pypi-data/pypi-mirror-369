import logging
import os

from flask_restful_resource.comm.zkCli import ZKClient


class EnvZk:
    """
    管理项目的参数配置，环境变量
    """

    def __init__(self, zk_servers, service_name, host):
        zk = ZKClient(zk_servers, service_name, host)
        zk.read_config()
        self._zk = zk
        self._conf_items = {}

    def init_conf(self, name, default=None, conftype=None, force=False, hash_log=None):
        """
        初始化参数配置
        """
        conf = ConfItem(self._zk, name, default, conftype, force, hash_log)
        self._conf_items[name] = conf
        return conf.value

    def __getitem__(self, key):
        """
        动态获取参数配置
        """
        try:
            return self._conf_items[key].value
        except KeyError:
            logging.error("getting conf failed. key [{}]".format(key))
            return None


class ConfItem:
    """
    保存每一项配置的附属信息
    """

    def __init__(self, zk, name, default=None, conftype=None, force=False, hash_log=None):
        self.zk = zk
        self.name = name
        self.default = default
        self.conftype = conftype
        self.force = force
        self.hash_log = hash_log

    @property
    def value(self):
        """
        读取配置变量

        读取顺序: 环境变量 > zk > default
        """

        env = os.environ.get(self.name)
        if not env:
            env = self.zk.config.get(self.name, None)
            if env is None or env == "":  # 防止 env=False, env=0 等现象
                env = self.default

        if (env is None or env == "") and self.force:
            raise Exception("Not found env: <{}>".format(self.name))

        if self.conftype == bool and not isinstance(env, bool):
            env = False if str(env) in ("0", "false", "False") else True
        elif self.conftype:
            env = self.conftype(env)

        if self.hash_log:
            logging.info("{}: {}".format(self.name, self.hash_log(env)))
        else:
            logging.info("{}: {}".format(self.name, env))

        return env
