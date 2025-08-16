import traceback
from collections import OrderedDict

import requests

from ..loggers.logger import Logger
from ..utils import mask_fields_in_data

logger = Logger()


class Service:
    # extension optional
    request_base_url: str = ""
    mask_request_headers_fields: list = []
    mask_request_data_fields: list = []
    mask_response_headers_fields: list = []
    mask_response_data_fields: list = []

    class Request:
        # extension optional
        default_headers: dict = {}
        default_data: dict = {}
        default_json: dict = {}

        def __init__(
            self,
            url: str = "",
            parameters: dict | None = None,
            method: str = "GET",
            headers: dict | None = None,
            cookies: dict | None = None,
            data: dict | None = None,
            json: dict | None = None,
            files: dict | None = None,
            verify_ssl: bool = True,
        ) -> None:
            """
            data and json are mutually exclusive parameters
            data can accept any Content-Type header
            json will add the application/json Content-Type header
            """
            # apply default headers
            self.headers = self.default_headers.copy()
            self.headers.update({} if headers is None else headers)

            # apply default data and json
            if isinstance(data, dict):
                self.data = self.default_data.copy()
                self.data.update({} if data is None else data)
            else:
                self.data = data  # type: ignore

            if isinstance(json, dict):
                self.json = self.default_json.copy()
                self.json.update({} if json is None else json)
            else:
                self.json = json  # type: ignore

            # defaults
            self.parameters = {} if parameters is None else parameters
            self.cookies = {} if cookies is None else cookies
            self.files = {} if files is None else files

            self.url = url
            self.method = method
            self.verify_ssl = verify_ssl

    class Response:
        def __init__(
            self,
            status_code: int = 400,
            headers: dict | None = None,
            cookies: dict | None = None,
            data: dict | None = None,
        ) -> None:
            # defaults
            self.headers = {} if headers is None else headers
            self.cookies = {} if cookies is None else cookies
            self.data = {} if data is None else data

            self.status_code = status_code

    def __init__(self, *args, **kwargs) -> None:
        pass

    def request(self, *args, **kwargs) -> Response:
        return self.invoke(self.Request(*args, **kwargs))

    def invoke(self, request: Request) -> Response:
        logger.debug(f"{self.__class__.__name__}.invoke", priority=2)
        self.log_request(request)

        # open all files before sending them
        opened_request_files = OrderedDict()
        for key, file in request.files.items():
            opened_request_files[key] = open(file, "rb")

        try:
            http_response = requests.request(
                url=self.request_base_url + request.url,
                params=request.parameters,
                method=request.method,
                headers=request.headers,
                cookies=request.cookies,
                data=request.data,
                json=request.json,
                files=opened_request_files,
                verify=request.verify_ssl,
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

    def log_request(self, request: Request) -> None:
        logger.debug(f"{self.__class__.__name__}.invoke - Request", priority=3)
        self.log_request_url(request)
        self.log_request_method(request)
        self.log_request_headers(request)
        self.log_request_cookies(request)
        self.log_request_data(request)

    def log_request_url(self, request: Request) -> None:
        logger.debug(f"request.url: {self.request_base_url + request.url}")

    def log_request_method(self, request: Request) -> None:
        logger.debug(f"request.method: {request.method}")

    def log_request_headers(self, request: Request) -> None:
        if request.headers:
            logger.debug(f"request.headers: {mask_fields_in_data(request.headers, self.mask_request_headers_fields)}")

    def log_request_cookies(self, request: Request) -> None:
        if request.cookies:
            logger.debug(f"request.cookies: {request.cookies}")

    def log_request_data(self, request: Request) -> None:
        if request.method != "GET":
            if request.data:
                logger.debug(f"request.data: {mask_fields_in_data(request.data, self.mask_request_data_fields)}")
            elif request.json:
                logger.debug(f"request.json: {mask_fields_in_data(request.json, self.mask_request_data_fields)}")

    def log_response(self, response: Response) -> None:
        logger.debug(f"{self.__class__.__name__}.invoke - Response", priority=3)
        self.log_response_status_code(response)
        self.log_response_headers(response)
        self.log_response_cookies(response)
        self.log_response_data(response)

    def log_response_status_code(self, response: Response) -> None:
        logger.debug(f"response.status_code: {response.status_code}")

    def log_response_headers(self, response: Response) -> None:
        if response.headers:
            logger.debug(f"response.headers: {mask_fields_in_data(response.headers, self.mask_response_headers_fields)}")

    def log_response_cookies(self, response: Response) -> None:
        if response.cookies:
            logger.debug(f"response.cookies: {response.cookies}")

    def log_response_data(self, response: Response) -> None:
        if response.data:
            logger.debug(f"response.data: {mask_fields_in_data(response.data, self.mask_response_data_fields)}")
