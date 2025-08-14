import json
import logging.handlers

import pytest

from flask import Flask, make_response
from flask_marshmallow import Marshmallow
from flask_mongoengine import MongoEngine
from flask_restful import Api
from flask_restful_resource.base_resource.exceptions import ResourceException
from flask_sqlalchemy import SQLAlchemy

CONSOLE_FORMAT = "%(asctime)s | %(levelname)s | %(lineno)s | %(funcName)s | %(message)s"
DATEFMT = "%Y-%m-%d %H:%M:%S"
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.INFO)
console_handler.setFormatter(logging.Formatter(fmt=CONSOLE_FORMAT, datefmt=DATEFMT))
logging.basicConfig(level=logging.INFO, handlers=[console_handler])

app = Flask(__name__)
app.config["TESTING"] = True
app.config["SERVER_NAME"] = "127.0.0.1:5000"
api = Api(app)

# 初始化 mongoengine 配置
app.config.update({"MONGODB_SETTINGS": {"host": "mongodb://127.0.0.1:27017/xwjk_base"}})
mongodb = MongoEngine(app)

# 初始化 mysql 配置
app.config.update({"SQLALCHEMY_DATABASE_URI": "sqlite:///test.db", "SQLALCHEMY_TRACK_MODIFICATIONS": False})
sqldb = SQLAlchemy(app)
sqlma = Marshmallow(app)


@api.representation("application/json")
def output_json(data, code, headers):
    if isinstance(data, ResourceException):
        return data.get_response()

    resp = make_response(json.dumps({"code": 0, "msg": "OK", "data": data}), code)
    return resp


@pytest.fixture
def client():
    """
    返回 flask client
    """

    ctx = app.app_context()
    ctx.push()
    sqldb.create_all()
    yield app.test_client()
    mongodb.connection.drop_database("xwjk_base")
    sqldb.drop_all()
    ctx.pop()
