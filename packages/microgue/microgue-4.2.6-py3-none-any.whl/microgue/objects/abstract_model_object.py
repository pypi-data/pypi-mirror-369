import uuid
from .attribute import Attribute
from ..models.abstract_model import *  # noqa
from .object import *  # noqa


class RequiredAttributes(Exception): pass  # noqa
class UniqueAttributes(Exception): pass  # noqa


class AbstractModelObject(Object):  # noqa
    """
    model: the instantiated model that AbstractModelObject will use to connect to the database
        two options:
        - instantiate an external model
        - define a class Model inside the object definition

    attributes: defines the attributes of the Object

    hidden_attributes: attributes to hide when calling Object.serialize() / Object.serialize(hide_attributes=True)

    required_attributes: attributes that must be included when creating a new object in the database

    unique_attributes: attributes that must be unique across all entries in the database

    default_attributes: defines the default values to use when creating a new object

    type_check_attributes: defines the types of the attributes

    serialize_attributes: defines custom serialization functions for attributes ex. lambda x: x.upper()

    deserialize_attributes: defines custom deserialization functions for attributes ex. lambda x: x.lower()
    """
    # extension required
    model = None

    # extension optional
    class Model(AbstractModel): pass  # noqa
    attributes = []
    hidden_attributes = []
    required_attributes = []
    unique_attributes = []
    default_attributes = {}
    type_check_attributes = {}
    serialize_attributes = {}
    deserialize_attributes = {}

    def __new__(cls, *args, **kwargs):
        cls._set_model()

        # get the pk from the Object definition
        try:
            pk = getattr(cls, cls.model.pk)
        except AttributeError:
            pk = None

        # check if the Object definition is using Attribute notation
        if isinstance(pk, Attribute):
            # for every attribute in the Object definition
            for attribute_name in dir(cls):
                # check if the attribute is an Attribute
                attribute_value = getattr(cls, attribute_name)
                if isinstance(attribute_value, Attribute):
                    # process the Attribute into the Object definition
                    cls.attributes.append(attribute_name)
                    if attribute_value.hidden:
                        cls.hidden_attributes.append(attribute_name)
                    if attribute_value.required:
                        cls.required_attributes.append(attribute_name)
                    if attribute_value.unique:
                        cls.unique_attributes.append(attribute_name)
                    if attribute_value.default:
                        cls.default_attributes[attribute_name] = attribute_value.default_value
                    if attribute_value.type:
                        cls.type_check_attributes[attribute_name] = attribute_value.type
                    if attribute_value.serialize:
                        cls.serialize_attributes[attribute_name] = attribute_value.serialize
                    if attribute_value.deserialize:
                        cls.deserialize_attributes[attribute_name] = attribute_value.deserialize

                    # remove the Attribute from the Object definition after processing
                    setattr(cls, attribute_name, None)

        return super().__new__(cls)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # set default values
        for key, value in self.default_attributes.items():
            if getattr(self, key) is None:
                self.__setattr__(key, value)

    def serialize(self, *args, **kwargs):
        attributes = super().serialize(*args, **kwargs)

        # apply serializer functions to attributes
        for attribute, serialize_function in self.serialize_attributes.items():
            if attribute in attributes:
                attributes[attribute] = serialize_function(attributes[attribute])

        return attributes

    def deserialize(self, attributes=None, *args, **kwargs):
        super().deserialize(attributes, *args, **kwargs)

        # apply deserializer functions to attributes
        for attribute, deserialize_function in self.deserialize_attributes.items():
            if attribute in self.__dict__:
                self.__dict__[attribute] = deserialize_function(self.__dict__[attribute])

    @property
    def _pk(self):
        return self.model.pk

    @property
    def _pk_value(self):
        return self.__dict__.get(self._pk)

    @property
    def _sk(self):
        return self.model.sk

    @property
    def _sk_value(self):
        return self.__dict__.get(self._sk)

    @classmethod
    def _set_model(cls):
        # use the default model if one is not provided
        if cls.model is None:
            cls.model = cls.Model()

    @classmethod
    def get(cls, pk_value, sk_value=None):
        cls._set_model()

        return cls(
            cls.model.get(pk_value, sk_value),
            raise_errors=False
        )

    @classmethod
    def get_by_unique_attribute(cls, attribute, value):
        cls._set_model()

        unique_key = f"{attribute.upper()}#{value}"
        reference = cls.model.get(unique_key, "#UNIQUE")

        model_object = cls()
        model_object.deserialize(
            attributes=cls.model.get(reference.get("reference_pk"), reference.get("reference_sk")),
            raise_errors=False
        )

        return model_object

    def insert(self):
        # enforce required attributes
        self._enforce_required_attributes()

        # enforce type checking
        self._enforce_type_checking()

        # auto generate pk if needed
        if self.model.auto_generate_pk and not self._pk_value:
            self.__setattr__(self._pk, str(uuid.uuid4()))

        # auto generate sk if needed
        if self.model.auto_generate_sk and self._sk and not self._sk_value:
            self.__setattr__(self._sk, str(uuid.uuid4()))

        # create a list of unique attributes to try and insert into the database
        insert_unique_attributes = []
        for attribute in self.unique_attributes:
            # check if the unique attribute has a value
            if self.__dict__.get(attribute):
                insert_unique_attributes.append(attribute)

        # attempt to insert all unique attributes
        self._insert_unique_attributes(insert_unique_attributes)

        try:
            # insert the object
            self.deserialize(
                attributes=self.model.insert(self.serialize(hide_attributes=False)),
                raise_errors=False
            )
        except Exception as e:
            # undo all unique inserts if the object insert fails
            self._undo_insert_unique_attributes(insert_unique_attributes)
            raise e

    def update(self):
        # enforce type checking
        self._enforce_type_checking()

        # only pull the previous state of the object if necessary for checking uniqueness
        previous_state = None
        insert_unique_attributes = []

        # create a list of unique attributes to try and insert into the database
        for attribute in self.unique_attributes:
            # check if the unique attribute has a value
            attribute_value = self.__dict__.get(attribute)

            # pull the previous state of the object for checking if the unique attribute has changed
            if attribute_value and previous_state is None:
                previous_state = self.model.get(self._pk_value, self._sk_value)

            # only insert the new unique attribute if the value is different than in the previous state
            if attribute_value and attribute_value != previous_state.get(attribute):
                insert_unique_attributes.append(attribute)

        # attempt to insert all unique attributes
        self._insert_unique_attributes(insert_unique_attributes)

        try:
            # update the object
            self.deserialize(
                attributes=self.model.update(self.serialize(hide_attributes=False)),
                raise_errors=False
            )
        except Exception as e:
            # undo all unique inserts if the object update fails
            self._undo_insert_unique_attributes(insert_unique_attributes)
            raise e
        else:
            # remove previous unique attribute values
            if previous_state:
                for old_attribute in insert_unique_attributes:
                    try:
                        self.model.delete(f"{old_attribute.upper()}#{previous_state.get(old_attribute)}", "#UNIQUE")
                    except:  # noqa
                        pass

    def save(self):
        # check if the record exists
        if self._pk_value:
            try:
                record_exists = bool(self.model.get(self._pk_value, self._sk_value))
            except:  # noqa
                record_exists = False

        # call update or insert accordingly
        if self._pk_value and record_exists:
            self.update()
        else:
            self.insert()

    def delete(self):
        # check if the object has unique attributes
        if self.unique_attributes:
            try:
                # undo all unique attributes before deleting the object
                self._undo_insert_unique_attributes(self.unique_attributes)
            except:  # noqa
                pass

        # delete the object
        return self.model.delete(self._pk_value, self._sk_value)

    def _enforce_required_attributes(self):
        missing_required_attributes = []
        for required_attribute in self.required_attributes:
            if getattr(self, required_attribute) is None:
                missing_required_attributes.append(required_attribute)
        if missing_required_attributes:
            raise RequiredAttributes("missing the following required attributes: " + ", ".join(missing_required_attributes))

    def _enforce_type_checking(self):
        failed_type_checks = []
        for attribute, attribute_type in self.type_check_attributes.items():
            attribute_value = getattr(self, attribute)
            if attribute_value is not None and not isinstance(attribute_value, attribute_type):
                failed_type_checks.append(attribute)
        if failed_type_checks:
            raise TypeError("the following attributes failed type checking: " + ", ".join(failed_type_checks))

    def _insert_unique_attributes(self, unique_attributes):
        successes = []
        failures = []

        # attempt to insert each unique attribute as a special entry in the database ex EMAIL#test@test.com / #UNIQUE
        for attribute in unique_attributes:
            attribute_value = self.__dict__.get(attribute)

            unique_entry = self._build_unique_entry(
                attribute,
                attribute_value,
                self._pk_value,
                self._sk_value
            )

            try:
                # attempt to insert
                self.model.insert(unique_entry)
            except ItemAlreadyExists:  # noqa
                # track failures
                failures.append(attribute)
            else:
                # track successes
                successes.append(attribute)

        # undo all success if any failures occurred
        if failures:
            self._undo_insert_unique_attributes(successes)
            raise UniqueAttributes("the following unique attributes already exists: " + ", ".join(failures))

    def _build_unique_entry(self, unique_attribute, attribute_value, reference_pk, reference_sk=None):
        unique_entry = {}
        unique_entry[self._pk] = f"{unique_attribute.upper()}#{attribute_value}"
        unique_entry["reference_pk"] = reference_pk
        if reference_sk:
            unique_entry[self._sk] = "#UNIQUE"
            unique_entry["reference_sk"] = reference_sk
        return unique_entry

    def _undo_insert_unique_attributes(self, unique_attributes):
        for attribute in unique_attributes:
            try:
                delete_pk = f"{attribute.upper()}#{self.__dict__.get(attribute)}"
                delete_sk = "#UNIQUE"
                self.model.delete(delete_pk, delete_sk)
            except:  # noqa
                pass
