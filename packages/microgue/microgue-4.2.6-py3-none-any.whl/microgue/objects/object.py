import json


class Object:
    class Null:
        """
        used internally by Object to distinguish between an attribute being not set vs set to None

        Null: attribute value is explicitly set to None
        None: attribute value is not set
        """
        pass
    """
    attributes: defines the attributes of the Object

    hidden_attributes: attributes that should not be included when calling Object.serialize()
        Unless passing hide_attributes=False in to Object.serialize()
    """
    attributes = []
    hidden_attributes = []

    def __init__(self, attributes=None, raise_errors=True, *args, **kwargs):
        # defaults
        attributes = {} if attributes is None else attributes

        # add all attributes to the object
        for key in self.attributes:
            self.__dict__[key] = None

        # load object with attributes received
        self.deserialize(
            attributes=attributes,
            raise_errors=raise_errors
        )

        super().__init__(*args, **kwargs)

    def __str__(self):
        return json.dumps(
            self.serialize(),
            indent=4
        )

    def __repr__(self):
        return self.__str__()

    def __getattribute__(self, key):
        value = super().__getattribute__(key)
        if value is Object.Null:
            return None
        else:
            return value

    def __setattr__(self, key, value):
        if key not in self.attributes:
            raise AttributeError(f"{self.__class__.__name__} object does not have {key} attribute to set")
        if value is None:
            self.__dict__[key] = Object.Null
        else:
            self.__dict__[key] = value

    def copy(self):
        return self.__class__(self.serialize(hide_attributes=False))

    def serialize(self, hide_attributes=True):
        attributes = dict()
        for key, value in self.__dict__.items():
            if value is not None:
                if value is Object.Null:
                    attributes[key] = None
                else:
                    attributes[key] = value
        if hide_attributes:
            for key in self.hidden_attributes:
                attributes.pop(key, None)

        return attributes

    def deserialize(self, attributes=None, raise_errors=True):
        # defaults
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
