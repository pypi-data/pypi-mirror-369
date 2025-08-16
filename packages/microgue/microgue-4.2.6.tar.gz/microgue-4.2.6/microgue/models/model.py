import uuid

from .attributes import Attribute
from .base_table import BaseTable, InsertFailed
from .object import Object


class RelatedModelsMissing(Exception):
    pass


class UniqueAttributesExist(Exception):
    pass


class Model(Object):
    """
    table: the instantiated table that the Model will use to connect to the database
        two options:
        - instantiate an external table
        - define a class Table inside the Model definition

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

        pk_attribute: the name of the attribute that will be used as the partition key

        sk_attribute: the name of the attribute that will be used as the sort key

        key_attributes: dict of attributes with the key attribute and label
            key: the key attribute name ex. pk, sk, id, etc.
            label: the label to apply to the key attribute value when inserting into the database ex. USER#1234
            {
                "company_id": {
                    "key": "pk",
                    "label": "COMPANY",
                },
                "id": {
                    "key": "sk",
                    "label": "USER",
                }
            }

        auto_generate_attributes: set of attributes that will auto generate a uuid if not set before inserting into the database

        unique_attributes: set of attributes that must be unique across all entries in the database

        related_models: dict of related models by partition key label and sort key label
            ex.
            {
                "COMPANY": {
                    "USER": User,
                    "DEPARTMENT": Department,
                }
            }

    related_models: list of related model classes that will be used to build the related_models dict in the schema
    """

    # extension required
    table = None

    class Table(BaseTable):
        pass

    # extension optional
    related_models = []

    def __new__(cls, *args, **kwargs):
        cls._set_table()
        return super().__new__(cls)

    @classmethod
    def _define_schema(cls):
        super()._define_schema()
        cls.schema().update(
            {
                "pk_attribute": None,
                "sk_attribute": None,
                "key_attributes": dict(),
                "auto_generate_attributes": set(),
                "unique_attributes": set(),
                "related_models": dict(),
            }
        )

    @classmethod
    def _build_schema(cls):
        super()._build_schema()

        # add created_on and updated_on attributes if they are not defined
        if "created_on" not in cls.schema()["attributes"]:
            cls._process_attribute("created_on", Attribute())
        if "updated_on" not in cls.schema()["attributes"]:
            cls._process_attribute("updated_on", Attribute())

        # build the dict of related models
        for model in cls.related_models:
            object = model()

            # get pk and sk labels
            pk_label = object._pk_label()
            sk_label = object._sk_label()

            # add the related model to the schema
            if pk_label and sk_label:
                if cls.schema()["related_models"].get(pk_label):
                    cls.schema()["related_models"][pk_label][sk_label] = model
                else:
                    cls.schema()["related_models"][pk_label] = {sk_label: model}

    @classmethod
    def _process_attribute(cls, attribute_name, attribute_value):
        super()._process_attribute(attribute_name, attribute_value)
        if getattr(attribute_value, "key", False):
            if attribute_value.key == cls.table.pk:
                cls.schema()["pk_attribute"] = attribute_name
            elif attribute_value.key == cls.table.sk:
                cls.schema()["sk_attribute"] = attribute_name
            cls.schema()["key_attributes"][attribute_name] = {
                "key": attribute_value.key,
                "label": attribute_value.label,
            }
        if getattr(attribute_value, "auto_generate", False):
            cls.schema()["auto_generate_attributes"].add(attribute_name)
        if getattr(attribute_value, "unique", False):
            cls.schema()["unique_attributes"].add(attribute_name)

    @classmethod
    def get(cls, pk_value=None, sk_value=None):
        # create empty object and ensure the schema is built
        get_object = cls()

        # deserialize the object from the database
        get_object.deserialize_from_table(
            cls._table_get(pk_value, sk_value),
        )

        return get_object

    @classmethod
    def get_by_unique_attribute(cls, unique_attribute, attribute_value):
        # create empty object and ensure the schema is built
        get_object = cls()

        # get the unique object from the database
        unique_pk = cls._build_unique_pk(cls.__name__, unique_attribute, attribute_value)
        unique_sk = "__UNIQUE__"
        unique_object = cls.table.get(unique_pk, unique_sk)

        # use the unique object as a reference to get the actual object
        get_object.deserialize_from_table(
            cls._table_get(unique_object["reference_pk"], unique_object.get("reference_sk", None)),
        )

        return get_object

    @classmethod
    def get_all(cls, pk_value=None, sk_value=None, get_related=False, index=None):
        # create empty object and ensure the schema is built
        cls()

        # check that the class has related models defined
        if get_related and not cls.schema()["related_models"]:
            raise RelatedModelsMissing("related_models are not defined for this object")

        get_objects = []

        # label the pk_value when not using an index or when using an index with the same pk as the table
        if not index or cls.table.indexes.get(index, {}).get("pk") == cls.table.pk:
            pk_value = cls._apply_label_to_value(cls._pk_label(), pk_value)

        # label the sk_value when not using an index and not getting related objects
        if not index and not get_related:
            sk_attribute = cls.schema()["sk_attribute"]

            # if the sk_value is None and the object has an sk_attribute defined in the schema
            if sk_value is None and sk_attribute is not None:
                # use the default value if one has been defined in the schema
                if sk_attribute in cls.schema()["default_attributes"]:
                    sk_value = cls.schema()["default_attributes"].get(sk_attribute, "")
                # else use empty string
                else:
                    sk_value = ""

            # apply labels to pk and sk values
            sk_value = cls._apply_label_to_value(cls._sk_label(), sk_value)

        # get all items from the database that match the pk and sk values
        items = cls.table.get_all(pk_value, sk_value, index=index)
        for item in items:
            # get the pk_label and sk_label from the item
            pk_label = item.get(cls.table.pk).split("#")[0]
            sk_label = item.get(cls.table.sk, "").split("#")[0]

            # select a class to use based on the labels - defaulting to the current class
            this_class = cls.schema()["related_models"].get(pk_label, {}).get(sk_label, cls)

            # create an object of the selected class
            this_object = this_class()

            # deserialize the object from the item
            this_object.deserialize_from_table(item, raise_errors=True)

            # add the object to the list of get_objects
            get_objects.append(this_object)

        return get_objects

    def create(self):
        # auto generate attributes if needed
        self._auto_generate_attributes()

        # enforce required attributes
        self._validate_required_attributes()

        # enforce type checking
        self._validate_typed_attributes()

        # create a list of unique attributes to try and insert into the database
        insert_unique_attributes = []
        for attribute in self.schema()["unique_attributes"]:
            # check if the unique attribute has a value
            if self.__dict__.get(attribute):
                insert_unique_attributes.append(attribute)

        # attempt to insert all unique attributes
        self._insert_unique_attributes(insert_unique_attributes)

        try:
            # insert the object into the database
            self.deserialize_from_table(
                self.table.insert(
                    self.serialize_to_table(),
                ),
            )
        except Exception as e:
            # undo all unique inserts if the object insert fails
            self._undo_insert_unique_attributes(insert_unique_attributes)
            raise e

    def update(self):
        # enforce type checking
        self._validate_typed_attributes()

        # only pull the previous state of the object if necessary for checking uniqueness
        previous_state = None
        insert_unique_attributes = []

        # create a list of unique attributes to try and insert into the database
        for attribute in self.schema()["unique_attributes"]:
            # check if the unique attribute has a value
            attribute_value = self.__dict__.get(attribute)

            # pull the previous state of the object for checking if the unique attribute has changed
            if attribute_value and previous_state is None:
                previous_state = self._table_get(self._pk_value, self._sk_value)

            # only insert the new unique attribute if the value is different than in the previous state
            if attribute_value and attribute_value != previous_state.get(attribute):
                insert_unique_attributes.append(attribute)

        # attempt to insert all unique attributes
        self._insert_unique_attributes(insert_unique_attributes)
        try:
            # update the object in the database
            self.deserialize_from_table(
                self.table.update(
                    self.serialize_to_table(),
                ),
            )
        except Exception as e:
            # undo all unique inserts if the object update fails
            self._undo_insert_unique_attributes(insert_unique_attributes)
            raise e
        else:
            # remove previous unique objects
            if previous_state:
                for old_attribute in insert_unique_attributes:
                    try:
                        unique_pk = self._build_unique_pk(self.__class__.__name__, old_attribute, previous_state.get(old_attribute))
                        self.table.delete(unique_pk, "__UNIQUE__")
                    except:  # noqa
                        pass

    def delete(self):
        # check if the object has unique attributes
        if self.schema()["unique_attributes"]:
            try:
                # undo all unique attributes before deleting the object
                self._undo_insert_unique_attributes(self.schema()["unique_attributes"])
            except:  # noqa
                pass

        # get the labeled attributes for deletion
        labeled_attributes = self.serialize_to_table()

        # delete the object
        return self.table.delete(labeled_attributes[self.table.pk], labeled_attributes.get(self.table.sk, None))

    def save(self):
        # check if the record exists
        if self._pk_value:
            try:
                record_exists = bool(self._table_get(self._pk_value, self._sk_value))
            except:  # noqa
                record_exists = False

        # call update or insert accordingly
        if self._pk_value and record_exists:
            self.update()
        else:
            self.create()

    """
    Helper functions
    """

    @property
    def _pk_attribute(self):
        return self.schema().get("pk_attribute")

    @property
    def _sk_attribute(self):
        return self.schema().get("sk_attribute")

    @property
    def _pk_value(self):
        return self.__dict__.get(self._pk_attribute)

    @property
    def _sk_value(self):
        return self.__dict__.get(self._sk_attribute)

    @classmethod
    def _pk_label(cls):
        return cls.schema()["key_attributes"][cls.schema().get("pk_attribute")]["label"]

    @classmethod
    def _sk_label(cls):
        return cls.schema()["key_attributes"].get(cls.schema().get("sk_attribute"), {}).get("label", "")

    @classmethod
    def _set_table(cls):
        # use the default table if one is not provided
        if cls.table is None:
            cls.table = cls.Table()

    @classmethod
    def _table_get(cls, pk_value=None, sk_value=None):
        # use default sk value if one has been defined in the schema
        sk_attribute = cls.schema()["sk_attribute"]
        if sk_value is None and sk_attribute is not None:
            sk_value = cls.schema()["default_attributes"].get(sk_attribute, None)

        # apply labels to pk and sk values
        pk_value = cls._apply_label_to_value(cls._pk_label(), pk_value)
        sk_value = cls._apply_label_to_value(cls._sk_label(), sk_value)

        return cls.table.get(pk_value, sk_value)

    @classmethod
    def _apply_label_to_value(cls, label, value):
        if label:
            return f"{label}#{value}"
        return value

    @classmethod
    def _apply_labels_and_keys_to_attributes(cls, attributes):
        for attribute, key_attribute in cls.schema()["key_attributes"].items():
            key = key_attribute["key"]
            label = key_attribute["label"]
            if attribute in attributes:
                if label:
                    attributes[key] = f"{label}#{attributes.pop(attribute)}"
                else:
                    attributes[key] = attributes.pop(attribute)
        return attributes

    @classmethod
    def _remove_labels_and_keys_from_attributes(cls, attributes):
        for attribute, key_attribute in cls.schema()["key_attributes"].items():
            key = key_attribute["key"]
            label = key_attribute["label"]
            if key in attributes:
                attributes[attribute] = attributes.pop(key).replace(f"{label}#", "")
        return attributes

    def serialize_to_table(self, *args, **kwargs):
        return self._apply_labels_and_keys_to_attributes(
            self.serialize(hide_attributes=False, *args, **kwargs),
        )

    def deserialize_from_table(self, attributes=None, raise_errors=False, *args, **kwargs):
        return self.deserialize(
            self._remove_labels_and_keys_from_attributes(attributes),
            raise_errors=raise_errors,
            *args,
            **kwargs,
        )

    def _auto_generate_attributes(self):
        for attribute in self.schema()["auto_generate_attributes"]:
            if self.__dict__.get(attribute) is None:
                self.__setattr__(attribute, str(uuid.uuid4()))

    @staticmethod
    def _build_unique_pk(object_name, attribute_name, attribute_value):
        return f"{object_name}.{attribute_name}={attribute_value}"

    def _build_unique_object(self, unique_attribute, attribute_value, reference_pk, reference_sk=None):
        unique_object = dict()
        unique_object[self.table.pk] = self._build_unique_pk(self.__class__.__name__, unique_attribute, attribute_value)
        unique_object["reference_pk"] = reference_pk
        if reference_sk is not None:
            unique_object[self.table.sk] = "__UNIQUE__"
            unique_object["reference_sk"] = reference_sk
        return unique_object

    def _insert_unique_attributes(self, unique_attributes):
        successes = []
        failures = []

        # attempt to insert each unique attribute as a special entry in the database ex EMAIL#test@test.com / __UNIQUE__
        for attribute in unique_attributes:
            attribute_value = self.__dict__.get(attribute)

            unique_object = self._build_unique_object(
                attribute,
                attribute_value,
                self._pk_value,
                self._sk_value,
            )

            try:
                # attempt to insert the unique object
                self.table.insert(unique_object)
            except InsertFailed:  # noqa
                # track failures
                failures.append(attribute)
            else:
                # track successes
                successes.append(attribute)

        # undo all success if any failures occurred
        if failures:
            self._undo_insert_unique_attributes(successes)
            raise UniqueAttributesExist("the following attributes are not unique: " + ", ".join(failures))

    def _undo_insert_unique_attributes(self, unique_attributes):
        for unique_attribute in unique_attributes:
            try:
                unique_pk = self._build_unique_pk(self.__class__.__name__, unique_attribute, self.__dict__.get(unique_attribute))
                self.table.delete(unique_pk, "__UNIQUE__")
            except:  # noqa
                pass
