import logging


def handle_endpoint_connection_error(error, error_message):
    """Handle Boto EndpointConnectionError."""
    logging.error("{} {}".format(error_message, traceback.format_exc()))
    # TODO: exact error message to be updated after PM sign off.
    raise ConnectionError(
        "{}. Please check your network settings or contact support for assistance.".format(
            error_message
        )
    ) from error
