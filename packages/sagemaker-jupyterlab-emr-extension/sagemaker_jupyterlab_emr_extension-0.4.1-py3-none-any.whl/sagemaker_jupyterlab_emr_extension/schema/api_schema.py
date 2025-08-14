from enum import Enum


class ClusterStateEnum(Enum):
    """
    Cluster State Status type enum
    """

    STARTING = "STARTING"
    BOOTSTRAPPING = "BOOTSTRAPPING"
    RUNNING = "RUNNING"
    WAITING = "WAITING"
    TERMINATING = "TERMINATING"
    TERMINATED = "TERMINATED"
    TERMINATED_WITH_ERRORS = "TERMINATED_WITH_ERRORS"
    UNDEFINED = "UNDEFINED"


class PersistentAppUiType(Enum):
    """Enum for PersistentAppUi Type"""

    SHS = "SHS"
    TEZUI = "TEZUI"
    YTS = "YTS"


describe_cluster_request_schema = {
    "type": "object",
    "properties": {
        "ClusterId": {"type": "string"},
        "RoleArn": {"type": "string"},
    },
    "required": ["ClusterId"],
    "additionalProperties": False,
}


list_cluster_request_schema = {
    "type": "object",
    "properties": {
        "CreatedAfter": {"type": "string"},
        "CreatedBefore": {"type": "string"},
        "Marker": {"type": "string"},
        "ClusterStates": {
            "type": "array",
            "items": {"enum": [m.value for m in ClusterStateEnum]},
        },
        "RoleArn": {"type": "string"},
    },
    "additionalProperties": False,
}

get_on_cluster_app_ui_presigned_url_schema = {
    "type": "object",
    "properties": {
        "ClusterId": {"type": "string"},
        "OnClusterAppUIType": {"type": "string"},
        "ApplicationId": {"type": "string"},
        "AccountId": {"type": "string"},
        "RoleArn": {"type": "string"},
    },
    "required": ["ClusterId", "OnClusterAppUIType", "ApplicationId"],
    "additionalProperties": False,
}


create_presistent_app_ui_schema = {
    "type": "object",
    "properties": {
        "TargetResourceArn": {"type": "string"},
        "EmrContainersConfig": {"$ref": "#/$defs/EMRContainersConfig"},
        "XReferer": {"type": "string"},
        "Tags": {"type": "array", "items": {"$ref": "#/$defs/InputTag"}},
        "AccountId": {"type": "string"},
        "RoleArn": {"type": "string"},
    },
    "required": ["TargetResourceArn"],
    "additionalProperties": False,
    "$defs": {
        "InputTag": {
            "type": "object",
            "properties": {
                "Key": {"type": "string"},
                "Valye": {"type": "string"},
            },
        },
        "EMRContainersConfig": {
            "type": "object",
            "properties": {"JobRunId": {"type": "string"}},
        },
    },
}

describe_persistent_app_ui_schema = {
    "type": "object",
    "properties": {
        "PersistentAppUIId": {"type": "string"},
        "ClusterId": {"type": "string"},
        "AccountId": {"type": "string"},
        "RoleArn": {"type": "string"},
    },
    "required": ["PersistentAppUIId"],
    "additionalProperties": False,
}


get_persistent_app_ui_presigned_url_schema = {
    "type": "object",
    "properties": {
        "PersistentAppUIId": {"type": "string"},
        "PersistentAppUIType": {"type": "string"},
        "ClusterId": {"type": "string"},
        "ApplicationId": {"type": "string"},
        "AccountId": {"type": "string"},
        "RoleArn": {"type": "string"},
    },
    "required": ["PersistentAppUIId"],
    "additionalProperties": False,
}

list_instance_groups_schema = {
    "type": "object",
    "properties": {
        "ClusterId": {"type": "string"},
        "Marker": {"type": "string"},
        "RoleArn": {"type": "string"},
    },
    "required": ["ClusterId"],
    "additionalProperties": False,
}

describe_security_configuration_schema = {
    "type": "object",
    "properties": {
        "ClusterId": {"type": "string"},
        "RoleArn": {"type": "string"},
        "SecurityConfigurationName": {"type": "string"},
    },
    "required": ["SecurityConfigurationName"],
    "additionalProperties": False,
}
