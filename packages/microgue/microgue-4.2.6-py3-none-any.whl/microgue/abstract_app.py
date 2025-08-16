import json
import traceback
from .constants.error_constants import ErrorConstants
from flask import Flask, request, g
from .loggers.logger import Logger
from .security.generic import is_allowed_by_all
from werkzeug.exceptions import Unauthorized, Forbidden, NotFound, MethodNotAllowed
from .utils import JSONResponse, mask_fields_in_data

logger = Logger()


class AbstractApp:
    app = None
    views = []
    blueprints = []
    mask_request_headers_fields = []
    mask_request_data_fields = []
    mask_response_headers_fields = []
    mask_response_data_fields = []

    def __init__(self):
        self.create_app()
        self.register_index()
        self.register_views()
        self.register_blueprints()
        self.register_before_request_handler()
        self.register_after_request_handler()
        self.register_error_handlers()

    def create_app(self):
        self.app = Flask(__name__)
        self.app.url_map.strict_slashes = False

    def register_index(self):
        @self.app.route("/", methods=["GET"])
        @is_allowed_by_all
        def index():
            return JSONResponse({"message": "success"}, status=200)

    def register_views(self):
        for view in self.views:
            view.register(self.app)

    def register_blueprints(self):
        for blueprint in self.blueprints:
            self.app.register_blueprint(blueprint)

    def register_before_request_handler(self):
        self.app.before_request(self.before_request_handler)

    @classmethod
    def before_request_handler(cls):
        # mask request header fields
        try:
            request_headers = mask_fields_in_data(
                dict(request.headers),
                cls.mask_request_headers_fields
            )
        except:  # noqa
            request_headers = {}

        # mask request data fields
        try:
            request_data = mask_fields_in_data(
                json.loads(request.data.decode("utf-8")),
                cls.mask_request_data_fields
            )
        except:  # noqa
            request_data = {}

        logger.debug("Request Received", priority=1)
        logger.debug(f"method: {request.method}")
        logger.debug(f"url: {request.url}")
        logger.debug(f"headers: {request_headers}")
        logger.debug(f"body: {request_data}")

    def register_after_request_handler(self):
        self.app.after_request(self.after_request_handler)

    @classmethod
    def after_request_handler(cls, response):
        if not g.get("authenticated") and int(response.status_code) < 400:
            response = JSONResponse(json.dumps({"error": ErrorConstants.App.UNABLE_TO_AUTHENTICATE}), status=401)

        # mask response header fields
        try:
            response_headers = {key: value for key, value in response.headers.items()}
            response_headers = mask_fields_in_data(response_headers, cls.mask_response_headers_fields)
        except:  # noqa
            response_headers = {}

        # mask response data fields
        try:
            response_data = json.loads(response.response[0].decode("utf-8"))
            response_data = mask_fields_in_data(response_data, cls.mask_response_data_fields)
        except:  # noqa
            response_data = {}

        logger.debug("Response Sent", priority=1)
        logger.debug(f"status: {response.status}")
        logger.debug(f"headers: {response_headers}")
        logger.debug(f"body: {response_data}")

        return response

    def register_error_handlers(self):
        self.register_unauthorized_error()
        self.register_forbidden_error()
        self.register_not_found_error()
        self.register_method_not_allowed_error()
        self.register_internal_server_error()

    def register_unauthorized_error(self):
        self.app.register_error_handler(Unauthorized, self.unauthorized_error)

    @staticmethod
    def unauthorized_error(e):
        logger.debug("Authentication Error", priority=1)
        logger.debug(f"{e.__class__.__name__}: {e}")
        return JSONResponse({"error": ErrorConstants.App.UNABLE_TO_AUTHENTICATE}, status=401)

    def register_forbidden_error(self):
        self.app.register_error_handler(Forbidden, self.forbidden_error)

    @staticmethod
    def forbidden_error(e):
        logger.debug("Authorization Error", priority=1)
        logger.debug(f"{e.__class__.__name__}: {e}")
        return JSONResponse({"error": ErrorConstants.App.UNABLE_TO_AUTHORIZE}, status=403)

    def register_not_found_error(self):
        self.app.register_error_handler(NotFound, self.not_found_error)

    @staticmethod
    def not_found_error(e):
        logger.debug("Not Found Error", priority=1)
        logger.debug(f"{e.__class__.__name__}: {e}")
        return JSONResponse({"error": ErrorConstants.App.REQUESTED_URL_NOT_FOUND}, status=404)

    def register_method_not_allowed_error(self):
        self.app.register_error_handler(MethodNotAllowed, self.method_not_allowed_error)

    @staticmethod
    def method_not_allowed_error(e):
        logger.debug("Method Not Allowed Error", priority=1)
        logger.debug(f"{e.__class__.__name__}: {e}")
        return JSONResponse({"error": ErrorConstants.App.METHOD_NOT_ALLOWED}, status=405)

    def register_internal_server_error(self):
        self.app.register_error_handler(Exception, self.internal_server_error)

    @staticmethod
    def internal_server_error(e):
        logger.error("Internal Server Error", priority=1)
        logger.error(f"{e.__class__.__name__}: {e}")
        logger.error(traceback.format_exc())
        return JSONResponse({"error": ErrorConstants.App.INTERNAL_SERVER_ERROR}, status=500)
