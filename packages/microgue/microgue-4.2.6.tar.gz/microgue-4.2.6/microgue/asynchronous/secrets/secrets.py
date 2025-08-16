import json

import aioboto3

from ...loggers.logger import Logger

logger = Logger()


class GetSecretFailed(Exception):
    pass


class Secrets:
    def __init__(self, *args, **kwargs):
        pass

    async def get(self, secret_name):
        async with aioboto3.Session().client("secretsmanager") as secrets_client:
            try:
                get_secret_value_response = await secrets_client.get_secret_value(
                    SecretId=secret_name,
                )
            except Exception as e:
                logger.error(f"{self.__class__.__name__}.get - error", priority=3)
                logger.error(f"secret_name: {secret_name}")
                logger.error(f"{e.__class__.__name__}: {str(e)}")
                raise GetSecretFailed(str(e))

            try:
                return json.loads(get_secret_value_response["SecretString"])
            except:  # noqa
                return get_secret_value_response["SecretString"]
