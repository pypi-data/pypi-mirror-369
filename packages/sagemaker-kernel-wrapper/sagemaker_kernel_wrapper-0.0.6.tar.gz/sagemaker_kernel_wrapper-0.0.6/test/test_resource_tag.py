import unittest
from unittest.mock import Mock

from sagemaker_kernel_wrapper.resource_tag import ResourceTagRetriever


class TestResourceTagRetriever(unittest.TestCase):
    def setUp(self):
        # Create a mock Boto3 client for testing
        self.mock_client = Mock()
        self.tag_retriever = ResourceTagRetriever(self.mock_client)

    def test_get_space_tags(self):
        space_arn = "arn:aws:sagemaker:us-west-2:123456789012:domain/domain-123/space/space-123"
        self.mock_client.describe_space.return_value = {"SpaceArn": space_arn}
        self.mock_client.list_tags.return_value = {
            "Tags": [
                {"Key": "tag1", "Value": "value1"},
                {"Key": "tag2", "Value": "value2"},
                {
                    "Key": "aws:internal-tag",
                    "Value": "internal-value",
                },  # An "aws:" internal tag
            ]
        }

        # Call the method under test
        tags = self.tag_retriever.get_space_tags("domain-123", "space-123")

        # Assert the expected results
        self.assertEqual(
            tags, {"tag1": "value1", "tag2": "value2", "sagemaker:space-arn": space_arn}
        )

    def test_get_domain_tags(self):
        mock_client = Mock()
        mock_client.describe_domain.return_value = {
            "DomainArn": "arn:aws:sagemaker:us-west-2:123456789012:domain/test-domain",
        }

        # mock_client.list_tags.return_value = {
        #     "Tags": [
        #         {"Key": "tag1", "Value": "value1"},
        #         {"Key": "tag2", "Value": "value2"},
        #         {
        #             "Key": "aws:internal-tag",
        #             "Value": "internal-value",
        #         },  # An "aws:" internal tag
        #     ]
        # }

        tag_retriever = ResourceTagRetriever(mock_client)
        tags = tag_retriever.get_domain_tags("test-domain")

        expected_tags = {
            "sagemaker:domain-arn": "arn:aws:sagemaker:us-west-2:123456789012:domain/test-domain",
        }

        self.assertEqual(tags, expected_tags)
        mock_client.describe_domain.assert_called_once_with(DomainId="test-domain")
        # mock_client.list_tags.assert_called_once_with(
        #     ResourceArn="arn:aws:sagemaker:us-west-2:123456789012:domain/test-domain"
        # )
