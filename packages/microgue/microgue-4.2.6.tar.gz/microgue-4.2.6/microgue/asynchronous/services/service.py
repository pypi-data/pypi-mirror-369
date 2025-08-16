import traceback
from collections import OrderedDict

import httpx

from ...loggers.logger import Logger
from ...services.service import Service as _Service

logger = Logger()


class Service(_Service):
    async def request(self, *args, **kwargs) -> _Service.Response:  # type: ignore
        return await self.invoke(self.Request(*args, **kwargs))

    async def invoke(self, request: _Service.Request) -> _Service.Response:  # type: ignore
        logger.debug(f"{self.__class__.__name__}.invoke", priority=2)
        self.log_request(request)

        # open all files before sending them
        opened_request_files = OrderedDict()
        for key, file in request.files.items():
            opened_request_files[key] = open(file, "rb")

        try:
            async with httpx.AsyncClient() as client:
                http_response = await client.request(
                    url=self.request_base_url + request.url,
                    params=request.parameters,
                    method=request.method,
                    headers=request.headers,
                    cookies=request.cookies,
                    data=request.data,
                    json=request.json,
                    files=opened_request_files,
                )

            response_status_code = http_response.status_code
            response_headers = dict(http_response.headers)
            response_cookies = dict(http_response.cookies)

            try:
                response_data = http_response.json()
            except:  # noqa
                response_data = http_response.text

            response = self.Response(
                status_code=response_status_code,
                headers=response_headers,
                cookies=response_cookies,
                data=response_data,
            )

        except Exception as e:
            logger.error(f"{self.__class__.__name__}.invoke - error", priority=3)
            logger.error(f"{e.__class__.__name__}: {str(e)}")
            logger.error(traceback.format_exc())

            response = self.Response(
                status_code=500,
                headers={},
                cookies={},
                data={
                    "error": "internal server error",
                },
            )

        self.log_response(response)
        return response
