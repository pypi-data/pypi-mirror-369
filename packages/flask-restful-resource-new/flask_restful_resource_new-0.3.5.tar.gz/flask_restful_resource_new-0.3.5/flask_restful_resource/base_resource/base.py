import logging as logger
from typing import Any, Optional  # 新增类型导入

from flask import request
from flask_restful import Resource, reqparse
from flask_restful_resource.comm.utils import move_space, validate_schema
from schema import Schema

from .exceptions import ErrorCode, ResourceException


class BaseResource(Resource):
    validate_data: Optional[dict[str, Any]] = None
    validate_schemas: dict[str, Schema | reqparse.RequestParser] = {}
    allow_methods: list[str] = ["get", "post", "put", "delete"]

    def dispatch_request(self, *args: Any, **kwargs: Any) -> Any:  # 明确参数类型
        if request.method.lower() not in self.allow_methods:
            return ResourceException(ErrorCode.METHOD_NOT_ALLOW, 405)
        req: Optional[dict[str, Any]] = None
        schema: Optional[Schema | reqparse.RequestParser] = None
        
        if request.method == "GET":
            schema = self.validate_schemas.get("get")
            req = dict(request.args)  # 替代to_dict()，兼容3.12
        else:
            method = request.method.lower()
            schema = self.validate_schemas.get(method)
            req = request.get_json(silent=True) or {}  # 更安全的JSON获取方式

        req = move_space(req)
        if isinstance(schema, Schema):
            data, errors = validate_schema(schema, req)
            if errors:
                logger.info(str(errors))
                return ResourceException(ErrorCode.VALIDATE_ERROR)
            self.validate_data = data
        elif isinstance(schema, reqparse.RequestParser):
            strict = self.validate_schemas.get("strict", False)
            parse_req = schema.parse_args(strict=strict)
            self.validate_data = {k: v for k, v in parse_req.items() if v is not None}

        if not self.validate_data:
            self.validate_data = req
        return super().dispatch_request(*args, **kwargs)

    def get(self) -> Any:
        pass

    def put(self) -> Any:
        pass

    def delete(self) -> Any:
        pass