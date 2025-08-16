import json
import os
import traceback

import botocore
import botocore.credentials
import jsonschema
from jsonschema.exceptions import ValidationError
from jupyter_server.utils import url_path_join
from sagemaker_jupyterlab_extension_common.clients import get_domain_id, get_space_name
from sagemaker_jupyterlab_extension_common.util.app_metadata import (
    get_aws_account_id,
    get_domain_id,
    get_space_name,
    get_user_profile_name,
)
from tornado import web

from sagemaker_jupyterlab_emr_extension.clients import (
    get_emr_client,
    get_emrprivate_client,
    get_sagemaker_client,
)
from sagemaker_jupyterlab_emr_extension.converters import (
    convertDescribeClusterResponse,
    convertDescribeDomainResponse,
    convertDescribeUserProfileResponse,
    convertInstanceGroupsResponse,
    convertListClustersResponse,
    convertPersistentAppUIResponse,
    convertDescribeSecurityConfigurationResponse,
)
from sagemaker_jupyterlab_emr_extension.handler.emr_serverless_handlers import (
    GetServerlessApplicationHandler,
    ListServerlessApplicationsHandler,
    RefreshSparkUIHandler,
)
from sagemaker_jupyterlab_emr_extension.schema.api_schema import (
    create_presistent_app_ui_schema,
    describe_cluster_request_schema,
    describe_persistent_app_ui_schema,
    describe_security_configuration_schema,
    get_on_cluster_app_ui_presigned_url_schema,
    get_persistent_app_ui_presigned_url_schema,
    list_cluster_request_schema,
    list_instance_groups_schema,
)
from sagemaker_jupyterlab_emr_extension.handler.base_emr_handler import BaseEmrHandler


class DescribeClusterHandler(BaseEmrHandler):
    """
    Response schema
    {
        cluster: Cluster
        errorMessage: String
    }
    """

    @web.authenticated
    async def post(self):
        self.set_header("Content-Type", "application/json")
        try:
            body = self.get_json_body()
            jsonschema.validate(body, describe_cluster_request_schema)
            cluster_id = body["ClusterId"]
            role_arn = body.pop("RoleArn", None)
            self.log.info(
                f"Describe cluster request {cluster_id}",
                extra={"Component": "DescribeCluster"},
            )
            response = await get_emr_client(roleArn=role_arn).describe_cluster(**body)
            self.log.info(
                f"Successfuly described cluster for id {cluster_id}",
                extra={"Component": "DescribeCluster"},
            )
            converted_resp = convertDescribeClusterResponse(response)
            self.set_status(200)
            self.finish(json.dumps(converted_resp))
        except web.HTTPError as error:
            await self._handle_http_error(error)
        except (
            botocore.exceptions.ParamValidationError,
            ValidationError,
        ) as error:
            await self._handle_validation_error(error, body, "DescribeCluster")
        except botocore.exceptions.ClientError as error:
            await self._handle_client_error(error, "DescribeCluster")
        except botocore.exceptions.EndpointConnectionError as error:
            await self._handle_connection_error(error, "DescribeCluster")
        except Exception as error:
            await self._handle_error(error, "DescribeCluster")


class ListClustersHandler(BaseEmrHandler):
    """
    Response schema
    {
        clusters: [ClusterSummary]!
        errorMessage: String
    }
    """

    @web.authenticated
    async def post(self):
        self.set_header("Content-Type", "application/json")
        try:
            body = self.get_json_body()
            jsonschema.validate(body, list_cluster_request_schema)
            self.log.info(
                f"List clusters request {body}", extra={"Component": "ListClusters"}
            )
            roleArn = body.pop("RoleArn", None)
            response = await get_emr_client(roleArn=roleArn).list_clusters(**body)
            converted_resp = convertListClustersResponse(response)
            self.set_status(200)
            self.finish(json.dumps(converted_resp))
        except web.HTTPError as error:
            await self._handle_http_error(error)
        except (
            botocore.exceptions.ParamValidationError,
            jsonschema.exceptions.ValidationError,
        ) as error:
            await self._handle_validation_error(error, body, "ListClusters")
        except botocore.exceptions.ClientError as error:
            await self._handle_client_error(error, "ListClusters")
        except botocore.exceptions.EndpointConnectionError as error:
            await self._handle_connection_error(error, "ListClusters")
        except Exception as error:
            await self._handle_error(error, "ListClusters")


class ListInstanceGroupsHandler(BaseEmrHandler):
    """
    Response schema

    InstanceGroup = {
        id: String;
        instanceGroupType: String;
        instanceType: String;
        name: String;
        requestedInstanceCount: Int;
        runningInstanceCount: Int;
    }

    {
        instanceGroups: InstanceGroup
    }
    """

    @web.authenticated
    async def post(self):
        self.set_header("Content-Type", "application/json")
        try:
            body = self.get_json_body()
            jsonschema.validate(body, list_instance_groups_schema)
            cluster_id = body["ClusterId"]
            role_arn = body.pop("RoleArn", None)
            self.log.info(
                f"ListInstanceGroups for cluster {cluster_id}",
                extra={"Component": "ListInstanceGroups"},
            )
            response = await get_emr_client(roleArn=role_arn).list_instance_groups(
                **body
            )
            self.log.info(
                f"Successfuly listed instance groups for cluster {cluster_id}",
                extra={"Component": "ListInstanceGroups"},
            )
            converted_resp = convertInstanceGroupsResponse(response)
            self.set_status(200)
            self.finish(json.dumps(converted_resp))
        except web.HTTPError as error:
            await self._handle_http_error(error)
        except (
            botocore.exceptions.ParamValidationError,
            jsonschema.exceptions.ValidationError,
        ) as error:
            await self._handle_validation_error(error, body, "ListInstanceGroups")
        except botocore.exceptions.ClientError as error:
            await self._handle_client_error(error, "ListInstanceGroups")
        except botocore.exceptions.EndpointConnectionError as error:
            await self._handle_connection_error(error, "ListInstanceGroups")
        except Exception as error:
            await self._handle_error(error, "ListInstanceGroups")


class DescribeSecurityConfigurationHandler(BaseEmrHandler):
    """
    Response schema

    {
        securityConfiguration: SecurityConfiguration,
        errorMessage: String
    }
    """

    @web.authenticated
    async def post(self):
        self.set_header("Content-Type", "application/json")
        try:
            body = self.get_json_body()
            jsonschema.validate(body, describe_security_configuration_schema)
            cluster_id = body.get("ClusterId", "unknown")
            security_configuration_name = body.get("SecurityConfigurationName", "")
            role_arn = body.get("RoleArn", None)
            response = await get_emr_client(
                roleArn=role_arn
            ).describe_security_configuration(
                ClusterId=cluster_id,
                SecurityConfigurationName=security_configuration_name,
            )
            converted_resp = convertDescribeSecurityConfigurationResponse(response)
            self.set_status(200)
            self.finish(json.dumps(converted_resp))
        except web.HTTPError as error:
            await self._handle_http_error(error)
        except (
            botocore.exceptions.ParamValidationError,
            jsonschema.exceptions.ValidationError,
        ) as error:
            await self._handle_validation_error(
                error, body, "DescribeSecurityConfiguration"
            )
        except botocore.exceptions.ClientError as error:
            await self._handle_client_error(error, "DescribeSecurityConfiguration")
        except botocore.exceptions.EndpointConnectionError as error:
            await self._handle_connection_error(error, "DescribeSecurityConfiguration")
        except Exception as error:
            await self._handle_error(error, "DescribeSecurityConfiguration")


class CreatePersistentAppUiHandler(BaseEmrHandler):
    """
    Response schema
    {
        persistentAppUIId: String
    }
    """

    @web.authenticated
    async def post(self):
        self.set_header("Content-Type", "application/json")
        try:
            body = self.get_json_body()
            jsonschema.validate(body, create_presistent_app_ui_schema)
            target_resource_arn = body.get("TargetResourceArn")
            role_arn = body.pop("RoleArn", None)
            self.log.info(
                f"Create Persistent App UI for Arn {target_resource_arn}",
                extra={"Component": "CreatePersistentAppUI"},
            )
            response = await get_emrprivate_client(
                roleArn=role_arn
            ).create_persistent_app_ui(**body)
            persistent_app_ui_id = response.get("PersistentAppUIId")
            self.log.info(
                f"Successfully cretaed Persistent App UI withId {persistent_app_ui_id}",
                extra={"Component": "CreatePersistentAppUI"},
            )
            converted_resp = {
                "persistentAppUIId": persistent_app_ui_id,
                "roleArn": role_arn,
            }
            self.set_status(200)
            self.finish(json.dumps(converted_resp))
        except web.HTTPError as error:
            await self._handle_http_error(error)
        except (
            botocore.exceptions.ParamValidationError,
            jsonschema.exceptions.ValidationError,
        ) as error:
            await self._handle_validation_error(error, body, "CreatePersistentAppUI")
        except botocore.exceptions.ClientError as error:
            await self._handle_client_error(error, "CreatePersistentAppUI")
        except botocore.exceptions.EndpointConnectionError as error:
            await self._handle_connection_error(error, "CreatePersistentAppUI")
        except Exception as error:
            await self._handle_error(error, "CreatePersistentAppUI")


class DescribePersistentAppUiHandler(BaseEmrHandler):
    """
    Response schema
    {
        persistentAppUI: PersistentAppUI
        errorMessage: String
    }
    """

    @web.authenticated
    async def post(self):
        self.set_header("Content-Type", "application/json")
        try:
            body = self.get_json_body()
            jsonschema.validate(body, describe_persistent_app_ui_schema)
            persistent_app_ui_id = body.get("PersistentAppUIId")
            role_arn = body.pop("RoleArn", None)
            self.log.info(
                f"DescribePersistentAppUi for Id {persistent_app_ui_id}",
                extra={"Component": "DescribePersistentAppUI"},
            )
            response = await get_emrprivate_client(
                roleArn=role_arn
            ).describe_persistent_app_ui(**body)
            converted_resp = convertPersistentAppUIResponse(response)
            converted_resp["roleArn"] = role_arn
            self.set_status(200)
            self.finish(json.dumps(converted_resp))
        except web.HTTPError as error:
            await self._handle_http_error(error)
        except (
            botocore.exceptions.ParamValidationError,
            jsonschema.exceptions.ValidationError,
        ) as error:
            await self._handle_validation_error(error, body, "DescribePersistentAppUI")
        except botocore.exceptions.ClientError as error:
            await self._handle_client_error(error, "DescribePersistentAppUI")
        except botocore.exceptions.EndpointConnectionError as error:
            await self._handle_connection_error(error, "DescribePersistentAppUI")
        except Exception as error:
            await self._handle_error(error, "DescribePersistentAppUI")


class GetPersistentAppUiPresignedUrlHandler(BaseEmrHandler):
    """
    Response schema
    {
        presignedURLReady: Boolean
        presignedURL: String
    }
    """

    @web.authenticated
    async def post(self):
        self.set_header("Content-Type", "application/json")
        try:
            body = self.get_json_body()
            jsonschema.validate(body, get_persistent_app_ui_presigned_url_schema)
            role_arn = body.pop("RoleArn", None)
            persistent_app_ui_id = body["PersistentAppUIId"]
            self.log.info(
                f"Get Persistent App UI for {persistent_app_ui_id}",
                extra={"Component": "GetPersistentAppUiPresignedUrl"},
            )
            response = await get_emrprivate_client(
                roleArn=role_arn
            ).get_persistent_app_ui_presigned_url(**body)
            converted_resp = {
                "presignedURLReady": response.get("PresignedURLReady"),
                "presignedURL": response.get("PresignedURL"),
            }
            self.set_status(200)
            self.finish(json.dumps(converted_resp))
        except web.HTTPError as error:
            await self._handle_http_error(error)
        except (
            botocore.exceptions.ParamValidationError,
            jsonschema.exceptions.ValidationError,
        ) as error:
            await self._handle_validation_error(
                error, body, "GetPersistentAppUiPresignedUrl"
            )
        except botocore.exceptions.ClientError as error:
            await self._handle_client_error(error, "GetPersistentAppUiPresignedUrl")
        except botocore.exceptions.EndpointConnectionError as error:
            await self._handle_connection_error(error, "GetPersistentAppUiPresignedUrl")
        except Exception as error:
            await self._handle_error(error, "GetPersistentAppUiPresignedUrl")


class GetOnClustersAppUiPresignedUrlHandler(BaseEmrHandler):
    """
    Response schema
    {
        presignedURLReady: Boolean
        presignedURL: String
    }
    """

    @web.authenticated
    async def post(self):
        self.set_header("Content-Type", "application/json")
        try:
            body = self.get_json_body()
            jsonschema.validate(body, get_on_cluster_app_ui_presigned_url_schema)
            cluster_id = body["ClusterId"]
            role_arn = body.get("RoleArn", None)
            self.log.info(
                f"GetOnClusterAppUiPresignedUrl for cluster id {cluster_id}",
                extra={"Component": "GetOnClustersAppUiPresignedUrl"},
            )
            response = await get_emrprivate_client(
                roleArn=role_arn
            ).get_on_cluster_app_ui_presigned_url(**body)
            converted_resp = {
                "presignedURLReady": response.get("PresignedURLReady"),
                "presignedURL": response.get("PresignedURL"),
            }
            self.set_status(200)
            self.finish(json.dumps(converted_resp))
        except web.HTTPError as error:
            await self._handle_http_error(error)
        except (
            botocore.exceptions.ParamValidationError,
            jsonschema.exceptions.ValidationError,
        ) as error:
            await self._handle_validation_error(
                error, body, "GetOnClustersAppUiPresignedUrl"
            )
        except botocore.exceptions.ClientError as error:
            await self._handle_client_error(error, "GetOnClustersAppUiPresignedUrl")
        except botocore.exceptions.EndpointConnectionError as error:
            await self._handle_connection_error(error, "GetOnClustersAppUiPresignedUrl")
        except Exception as error:
            await self._handle_error(error, "GetOnClustersAppUiPresignedUrl")


# This is a custom handler calling multiple APIs to fetch EMR assumable
# and execution roles
class FetchEMRRolesHandler(BaseEmrHandler):
    """
    Response schema
    {
        EmrAssumableRoleArns: [roleArn]!
        EmrExecutionRoleArns: [roleArn]!
        CallerAccountId: String
        ErrorMessage: String
    }
    """

    @web.authenticated
    async def post(self):
        self.set_header("Content-Type", "application/json")
        try:
            client = get_sagemaker_client()
            domain_id = get_domain_id()
            space_name = get_space_name()
            space_details = await client.describe_space(
                DomainId=domain_id, SpaceName=space_name
            )
            space_type = space_details.get("SpaceSharingSettings", {}).get(
                "SharingType"
            )
            # Since there is no easy way to get user name directly, we get it from space owner name. If the
            # space is a shared space, we would use the EmrSettings under domain instead.
            if space_type == "Private":
                user_profile_name = space_details.get("OwnershipSettings", {}).get(
                    "OwnerUserProfileName", None
                )
                describe_user_profile_response = await client.describe_user_profile(
                    DomainId=domain_id, UserProfileName=user_profile_name
                )
                converted_response = convertDescribeUserProfileResponse(
                    response=describe_user_profile_response
                )

                # if both role arn lists under user are empty, use domain level EMR roles
                if (not converted_response.get("EmrAssumableRoleArns")) and (
                    not converted_response.get("EmrExecutionRoleArns")
                ):
                    describe_domain_response = await client.describe_domain(
                        DomainId=domain_id
                    )
                    converted_response = convertDescribeDomainResponse(
                        response=describe_domain_response
                    )
            else:
                describe_domain_response = await client.describe_domain(
                    DomainId=domain_id
                )
                converted_response = convertDescribeDomainResponse(
                    response=describe_domain_response
                )

            # add more keys to response
            converted_response.update({"CallerAccountId": get_aws_account_id()})
            self.set_status(200)
            self.finish(json.dumps(converted_response))
        except web.HTTPError as error:
            await self._handle_http_error(error)
        except (
            botocore.exceptions.ParamValidationError,
            jsonschema.exceptions.ValidationError,
        ) as error:
            await self._handle_validation_error(error, body, "FetchEMRRoles")
        except botocore.exceptions.ClientError as error:
            await self._handle_client_error(error, "FetchEMRRoles")
        except botocore.exceptions.EndpointConnectionError as error:
            await self._handle_connection_error(error, "FetchEMRRoles")
        except Exception as error:
            await self._handle_error(error, "FetchEMRRoles")


def build_url(web_app, endpoint):
    base_url = web_app.settings["base_url"]
    return url_path_join(base_url, endpoint)


def register_handlers(nbapp):
    web_app = nbapp.web_app
    host_pattern = ".*$"
    handlers = [
        (
            build_url(web_app, r"/aws/sagemaker/api/emr/describe-cluster"),
            DescribeClusterHandler,
        ),
        (
            build_url(
                web_app, r"/aws/sagemaker/api/emr/describe-security-configuration"
            ),
            DescribeSecurityConfigurationHandler,
        ),
        (
            build_url(web_app, r"/aws/sagemaker/api/emr/list-clusters"),
            ListClustersHandler,
        ),
        (
            build_url(web_app, r"/aws/sagemaker/api/emr/create-persistent-app-ui"),
            CreatePersistentAppUiHandler,
        ),
        (
            build_url(web_app, r"/aws/sagemaker/api/emr/describe-persistent-app-ui"),
            DescribePersistentAppUiHandler,
        ),
        (
            build_url(
                web_app, r"/aws/sagemaker/api/emr/get-persistent-app-ui-presigned-url"
            ),
            GetPersistentAppUiPresignedUrlHandler,
        ),
        (
            build_url(
                web_app, r"/aws/sagemaker/api/emr/get-on-cluster-app-ui-presigned-url"
            ),
            GetOnClustersAppUiPresignedUrlHandler,
        ),
        (
            build_url(web_app, r"/aws/sagemaker/api/emr/list-instance-groups"),
            ListInstanceGroupsHandler,
        ),
        (
            build_url(web_app, r"/aws/sagemaker/api/sagemaker/fetch-emr-roles"),
            FetchEMRRolesHandler,
        ),
        (
            build_url(web_app, r"/aws/sagemaker/api/emr-serverless/list-applications"),
            ListServerlessApplicationsHandler,
        ),
        (
            build_url(web_app, r"/aws/sagemaker/api/emr-serverless/get-application"),
            GetServerlessApplicationHandler,
        ),
        (
            build_url(
                web_app, r"/aws/sagemaker/redirect/emr-serverless/refresh-spark-ui/(.*)"
            ),
            RefreshSparkUIHandler,
        ),
    ]
    web_app.add_handlers(host_pattern, handlers)

    # Set environment variable to enable Spark UI link replacement
    # See https://tiny.amazon.com/pi5ym43x/
    os.environ["SPARK_UI_LINK_OVERRIDE"] = "true"
