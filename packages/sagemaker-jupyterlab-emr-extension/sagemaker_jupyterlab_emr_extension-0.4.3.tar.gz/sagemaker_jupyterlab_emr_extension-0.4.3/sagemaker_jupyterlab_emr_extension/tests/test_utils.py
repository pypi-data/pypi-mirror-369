import unittest
import botocore

from unittest.mock import patch, MagicMock

from sagemaker_jupyterlab_emr_extension.utils.utils import (
    get_regional_service_endpoint_url,
    get_credential,
)

ASSUME_ROLE_RESPONSE = {
    "Credentials": {
        "AccessKeyId": "id",
        "SecretAccessKey": "key",
        "SessionToken": "token",
        "Expiration": "2021-11-15T21:52:45Z",
    },
    "PackedPolicySize": 15,
}


class TestUtils(unittest.TestCase):

    @patch(
        "sagemaker_jupyterlab_emr_extension.utils.utils.USE_DUALSTACK_ENDPOINT", False
    )
    def test_get_regional_service_endpoint_url_ipv4(self):
        test_cases = [
            ("us-west-2", "https://sts.us-west-2.amazonaws.com"),
            ("cn-north-1", "https://sts.cn-north-1.amazonaws.com.cn"),
            ("us-gov-west-1", "https://sts.us-gov-west-1.amazonaws.com"),
            ("us-isof-east-1", "https://sts.us-isof-east-1.csp.hci.ic.gov"),
        ]

        for region, expected_url in test_cases:
            with self.subTest(region=region):
                session = botocore.session.get_session()
                url = get_regional_service_endpoint_url(session, "sts", region)
                self.assertEqual(url, expected_url)

    @patch(
        "sagemaker_jupyterlab_emr_extension.utils.utils.USE_DUALSTACK_ENDPOINT", True
    )
    def test_get_regional_service_endpoint_url_dualstack(self):
        test_cases = [
            ("us-west-2", "https://sts.us-west-2.api.aws"),
            ("cn-north-1", "https://sts.cn-north-1.api.amazonwebservices.com.cn"),
            ("us-gov-west-1", "https://sts.us-gov-west-1.api.aws"),
            # 'aws-iso', 'aws-iso-b' are not unsupported dualstack partitions.
            # ref: https://github.com/boto/botocore/blob/37e49668d11ffe66ca03d1e20d01b288512af457/botocore/regions.py#L118
            # ("us-isof-east-1", "https://sts.us-isof-east-1.csp.hci.ic.gov"),
        ]

        for region, expected_url in test_cases:
            with self.subTest(region=region):
                session = botocore.session.get_session()
                url = get_regional_service_endpoint_url(session, "sts", region)
                self.assertEqual(url, expected_url)

    @patch(
        "sagemaker_jupyterlab_emr_extension.utils.utils.get_regional_service_endpoint_url"
    )
    @patch("botocore.session.get_session")
    def test_get_credential(
        self, mock_get_session, mock_get_regional_service_endpoint_url
    ):
        mock_session = MagicMock()
        mock_get_session.return_value = mock_session

        mock_sts_client = MagicMock()
        mock_session.create_client.return_value = mock_sts_client

        mock_get_regional_service_endpoint_url.return_value = (
            "https://sts.us-west-2.amazonaws.com"
        )
        mock_sts_client.assume_role.return_value = ASSUME_ROLE_RESPONSE

        dummy_role_arn = "role_arn"
        credentials = get_credential(dummy_role_arn, "us-west-2")

        mock_sts_client.assume_role.assert_called_with(
            RoleArn=dummy_role_arn, RoleSessionName="SagemakerAssumableSession"
        )
        assert credentials == ASSUME_ROLE_RESPONSE["Credentials"]
