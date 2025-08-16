from .base_object import BaseObject


class RequiredAttributesMissing(Exception):
    pass


class TypeCheckFailed(Exception):
    pass


class Object(BaseObject):
    """
    _schema: defines the schema for all objects that extend BaseObject

    schema: defines the schema of the current instantiated object
        attributes: set of attributes for the object

        hidden_attributes: set of attributes to hide when calling object.serialize() / object.serialize(hide_attributes=True)

        default_attributes: dict of attributes with default values (static or callable)

        required_attributes: set of required attributes

        typed_attributes: dict of attributes with types to check

        serialize_attributes: dict of attributes with custom serialization functions ex. lambda x: x.upper()

        deserialize_attributes: dict of attributes with custom deserialization functions ex. lambda x: x.lower()

        object_attributes: dict of attributes with the Object type
    """

    @classmethod
    def _define_schema(cls):
        super()._define_schema()
        cls.schema().update(
            {
                "required_attributes": set(),
                "typed_attributes": dict(),
                "serialize_attributes": dict(),
                "deserialize_attributes": dict(),
                "object_attributes": dict(),
            }
        )

    @classmethod
    def _process_attribute(cls, attribute_name, attribute_value):
        super()._process_attribute(attribute_name, attribute_value)
        if attribute_value.required:
            cls.schema()["required_attributes"].add(attribute_name)
        if attribute_value.type:
            cls.schema()["typed_attributes"][attribute_name] = attribute_value.type
        if attribute_value.serialize:
            cls.schema()["serialize_attributes"][attribute_name] = attribute_value.serialize
        if attribute_value.deserialize:
            cls.schema()["deserialize_attributes"][attribute_name] = attribute_value.deserialize
        if attribute_value.type and issubclass(attribute_value.type, Object):
            cls.schema()["object_attributes"][attribute_name] = attribute_value.type

    def serialize(self, *args, **kwargs):
        attributes = super().serialize(*args, **kwargs)

        # serialize sub objects
        for attribute, object_type in self.schema()["object_attributes"].items():
            if attribute is not None and attribute in attributes:
                attributes[attribute] = attributes[attribute].serialize(*args, **kwargs)

        # apply serializer functions to attributes
        for attribute, serialize_function in self.schema()["serialize_attributes"].items():
            if attribute in attributes:
                attributes[attribute] = serialize_function(attributes[attribute])

        return attributes

    def deserialize(self, attributes=None, *args, **kwargs):
        super().deserialize(attributes, *args, **kwargs)

        # deserialize sub objects
        for attribute, object_type in self.schema()["object_attributes"].items():
            if attribute in self.__dict__ and self.__dict__[attribute] is not None:
                self.__dict__[attribute] = object_type(self.__dict__[attribute], *args, **kwargs)

        # apply deserializer functions to attributes
        for attribute, deserialize_function in self.schema()["deserialize_attributes"].items():
            if attribute in self.__dict__:
                self.__dict__[attribute] = deserialize_function(self.__dict__[attribute])

    def _validate_required_attributes(self):
        missing_required_attributes = self._get_missing_required_attributes()
        if missing_required_attributes:
            raise RequiredAttributesMissing("missing the following required attributes: " + ", ".join(missing_required_attributes))

    def _get_missing_required_attributes(self, prefix=""):
        missing_required_attributes = []
        for attribute_name in self.schema()["required_attributes"]:
            attribute_value = getattr(self, attribute_name)
            # fail if attribute is None
            if attribute_value is None:
                missing_required_attributes.append(prefix + attribute_name)
            # recursively check sub objects
            elif isinstance(attribute_value, Object):
                missing_required_attributes.extend(
                    attribute_value._get_missing_required_attributes(
                        prefix=prefix + attribute_name + ".",
                    )
                )
        return missing_required_attributes

    def _validate_typed_attributes(self):
        failed_typed_attributes = self._get_failed_typed_attributes()
        if failed_typed_attributes:
            raise TypeCheckFailed("the following attributes failed type checking: " + ", ".join(failed_typed_attributes))

    def _get_failed_typed_attributes(self, prefix=""):
        failed_typed_attributes = []
        for attribute_name, attribute_type in self.schema()["typed_attributes"].items():
            attribute_value = getattr(self, attribute_name)
            # fail if attribute is not None and not the correct type
            if attribute_value is not None and not isinstance(attribute_value, attribute_type):
                failed_typed_attributes.append(prefix + attribute_name)
            # recursively check sub objects
            elif isinstance(attribute_value, Object):
                failed_typed_attributes.extend(
                    attribute_value._get_failed_typed_attributes(
                        prefix=prefix + attribute_name + ".",
                    )
                )
        return failed_typed_attributes
