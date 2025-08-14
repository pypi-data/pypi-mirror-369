import pytest
import asyncio
from typing import Dict
from unittest.mock import Mock, MagicMock, patch

from sagemaker_jupyterlab_emr_extension.clients import (
    EMRAsyncBoto3Client,
    PrivateEMRAsyncBoto3Client,
)


def get_future_results(result):
    future = asyncio.Future()
    future.set_result(result)
    return future


def mock_emr_client(method_mock: Dict) -> (Mock, Mock):
    emr_client = EMRAsyncBoto3Client("us-west-2", "aws")
    inner_client = Mock(**method_mock)
    emr_client.sess = Mock(
        **{
            "create_client.return_value": MagicMock(
                **{"__aenter__.return_value": inner_client}
            )
        }
    )
    return emr_client, inner_client


def mock_emrprivate_client(method_mock: Dict) -> (Mock, Mock):
    emrprivate_client = PrivateEMRAsyncBoto3Client(
        "us-west-2", "aws", "MODEL_DATA_PATH"
    )
    inner_client = Mock(**method_mock)
    emrprivate_client.sess = Mock(
        **{
            "create_client.return_value": MagicMock(
                **{"__aenter__.return_value": inner_client}
            )
        }
    )
    return emrprivate_client, inner_client


TEST_DESCRIBE_CLUSTER_RESPONSE = {
    "Cluster": {
        "Id": "string",
        "applications": ["Application1"],
        "clusterArn": "someArn",
        "Name": "string",
        "kerberosAttributes": {},
        "masterPublicDnsName": "masterDns",
        "normalizedInstanceHours": 123,
        "Status": {"State": "STARTING", "ErrorDetails": []},
        "releaseLabel": "releaseLabel",
        "configurations": {},
        "securityConfiguration": "securityConfig",
        "outpostArn": "someOutPostArn",
    }
}


TEST_LIST_CLUSTER_RESPONSE = {
    "Clusters": [
        {
            "Id": "string",
            "Name": "string",
            "Status": {
                "State": "STARTING",
                "Timeline": {
                    "CreationDateTime": "2015-01-01 00:00:00",
                },
                "ErrorDetails": [],
            },
            "NormalizedInstanceHours": 123,
        },
    ],
    "Marker": "string",
}

TEST_LIST_INSTANCE_GROUP_RESPONSE = {
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


@pytest.mark.asyncio
async def test_describe_cluster():
    # Given
    emr_client, inner_client = mock_emr_client(
        {
            "describe_cluster.return_value": get_future_results(
                TEST_DESCRIBE_CLUSTER_RESPONSE
            )
        }
    )

    # When
    request = {"ClusterId": "id120202020"}
    result = await emr_client.describe_cluster(**request)

    # Then
    emr_client.sess.create_client.assert_called_with(
        service_name="emr", config=emr_client.cfg, region_name="us-west-2"
    )
    inner_client.describe_cluster.assert_called_with(**request)
    assert result == TEST_DESCRIBE_CLUSTER_RESPONSE


@pytest.mark.asyncio
async def test_describe_cluster_missing_cluster_id_failure():
    # Given
    emr_client, inner_client = mock_emr_client(
        {
            "describe_cluster.return_value": get_future_results(
                TEST_DESCRIBE_CLUSTER_RESPONSE
            )
        }
    )

    # When
    request = {}
    exception = None
    try:
        result = await emr_client.describe_cluster(**request)
    except Exception as ex:
        exception = ex

    # Then
    assert not emr_client.sess.create_client.called
    assert not inner_client.describe_cluster.called
    assert exception.__class__.__name__ == "ValueError"


@pytest.mark.asyncio
async def test_list_clusters_no_args_success():
    # Given
    emr_client, inner_client = mock_emr_client(
        {"list_clusters.return_value": get_future_results(TEST_LIST_CLUSTER_RESPONSE)}
    )

    # When
    result = await emr_client.list_clusters()

    # Then
    emr_client.sess.create_client.assert_called_with(
        service_name="emr", config=emr_client.cfg, region_name="us-west-2"
    )
    inner_client.list_clusters.assert_called_with()
    assert result == TEST_LIST_CLUSTER_RESPONSE


@pytest.mark.asyncio
async def test_list_clusters_all_args_success():
    # Given
    emr_client, inner_client = mock_emr_client(
        {"list_clusters.return_value": get_future_results(TEST_LIST_CLUSTER_RESPONSE)}
    )

    # When
    request = {
        "CreatedAfter": "2015-01-01 00:00:00",
        "CreatedBefore": "2018-01-01 00:00:00",
        "ClusterStates": ["RUNNING"],
        "Marker": "45790087",
    }
    result = await emr_client.list_clusters(**request)

    # Then
    emr_client.sess.create_client.assert_called_with(
        service_name="emr", config=emr_client.cfg, region_name="us-west-2"
    )
    inner_client.list_clusters.assert_called_with(**request)
    assert result == TEST_LIST_CLUSTER_RESPONSE


@pytest.mark.asyncio
async def test_list_instance_groups():
    # Given
    emr_client, inner_client = mock_emr_client(
        {
            "list_instance_groups.return_value": get_future_results(
                TEST_LIST_INSTANCE_GROUP_RESPONSE
            )
        }
    )

    # When
    request = {"ClusterId": "id120202020"}
    result = await emr_client.list_instance_groups(**request)

    # Then
    emr_client.sess.create_client.assert_called_with(
        service_name="emr", config=emr_client.cfg, region_name="us-west-2"
    )
    inner_client.list_instance_groups.assert_called_with(**request)
    assert result == TEST_LIST_INSTANCE_GROUP_RESPONSE


""""
===============  Private client tests ===============
"""


@pytest.mark.asyncio
async def test_get_persistent_app_ui_presigned_url():
    # Given
    private_emr_client, inner_client = mock_emrprivate_client(
        {
            "get_persistent_app_ui_presigned_url.return_value": get_future_results(
                {
                    "presignedURLReady": True,
                    "presignedURL": "https://d0hkekkdasd.sagemaker.presigned/url/",
                },
            )
        }
    )

    request = {
        "PersistentAppUIId": "p-1234567890",
        "PersistentAppUIType": "SHS",
        "ApplicationId": "applicationId",
    }
    # When
    result = await private_emr_client.get_persistent_app_ui_presigned_url(**request)

    # Then
    private_emr_client.sess.create_client.assert_called_with(
        service_name="emrprivate",
        config=private_emr_client.cfg,
        region_name="us-west-2",
    )
    inner_client.get_persistent_app_ui_presigned_url.assert_called_with(**request)
    assert result == {
        "presignedURLReady": True,
        "presignedURL": "https://d0hkekkdasd.sagemaker.presigned/url/",
    }


@pytest.mark.asyncio
async def test_get_persistent_app_ui_presigned_url_missing_app_id_failure():
    # Given
    private_emr_client, inner_client = mock_emrprivate_client(
        {
            "get_persistent_app_ui_presigned_url.return_value": get_future_results(
                {
                    "presignedURLReady": True,
                    "presignedURL": "https://d0hkekkdasd.sagemaker.presigned/url/",
                },
            )
        }
    )

    request = {
        "PersistentAppUIType": "SHS",
        "ApplicationId": "applicationId",
    }
    exception = None
    # When
    try:
        result = await private_emr_client.get_persistent_app_ui_presigned_url(**request)
    except Exception as ex:
        exception = ex

    # Then
    assert not private_emr_client.sess.create_client.called
    assert not inner_client.get_persistent_app_ui_presigned_url.called
    assert exception.__class__.__name__ == "ValueError"


@pytest.mark.asyncio
async def test_describe_persistent_app_ui():
    # Given
    private_emr_client, inner_client = mock_emrprivate_client(
        {
            "describe_persistent_app_ui.return_value": get_future_results(
                {
                    "PersistentAppUI": {
                        "PersistentAppUIId": "p-1234567890",
                        "PersistentAppUITypeList": ["SHS", "TEZUI", "YTS"],
                        "PersistentAppUIStatus": "ATTACHED",
                        "CreationTime": "1696712723578.0",
                        "LastModifiedTime": "1697742468972.0",
                        "LastStateChangeReason": "Reason",
                        "Tags": [],
                    },
                }
            )
        }
    )

    request = {"PersistentAppUIId": "p-1234567890"}
    # When
    result = await private_emr_client.describe_persistent_app_ui(**request)

    # Then
    private_emr_client.sess.create_client.assert_called_with(
        service_name="emrprivate",
        config=private_emr_client.cfg,
        region_name="us-west-2",
    )
    inner_client.describe_persistent_app_ui.assert_called_with(**request)
    assert result == {
        "PersistentAppUI": {
            "PersistentAppUIId": "p-1234567890",
            "PersistentAppUITypeList": ["SHS", "TEZUI", "YTS"],
            "PersistentAppUIStatus": "ATTACHED",
            "CreationTime": "1696712723578.0",
            "LastModifiedTime": "1697742468972.0",
            "LastStateChangeReason": "Reason",
            "Tags": [],
        },
    }


@pytest.mark.asyncio
async def test_describe_persistent_app_ui_missing_app_id_failure():
    # Given
    private_emr_client, inner_client = mock_emrprivate_client(
        {
            "describe_persistent_app_ui.return_value": get_future_results(
                {
                    "PersistentAppUI": {
                        "PersistentAppUIId": "p-1234567890",
                        "PersistentAppUITypeList": ["SHS", "TEZUI", "YTS"],
                        "PersistentAppUIStatus": "ATTACHED",
                        "CreationTime": "1696712723578.0",
                        "LastModifiedTime": "1697742468972.0",
                        "LastStateChangeReason": "Reason",
                        "Tags": [],
                    },
                }
            )
        }
    )

    request = {}
    exception = None
    # When
    try:
        result = await private_emr_client.describe_persistent_app_ui(**request)
    except Exception as ex:
        exception = ex

    # Then
    assert not private_emr_client.sess.create_client.called
    assert not inner_client.describe_persistent_app_ui.called
    assert exception.__class__.__name__ == "ValueError"


@pytest.mark.asyncio
async def test_create_persistent_app_ui():
    # Given
    private_emr_client, inner_client = mock_emrprivate_client(
        {
            "create_persistent_app_ui.return_value": get_future_results(
                {
                    "PersistentAppUIId": "p-1234567890",
                }
            )
        }
    )

    # When
    request = {"TargetResourceArn": "arn:xuz:123456"}
    result = await private_emr_client.create_persistent_app_ui(**request)

    # Then
    private_emr_client.sess.create_client.assert_called_with(
        service_name="emrprivate",
        config=private_emr_client.cfg,
        region_name="us-west-2",
    )
    inner_client.create_persistent_app_ui.assert_called_with(**request)
    assert result == {
        "PersistentAppUIId": "p-1234567890",
    }


@pytest.mark.asyncio
async def test_create_persistent_app_ui_missing_resource_arn_failure():
    # Given
    private_emr_client, inner_client = mock_emrprivate_client(
        {
            "create_persistent_app_ui.return_value": get_future_results(
                {
                    "PersistentAppUIId": "p-1234567890",
                }
            )
        }
    )

    # When
    request = {}
    exception = None
    try:
        result = await private_emr_client.create_persistent_app_ui(**request)
    except Exception as ex:
        exception = ex

    # Then
    assert not private_emr_client.sess.create_client.called
    assert not inner_client.create_persistent_app_ui.called
    assert exception.__class__.__name__ == "ValueError"


@pytest.mark.asyncio
async def test_get_on_cluster_app_ui_presigned_url():
    # Given
    private_emr_client, inner_client = mock_emrprivate_client(
        {
            "get_on_cluster_app_ui_presigned_url.return_value": get_future_results(
                {
                    "PresignedURL": "https://d0hkekkdasd.sagemaker.presigned/url/",
                    "PresignedURLReady": True,
                }
            )
        }
    )

    # When
    request = {
        "ClusterId": "j-1234567890",
        "OnClusterAppUIType": "applicationMaster",
        "ApplicationId": "applicationId",
    }
    result = await private_emr_client.get_on_cluster_app_ui_presigned_url(**request)

    # Then
    private_emr_client.sess.create_client.assert_called_with(
        service_name="emrprivate",
        config=private_emr_client.cfg,
        region_name="us-west-2",
    )
    inner_client.get_on_cluster_app_ui_presigned_url.assert_called_with(**request)
    assert result == {
        "PresignedURL": "https://d0hkekkdasd.sagemaker.presigned/url/",
        "PresignedURLReady": True,
    }


@pytest.mark.asyncio
async def test_get_on_cluster_app_ui_presigned_url_missing_cluster_id_failure():
    # Given
    private_emr_client, inner_client = mock_emrprivate_client(
        {
            "get_on_cluster_app_ui_presigned_url.return_value": get_future_results(
                {
                    "PresignedURL": "https://d0hkekkdasd.sagemaker.presigned/url/",
                    "PresignedURLReady": True,
                }
            )
        }
    )

    # When
    request = {
        "OnClusterAppUIType": "applicationMaster",
        "ApplicationId": "applicationId",
    }
    exception = None
    try:
        result = await private_emr_client.get_on_cluster_app_ui_presigned_url(**request)
    except Exception as ex:
        exception = ex

    # Then
    assert not private_emr_client.sess.create_client.called
    assert not inner_client.get_on_cluster_app_ui_presigned_url.called
    assert exception.__class__.__name__ == "ValueError"
