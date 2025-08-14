# 介绍

xwjk 常用基础类库整理

# 安装

到 [tags](http://gitlab.xwfintech.com/backend/base-pypi/tags) 页面下载对应版本的 tar.gz 包。

```
pip install flask_restful_resource-version.tar.gz
```

# 依赖安装

## 使用 mongo 请安装:

```
marshmallow-mongoengine==0.9.1
flask-mongoengine==0.9.5
```

## 使用 sql 请安装:

```
Flask-SQLAlchemy==2.3.2
flask-marshmallow==0.9.0
marshmallow-sqlalchemy==0.15.0
```

# 使用方法

## 初始化

``` python
import json
import logging

import pytest
from flask import Flask, make_response
from flask_marshmallow import Marshmallow
from flask_mongoengine import MongoEngine
from flask_restful import Api
from flask_sqlalchemy import SQLAlchemy

from flask_restful_resource.base_resource.exceptions import ResourceException

logging.basicConfig(level=logging.INFO)

app = Flask(__name__)
api = Api(app)

# 初始化 mongoengine 配置
app.config.update({"MONGODB_SETTINGS": {"host": "mongodb://127.0.0.1:27017/xwjk_base"}})
mongodb = MongoEngine(app)

# 初始化 mysql 配置
app.config.update({"SQLALCHEMY_DATABASE_URI": "sqlite:///test.db"})
sqldb = SQLAlchemy(app)
sqlma = Marshmallow(app)


@api.representation("application/json")
def output_json(data, code, headers):
    if isinstance(data, ResourceException):
        return data.get_response()

    resp = make_response(json.dumps({"code": 0, "msg": "OK", "data": data}), code)
    return resp
```

## BaseResource 用法

``` python
from schema import Schema, Use

from flask_restful_resource import BaseResource

from .conftest import api


class MyBase(BaseResource):

    validate_schemas = {"get": Schema({"name": str, "age": Use(int)})}

    allow_methods = ["get"]

    def get(self):
        return self.validate_data


api.add_resource(MyBase, "/base")
```

## SQLModelSchemaResource 用法

``` python
from schema import Optional, Schema, Use

from flask_restful_resource import SQLModelSchemaResource

from .conftest import api
from .conftest import sqldb as db


class Person(db.Model):

    __tablename__ = "person"

    id = db.Column(db.Integer, primary_key=True, doc="主键")
    name = db.Column(db.String(128), nullable=False, doc="名称")
    age = db.Column(db.Integer, nullable=False, doc="年龄")


class MySql(SQLModelSchemaResource):

    model = Person
    allow_query_all = True
    # allow_methods = ["get", "post", "put", "delete"]

    filter_fields = [["name", "==", "name", str], ["age", "==", "age", int]]

    list_fields = ["name", "age"]

    update_include_fields = ["name", "age"]

    validate_schemas = {
        "get": Schema(
            {
                Optional("id"): Use(int),
                Optional("name"): str,
                Optional("age"): Use(int),
                Optional("page_size"): Use(int),
            }
        ),
        "post": Schema({"name": str, "age": Use(int), Optional("page_size"): Use(int)}),
        "put": Schema({"id": int, Optional("name"): str, "age": Use(int), Optional("page_size"): Use(int)}),
        "delete": Schema({"id": int}),
    }


api.add_resource(MySql, "/mysql")
```

## MongoModelSchemaResource 用法

``` python
from schema import Optional, Schema, Use

from flask_restful_resource import MongoModelSchemaResource
from flask_restful_resource.base_resource.exceptions import ErrorCode

from .conftest import api
from .conftest import mongodb as db


class Person(db.Document):
    meta = {"collection": "person", "indexes": ["name", "age"]}

    name = db.StringField(required=True)
    age = db.IntField(required=True)


class MyMongo(MongoModelSchemaResource):

    model = Person
    allow_query_all = True
    # allow_methods = ["get", "post", "put", "delete"]

    filter_fields = [["name", "==", "name", str], ["age", "==", "age", int]]

    list_fields = ["name", "age"]

    update_include_fields = ["name", "age"]

    validate_schemas = {
        "get": Schema(
            {Optional("id"): str, Optional("name"): str, Optional("age"): Use(int), Optional("page_size"): Use(int)}
        ),
        "post": Schema({"name": str, "age": Use(int), Optional("page_size"): Use(int)}),
        "put": Schema({"id": str, Optional("name"): str, "age": Use(int), Optional("page_size"): Use(int)}),
        "delete": Schema({"id": str}),
    }


api.add_resource(MyMongo, "/mongo")
```

## 自定义内部异常处理

``` python
from flask_restful_resource.base_resource.exceptions import ResourceException, ErrorCode

@api.representation("application/json")
def output_json(data, code, headers):
    if isinstance(data, ResourceException):
        return data.get_response({
            ErrorCode.METHOD_NOT_ALLOW: 1,
            ErrorCode.VALIDATE_ERROR: 2,
            ErrorCode.FIELD_TYPE_ERROR: 3,
            ErrorCode.INSTANCE_IS_NOT_EXIST: 4,
            ErrorCode.NOT_ALLOW_UPDATE_FIELD_IS_EXIST: 5,
            ErrorCode.DB_COMMIT_ERROR: 6,
        })

    resp = make_response(json.dumps({"code": 0, "msg": "OK", "data": data}), code)
    return resp

# {
#     内部错误码1: 自定义错误码1,
#     内部错误码2: 自定义错误码2,
#     内部错误码3: 自定义错误码3,
# }
```

完全自定义返回格式

``` python
@api.representation("application/json")
def output_json(data, code, headers):
    if isinstance(data, ResourceException):
        errcode = data.code
        status_code = data.status_code
        errmsg = data.msg
        ......
        return ...

    resp = make_response(json.dumps({"code": 0, "msg": "OK", "data": data}), code)
    return resp
```



## 其他用法，请看源码～

## [requirements](requirements.txt)

## [Change log](changelog.md)