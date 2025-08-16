import logging
import os
import traceback

import botocore
from sagemaker_jupyterlab_extension_common.clients import (
    BaseAysncBoto3Client,
    get_partition,
    get_region_name,
)
from traitlets.config import SingletonConfigurable

from sagemaker_jupyterlab_emr_extension.utils.utils import get_credential
from sagemaker_jupyterlab_emr_extension.utils.exception_utils import (
    handle_endpoint_connection_error,
)


class PrivateEMRAsyncBoto3Client(BaseAysncBoto3Client, SingletonConfigurable):
    def __init__(
        self, region_name: str, partition: str, model_data_path=None, roleArn=None
    ):
        super().__init__(region_name, partition, model_data_path)
        self.role_arn = roleArn

    def _create_emrprivate_client(self):
        create_client_args = {
            "service_name": "emrprivate",
            "config": self.cfg,
            "region_name": self.region_name,
        }
        if self.role_arn:
            credential_detail = get_credential(
                role_arn=self.role_arn, region_name=self.region_name
            )
            create_client_args = {
                "service_name": "emrprivate",
                "config": self.cfg,
                "region_name": self.region_name,
                "aws_access_key_id": credential_detail["AccessKeyId"],
                "aws_secret_access_key": credential_detail["SecretAccessKey"],
                "aws_session_token": credential_detail["SessionToken"],
            }

        return self.sess.create_client(**create_client_args)

    def update_arn(self, roleArn):
        self.role_arn = roleArn

    async def get_on_cluster_app_ui_presigned_url(self, **kwargs):
        try:
            cluster_Id = kwargs.get("ClusterId")
            if not cluster_Id:
                raise ValueError("Required argument ClusterId is invalid or missing")
            async with self._create_emrprivate_client() as emrprivate:
                response = await emrprivate.get_on_cluster_app_ui_presigned_url(
                    **kwargs
                )
        except botocore.exceptions.EndpointConnectionError as error:
            error_message = "Error getting OnCluster app ui presigned url cluster_Id {}: {} {}".format(
                cluster_Id, str(error), traceback.format_exc()
            )
            handle_endpoint_connection_error(error, error_message)
        except (
            botocore.exceptions.BotoCoreError,
            botocore.exceptions.ClientError,
        ) as error:
            logging.error(
                "Error getting OnCluster app ui presigned url cluster_Id {}, {}".format(
                    cluster_Id,
                    traceback.format_exc(),
                )
            )
            raise error
        except ValueError as e:
            logging.error("Invalid argument:" + str(e))
            raise e
        except Exception as ex:
            logging.error(
                "Error getting OnCluster app ui presigned url cluster_Id {} {}".format(
                    cluster_Id, traceback.format_exc()
                )
            )
            raise ex
        return response

    async def create_persistent_app_ui(self, **kwargs):
        try:
            target_resource_arn = kwargs.get("TargetResourceArn")
            if not target_resource_arn:
                raise ValueError(
                    "Required argument TargetResourceArn is invalid or missing"
                )
            async with self._create_emrprivate_client() as emrprivate:
                response = await emrprivate.create_persistent_app_ui(**kwargs)
        except botocore.exceptions.EndpointConnectionError as error:
            error_message = (
                "Error creating persistent app UI {} EMR clusters: {} {}".format(
                    target_resource_arn, str(error), traceback.format_exc()
                )
            )
            handle_endpoint_connection_error(error, error_message)
        except (
            botocore.exceptions.BotoCoreError,
            botocore.exceptions.ClientError,
        ) as error:
            logging.error(
                "Error creating persistent app UI {} EMR clusters {}".format(
                    target_resource_arn, traceback.format_exc()
                )
            )
            raise error
        except ValueError as e:
            logging.error("Invalid argument:" + str(e))
            raise e
        except Exception as ex:
            logging.error(
                "Error creating persistent app UI for arn {} {}".format(
                    target_resource_arn, traceback.format_exc()
                )
            )
            raise ex
        return response

    async def describe_persistent_app_ui(self, **kwargs):
        try:
            persistent_app_ui_id = kwargs.get("PersistentAppUIId")
            if not persistent_app_ui_id:
                raise ValueError(
                    "Required argument PersistentAppUIId is invalid or missing"
                )
            async with self._create_emrprivate_client() as emrprivate:
                response = await emrprivate.describe_persistent_app_ui(**kwargs)
        except botocore.exceptions.EndpointConnectionError as error:
            error_message = (
                "Error describing persistent app UI for Id {}: {} {}".format(
                    persistent_app_ui_id, str(error), traceback.format_exc()
                )
            )
            handle_endpoint_connection_error(error, error_message)
        except (
            botocore.exceptions.BotoCoreError,
            botocore.exceptions.ClientError,
        ) as error:
            logging.error(
                "Error describing persistent app UI for Id {}. {}".format(
                    persistent_app_ui_id, traceback.format_exc()
                )
            )
            raise error
        except ValueError as e:
            logging.error("Invalid argument:" + str(e))
            raise e
        except Exception as ex:
            logging.error(
                "Error describing persistent app UI Id {} {}".format(
                    persistent_app_ui_id, traceback.format_exc()
                )
            )
            raise ex
        return response

    async def get_persistent_app_ui_presigned_url(self, **kwargs):
        try:
            persistent_app_ui_id = kwargs.get("PersistentAppUIId")
            if not persistent_app_ui_id:
                raise ValueError(
                    "Required argument PersistentAppUIId is invalid or missing"
                )
            async with self._create_emrprivate_client() as emrprivate:
                response = await emrprivate.get_persistent_app_ui_presigned_url(
                    **kwargs
                )
        except botocore.exceptions.EndpointConnectionError as error:
            error_message = (
                "Error getting persistent app ui presigned url {}: {} {}".format(
                    persistent_app_ui_id, str(error), traceback.format_exc()
                )
            )
            handle_endpoint_connection_error(error, error_message)
        except (
            botocore.exceptions.BotoCoreError,
            botocore.exceptions.ClientError,
        ) as error:
            logging.error(
                "Error getting persistent app ui presigned url {} {}".format(
                    persistent_app_ui_id,
                    traceback.format_exc(),
                )
            )
            raise error
        except ValueError as e:
            logging.error("Invalid argument:" + str(e))
            raise e
        except Exception as ex:
            logging.error(
                "Error getting persistent app ui presigned url {} {}".format(
                    persistent_app_ui_id, traceback.format_exc()
                )
            )
            raise ex
        return response


def get_emrprivate_client(createNew=False, roleArn=None):
    PACKAGE_ROOT = os.path.abspath(os.path.dirname(__file__))
    os.environ["EMR_DATA_PATH"] = os.path.join(PACKAGE_ROOT, "botocore_model")
    model_path = os.environ.get("EMR_DATA_PATH")
    if createNew:
        return PrivateEMRAsyncBoto3Client(
            get_region_name(),
            get_partition(),
            model_data_path=model_path,
            roleArn=roleArn,
        )
    else:
        client = PrivateEMRAsyncBoto3Client.instance(
            get_region_name(), get_partition(), model_data_path=model_path
        )
        client.update_arn(roleArn)
        return client


class EMRAsyncBoto3Client(BaseAysncBoto3Client, SingletonConfigurable):
    def __init__(
        self, region_name: str, partition: str, model_data_path=None, roleArn=None
    ):
        super().__init__(region_name, partition, model_data_path)
        self.role_arn = roleArn

    def _create_emr_client(self):
        create_client_args = {
            "service_name": "emr",
            "config": self.cfg,
            "region_name": self.region_name,
        }
        if self.role_arn:
            credential_detail = get_credential(
                role_arn=self.role_arn, region_name=self.region_name
            )
            create_client_args = {
                "service_name": "emr",
                "config": self.cfg,
                "region_name": self.region_name,
                "aws_access_key_id": credential_detail["AccessKeyId"],
                "aws_secret_access_key": credential_detail["SecretAccessKey"],
                "aws_session_token": credential_detail["SessionToken"],
            }
        return self.sess.create_client(**create_client_args)

    def update_arn(self, roleArn):
        self.role_arn = roleArn

    async def list_clusters(self, **kwargs):
        try:
            async with self._create_emr_client() as em_client:
                response = await em_client.list_clusters(**kwargs)
        except botocore.exceptions.EndpointConnectionError as error:
            error_message = "Error in listing clusters: {} {}".format(
                str(error), traceback.format_exc()
            )
            handle_endpoint_connection_error(error, error_message)
        except (
            botocore.exceptions.BotoCoreError,
            botocore.exceptions.ClientError,
        ) as error:
            logging.error("Error in listing clusters {}".format(traceback.format_exc()))
            raise error
        return response

    async def describe_cluster(self, **kwargs):
        try:
            cluster_Id = kwargs.get("ClusterId")
            if not cluster_Id:
                raise ValueError("Required argument ClusterId is invalid or missing")
            async with self._create_emr_client() as em_client:
                response = await em_client.describe_cluster(**kwargs)
        except botocore.exceptions.EndpointConnectionError as error:
            error_message = "Error in describing cluster Id {}: {} {}".format(
                cluster_Id, str(error), traceback.format_exc()
            )
            handle_endpoint_connection_error(error, error_message)
        except (
            botocore.exceptions.BotoCoreError,
            botocore.exceptions.ClientError,
        ) as error:
            logging.error(
                "Error describing cluster for Id {}. {}".format(
                    cluster_Id, traceback.format_exc()
                )
            )
            raise error
        except ValueError as e:
            logging.error("Invalid argument:" + str(e))
            raise e
        except Exception as ex:
            logging.error(
                "Error describing cluster for Id {} {}".format(
                    cluster_Id, traceback.format_exc()
                )
            )
            raise ex
        return response

    async def describe_security_configuration(self, **kwargs):
        """
        Describes a security configuration.
        Args:
            - SecurityConfigurationName (str): Required. Name of the security configuration.
            - ClusterId (str): Optional. Used for logging purposes
        Returns:
            dict: The security configuration details.
        Raises:
            ValueError: If SecurityConfigurationName is missing or invalid.
        """
        try:
            cluster_Id = kwargs.get("ClusterId")
            if not cluster_Id:
                cluster_Id = "unknown"

            security_conf_name = kwargs.get("SecurityConfigurationName")
            if not security_conf_name or security_conf_name.strip() == "":
                raise ValueError(
                    "Required argument security configuration name is invalid or missing"
                )

            async with self._create_emr_client() as em_client:
                response = await em_client.describe_security_configuration(
                    Name=security_conf_name
                )
        except botocore.exceptions.EndpointConnectionError as error:
            error_message = "Error in describing security configuration {} for cluster {}. {}".format(
                security_conf_name, cluster_Id, traceback.format_exc()
            )
            handle_endpoint_connection_error(error, error_message)
        except (
            botocore.exceptions.BotoCoreError,
            botocore.exceptions.ClientError,
        ) as error:
            logging.error(
                "Error describing security configuration {} for cluster {}. {}".format(
                    security_conf_name, cluster_Id, traceback.format_exc()
                )
            )
            raise error
        except ValueError as e:
            logging.error("Invalid argument:" + str(e))
            raise e
        except Exception as ex:
            logging.error(
                "Error describing security configuration {} for cluster {}: {}".format(
                    security_conf_name, cluster_Id, traceback.format_exc()
                )
            )
            raise ex
        return response

    async def list_instance_groups(self, **kwargs):
        try:
            cluster_Id = kwargs.get("ClusterId")
            if not cluster_Id:
                raise ValueError("Required argument ClusterId is invalid or missing")
            async with self._create_emr_client() as em_client:
                response = await em_client.list_instance_groups(**kwargs)
        except botocore.exceptions.EndpointConnectionError as error:
            error_message = (
                "Error in listing Instance Group for Cluster Id {}: {} {}".format(
                    cluster_Id, str(error), traceback.format_exc()
                )
            )
            handle_endpoint_connection_error(error, error_message)
        except (
            botocore.exceptions.BotoCoreError,
            botocore.exceptions.ClientError,
        ) as error:
            logging.error(
                "Error listing Instance Group for Cluster Id {}. {}".format(
                    cluster_Id, traceback.format_exc()
                )
            )
            raise error
        except ValueError as e:
            logging.error("Invalid argument:" + str(e))
            raise e
        except Exception as ex:
            logging.error(
                "Error listing Instance Group for Cluster Id {} {}".format(
                    cluster_Id, traceback.format_exc()
                )
            )
            raise ex
        return response


def get_emr_client(createNew=False, roleArn=None):
    if createNew:
        return EMRAsyncBoto3Client(get_region_name(), get_partition(), roleArn=roleArn)
    else:
        client = EMRAsyncBoto3Client.instance(get_region_name(), get_partition())
        client.update_arn(roleArn)
        return client


class SageMakerAsyncBoto3Client(BaseAysncBoto3Client, SingletonConfigurable):
    def __init__(self, region_name: str, partition: str, model_data_path=None):
        super().__init__(region_name, partition, model_data_path)

    def _create_sagemaker_client(self):
        create_client_args = {
            "service_name": "sagemaker",
            "config": self.cfg,
            "region_name": self.region_name,
        }
        return self.sess.create_client(**create_client_args)

    async def describe_user_profile(self, **kwargs):
        try:
            domain_id = kwargs.get("DomainId")
            user_profile_name = kwargs.get("UserProfileName")
            if not domain_id or not user_profile_name:
                raise ValueError(
                    "Required argument DomainId or UserProfileName is invalid or missing"
                )
            async with self._create_sagemaker_client() as sm:
                return await sm.describe_user_profile(**kwargs)
        except botocore.exceptions.EndpointConnectionError as error:
            error_message = (
                "Error in listing user profiles for domain Id {}: {} {}".format(
                    domain_id, str(error), traceback.format_exc()
                )
            )
            handle_endpoint_connection_error(error, error_message)
        except (
            botocore.exceptions.BotoCoreError,
            botocore.exceptions.ClientError,
        ) as error:
            logging.error(
                "Error in listing user profiles for domain Id {}. {}".format(
                    domain_id, traceback.format_exc()
                )
            )

    async def describe_space(self, **kwargs):
        try:
            domain_id = kwargs.get("DomainId")
            space_name = kwargs.get("SpaceName")
            if not domain_id or not space_name:
                raise ValueError(
                    "Required argument DomainId or SpaceName is invalid or missing"
                )
            async with self._create_sagemaker_client() as sm:
                return await sm.describe_space(**kwargs)
        except botocore.exceptions.EndpointConnectionError as error:
            error_message = "Error in listing spaces for domain Id {}: {} {}".format(
                domain_id, str(error), traceback.format_exc()
            )
            handle_endpoint_connection_error(error, error_message)
        except (
            botocore.exceptions.BotoCoreError,
            botocore.exceptions.ClientError,
        ) as error:
            logging.error(
                "Error in listing spaces for domain Id {}. {}".format(
                    domain_id, traceback.format_exc()
                )
            )

    async def describe_domain(self, **kwargs):
        try:
            domain_id = kwargs.get("DomainId")
            if not domain_id:
                raise ValueError("Required argument DomainId is invalid or missing")
            async with self._create_sagemaker_client() as sm:
                return await sm.describe_domain(**kwargs)
        except botocore.exceptions.EndpointConnectionError as error:
            error_message = "Error in listing domains for domain Id {}: {} {}".format(
                domain_id, str(error), traceback.format_exc()
            )
            handle_endpoint_connection_error(error, error_message)
        except (
            botocore.exceptions.BotoCoreError,
            botocore.exceptions.ClientError,
        ) as error:
            logging.error(
                "Error in listing domains for domain Id {}. {}".format(
                    domain_id, traceback.format_exc()
                )
            )


def get_sagemaker_client(createNew=False):
    PACKAGE_ROOT = os.path.abspath(os.path.dirname(__file__))
    os.environ["SAGEMAKER_DATA_PATH"] = os.path.join(PACKAGE_ROOT, "botocore_model")
    model_path = os.environ.get("SAGEMAKER_DATA_PATH")
    if createNew:
        return SageMakerAsyncBoto3Client(get_region_name(), get_partition(), model_path)
    else:
        return SageMakerAsyncBoto3Client.instance(
            get_region_name(), get_partition(), model_path
        )
