from datetime import datetime

import pytest
import asyncio
from typing import Dict
from unittest.mock import Mock, MagicMock

from sagemaker_jupyterlab_emr_extension.client.emr_serverless_client import (
    EMRServerlessAsyncBoto3Client,
)


def get_future_results(result):
    future = asyncio.Future()
    future.set_result(result)
    return future


def mock_emr_serverless_client(method_mock: Dict) -> (Mock, Mock):
    emrs_client = EMRServerlessAsyncBoto3Client("us-west-2", "aws")
    inner_client = Mock(**method_mock)
    emrs_client.sess = Mock(
        **{
            "create_client.return_value": MagicMock(
                **{"__aenter__.return_value": inner_client}
            )
        }
    )
    return emrs_client, inner_client


TEST_LIST_APPLICATIONS_RESPONSE = {
    "applications": [
        {
            "id": "applicationId1",
            "arn": "applicationArn1",
            "name": "applicationName1",
            "state": "STARTED",
            "createdAt": datetime(2015, 1, 1),
        },
        {
            "id": "applicationId2",
            "arn": "applicationArn2",
            "name": "applicationName2",
            "state": "STARTED",
            "createdAt": datetime(2015, 1, 1),
        },
    ],
    "nextToken": "",
}

TEST_GET_APPLICATION_RESPONSE = {
    "application": {
        "arn": "applicationArn",
        "id": "applicationId",
        "name": "applicationName",
        "releaseLabel": "releaseLabel",
        "state": "STARTED",
        "tags": [],
        "createdAt": datetime(2015, 1, 1),
    }
}


@pytest.mark.asyncio
async def test_get_application():
    # Given
    emrs_client, inner_client = mock_emr_serverless_client(
        {
            "get_application.return_value": get_future_results(
                TEST_GET_APPLICATION_RESPONSE
            )
        }
    )

    # When
    request = {"applicationId": "applicationId"}
    result = await emrs_client.get_application(**request)

    # Then
    emrs_client.sess.create_client.assert_called_with(
        service_name="emr-serverless", config=emrs_client.cfg, region_name="us-west-2"
    )
    inner_client.get_application.assert_called_with(**request)
    assert result == TEST_GET_APPLICATION_RESPONSE


@pytest.mark.asyncio
async def test_get_application_missing_application_id_failure():
    # Given
    emrs_client, inner_client = mock_emr_serverless_client(
        {
            "get_application.return_value": get_future_results(
                TEST_GET_APPLICATION_RESPONSE
            )
        }
    )

    # When
    request = {}
    exception = None
    try:
        result = await emrs_client.get_application(**request)
    except Exception as ex:
        exception = ex

    # Then
    assert not emrs_client.sess.create_client.called
    assert not inner_client.get_application.called
    assert exception.__class__.__name__ == "ValueError"


@pytest.mark.asyncio
async def test_list_applications_no_args_success():
    # Given
    emrs_client, inner_client = mock_emr_serverless_client(
        {
            "list_applications.return_value": get_future_results(
                TEST_LIST_APPLICATIONS_RESPONSE
            )
        }
    )

    # When
    result = await emrs_client.list_applications()

    # Then
    emrs_client.sess.create_client.assert_called_with(
        service_name="emr-serverless", config=emrs_client.cfg, region_name="us-west-2"
    )
    inner_client.list_applications.assert_called_with()
    assert result == TEST_LIST_APPLICATIONS_RESPONSE


@pytest.mark.asyncio
async def test_list_applications_all_args_success():
    # Given
    emrs_client, inner_client = mock_emr_serverless_client(
        {
            "list_applications.return_value": get_future_results(
                TEST_LIST_APPLICATIONS_RESPONSE
            )
        }
    )

    # When
    request = {
        "states": ["STARTED", "STOPPED", "CREATED"],
        "nextToken": "45790087",
    }
    result = await emrs_client.list_applications(**request)

    # Then
    emrs_client.sess.create_client.assert_called_with(
        service_name="emr-serverless", config=emrs_client.cfg, region_name="us-west-2"
    )
    inner_client.list_applications.assert_called_with(**request)
    assert result == TEST_LIST_APPLICATIONS_RESPONSE
