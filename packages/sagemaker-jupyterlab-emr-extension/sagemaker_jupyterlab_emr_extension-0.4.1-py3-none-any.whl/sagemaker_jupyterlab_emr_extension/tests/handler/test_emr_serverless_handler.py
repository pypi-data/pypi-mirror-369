import os
import json
from datetime import datetime

import pytest

from unittest.mock import patch, MagicMock, Mock, ANY

from sagemaker_jupyterlab_emr_extension import register_handlers

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
        "applicationId": "applicationId",
        "name": "applicationName",
        "releaseLabel": "releaseLabel",
        "architecture": "X86_64",
        "state": "STARTED",
        "tags": {},
        "maximumCapacity": {"cpu": 1, "memory": 1, "disk": 1},
        "interactiveConfiguration": {"livyEndpointEnabled": True},
        "createdAt": datetime(2015, 1, 1),
    }
}


class EmrServerlessClientMock:
    get_application_response: any
    list_applications_response: any

    def __init__(self, get_application_response, list_applications_response):
        self.get_application_response = get_application_response
        self.list_applications_response = list_applications_response

    async def get_application(self, **kwargs):
        return self.get_application_response

    async def list_applications(self, **kwargs):
        return self.list_applications_response


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


@pytest.mark.aysncio
@patch(
    "sagemaker_jupyterlab_emr_extension.handlers.GetServerlessApplicationHandler.log",
    return_value="someInfoLog",
)
@patch.dict(os.environ, {"DomainId": "domainId"}, {"SpaceName": "spaceName"})
@patch(
    "sagemaker_jupyterlab_emr_extension.handler.emr_serverless_handlers.get_emr_serverless_client"
)
async def test_get_application_success(
    emrs_client_mock,
    mock_logger,
    jp_fetch,
):
    emrs_client_mock.return_value = EmrServerlessClientMock(
        TEST_GET_APPLICATION_RESPONSE, TEST_LIST_APPLICATIONS_RESPONSE
    )

    kwargs = {"applicationId": "a12345688"}
    response = await jp_fetch(
        "aws/sagemaker/api/emr-serverless/get-application",
        method="POST",
        body=json.dumps(kwargs),
    )
    resp = json.loads(response.body.decode("utf-8"))
    assert resp == {
        "application": {
            "id": "applicationId",
            "arn": "applicationArn",
            "name": "applicationName",
            "architecture": "X86_64",
            "releaseLabel": "releaseLabel",
            "livyEndpointEnabled": "True",
            "maximumCapacityCpu": 1,
            "maximumCapacityMemory": 1,
            "maximumCapacityDisk": 1,
            "status": "STARTED",
            "tags": {},
            "createdAt": "2015-01-01 00:00:00",
        }
    }


@pytest.mark.aysncio
@patch(
    "sagemaker_jupyterlab_emr_extension.handlers.GetServerlessApplicationHandler.log",
    return_value="someInfoLog",
)
@patch.dict(os.environ, {"DomainId": "domainId"}, {"SpaceName": "spaceName"})
@patch(
    "sagemaker_jupyterlab_emr_extension.handler.emr_serverless_handlers.get_emr_serverless_client"
)
async def test_get_application_bad_request(
    emrs_client_mock,
    mock_logger,
    jp_fetch,
):
    emrs_client_mock.return_value = EmrServerlessClientMock(
        TEST_GET_APPLICATION_RESPONSE, TEST_LIST_APPLICATIONS_RESPONSE
    )
    kwargs = {}
    exception = None
    try:
        await jp_fetch(
            "aws/sagemaker/api/emr-serverless/get-application",
            method="POST",
            body=json.dumps(kwargs),
        )
    except Exception as ex:
        exception = ex
    assert exception.code == 400


@pytest.mark.aysncio
@patch(
    "sagemaker_jupyterlab_emr_extension.handlers.ListServerlessApplicationsHandler.log",
    return_value="someInfoLog",
)
@patch.dict(os.environ, {"DomainId": "domainId"}, {"SpaceName": "spaceName"})
@patch(
    "sagemaker_jupyterlab_emr_extension.handler.emr_serverless_handlers.get_emr_serverless_client"
)
async def test_list_applications_success(
    emrs_client_mock,
    mock_logger,
    jp_fetch,
):
    emrs_client_mock.return_value = EmrServerlessClientMock(
        TEST_GET_APPLICATION_RESPONSE, TEST_LIST_APPLICATIONS_RESPONSE
    )

    kwargs = {}
    response = await jp_fetch(
        "aws/sagemaker/api/emr-serverless/list-applications",
        method="POST",
        body=json.dumps(kwargs),
    )
    resp = json.loads(response.body.decode("utf-8"))
    assert resp == {
        "applications": [
            {
                "id": "applicationId1",
                "arn": "applicationArn1",
                "name": "applicationName1",
                "status": "STARTED",
                "createdAt": "2015-01-01 00:00:00",
            },
            {
                "id": "applicationId2",
                "arn": "applicationArn2",
                "name": "applicationName2",
                "status": "STARTED",
                "createdAt": "2015-01-01 00:00:00",
            },
        ],
        "nextToken": "",
    }


@pytest.mark.aysncio
@patch(
    "sagemaker_jupyterlab_emr_extension.handlers.ListServerlessApplicationsHandler.log",
    return_value="someInfoLog",
)
@patch.dict(os.environ, {"DomainId": "domainId"}, {"SpaceName": "spaceName"})
@patch(
    "sagemaker_jupyterlab_emr_extension.handler.emr_serverless_handlers.get_emr_serverless_client"
)
async def test_list_application_bad_request(
    emrs_client_mock,
    mock_logger,
    jp_fetch,
):
    emrs_client_mock.return_value = EmrServerlessClientMock(
        TEST_GET_APPLICATION_RESPONSE, TEST_LIST_APPLICATIONS_RESPONSE
    )
    kwargs = {}
    exception = None
    try:
        await jp_fetch(
            "aws/sagemaker/api/emr-serverless/get-application",
            method="POST",
            body=json.dumps(kwargs),
        )
    except Exception as ex:
        exception = ex
    assert exception.code == 400
