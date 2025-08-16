from datetime import datetime


class Attribute:
    def __init__(
        self,
        hidden=False,
        required=False,
        default=False,
        default_value=None,
        type=None,
        serialize=None,
        deserialize=None,
    ):
        self.hidden = hidden
        self.required = required
        self.default = default
        self.default_value = default_value
        self.type = type
        self.serialize = serialize
        self.deserialize = deserialize


class KeyAttribute(Attribute):
    def __init__(self, *args, key="pk", label="", auto_generate=True, **kwargs):
        # required configuration
        kwargs["type"] = str
        kwargs["required"] = True

        # added functionality
        self.key = key
        self.label = label
        self.auto_generate = auto_generate

        super().__init__(*args, **kwargs)


class PartitionKeyAttribute(KeyAttribute):
    def __init__(self, *args, **kwargs):
        # required configuration
        kwargs["key"] = "pk"
        super().__init__(*args, **kwargs)


class SortKeyAttribute(KeyAttribute):
    def __init__(self, *args, **kwargs):
        # required configuration
        kwargs["key"] = "sk"
        super().__init__(*args, **kwargs)


class EmptySortKeyAttribute(SortKeyAttribute):
    def __init__(self, *args, **kwargs):
        # required configuration
        kwargs["default"] = True
        kwargs["default_value"] = ""
        kwargs["serialize"] = lambda x: ""
        kwargs["deserialize"] = lambda x: ""
        super().__init__(*args, **kwargs)


class UniqueAttribute(Attribute):
    def __init__(self, *args, **kwargs):
        # required configuration
        kwargs["type"] = str

        # added functionality
        self.unique = True

        super().__init__(*args, **kwargs)


class DatetimeAttribute(Attribute):
    def __init__(self, *args, **kwargs):
        # required configuration
        kwargs["type"] = datetime

        # default values
        if kwargs.get("serialize") is None:
            kwargs["serialize"] = lambda x: None if x is None else x.isoformat()
        if kwargs.get("deserialize") is None:
            kwargs["deserialize"] = lambda x: None if x is None else datetime.fromisoformat(x)

        super().__init__(*args, **kwargs)


class ListAttribute(Attribute):
    def __init__(self, *args, **kwargs):
        # required configuration
        kwargs["type"] = list

        # default values
        if kwargs.get("default") is None:
            kwargs["default"] = True
        if kwargs.get("default_value") is None:
            kwargs["default_value"] = list

        super().__init__(*args, **kwargs)


class ObjectListAttribute(ListAttribute):
    def __init__(self, *args, item_type=None, **kwargs):
        # required configuration
        if item_type is None or "microgue.models.object.Object" not in str(item_type.__mro__):
            raise AttributeError("ObjectListAttribute requires an item_type of Object")

        # default values
        if kwargs.get("serialize") is None:
            kwargs["serialize"] = lambda x: None if x is None else [i.serialize() for i in x]
        if kwargs.get("deserialize") is None:
            kwargs["deserialize"] = lambda x: None if x is None else [item_type(i) for i in x]

        super().__init__(*args, **kwargs)


class ObjectAttribute(Attribute):
    def __init__(self, *args, **kwargs):
        # required configuration
        if kwargs.get("type") is None or "microgue.models.object.Object" not in str(kwargs["type"].__mro__):
            raise AttributeError("ObjectAttribute requires a type of Object")

        # default values
        if kwargs.get("default") is None:
            kwargs["default"] = True
        if kwargs.get("default_value") is None:
            kwargs["default_value"] = lambda: kwargs["type"]()

        super().__init__(*args, **kwargs)
