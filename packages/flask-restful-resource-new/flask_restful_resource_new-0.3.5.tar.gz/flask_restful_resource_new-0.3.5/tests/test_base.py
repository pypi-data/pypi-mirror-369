from flask import url_for
from flask_restful_resource import BaseResource
from flask_restful_resource.base_resource.exceptions import ErrorCode
from schema import Schema, Use

from .conftest import api


class MyBase(BaseResource):

    validate_schemas = {"get": Schema({"name": str, "age": Use(int)})}

    allow_methods = ["get"]

    def get(self):
        return self.validate_data


api.add_resource(MyBase, "/base")


def test_get_success(client):
    result = client.get(url_for("mybase"), query_string={"name": "jack", "age": 18}).json
    assert result["data"] == {"name": "jack", "age": 18}


def test_get_fail(client):
    result = client.get(url_for("mybase"), query_string={"name": "jack"}).json
    assert result["code"] == ErrorCode.VALIDATE_ERROR
