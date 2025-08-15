import logging
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


class EMRServerlessAsyncBoto3Client(BaseAysncBoto3Client, SingletonConfigurable):
    def __init__(
        self, region_name: str, partition: str, model_data_path=None, roleArn=None
    ):
        super().__init__(region_name, partition, model_data_path)
        self.role_arn = roleArn

    def _create_emr_serverless_client(self):
        create_client_args = {
            "service_name": "emr-serverless",
            "config": self.cfg,
            "region_name": self.region_name,
        }
        if self.role_arn:
            credential_detail = get_credential(
                role_arn=self.role_arn, region_name=self.region_name
            )
            create_client_args = {
                "service_name": "emr-serverless",
                "config": self.cfg,
                "region_name": self.region_name,
                "aws_access_key_id": credential_detail["AccessKeyId"],
                "aws_secret_access_key": credential_detail["SecretAccessKey"],
                "aws_session_token": credential_detail["SessionToken"],
            }
        return self.sess.create_client(**create_client_args)

    def update_arn(self, roleArn):
        self.role_arn = roleArn

    async def list_applications(self, **kwargs):
        try:
            async with self._create_emr_serverless_client() as emrs_client:
                response = await emrs_client.list_applications(**kwargs)
        except botocore.exceptions.EndpointConnectionError as error:
            error_message = "Error in listing clusters: {}".format(str(error))
            handle_endpoint_connection_error(error, error_message)
        except (
            botocore.exceptions.BotoCoreError,
            botocore.exceptions.ClientError,
        ) as error:
            logging.error(
                "Error in listing clusters {}".format(traceback.format_exc()),
            )
            raise error
        return response

    async def get_application(self, **kwargs):
        try:
            application_id = kwargs.get("applicationId")
            if not application_id:
                raise ValueError(
                    "Required argument ApplicationId is invalid or missing"
                )
            async with self._create_emr_serverless_client() as emrs_client:
                response = await emrs_client.get_application(**kwargs)
        except botocore.exceptions.EndpointConnectionError as error:
            error_message = "Error getting application for Id {}: {}".format(
                application_id, str(error)
            )
            handle_endpoint_connection_error(error, error_message)
        except (
            botocore.exceptions.BotoCoreError,
            botocore.exceptions.ClientError,
        ) as error:
            logging.error(
                "Error getting application for Id {}. {}".format(
                    application_id, traceback.format_exc()
                )
            )
            raise error
        except ValueError as e:
            logging.error("Invalid argument:" + str(e))
            raise e
        except Exception as ex:
            logging.error(
                "Error getting application for Id {} {}".format(
                    application_id, traceback.format_exc()
                )
            )
            raise ex
        return response

    async def get_dashboard_for_job_run(self, **kwargs):
        try:
            application_id = kwargs.get("applicationId")
            job_run_id = kwargs.get("jobRunId")
            if not application_id:
                raise ValueError(
                    "Required argument 'applicationId' is invalid or missing"
                )
            if not job_run_id:
                raise ValueError("Required argument 'jobRunId' is invalid or missing")
            async with self._create_emr_serverless_client() as emrs_client:
                response = await emrs_client.get_dashboard_for_job_run(**kwargs)
        except botocore.exceptions.EndpointConnectionError as error:
            error_message = "Error getting dashboard for job run {}: {}".format(
                job_run_id, str(error)
            )
            handle_endpoint_connection_error(error, error_message)
        except (
            botocore.exceptions.BotoCoreError,
            botocore.exceptions.ClientError,
        ) as error:
            logging.error(
                "Error getting dashboard for job run {}. {}".format(
                    job_run_id, traceback.format_exc()
                )
            )
            raise error
        except ValueError as e:
            logging.error("Invalid argument:" + str(e))
            raise e
        except Exception as ex:
            logging.error(
                "Error getting dashboard for job run {} {}".format(
                    job_run_id, traceback.format_exc()
                )
            )
            raise ex
        return response


def get_emr_serverless_client(createNew=False, roleArn=None):
    if createNew:
        return EMRServerlessAsyncBoto3Client(
            get_region_name(), get_partition(), roleArn=roleArn
        )
    else:
        client = EMRServerlessAsyncBoto3Client.instance(
            get_region_name(), get_partition()
        )
        client.update_arn(roleArn)
        return client
