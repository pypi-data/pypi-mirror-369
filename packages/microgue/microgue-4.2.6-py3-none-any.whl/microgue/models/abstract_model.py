import boto3
import datetime
import uuid
from boto3.dynamodb.conditions import Key
from boto3.dynamodb.types import Decimal
from ..utils import mask_fields_in_data
from ..loggers.logger import Logger

logger = Logger()


class DatabaseConnectionFailed(Exception): pass  # noqa
class DeleteFailed(Exception): pass  # noqa
class GetFailed(Exception): pass  # noqa
class ItemAlreadyExists(Exception): pass  # noqa
class MissingKey(Exception): pass  # noqa
class UpdateFailed(Exception): pass  # noqa


class AbstractModel:
    """
    database: the connection to dynamodb - internal use only
    table_name: name of table in dynamodb - extension required
    pk: partion key of the table - defaulted to id
    auto_generate_pk: auto generate the pk value using uuid
    sk: sort key for the partition key of the table - defaulted to None
    auto_generate_sk: auto generate the pk value using uuid
    indexes: defines all indexes on your table
        local secondary indexes (lsi) do not require the pk to be defined
        global secondary indexes (gsi) do not require the sk to be defined
        {
            "example_index-index": {
                "pk": "example_index_partition_key",
                "sk": "example_index_sort_key"
            }
        }
    mask_attributes: list of attributes to mask when logging
    """
    # internal use only
    database = None

    # extension required
    table_name = None

    # extension optional
    pk = "id"
    auto_generate_pk = True
    sk = None
    auto_generate_sk = True
    indexes = {}
    mask_attributes = []

    def __init__(self, *args, **kwargs):
        logger.debug(f"{self.__class__.__name__}.__init__", priority=2)
        logger.debug(f"AbstractModel.database: {AbstractModel.database}")
        try:
            logger.debug("connecting to dynamodb", priority=3)
            logger.debug(f"table_name: {self.table_name}")
            if AbstractModel.database is None:
                AbstractModel.database = boto3.resource("dynamodb")
                logger.debug("successfully connected to dynamodb", priority=3)
            else:
                logger.debug("using existing connection to dynamodb", priority=3)

            self.table = AbstractModel.database.Table(self.table_name)
        except Exception as e:
            logger.error(f"{self.__class__.__name__}.__init__ - error", priority=3)
            logger.error(f"{e.__class__.__name__}: {str(e)}")
            raise DatabaseConnectionFailed(str(e))
        super().__init__(*args, **kwargs)

    def get(self, pk_value, sk_value=None):
        logger.debug(f"{self.__class__.__name__}.get", priority=2)
        logger.debug(f"{self.pk}: {pk_value}")
        if self.sk:
            logger.debug(f"{self.sk}: {sk_value}")

        # create key based on presence of pk and sk
        key = {self.pk: pk_value}
        if self.sk:
            key[self.sk] = sk_value

        try:
            item = self.table.get_item(Key=key)["Item"]
        except Exception as e:
            logger.debug(f"{self.__class__.__name__}.get - failed", priority=3)
            logger.debug(f"{e.__class__.__name__}: {str(e)}")
            raise GetFailed("failed to get item")

        logger.debug(f"return: {mask_fields_in_data(item, self.mask_attributes)}")

        return self._replace_decimals(item)

    def insert(self, item):
        item = item.copy()
        logger.debug(f"{self.__class__.__name__}.insert", priority=2)
        logger.debug(f"item: {mask_fields_in_data(item, self.mask_attributes)}")

        # add created on to item
        item["created_on"] = datetime.datetime.utcnow().isoformat()

        # check if pk should be generated or if an error should be raise
        if item.get(self.pk) is None:
            if self.auto_generate_pk:
                item[self.pk] = str(uuid.uuid4())
            else:
                raise MissingKey(f"missing key: {self.pk}")

        # check if sk should be generated or if an error should be raise
        if self.sk and item.get(self.sk) is None:
            if self.auto_generate_pk:
                item[self.sk] = str(uuid.uuid4())
            else:
                raise MissingKey(f"missing key: {self.sk}")

        # create condition expression to ensure uniqueness based on pk and sk
        condition_expression = f"attribute_not_exists({self.pk})"
        if self.sk:
            condition_expression += f" AND attribute_not_exists({self.sk})"

        try:
            # convert floats to decimals for sending to dynamodb
            self.table.put_item(
                Item=self._replace_floats(item),
                ConditionExpression=condition_expression
            )
        except Exception as e:
            logger.error(f"{self.__class__.__name__}.insert - error", priority=3)
            logger.error(f"{e.__class__.__name__}: {str(e)}")
            if self.sk:
                error = f"{self.pk} and {self.sk} key combo ({item[self.pk]} and {item[self.sk]}) already exists"
            else:
                error = f"{self.pk} ({item[self.pk]}) already exists"
            raise ItemAlreadyExists(error)

        logger.debug(f"return: {mask_fields_in_data(item, self.mask_attributes)}")

        return self._replace_decimals(item)

    def update(self, updated_item):
        updated_item = updated_item.copy()
        logger.debug(f"{self.__class__.__name__}.update", priority=2)
        logger.debug(f"updated_item: {mask_fields_in_data(updated_item, self.mask_attributes)}")

        # convert floats to decimals for sending to dynamodb
        updated_item = self._replace_floats(updated_item)

        # verify the pk exists
        if self.pk and not updated_item.get(self.pk):
            raise MissingKey(f"missing key: {self.pk}")

        # verify the sk exists if one is required
        if self.sk and not updated_item.get(self.sk):
            raise MissingKey(f"missing key: {self.sk}")

        # add updated on to item
        updated_item["updated_on"] = datetime.datetime.utcnow().isoformat()

        # create key based on presence of pk and sk
        pk_value = updated_item.pop(self.pk)
        key = {self.pk: pk_value}
        if self.sk:
            key[self.sk] = updated_item.pop(self.sk)

        # generage the update expression and the expression attribute values
        update_expressions = []
        expression_attribute_values = {}
        for k, v in updated_item.items():
            update_expressions.append(f"{k} = :{k}")
            expression_attribute_values[f":{k}"] = updated_item[k]

        # run the update
        try:
            item = self.table.update_item(
                Key=key,
                UpdateExpression="set {}".format(", ".join(update_expressions)),
                ExpressionAttributeValues=expression_attribute_values,
                ReturnValues="ALL_NEW"
            )["Attributes"]
        except Exception as e:
            logger.debug(f"{self.__class__.__name__}.update - failed", priority=3)
            logger.debug(f"{e.__class__.__name__}: {str(e)}")
            raise UpdateFailed("failed to update item")

        logger.debug(f"return: {mask_fields_in_data(item, self.mask_attributes)}")

        return self._replace_decimals(item)

    def delete(self, pk_value, sk_value=None):
        logger.debug(f"{self.__class__.__name__}.delete", priority=2)
        logger.debug(f"{self.pk}: {pk_value}")
        if self.sk:
            logger.debug(f"{self.sk}: {sk_value}")

        # create key based on presence of pk and sk
        key = {self.pk: pk_value}
        if self.sk:
            key[self.sk] = sk_value

        try:
            self.table.delete_item(Key=key)
        except Exception as e:
            logger.debug(f"{self.__class__.__name__}.delete - failed", priority=3)
            logger.debug(f"{e.__class__.__name__}: {str(e)}")
            raise DeleteFailed("failed to delete item")

        return True

    def get_all_by_pk(self, pk_value):
        logger.debug(f"{self.__class__.__name__}.get_all_by_pk", priority=2)
        logger.debug(f"{self.pk}: {pk_value}")
        return self.query(Key(self.pk).eq(pk_value))

    def get_all_by_index(self, index, pk_value, sk_value=None):
        pk, sk = self._get_pk_and_sk_for_index(index)
        logger.debug(f"{self.__class__.__name__}.get_all_by_index", priority=2)
        logger.debug(f"index: {index}")
        logger.debug(f"{pk}: {pk_value}")
        if sk and sk_value:
            logger.debug(f"{sk}: {sk_value}")

        # create key condition expression based on presence of pk and sk for the index
        key_condition_expression = Key(pk).eq(pk_value)
        if sk and sk_value:
            key_condition_expression = key_condition_expression & Key(sk).eq(sk_value)

        return self.query(key_condition_expression, index)

    def query(self, key_condition_expression, index=None):
        if index:
            response = self.table.query(
                IndexName=index,
                KeyConditionExpression=key_condition_expression
            )
        else:
            response = self.table.query(
                KeyConditionExpression=key_condition_expression
            )

        items = response.get("Items")
        while "LastEvaluatedKey" in response:
            response = self.table.query(ExclusiveStartKey=response["LastEvaluatedKey"])
            items.append(response["Items"])

        return self._replace_decimals(items)

    def _get_pk_and_sk_for_index(self, index):
        pk = self.indexes.get(index, {}).get("pk", self.pk)
        sk = self.indexes.get(index, {}).get("sk", None)
        return pk, sk

    def _replace_floats(self, item):
        # convert floats to Decimals when sending data to dynamodb
        if isinstance(item, list):
            for index in range(len(item)):
                item[index] = self._replace_floats(item[index])
            return item
        elif isinstance(item, dict):
            for key in item.keys():
                item[key] = self._replace_floats(item[key])
            return item
        elif isinstance(item, float):
            return Decimal(str(item))
        else:
            return item

    def _replace_decimals(self, item):
        # convert Decimals to floats or ints when receiving data from dynamodb
        if isinstance(item, list):
            for index in range(len(item)):
                item[index] = self._replace_decimals(item[index])
            return item
        elif isinstance(item, dict):
            for key in item.keys():
                item[key] = self._replace_decimals(item[key])
            return item
        elif isinstance(item, Decimal):
            if item % 1 == 0:
                return int(item)
            else:
                return float(item)
        else:
            return item
