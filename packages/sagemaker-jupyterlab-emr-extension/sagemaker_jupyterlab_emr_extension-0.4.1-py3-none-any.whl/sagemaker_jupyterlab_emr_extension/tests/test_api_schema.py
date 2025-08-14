import unittest
import jsonschema
import pytest
from jsonschema.exceptions import ValidationError

from sagemaker_jupyterlab_emr_extension.schema.api_schema import (
    describe_cluster_request_schema,
    list_cluster_request_schema,
    create_presistent_app_ui_schema,
    get_on_cluster_app_ui_presigned_url_schema,
    get_persistent_app_ui_presigned_url_schema,
    describe_persistent_app_ui_schema,
)


class TestAPISchema(unittest.TestCase):
    def test_describe_cluster_missing_cluster_id(self):
        describe_cluster_request = {}
        with pytest.raises(ValidationError):
            jsonschema.validate(
                describe_cluster_request, describe_cluster_request_schema
            )

    def test_valid_describe_cluster_request_success(self):
        describe_cluster_request = {"ClusterId": "c1229393"}
        val = jsonschema.validate(
            describe_cluster_request, describe_cluster_request_schema
        )
        assert val == None

    def test_list_cluster_raise_no_exception(self):
        list_cluster_request = {}
        val = jsonschema.validate(list_cluster_request, list_cluster_request_schema)
        assert val == None

    def test_create_persistent_app_ui_missing_target_resource_arn(self):
        create_presistent_request = {}
        with pytest.raises(ValidationError):
            jsonschema.validate(
                create_presistent_request, create_presistent_app_ui_schema
            )

    def test_valid_create_persistent_app_ui_request_success(self):
        create_presistent_request = {"TargetResourceArn": "someArn"}
        val = jsonschema.validate(
            create_presistent_request, create_presistent_app_ui_schema
        )
        assert val == None

    def test_describe_persistent_app_ui_missing_persistentAppUiId(self):
        describe_persistent_app_ui_request = {}
        with pytest.raises(ValidationError):
            jsonschema.validate(
                describe_persistent_app_ui_request, describe_persistent_app_ui_schema
            )

    def test_valid_describe_persistent_app_ui_request_success(self):
        describe_persistent_app_ui_request = {"PersistentAppUIId": "p-123456789"}
        val = jsonschema.validate(
            describe_persistent_app_ui_request, describe_persistent_app_ui_schema
        )
        assert val == None

    def test_get_on_cluster_app_ui_presigned_url_missing_clusterId(self):
        get_on_cluster_app_ui_presigned_request = {}
        with pytest.raises(ValidationError):
            jsonschema.validate(
                get_on_cluster_app_ui_presigned_request,
                get_on_cluster_app_ui_presigned_url_schema,
            )

    def test_valid_get_on_cluster_app_ui_presigned_url_reequest_success(self):
        get_on_cluster_app_ui_presigned_request = {
            "ClusterId": "cid120102",
            "OnClusterAppUIType": "ApplicationMaster",
            "ApplicationId": "appId",
        }
        val = jsonschema.validate(
            get_on_cluster_app_ui_presigned_request,
            get_on_cluster_app_ui_presigned_url_schema,
        )
        assert val == None

    def test_get_persistent_app_ui_presigned_url_missing_persistentAppUIId(self):
        get_persistent_app_ui_presigned_request = {}
        with pytest.raises(ValidationError):
            jsonschema.validate(
                get_persistent_app_ui_presigned_request,
                get_persistent_app_ui_presigned_url_schema,
            )

    def test_valid_get_persistent_app_ui_presigned_url_persistentAppUIId_success(self):
        get_persistent_app_ui_presigned_request = {"PersistentAppUIId": "c12767848"}
        val = jsonschema.validate(
            get_persistent_app_ui_presigned_request,
            get_persistent_app_ui_presigned_url_schema,
        )
        assert val == None

    def test_describe_cluster_invalid_parameter_failure(self):
        describe_cluster_request = {"cluster_id": "c12344678"}
        with pytest.raises(ValidationError):
            jsonschema.validate(
                describe_cluster_request, describe_cluster_request_schema
            )

    def test_list_clusters_invalid_optional_parameter_success(self):
        list_cluster_request = {"CreatedAfter": "2015-01-01T:00:00:000"}
        val = jsonschema.validate(list_cluster_request, list_cluster_request_schema)
        assert val == None

    def test_list_clusters_invalid_enun_parameter_for_state_failure(self):
        list_cluster_request = {"ClusterStates": ["INVALID"]}
        with pytest.raises(ValidationError):
            jsonschema.validate(list_cluster_request, list_cluster_request_schema)
