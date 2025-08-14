class MsgMetaClass(type):
    def __new__(cls, name, bases, attr_dict):
        attr_dict["msg"] = {}
        for key, attr in attr_dict.items():
            if isinstance(attr, tuple):
                code, message = attr
                attr_dict[key] = code
                attr_dict["msg"][code] = message
        return super().__new__(cls, name, bases, attr_dict)
