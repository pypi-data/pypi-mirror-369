import json

from flask import make_response
from flask_restful_resource.comm.config import MsgMetaClass


class ResourceException:
    def __init__(self, code, status_code=200):
        self.code = code
        self.status_code = status_code
        self.msg = ErrorCode.msg[code]

    def get_response(self, code_map=None):

        if code_map and isinstance(code_map, dict):
            self.code = code_map.get(self.code, self.code)

        return make_response(json.dumps({"code": self.code, "msg": self.msg, "data": None}), self.status_code)


class ErrorCode(metaclass=MsgMetaClass):
    METHOD_NOT_ALLOW = (9999000001, "不支持该请求")
    VALIDATE_ERROR = (9999000002, "字段未通过验证")
    FIELD_TYPE_ERROR = (9999000003, "字段类型错误")
    INSTANCE_IS_NOT_EXIST = (9999000004, "不存在该记录")
    INSTANCE_IS_EXIST = (9999000005, "该记录已经存在")
    NOT_ALLOW_UPDATE_FIELD_IS_EXIST = (9999000006, "存在不允许更新的字段")
    SERIALIZATION_ERROR = (9999000007, "序列化出错")
    DB_COMMIT_ERROR = (9999000006, "数据库错误")
