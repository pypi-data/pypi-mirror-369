import json

import boto3

from ..loggers.logger import Logger

logger = Logger()


class DeleteFailed(Exception):
    pass


class ReceiveFailed(Exception):
    pass


class SendFailed(Exception):
    pass


class QueueConnectionFailed(Exception):
    pass


class AbstractQueue:
    # internal use only
    _queue_client = None

    # extension required
    queue_url = None

    class Message:
        def __init__(self, message_data):
            self.id = message_data["ReceiptHandle"]
            self.data = json.loads(message_data["Body"])

    def __init__(self, *args, **kwargs):
        logger.debug(f"{self.__class__.__name__}.__init__", priority=2)

        # share the queue client at the global level
        if AbstractQueue._queue_client is None:
            try:
                logger.debug("connecting to sqs", priority=3)
                logger.debug(f"queue_url: {self.queue_url}")
                AbstractQueue._queue_client = boto3.client("sqs")
            except Exception as e:
                logger.error(f"{self.__class__.__name__}.__init__ - error", priority=3)
                logger.error(f"{e.__class__.__name__}: {str(e)}")
                raise QueueConnectionFailed(str(e))

    def send(self, message):
        logger.debug(f"{self.__class__.__name__}.send", priority=2)

        if isinstance(message, dict):
            message = json.dumps(message)
        try:
            self._queue_client.send_message(
                QueueUrl=self.queue_url,
                MessageBody=message,
            )
            logger.error(f"{self.__class__.__name__}.send - success", priority=3)
        except Exception as e:
            logger.error(f"{self.__class__.__name__}.send - error", priority=3)
            logger.error(f"{e.__class__.__name__}: {str(e)}")
            raise SendFailed(str(e))

        return True

    def receive(self, max_number_of_messages=1, visibility_timeout=1, wait_time=1):
        logger.debug(f"{self.__class__.__name__}.receive", priority=2)
        logger.debug(f"max_number_of_messages: {max_number_of_messages}")
        logger.debug(f"visibility_timeout: {visibility_timeout}")
        logger.debug(f"wait_time: {wait_time}")

        try:
            response = self._queue_client.receive_message(
                QueueUrl=self.queue_url,
                MaxNumberOfMessages=max_number_of_messages,
                VisibilityTimeout=visibility_timeout,
                WaitTimeSeconds=wait_time,
            )
        except Exception as e:
            logger.error(f"{self.__class__.__name__}.receive - error", priority=3)
            logger.error(f"{e.__class__.__name__}: {str(e)}")
            raise ReceiveFailed(str(e))

        response_messages = response.get("Messages", [])
        messages = [self.Message(msg) for msg in response_messages]

        logger.debug(f"number_of_messages_received: {len(messages)}")
        return messages

    def delete(self, message):
        logger.debug(f"{self.__class__.__name__}.delete", priority=2)
        logger.debug(f"message.id: {message.id}")

        try:
            self._queue_client.delete_message(
                QueueUrl=self.queue_url,
                ReceiptHandle=message.id,
            )
        except Exception as e:
            logger.error(f"{self.__class__.__name__}.delete - error", priority=3)
            logger.error(f"{e.__class__.__name__}: {str(e)}")
            raise DeleteFailed(str(e))

        return True
