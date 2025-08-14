import pytest

from flask import url_for
from flask_restful_resource import MongoModelSchemaResource
from flask_restful_resource.base_resource.exceptions import ErrorCode
from schema import Optional, Schema, Use

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

    filter_fields = [["name", "==", "name", str], ["age", "==", "age", None]]

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

    def pre_put_data(self, instance):
        self.validate_data["name"] = instance.name + ":" + self.validate_data["name"]
        return self.validate_data


api.add_resource(MyMongo, "/mongo")


@pytest.mark.parametrize("_id", ["123", "123123123123123123123123"])
def test_get_detail_none(client, _id):
    result = client.get(url_for("mymongo"), query_string={"id": _id}).json
    assert result["code"] == ErrorCode.INSTANCE_IS_NOT_EXIST


def test_get_success(client):
    result = client.get(url_for("mymongo"), query_string={"name": "jack", "age": 18, "page_size": -1}).json
    assert result["data"] == {"total": 0, "pages": 0, "page": 1, "page_size": 0, "results": []}


def test_post_success(client):
    result = client.post(url_for("mymongo"), json={"name": "jack", "age": 18}).json
    assert result["code"] == 0


def test_post_fail(client):
    result = client.post(url_for("mymongo"), query_string={"name": "jack"}).json
    assert result["code"] == ErrorCode.VALIDATE_ERROR


def test_put_success(client):
    result = client.post(url_for("mymongo"), json={"name": "jack", "age": 18}).json
    _id = result["data"]["id"]
    result = client.put(url_for("mymongo"), json={"id": _id, "name": "jack1", "age": 19}).json
    assert result["data"]["age"] == 19
    assert Person.objects.first().age == 19


def test_put_fail(client):
    result = client.post(url_for("mymongo"), json={"name": "jack", "age": 18}).json
    _id = "123123123123123123123123"
    result = client.put(url_for("mymongo"), json={"id": _id, "name": "jack1", "age": 19}).json
    assert result["code"] == ErrorCode.INSTANCE_IS_NOT_EXIST


def test_delete_success(client):
    result = client.post(url_for("mymongo"), json={"name": "jack", "age": 18}).json
    _id = result["data"]["id"]
    result = client.delete(url_for("mymongo"), json={"id": _id}).json
    assert result["code"] == 0

    result = client.get(url_for("mymongo")).json
    assert result["data"]["total"] == 0


def test_pre_put_data(client):
    result = client.post(url_for("mymongo"), json={"name": "jack", "age": 18}).json
    _id = result["data"]["id"]
    result = client.put(url_for("mymongo"), json={"id": _id, "name": "jack1", "age": 19}).json
    assert result["data"]["age"] == 19
    assert result["data"]["name"] == "jack:jack1"
