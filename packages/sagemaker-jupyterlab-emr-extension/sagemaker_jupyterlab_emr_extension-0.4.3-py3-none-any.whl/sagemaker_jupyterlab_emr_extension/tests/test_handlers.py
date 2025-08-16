import json
import pytest
import asyncio
from datetime import datetime

from unittest.mock import ANY, Mock, patch, MagicMock
from ..handlers import register_handlers
from sagemaker_jupyterlab_emr_extension.schema.api_schema import (
    PersistentAppUiType,
)


@pytest.fixture
def jp_server_config(jp_template_dir):
    return {
        "ServerApp": {
            "jpserver_extensions": {"sagemaker_jupyterlab_emr_extension": True}
        },
    }


def test_mapping_added():
    mock_nb_app = Mock()
    mock_web_app = Mock()
    mock_nb_app.web_app = mock_web_app
    mock_web_app.settings = {"base_url": "nb_base_url"}
    register_handlers(mock_nb_app)
    mock_web_app.add_handlers.assert_called_once_with(".*$", ANY)


TEST_DESCRIBE_CLUSTER_RESPONSE = {
    "Cluster": {
        "Id": "string",
        "Applications": [
            {
                "Name": "myApp",
                "Version": "1.0",
                "Args": [
                    "string",
                ],
            }
        ],
        "ClusterArn": "someArn",
        "Name": "string",
        "KerberosAttributes": {
            "Realm": "testRealm",
            "KdcAdminPassword": "testPassword",
            "CrossRealmTrustPrincipalPassword": "testPass",
            "ADDomainJoinUser": "adoUser",
            "ADDomainJoinPassword": "adoPass",
        },
        "MasterPublicDnsName": "masterDns",
        "NormalizedInstanceHours": 123,
        "Status": {
            "State": "STARTING",
            "ErrorDetails": [],
            "Timeline": {
                "CreationDateTime": datetime(2015, 1, 1),
                "ReadyDateTime": datetime(2015, 1, 1),
                "EndDateTime": datetime(2015, 1, 1),
            },
        },
        "ReleaseLabel": "releaseLabel",
        "Configurations": {},
        "SecurityConfiguration": "securityConfig",
        "OutpostArn": "someOutPostArn",
    }
}


TEST_DESCRIBE_CLUSTER_RESPONSE_EMPTY = {"Cluster": {}}


TEST_LIST_CLUSTER_RESPONSE = {
    "Clusters": [
        {
            "Id": "string",
            "Name": "myCluster",
            "ClusterArn": "someArn",
            "Status": {
                "State": "STARTING",
                "Timeline": {
                    "CreationDateTime": datetime(2015, 1, 1),
                    "ReadyDateTime": datetime(2015, 1, 1),
                    "EndDateTime": datetime(2015, 1, 1),
                },
            },
            "NormalizedInstanceHours": 123,
        },
    ],
    "outpostArn": "someOutPostArn",
    "Marker": "mark1234",
}

appUiTypeList = [type.value for type in PersistentAppUiType]

TEST_DESCRIBE_PERSISTENT_APP_UI_RESPONSE = {
    "PersistentAppUI": {
        "PersistentAppUIId": "pId123",
        "PersistentAppUITypeList": appUiTypeList,
        "PersistentAppUIStatus": "ATTACHED",
        "CreationTime": "1696712723578.0",
        "LastModifiedTime": "1697742468972.0",
        "LastStateChangeReason": "some-reason",
        "Tags": [],
    }
}


class EmrClientMock:
    describe_cluster_response: any
    list_cluster_response: any

    def __init__(self, desrcibe_cluster_resp, list_cluster_resp):
        self.describe_cluster_response = desrcibe_cluster_resp
        self.list_cluster_response = list_cluster_resp

    async def describe_cluster(self, **kwargs):
        return self.describe_cluster_response

    async def list_clusters(self, **kwargs):
        return self.list_cluster_response

    async def list_instance_groups(self, **kwargs):
        return {
            "InstanceGroups": [
                {
                    "Id": "id1",
                    "Name": "name1",
                    "Market": "ON_DEMAND",
                    "InstanceGroupType": "MASTER",
                    "BidPrice": "string",
                    "InstanceType": "string",
                    "RequestedInstanceCount": 123,
                    "RunningInstanceCount": 123,
                    "Status": {"State": "PROVISIONING"},
                    "EbsOptimized": True | False,
                    "CustomAmiId": "string",
                },
            ],
            "Marker": "marker1",
        }


class PrivateEmrClientMock:
    async def create_persistent_app_ui(self, **kwargs):
        return {"PersistentAppUIId": "p-a123456789"}

    async def describe_persistent_app_ui(self, **kwargs):
        return TEST_DESCRIBE_PERSISTENT_APP_UI_RESPONSE

    async def get_persistent_app_ui_presigned_url(self, **kwargs):
        return {
            "PresignedURLReady": True,
            "PresignedURL": "https://j-a123123123.sagemaler.aws/presigned-url",
        }

    async def get_on_cluster_app_ui_presigned_url(self, **kwargs):
        return {
            "PresignedURLReady": True,
            "PresignedURL": "https://j-a123123123.sagemaler.aws/geton-cluster-presigned-url",
        }


@patch(
    "sagemaker_jupyterlab_emr_extension.handlers.DescribeClusterHandler.log",
    return_value="someInfoLog",
)
@patch("sagemaker_jupyterlab_emr_extension.handlers.get_emr_client")
async def test_describe_cluster_success(
    emr_client_mock,
    mock_logger,
    jp_fetch,
):
    emr_client_mock.return_value = EmrClientMock(
        TEST_DESCRIBE_CLUSTER_RESPONSE, TEST_LIST_CLUSTER_RESPONSE
    )
    kwargs = {"ClusterId": "c12345688"}
    response = await jp_fetch(
        "aws/sagemaker/api/emr/describe-cluster",
        method="POST",
        body=json.dumps(kwargs),
    )
    resp = json.loads(response.body.decode("utf-8"))
    assert resp == {
        "cluster": {
            "clusterArn": "someArn",
            "id": "string",
            "name": "string",
            "autoTerminate": None,
            "masterPublicDnsName": "masterDns",
            "normalizedInstanceHours": 123,
            "outpostArn": "someOutPostArn",
            "securityConfiguration": "securityConfig",
            "terminationProtected": None,
            "releaseLabel": "releaseLabel",
            "crossAccountArn": None,
            "applications": [{"name": "myApp", "version": "1.0", "args": ["string"]}],
            "configurations": [],
            "kerberosAttributes": {
                "aDDomainJoinPassword": "adoPass",
                "aDDomainJoinUser": "adoUser",
                "crossRealmTrustPrincipalPassword": "testPass",
                "kdcAdminPassword": "testPassword",
                "realm": "testRealm",
            },
            "status": {
                "state": "STARTING",
                "timeline": {"creationDateTime": "2015-01-01T00:00:00"},
            },
            "tags": [],
        }
    }


@pytest.mark.aysncio
@patch(
    "sagemaker_jupyterlab_emr_extension.handlers.DescribeClusterHandler.log",
    return_value="someInfoLog",
)
@patch("sagemaker_jupyterlab_emr_extension.handlers.get_emr_client")
async def test_describe_cluster_bad_request(
    emr_client_mock,
    mock_logger,
    jp_fetch,
):
    emr_client_mock.return_value = EmrClientMock(
        TEST_DESCRIBE_CLUSTER_RESPONSE, TEST_LIST_CLUSTER_RESPONSE
    )
    kwargs = {"cluster_id": "c12345688"}
    exception = None
    try:
        await jp_fetch(
            "aws/sagemaker/api/emr/describe-cluster",
            method="POST",
            body=json.dumps(kwargs),
        )
    except Exception as ex:
        exception = ex
    assert exception.code == 400


@pytest.mark.aysncio
@patch(
    "sagemaker_jupyterlab_emr_extension.handlers.DescribeClusterHandler.log",
    return_value="someInfoLog",
)
@patch("sagemaker_jupyterlab_emr_extension.handlers.get_emr_client")
async def test_describe_cluster_cluster_cofiguration_empty(
    emr_client_mock,
    mock_logger,
    jp_fetch,
):
    emr_client_mock.return_value = EmrClientMock(
        TEST_DESCRIBE_CLUSTER_RESPONSE_EMPTY, TEST_LIST_CLUSTER_RESPONSE
    )
    kwargs = {"ClusterId": "c12345688"}
    response = await jp_fetch(
        "aws/sagemaker/api/emr/describe-cluster",
        method="POST",
        body=json.dumps(kwargs),
    )
    resp = json.loads(response.body.decode("utf-8"))
    assert resp == {"errorMessage": "Cluster is undefined"}


@patch(
    "sagemaker_jupyterlab_emr_extension.handlers.ListClustersHandler.log",
    return_value="someInfoLog",
)
@patch("sagemaker_jupyterlab_emr_extension.handlers.get_emr_client")
async def test_list_cluster_success(
    emr_client_mock,
    mock_logger,
    jp_fetch,
):
    emr_client_mock.return_value = EmrClientMock(
        TEST_DESCRIBE_CLUSTER_RESPONSE, TEST_LIST_CLUSTER_RESPONSE
    )
    kwargs = {}
    response = await jp_fetch(
        "/aws/sagemaker/api/emr/list-clusters",
        method="POST",
        body=json.dumps(kwargs),
    )
    resp = json.loads(response.body.decode("utf-8"))
    assert resp == {
        "clusters": [
            {
                "clusterArn": "someArn",
                "id": "string",
                "name": "myCluster",
                "status": {
                    "state": "STARTING",
                    "timeline": {"creationDateTime": "2015-01-01T00:00:00"},
                },
                "normalizedInstanceHours": 123,
            }
        ],
        "Marker": "mark1234",
    }


@patch(
    "sagemaker_jupyterlab_emr_extension.handlers.CreatePersistentAppUiHandler.log",
    return_value="someInfoLog",
)
@patch("sagemaker_jupyterlab_emr_extension.handlers.get_emrprivate_client")
async def test_create_persistent_app_ui_success(
    emrprivate_client_mock,
    mock_logger,
    jp_fetch,
):
    emrprivate_client_mock.return_value = PrivateEmrClientMock()
    kwargs = {"TargetResourceArn": "someResourceArn"}
    response = await jp_fetch(
        "/aws/sagemaker/api/emr/create-persistent-app-ui",
        method="POST",
        body=json.dumps(kwargs),
    )
    resp = json.loads(response.body.decode("utf-8"))
    assert resp == {
        "persistentAppUIId": "p-a123456789",
        "roleArn": None,
    }


@patch(
    "sagemaker_jupyterlab_emr_extension.handlers.GetPersistentAppUiPresignedUrlHandler.log",
    return_value="someInfoLog",
)
@patch("sagemaker_jupyterlab_emr_extension.handlers.get_emrprivate_client")
async def test_get_persistent_app_ui_presigned_url_success(
    emrprivate_client_mock,
    mock_logger,
    jp_fetch,
):
    emrprivate_client_mock.return_value = PrivateEmrClientMock()
    kwargs = {
        "PersistentAppUIId": "p-a123456789",
        "PersistentAppUIType": "test-type",
        "ClusterId": "testClusterId",
    }
    response = await jp_fetch(
        "/aws/sagemaker/api/emr/get-persistent-app-ui-presigned-url",
        method="POST",
        body=json.dumps(kwargs),
    )
    resp = json.loads(response.body.decode("utf-8"))
    assert resp == {
        "presignedURLReady": True,
        "presignedURL": "https://j-a123123123.sagemaler.aws/presigned-url",
    }


@patch(
    "sagemaker_jupyterlab_emr_extension.handlers.GetOnClustersAppUiPresignedUrlHandler.log",
    return_value="someInfoLog",
)
@patch("sagemaker_jupyterlab_emr_extension.handlers.get_emrprivate_client")
async def test_get_on_cluster_app_ui_presigned_url_success(
    emrprivate_client_mock,
    mock_logger,
    jp_fetch,
):
    emrprivate_client_mock.return_value = PrivateEmrClientMock()
    kwargs = {
        "ClusterId": "c1234567789",
        "OnClusterAppUIType": "ApplicationMaster",
        "ApplicationId": "appId",
    }
    response = await jp_fetch(
        "/aws/sagemaker/api/emr/get-on-cluster-app-ui-presigned-url",
        method="POST",
        body=json.dumps(kwargs),
    )
    resp = json.loads(response.body.decode("utf-8"))
    assert resp == {
        "presignedURLReady": True,
        "presignedURL": "https://j-a123123123.sagemaler.aws/geton-cluster-presigned-url",
    }


@patch(
    "sagemaker_jupyterlab_emr_extension.handlers.DescribePersistentAppUiHandler.log",
    return_value="someInfoLog",
)
@patch("sagemaker_jupyterlab_emr_extension.handlers.get_emrprivate_client")
async def test_describe_persistent_app_ui_success(
    emrprivate_client_mock,
    mock_logger,
    jp_fetch,
):
    emrprivate_client_mock.return_value = PrivateEmrClientMock()
    kwargs = {"PersistentAppUIId": "p-a123456789"}
    response = await jp_fetch(
        "/aws/sagemaker/api/emr/describe-persistent-app-ui",
        method="POST",
        body=json.dumps(kwargs),
    )
    resp = json.loads(response.body.decode("utf-8"))
    assert resp == {
        "persistentAppUI": {
            "persistentAppUIId": "pId123",
            "persistentAppUITypeList": ["SHS", "TEZUI", "YTS"],
            "persistentAppUIStatus": "ATTACHED",
            "creationTime": "1696712723578.0",
            "lastModifiedTime": "1697742468972.0",
            "lastStateChangeReason": "some-reason",
            "tags": [],
        },
        "roleArn": None,
    }


@patch(
    "sagemaker_jupyterlab_emr_extension.handlers.ListInstanceGroupsHandler.log",
    return_value="someInfoLog",
)
@patch("sagemaker_jupyterlab_emr_extension.handlers.get_emr_client")
async def test_list_instance_groups_success(
    emr_client_mock,
    mock_logger,
    jp_fetch,
):
    emr_client_mock.return_value = EmrClientMock(
        TEST_DESCRIBE_CLUSTER_RESPONSE, TEST_LIST_CLUSTER_RESPONSE
    )
    kwargs = {"ClusterId": "c12345688"}
    response = await jp_fetch(
        "/aws/sagemaker/api/emr/list-instance-groups",
        method="POST",
        body=json.dumps(kwargs),
    )
    resp = json.loads(response.body.decode("utf-8"))
    assert resp == {
        "instanceGroups": [
            {
                "id": "id1",
                "name": "name1",
                "instanceType": "string",
                "instanceGroupType": "MASTER",
                "requestedInstanceCount": 123,
                "runningInstanceCount": 123,
            }
        ],
        "Marker": "marker1",
    }


@pytest.mark.aysncio
@patch(
    "sagemaker_jupyterlab_emr_extension.handlers.ListInstanceGroupsHandler.log",
    return_value="someInfoLog",
)
@patch("sagemaker_jupyterlab_emr_extension.handlers.get_emr_client")
async def test_list_instance_groups_bad_request(
    emr_client_mock,
    mock_logger,
    jp_fetch,
):
    emr_client_mock.return_value = EmrClientMock(
        TEST_DESCRIBE_CLUSTER_RESPONSE, TEST_LIST_CLUSTER_RESPONSE
    )
    kwargs = {}
    exception = None
    try:
        await jp_fetch(
            "/aws/sagemaker/api/emr/list-instance-groups",
            method="POST",
            body=json.dumps(kwargs),
        )
    except Exception as ex:
        exception = ex
    assert exception.code == 400
