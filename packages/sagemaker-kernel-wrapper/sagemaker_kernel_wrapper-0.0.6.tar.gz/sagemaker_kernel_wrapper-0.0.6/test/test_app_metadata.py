import unittest
from unittest.mock import mock_open, patch

from sagemaker_kernel_wrapper.metadata import AppMetadata

# Test data
APP_METADATA_FILE_CONTENT = (
    '{"AppType": "KernelGateway",'
    '"DomainId": "d-fnytsoocmwo1",'
    '"ExecutionRoleArn":"arn:aws:iam::177118115371:role/service-role/test-exec-role",'
    '"ResourceArn": "arn:aws:sagemaker:us-east-1:177118115371:app/d-fnytsoocmwo1/tag-testing/'
    'KernelGateway/sagemaker-data-scienc-ml-t3-medium-ccb588b5efaf671be41927273f0c",    '
    '"ResourceName": "sagemaker-data-scienc-ml-t3-medium-ccb588b5efaf671be41927273f0c",    '
    '"AppImageVersion": "",    '
    '"SpaceName": "my_space"}'
)


class TestAppMetadata(unittest.TestCase):
    @patch("builtins.open", mock_open(read_data=APP_METADATA_FILE_CONTENT))
    def test_get_partition(self):
        under_test = AppMetadata()
        self.assertEqual(under_test.get_partition(), "aws")

    @patch("builtins.open", mock_open(read_data=APP_METADATA_FILE_CONTENT))
    def test_get_region_name(self):
        under_test = AppMetadata()
        self.assertEqual(under_test.get_region_name(), "us-east-1")

    @patch("builtins.open", mock_open(read_data=APP_METADATA_FILE_CONTENT))
    def test_get_aws_account_id(self):
        under_test = AppMetadata()
        self.assertEqual(under_test.get_aws_account_id(), "177118115371")

    @patch("builtins.open", mock_open(read_data=APP_METADATA_FILE_CONTENT))
    def test_get_space_name(self):
        under_test = AppMetadata()
        self.assertEqual(under_test.get_space_name(), "my_space")

    @patch("builtins.open", mock_open(read_data=APP_METADATA_FILE_CONTENT))
    def test_get_domain_id(self):
        under_test = AppMetadata()
        self.assertEqual(under_test.get_domain_id(), "d-fnytsoocmwo1")

    @patch("builtins.open", mock_open(read_data=APP_METADATA_FILE_CONTENT))
    def test_get_exec_role_arn(self):
        under_test = AppMetadata()
        self.assertEqual(
            under_test.get_exec_role_arn(),
            "arn:aws:iam::177118115371:role/service-role/test-exec-role",
        )

    @patch("builtins.open", mock_open(read_data=APP_METADATA_FILE_CONTENT))
    def test_singleton(self):
        self.assertIs(AppMetadata(), AppMetadata())


if __name__ == "__main__":
    unittest.main()
