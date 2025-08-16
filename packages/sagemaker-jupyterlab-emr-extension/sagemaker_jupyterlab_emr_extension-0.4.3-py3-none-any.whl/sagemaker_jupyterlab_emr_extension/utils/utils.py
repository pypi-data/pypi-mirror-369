import logging
import traceback

import botocore
from botocore.session import Session

from sagemaker_jupyterlab_emr_extension.constants import USE_DUALSTACK_ENDPOINT


def get_regional_service_endpoint_url(
    botocore_session: Session, service_name: str, region_name: str
) -> str:
    endpoint_resolver = botocore_session.get_component("endpoint_resolver")
    partition_name = endpoint_resolver.get_partition_for_region(region_name)
    endpoint_data = endpoint_resolver.construct_endpoint(
        service_name=service_name,
        region_name=region_name,
        partition_name=partition_name,
        use_dualstack_endpoint=USE_DUALSTACK_ENDPOINT,
    )
    if endpoint_data and "hostname" in endpoint_data:
        resolved_url = endpoint_data["hostname"]
        if not resolved_url.startswith("https://"):
            resolved_url = "https://" + resolved_url
        return resolved_url
    else:
        dns_suffix = endpoint_resolver.get_partition_dns_suffix(partition_name)
        return f"https://{service_name}.{region_name}.{dns_suffix}"


def get_credential(role_arn, region_name):
    session = botocore.session.get_session()
    endpoint_url = get_regional_service_endpoint_url(session, "sts", region_name)
    sts_client = session.create_client("sts", endpoint_url=endpoint_url)

    try:
        credential = sts_client.assume_role(
            RoleArn=role_arn,
            RoleSessionName="SagemakerAssumableSession",
        )
    except (
        botocore.exceptions.BotoCoreError,
        botocore.exceptions.ClientError,
    ) as error:
        logging.error(
            "Error in get credential in EMR {}".format(traceback.format_exc())
        )
        raise error
    return credential["Credentials"]
