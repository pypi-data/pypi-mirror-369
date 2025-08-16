from enum import Enum


class ServerlessApplicationStateEnum(Enum):
    """
    Application State type enum
    """

    STARTING = "STARTING"
    CREATING = "CREATING"
    STOPPING = "STOPPING"
    STARTED = "STARTED"
    CREATED = "CREATED"
    STOPPED = "STOPPED"
    TERMINATED = "TERMINATED"
    UNDEFINED = "UNDEFINED"


list_serverless_applications_request_schema = {
    "type": "object",
    "properties": {
        "nextToken": {"type": "string"},
        "states": {
            "type": "array",
            "items": {"enum": [m.value for m in ServerlessApplicationStateEnum]},
        },
        "roleArn": {"type": "string"},
    },
    "additionalProperties": False,
}

get_serverless_application_request_schema = {
    "type": "object",
    "properties": {
        "applicationId": {"type": "string"},
        "RoleArn": {"type": "string"},
    },
    "required": ["applicationId"],
    "additionalProperties": False,
}
