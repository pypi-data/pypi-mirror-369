import logging as logger

from flask import current_app
from flask_restful_resource.comm.utils import utc_timestamp

from .base import BaseResource
from .exceptions import ErrorCode, ResourceException

filter_op_map = {
    ">": "__gt__",
    "<": "__lt__",
    ">=": "__ge__",
    "<=": "__le__",
    "!=": "__not__",
    "==": "__eq__",
    "contains": "contains",
}


class SQLModelResource(BaseResource):
    pk_name = "id"
    model = None
    args_schema = None
    list_schema = None
    detail_schema = None
    exclude = []
    list_fields = []
    update_exclude_fields = []
    update_include_fields = []
    filter_fields = []
    allow_query_all = False
    max_page_size = 100
    default_page_size = 10
    has_is_delete = False
    business_unique_fields = []

    @property
    def db(self):
        if "sqlalchemy" not in current_app.extensions:
            raise Exception("Not found [sqlalchemy] in [app.extensions]. Please init flask-sqlalchemy")
        return current_app.extensions["sqlalchemy"].db

    @property
    def marshmallow(self):
        if "flask-marshmallow" not in current_app.extensions:
            raise Exception("Not found [flask-marshmallow] in [app.extensions]. Please init flask-marshmallow")
        return current_app.extensions["flask-marshmallow"]

    def list_serializable(self, items):
        return self.list_schema.dump(items)

    def get_queryset(self):
        filter_conditions = []
        for filter_field in self.filter_fields:
            column, op, field, convert_fn = filter_field
            value = self.validate_data.get(field)
            if value is not None:
                value = convert_fn(value)
                column = getattr(self.model, column)
                operator = filter_op_map[op]
                filter_conditions.append(getattr(column, operator)(value))

        queryset = self.model.query.filter(*filter_conditions)
        if self.has_is_delete:
            queryset = queryset.filter_by(is_delete=False)
        return queryset

    def get(self):
        pk = self.validate_data.get(self.pk_name)
        if pk:
            instance = self.model.query.get(pk)
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

        pagination = queryset.paginate(page=page, per_page=page_size)
        results, errors = self.list_serializable(pagination.items)
        if errors:
            logger.error(errors)
            return ErrorCode.SERIALIZATION_ERROR

        if self.list_fields:
            results = [{k: v for k, v in data.items() if k in self.list_fields} for data in results]

        return {
            "total": pagination.total,
            "pages": pagination.pages,
            "page": pagination.page,
            "page_size": pagination.per_page,
            "results": results,
        }

    def post(self):
        filter_conditions = []
        if self.business_unique_fields:
            basequery = self.model.query
            if self.has_is_delete:
                basequery = basequery.filter_by(is_delete=False)
            for field in self.business_unique_fields:
                column = getattr(self.model, field)
                filter_conditions.append(getattr(column, "__eq__")(self.validate_data.get(field)))
            instance = basequery.filter(*filter_conditions).first()
            if instance:
                logger.info("instance is exist")
                return ResourceException(ErrorCode.INSTANCE_IS_EXIST)

        instance, errors = self.detail_schema.load(self.validate_data)
        if errors:
            logger.info(errors)
            return ResourceException(ErrorCode.FIELD_TYPE_ERROR)
        try:
            self.db.session.add(instance)
            self.db.session.commit()
            data, errors = self.detail_schema.dump(instance)
            if errors:
                logger.error(errors)
                return ErrorCode.SERIALIZATION_ERROR
            return data

        except Exception as e:
            logger.info(str(e))
            return ResourceException(ErrorCode.DB_COMMIT_ERROR)

    def pre_put_data(self, instance):
        return self.validate_data

    def put(self):
        instance = self.model.query.get(self.validate_data.get(self.pk_name))
        if not instance:
            return ResourceException(ErrorCode.INSTANCE_IS_NOT_EXIST)
        exclude_fields = set(self.validate_data.keys()) & set(self.update_exclude_fields)
        include_fields = set(self.validate_data.keys()) - set(self.update_include_fields) - set([self.pk_name])
        if self.update_include_fields and include_fields:
            logger.info("Not allowed to update " + str(include_fields))
            return ResourceException(ErrorCode.NOT_ALLOW_UPDATE_FIELD_IS_EXIST)
        if exclude_fields:
            logger.info("Not allowed to update " + str(exclude_fields))
            return ResourceException(ErrorCode.NOT_ALLOW_UPDATE_FIELD_IS_EXIST)

        instance, errors = self.detail_schema.load(self.pre_put_data(instance), partial=True)
        if errors:
            logger.info(str(errors))
            return ResourceException(ErrorCode.FIELD_TYPE_ERROR)

        if hasattr(instance, "update_time"):
            instance.update_time = utc_timestamp()

        self.db.session.commit()
        data, errors = self.detail_schema.dump(instance)
        if errors:
            logger.error(errors)
            return ErrorCode.SERIALIZATION_ERROR
        return data

    def delete(self):
        pk = self.validate_data.get(self.pk_name)
        instance = self.model.query.get(pk)
        if not instance:
            return ResourceException(ErrorCode.INSTANCE_IS_NOT_EXIST)
        if self.has_is_delete:
            instance.is_delete = True
        else:
            self.db.session.delete(instance)
        self.db.session.commit()


class SQLModelSchemaResource(SQLModelResource):
    def dispatch_request(self, *args, **kwargs):
        meta = type("Meta", (object,), dict(model=self.model))
        schema = type("Schema", (self.marshmallow.ModelSchema,), dict(Meta=meta))
        self.list_schema = schema(many=True, exclude=self.exclude)
        self.detail_schema = schema(exclude=self.exclude)
        return super().dispatch_request(*args, **kwargs)
