import json

import aioboto3

from ...loggers.logger import Logger

logger = Logger()


class PublishFailed(Exception):
    pass


class AbstractEventBus:
    # extension required
    event_bus_name = None
    event_bus_region = None
    event_source = None

    async def publish(self, event_type, event_data=None):
        # defaults
        event_data = {} if event_data is None else event_data
        logger.debug(f"{self.__class__.__name__}.publish", priority=2)
        logger.debug(f"event_type: {event_type}")

        async with aioboto3.Session().client("events", region_name=self.event_bus_region) as event_bus_client:
            try:
                response = await event_bus_client.put_events(
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
                logger.error(f"event_bus_name: {self.event_bus_name}")
                logger.error(f"event_bus_region: {self.event_bus_region}")
                logger.error(f"{e.__class__.__name__}: {str(e)}")
                raise PublishFailed(str(e))

            if response.get("ResponseMetadata", {}).get("HTTPStatusCode") == 200:
                return True
            else:
                logger.error(f"{self.__class__.__name__}.publish - error", priority=3)
                logger.error(f"event_bus_name: {self.event_bus_name}")
                logger.error(f"event_bus_region: {self.event_bus_region}")
                logger.error(f"response: {response}")
                raise PublishFailed(response)
