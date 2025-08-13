import unittest
from unittest.mock import mock_open, patch

from sagemaker_kernel_wrapper.metadata import InternalMetadata

# Test data
SAGEMAKER_INTERNAL_METADATA_FILE_CONTENT = '{"Stage": "prod"}'


class TestInternalMetadata(unittest.TestCase):
    @patch("builtins.open", mock_open(read_data=SAGEMAKER_INTERNAL_METADATA_FILE_CONTENT))
    def test_get_stage(self):
        underTest = InternalMetadata()
        self.assertEqual(underTest.get_stage(), "prod")

    @patch("builtins.open", mock_open(read_data=SAGEMAKER_INTERNAL_METADATA_FILE_CONTENT))
    def test_singleton_instance(self):
        # Ensure that the instance is singleton
        internal_metadata_1 = InternalMetadata()
        internal_metadata_2 = InternalMetadata()
        self.assertIs(internal_metadata_1, internal_metadata_2)
