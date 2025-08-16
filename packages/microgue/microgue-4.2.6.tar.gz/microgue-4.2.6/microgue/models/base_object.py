import json

from ..models.attributes import Attribute


class BaseObject:
    class Null:  # noqa
        """
        used internally by BaseObject to distinguish between an attribute being not set vs set to None

        Null: attribute value is explicitly set to None
        None: attribute value is not set
        """

        pass

    """
    _schema: defines the schema for all objects that extend BaseObject

    schema: defines the schema of the current instantiated object
        attributes: set of attributes for the object

        hidden_attributes: set of attributes to hide when calling object.serialize() / object.serialize(hide_attributes=True)

        default_attributes: dict of attributes with default values (static or callable)
    """
    _schema = dict()

    def __new__(cls, *args, **kwargs):
        # build the schema for each object that extends BaseObject only once
        if cls._schema.get(cls.__name__) is None:
            cls._define_schema()
            cls._build_schema()

        return super().__new__(cls)

    @classmethod
    def schema(cls):
        # get the schema for the current object
        return cls._schema.get(cls.__name__)

    @classmethod
    def _define_schema(cls):
        cls._schema[cls.__name__] = {
            "attributes": set(),
            "hidden_attributes": set(),
            "default_attributes": dict(),
        }

    @classmethod
    def _build_schema(cls):
        # for every attribute in the BaseObject definition
        for attribute_name, attribute_value in cls.__dict__.items():
            # check if the attribute is of type Attribute
            if isinstance(attribute_value, Attribute):
                # process the attribute
                cls._process_attribute(attribute_name, attribute_value)

                # remove the attribute from the BaseObject definition
                setattr(cls, attribute_name, None)

    @classmethod
    def _process_attribute(cls, attribute_name, attribute_value):
        cls.schema()["attributes"].add(attribute_name)
        if attribute_value.hidden:
            cls.schema()["hidden_attributes"].add(attribute_name)
        if attribute_value.default:
            cls.schema()["default_attributes"][attribute_name] = attribute_value.default_value

    def __init__(self, attributes=None, raise_errors=True, *args, **kwargs):
        # default attributes to empty dict
        attributes = {} if attributes is None else attributes

        # add all attributes to the object
        for key in self.schema()["attributes"]:
            self.__dict__[key] = None

        # load object with attributes received
        self.deserialize(
            attributes=attributes,
            raise_errors=raise_errors,
        )

        # set default values
        for key, value in self.schema()["default_attributes"].items():
            if getattr(self, key) is None:
                if callable(value):
                    self.__setattr__(key, value())
                else:
                    self.__setattr__(key, value)

        super().__init__(*args, **kwargs)

    def __str__(self):
        return json.dumps(
            self.serialize(),
            indent=4,
        )

    def __repr__(self):
        return self.__str__()

    def __getattribute__(self, key):
        value = super().__getattribute__(key)
        if value is BaseObject.Null:
            return None
        else:
            return value

    def __setattr__(self, key, value):
        if key not in self.schema()["attributes"]:
            raise AttributeError(f"{self.__class__.__name__} object does not have {key} attribute to set")
        if value is None:
            self.__dict__[key] = BaseObject.Null
        else:
            self.__dict__[key] = value

    def copy(self):
        return self.__class__(self.serialize(hide_attributes=False))

    def serialize(self, hide_attributes=True):
        attributes = dict()
        for key, value in self.__dict__.items():
            if value is not None:
                if value is BaseObject.Null:
                    attributes[key] = None
                else:
                    attributes[key] = value
        if hide_attributes:
            for key in self.schema()["hidden_attributes"]:
                attributes.pop(key, None)

        return attributes

    def deserialize(self, attributes=None, raise_errors=True):
        # default attributes to empty dict
        attributes = {} if attributes is None else attributes

        for key, value in attributes.items():
            try:
                self.__setattr__(key, value)
            except:  # noqa
                if raise_errors:
                    raise

    @classmethod
    def bulk_serialize(cls, objects):
        dicts = []
        for obj in objects:
            dicts.append(obj.serialize())
        return dicts

    @classmethod
    def bulk_deserialize(cls, dicts):
        objects = []
        for dic in dicts:
            objects.append(cls(dic))
        return objects
