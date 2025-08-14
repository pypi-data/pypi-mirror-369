import logging as logger

from flask_restful_resource.comm.utils import utc_timestamp
from marshmallow_mongoengine import ModelSchema

from .base import BaseResource
from .exceptions import ErrorCode, ResourceException

mongo_filter_op_map = {
    ">": "__gt",
    "<": "__lt",
    ">=": "__gte",
    "<=": "__lte",
    "!=": "__ne",
    "==": "",
    "contains": "__contains",
}


class MongoModelResource(BaseResource):
    pk_name = "id"
    model = None
    list_schema = None
    detail_schema = None
    update_exclude_fields = []
    update_include_fields = []
    list_fields = []
    detail_fields = []
    filter_fields = []
    max_page_size = 100
    default_page_size = 10
    allow_query_all = False

    def get_queryset(self):
        filter_conditions = {}
        for filter_field in self.filter_fields:
            column, op, field, convert_fn = filter_field
            value = self.validate_data.get(field)
            if value is not None:
                value = convert_fn(value) if convert_fn else value
                operator = mongo_filter_op_map[op]
                filter_conditions["{column}{operator}".format(column=column, operator=operator)] = value

        queryset = self.model.objects.only(*self.list_fields).filter(**filter_conditions)
        return queryset

    def get(self):
        pk = self.validate_data.get(self.pk_name)
        if pk:
            try:
                instance = self.model.objects.only(*self.detail_fields).filter(pk=pk).first()
            except Exception as e:
                logger.warning(e)
                instance = None

            if not instance:
                return ResourceException(ErrorCode.INSTANCE_IS_NOT_EXIST)
            data, errors = self.detail_schema.dump(instance)
            if errors:
                logger.error(errors)
                return ErrorCode.SERIALIZATION_ERROR
            return data

        page = int(self.validate_data.get("page") or 1)
        page_size = min(int(self.validate_data.get("page_size") or self.default_page_size), self.max_page_size)

        queryset = self.get_queryset()
        if self.allow_query_all and page_size == -1:
            page_size = queryset.count()
        if page_size == 0:
            return {"total": 0, "pages": 0, "page": 1, "page_size": 0, "results": []}
        pagination = queryset.paginate(page=page, per_page=page_size)

        data, errors = self.list_schema.dump(pagination.items)
        if errors:
            logger.error(errors)
            return ErrorCode.SERIALIZATION_ERROR

        return {
            "total": pagination.total,
            "pages": pagination.pages,
            "page": pagination.page,
            "page_size": pagination.per_page,
            "results": data,
        }

    def post(self):
        instance, errors = self.detail_schema.load(self.validate_data)
        if errors:
            logger.info(str(errors))
            return ResourceException(ErrorCode.FIELD_TYPE_ERROR)
        instance.save()
        data, errors = self.detail_schema.dump(instance)
        if errors:
            logger.error(errors)
            return ErrorCode.SERIALIZATION_ERROR
        return data

    def pre_put_data(self, instance):
        return self.validate_data

    def put(self):
        instance = self.model.objects.filter(pk=self.validate_data.pop(self.pk_name)).first()
        if not instance:
            return ResourceException(ErrorCode.INSTANCE_IS_NOT_EXIST)
        exclude_fields = set(self.validate_data.keys()) & set(self.update_exclude_fields)
        include_fields = set(self.validate_data.keys()) - set(self.update_include_fields)
        if self.update_include_fields and include_fields:
            logger.info("Not Allowed To Update " + str(include_fields))
            return ResourceException(ErrorCode.NOT_ALLOW_UPDATE_FIELD_IS_EXIST)
        if exclude_fields:
            logger.info("Not Allowed To Update " + str(exclude_fields))
            return ResourceException(ErrorCode.NOT_ALLOW_UPDATE_FIELD_IS_EXIST)

        instance, errors = self.detail_schema.update(instance, self.pre_put_data(instance))
        if errors:
            logger.info(str(errors))
            return ResourceException(ErrorCode.FIELD_TYPE_ERROR)

        if hasattr(instance, "update_time"):
            instance.update_time = utc_timestamp()

        instance.save()
        data, errors = self.detail_schema.dump(instance)
        if errors:
            logger.error(errors)
            return ErrorCode.SERIALIZATION_ERROR
        return data

    def delete(self):
        pk = self.validate_data.get(self.pk_name)
        instance = self.model.objects.filter(pk=pk).first()
        if not instance:
            return ResourceException(ErrorCode.INSTANCE_IS_NOT_EXIST)
        instance.delete()


class MongoModelSchemaResource(MongoModelResource):
    def dispatch_request(self, *args, **kwargs):
        meta = type("Meta", (object,), dict(model=self.model))
        schema = type("Schema", (ModelSchema,), dict(Meta=meta))
        self.list_schema = schema(many=True)
        self.detail_schema = schema()
        return super().dispatch_request(*args, **kwargs)
