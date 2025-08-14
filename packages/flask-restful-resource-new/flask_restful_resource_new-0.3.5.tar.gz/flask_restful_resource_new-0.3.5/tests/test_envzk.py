import time

import pytest

from flask_restful_resource.comm.env import EnvZk


@pytest.mark.skip(reason="skip")
def test_one(client):
    ez = EnvZk("111.230.231.89:2181,111.230.231.89:2182,111.230.231.89:2183", "chaos", "localhost:12345")

    ez.init_conf("CUR_ENV", force=True)
    ez.init_conf("CHAOS_DB", force=True)
    ez.init_conf("SENTRY_URL")
    ez.init_conf("REDIS_URL", force=True)
    ez.init_conf("LOG_DB", force=True)
    ez.init_conf("SQLALCHEMY_TRACK_MODIFICATIONS", default=False, conftype=bool)
    ez.init_conf("SQLALCHEMY_POOL_SIZE", default=5, conftype=int)
    ez.init_conf("ALERT_SENTRY_DNS")
    ez.init_conf("SMS_SENDING_LIMIT", default=100, conftype=int)
    ez.init_conf("VERIFY_CODE_EXPIRE", default=2, conftype=int)
    ez.init_conf("VERIFY_CODE_EXPIRE_MAIL", default=5, conftype=int)
    ez.init_conf("AMAP_SERVICE_KEY", force=True)
    ez.init_conf("IPV4_DATX_URL", force=True)
    ez.init_conf("MONGO_URI", default="ssssss", force=True)
    ez.init_conf("IS_SEND_SMS", default=True, conftype=bool)
    ez.init_conf("IS_SKIP_CFCA", default=False, conftype=bool)
    ez.init_conf("REPORT_EXC_URL")
    for _ in range(1000):
        time.sleep(1)
        ez["REPORT_EXC_URL"]
    assert 1
