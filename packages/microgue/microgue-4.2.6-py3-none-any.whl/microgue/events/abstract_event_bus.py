import json

import boto3

from ..loggers.logger import Logger

logger = Logger()


class EventBusConnectionFailed(Exception):
    pass


class PublishFailed(Exception):
    pass


class AbstractEventBus:
    # internal use only
    _event_bus_client = None

    # extension required
    event_bus_name = None
    event_bus_region = None
    event_source = None

    def __init__(self, *args, **kwargs):
        logger.debug(f"{self.__class__.__name__}.__init__", priority=2)

        # share the event bus client at the global level
        if AbstractEventBus._event_bus_client is None:
            try:
                logger.debug("connecting to eventbridge", priority=3)
                logger.debug(f"event_bus_name: {self.event_bus_name}")
                logger.debug(f"event_bus_region: {self.event_bus_region}")
                AbstractEventBus._event_bus_client = boto3.client(service_name="events", region_name=self.event_bus_region)
            except Exception as e:
                logger.error(f"{self.__class__.__name__}.__init__ - error", priority=3)
                logger.error(f"{e.__class__.__name__}: {str(e)}")
                raise EventBusConnectionFailed(str(e))

    def publish(self, event_type, event_data=None):
        # defaults
        event_data = {} if event_data is None else event_data

        logger.debug(f"{self.__class__.__name__}.publish", priority=2)
        logger.debug(f"event_type: {event_type}")

        try:
            response = self._event_bus_client.put_events(
                Entries=[
                    {
                        "Source": self.event_source,
                        "DetailType": event_type,
                        "Detail": json.dumps(event_data),
                        "EventBusName": self.event_bus_name,
                    }
                ]
            )
        except Exception as e:
            logger.error(f"{self.__class__.__name__}.publish - error", priority=3)
            logger.error(f"{e.__class__.__name__}: {str(e)}")
            raise PublishFailed(str(e))

        if response.get("ResponseMetadata", {}).get("HTTPStatusCode") == 200:
            logger.debug(f"{self.__class__.__name__}.publish - success", priority=3)
            return True
        else:
            logger.critical(f"{self.__class__.__name__}.publish - error", priority=3)
            logger.critical(f"response: {response}")
            raise PublishFailed(response)
