import traceback
import json

from sagemaker_jupyterlab_extension_common.logging.logging_utils import HandlerLogMixin
from sagemaker_jupyterlab_emr_extension.utils.logging_utils import EmrErrorHandler
from jupyter_server.base.handlers import JupyterHandler

from sagemaker_jupyterlab_emr_extension._version import __version__ as ext_version

EXTENSION_NAME = "sagemaker_jupyterlab_emr_extension"
EXTENSION_VERSION = ext_version


class BaseEmrHandler(HandlerLogMixin, JupyterHandler):
    # Do not rename or change the variable names, these are used by
    # loggers in common package.
    jl_extension_name = EXTENSION_NAME
    jl_extension_version = EXTENSION_VERSION

    async def _handle_http_error(self, error):
        """Handle HTTP error"""
        message = error.log_message
        self.log.error(message)
        self.set_status(error.status_code)

        if error.status_code == 400:
            reply = dict(message="Invalid JSON in request", reason=error.reason)
        else:
            reply = dict(message=message, reason=error.reason)
        self.finish(json.dumps(reply))

    async def _handle_validation_error(self, _, body, component):
        """Handle parameter validation and JSON schema validation error"""
        self.log.error(
            "Invalid request {} {}".format(body, traceback.format_exc()),
            extra={"Component": component},
        )
        self.set_status(400)
        self.finish(
            json.dumps({"errorMessage": "Invalid request missing or wrong input"})
        )

    async def _handle_client_error(self, error, component):
        """Handle boto client errors"""
        error_code = error.response.get("Error", {}).get("Code", "UnknownError")

        if error_code == "AccessDeniedException":
            self.log.warning(
                f"Access denied for {component}. Returning empty response.",
                extra={"Component": component},
            )
            self.set_status(403)
            self.finish(
                json.dumps(
                    {
                        "errorMessage": "Access denied. You may not have sufficient permissions."
                    }
                )
            )
            return

        self.log.error(
            "SdkClientError {}".format(traceback.format_exc()),
            extra={"Component": component},
        )
        msg = EmrErrorHandler.get_boto_error(error)
        self.set_status(msg.get("http_code"))
        self.finish(json.dumps({"errorMessage": msg.get("message")}))

    async def _handle_connection_error(self, error, component):
        """Handle endpoint connection error"""
        self.log.error(
            "{} {}".format(str(error), traceback.format_exc()),
            extra={"Component": component},
        )
        self.set_status(503)
        # TODO: exact error message to be updated after PM sign off.
        self.finish(
            json.dumps(
                {
                    "errorMessage": "{} Please check your network settings or contact support for assistance.".format(
                        str(error)
                    )
                }
            )
        )

    async def _handle_connection_timeout_error(self, error_message, component):
        """Handle connection timeout error"""
        self.log.error(
            "SdkConnectError {}".format(traceback.format_exc()),
            extra={"Component": component},
        )
        self.set_status(400)
        self.finish(json.dumps(error_message))

    async def _handle_error(self, error, component):
        """Default exception handling"""
        self.log.error(
            "Internal Service Error: {}".format(traceback.format_exc()),
            extra={"Component": component},
        )
        self.set_status(500)
        self.finish(json.dumps({"errorMessage": str(error)}))
