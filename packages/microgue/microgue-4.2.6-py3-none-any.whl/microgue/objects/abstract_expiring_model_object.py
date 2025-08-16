import datetime
import time
from .abstract_model_object import *  # noqa
from ..loggers.logger import Logger

logger = Logger()


class AbstractExpiringModelObject(AbstractModelObject):  # noqa
    expiration_seconds = 0

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.expires_in and self.expires_in < int(time.mktime(datetime.datetime.utcnow().timetuple())):
            logger.debug(f"{self.__class__.__name__}.__init__ - expired", priority=2)
            raise GetFailed("item expired")  # noqa

    def insert(self):
        # add expires_in
        expires_in = datetime.datetime.utcnow() + datetime.timedelta(seconds=self.expiration_seconds)
        self.expires_in = int((expires_in - datetime.datetime(1970, 1, 1)).total_seconds())
        super().insert()

    def update(self, *args, **kwargs):
        # add expires_in
        expires_in = datetime.datetime.utcnow() + datetime.timedelta(seconds=self.expiration_seconds)
        self.expires_in = int((expires_in - datetime.datetime(1970, 1, 1)).total_seconds())
        super().update()

    def _build_unique_entry(self, unique_attribute, attribute_value, reference_pk, reference_sk=None):
        # add expires_in
        unique_entry = super()._build_unique_entry(
            unique_attribute,
            attribute_value,
            reference_pk,
            reference_sk
        )
        unique_entry["expires_in"] = self.expires_in
        return unique_entry
