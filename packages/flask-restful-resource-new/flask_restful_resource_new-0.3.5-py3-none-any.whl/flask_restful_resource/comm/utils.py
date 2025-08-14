import logging
import time
from datetime import datetime
from typing import dict, list, Any  # 新增类型导入

from schema import Schema, SchemaError


def move_space(data: dict[str, Any]) -> dict[str, Any]:  # 明确类型注解
    if data:
        for k, v in data.items():
            if isinstance(v, str):
                data[k] = str.strip(v)
        return data
    return {}


def validate_schema(schema: Schema, data: dict[str, Any], remove_blank: bool = False) -> tuple[dict[str, Any], list[str]]:
    """schema验证,验证成功返回数据，验证失败返回错误信息"""
    if not isinstance(data, dict):
        return {}, ["Not found params"]
    d: dict[str, Any] = {}
    if remove_blank:
        for k, v in data.items():
            if v != "":
                d[k] = v
    else:
        d = data.copy()  # 避免修改原数据
    try:
        validate_data = schema.validate(d)
        return validate_data, []
    except SchemaError as e:
        return {}, [str(e.autos)]
    return validate_data, []  # 移除冗余else


def utc_timestamp() -> int:
    """返回utc时间戳（秒）"""
    return int(datetime.now().timestamp())


def utc_strftime(fmt: str) -> str:
    return datetime.now().strftime(fmt)


def print_run_time(func):
    """计算时间函数"""
    def wrapper(*args, **kw):
        local_time = int(time.time() * 1000)
        result = func(*args, **kw)
        logging.info("current Function [%s] run time is %s ms", 
                    func.__name__, int(time.time() * 1000) - local_time)  # 改用位置参数
        return result
    return wrapper