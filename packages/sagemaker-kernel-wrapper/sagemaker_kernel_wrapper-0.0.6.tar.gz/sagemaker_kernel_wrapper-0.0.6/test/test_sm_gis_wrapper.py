import unittest
from unittest.mock import patch, call
import json
import sys
import os

from sagemaker_kernel_wrapper.sm_gis_wrapper import _get_tags_string
from sagemaker_kernel_wrapper.sm_gis_wrapper import exec_kernel


class TestGetTagsString(unittest.TestCase):
    @patch("sagemaker_kernel_wrapper.sm_gis_wrapper.ResourceTagRetriever")
    def test_get_tags_string_space(
        self,
        mock_tag_retriever,
    ):
        mock_tag_retriever_instance = mock_tag_retriever.return_value

        mock_tag_retriever_instance.get_domain_tags.return_value = {
            "tag1": "value1",
            "tag2": "value2",
        }

        mock_tag_retriever_instance.get_space_tags.return_value = {
            "tag2": "value2_override",
            "tag3": "value3",
        }

        # Call the function under test
        result = _get_tags_string(mock_tag_retriever_instance, "domain-123", "myspace")

        # Assert the expected result and interactions with dependencies
        self.assertEqual(
            result,
            json.dumps(
                {
                    "tag1": "value1",
                    "tag2": "value2_override",
                    "tag3": "value3",
                }
            ),
        )
        mock_tag_retriever_instance.get_space_tags.assert_called_once_with(
            domain_id="domain-123", space_name="myspace"
        )
        mock_tag_retriever_instance.get_domain_tags.assert_called_once_with(domain_id="domain-123")


class TestExecKernel(unittest.TestCase):
    def setUp(self):
        self.original_env = dict(os.environ)

    def tearDown(self):
        os.environ.clear()
        os.environ.update(self.original_env)

    @patch("sagemaker_kernel_wrapper.sm_gis_wrapper.ResourceTagRetriever")
    @patch("sagemaker_kernel_wrapper.sm_gis_wrapper.AppMetadata")
    @patch("sagemaker_kernel_wrapper.sm_gis_wrapper.InternalMetadata")
    @patch("sagemaker_kernel_wrapper.sm_gis_wrapper._get_tags_string")
    @patch("sagemaker_kernel_wrapper.sm_gis_wrapper.os")
    def test_exec_kernel(
        self,
        mock_os,
        mock_get_tags_string,
        mock_internal_metadata,
        mock_app_metadata,
        mock_tag_retriever,
    ):
        app_metadata_instance = mock_app_metadata.return_value
        app_metadata_instance.get_space_name.return_value = "myspace"
        app_metadata_instance.get_user_profile_name.return_value = "user-profile-123"
        app_metadata_instance.get_domain_id.return_value = "domain-123"
        app_metadata_instance.get_region_name.return_value = "us-west-2"
        app_metadata_instance.get_exec_role_arn.return_value = "execution-role-arn"
        mock_internal_metadata_instance = mock_internal_metadata.return_value
        mock_internal_metadata_instance.get_stage.return_value = "prod"
        mock_tag_retriever_instance = mock_tag_retriever.return_value

        mock_get_tags_string.return_value = '{"key": "value"}'

        # Call the function under test
        exec_kernel()

        # Assert the expected interactions with dependencies
        mock_get_tags_string.assert_called_once()
        mock_os.environ.__setitem__.assert_has_calls(
            [
                call("glue_tags", '{"key": "value"}'),
                call("glue_role_arn", "execution-role-arn"),
            ]
        )
        mock_os.execvp.assert_called_once_with(sys.argv[0], sys.argv)
        mock_get_tags_string.assert_called_once_with(
            mock_tag_retriever_instance, "domain-123", "myspace"
        )

    @patch("sagemaker_kernel_wrapper.sm_gis_wrapper.ResourceTagRetriever")
    @patch("sagemaker_kernel_wrapper.sm_gis_wrapper.AppMetadata")
    @patch("sagemaker_kernel_wrapper.sm_gis_wrapper.InternalMetadata")
    @patch("sagemaker_kernel_wrapper.sm_gis_wrapper._get_tags_string")
    @patch("sagemaker_kernel_wrapper.sm_gis_wrapper.os")
    @patch("sagemaker_kernel_wrapper.sm_gis_wrapper.logger")
    def test_exec_kernel_for_simulated_job_case(
        self,
        mock_logger,
        mock_os,
        mock_get_tags_string,
        mock_internal_metadata,
        mock_app_metadata,
        mock_tag_retriever,
    ):
        app_metadata_instance = mock_app_metadata.return_value
        app_metadata_instance.get_space_name.return_value = "myspace"
        app_metadata_instance.get_user_profile_name.return_value = "user-profile-123"
        app_metadata_instance.get_domain_id.return_value = "domain-123"
        app_metadata_instance.get_region_name.return_value = "us-west-2"
        app_metadata_instance.get_exec_role_arn.return_value = "execution-role-arn"
        mock_internal_metadata_instance = mock_internal_metadata.return_value
        mock_internal_metadata_instance.get_stage.return_value = "prod"
        mock_tag_retriever_instance = mock_tag_retriever.return_value

        # Mock that SM_JOB_DEF_VERSION is in the environment
        def contains_side_effect(key):
            return key == "SM_JOB_DEF_VERSION"

        mock_os.environ.__contains__.side_effect = contains_side_effect

        exec_kernel()
        mock_os.execvp.assert_called_once_with(sys.argv[0], sys.argv)
        mock_get_tags_string.assert_not_called()
        # Since SM_JOB_DEF_VERSION is in the environment, the code should not set glue_role_arn
        mock_os.environ.__setitem__.assert_not_called()

    @patch("sagemaker_kernel_wrapper.sm_gis_wrapper.ResourceTagRetriever")
    @patch("sagemaker_kernel_wrapper.sm_gis_wrapper.AppMetadata")
    @patch("sagemaker_kernel_wrapper.sm_gis_wrapper.InternalMetadata")
    @patch("sagemaker_kernel_wrapper.sm_gis_wrapper._get_tags_string")
    @patch("sagemaker_kernel_wrapper.sm_gis_wrapper.os")
    def test_exec_kernel_for_no_execution_role_arn(
        self,
        mock_os,
        mock_get_tags_string,
        mock_internal_metadata,
        mock_app_metadata,
        mock_tag_retriever,
    ):
        app_metadata_instance = mock_app_metadata.return_value
        app_metadata_instance.get_space_name.return_value = "myspace"
        app_metadata_instance.get_user_profile_name.return_value = "user-profile-123"
        app_metadata_instance.get_domain_id.return_value = "domain-123"
        app_metadata_instance.get_region_name.return_value = "us-west-2"
        app_metadata_instance.get_exec_role_arn.return_value = None
        mock_internal_metadata_instance = mock_internal_metadata.return_value
        mock_internal_metadata_instance.get_stage.return_value = "prod"
        mock_tag_retriever_instance = mock_tag_retriever.return_value

        mock_get_tags_string.return_value = '{"key": "value"}'

        # Call the function under test
        exec_kernel()

        # Assert the expected interactions with dependencies
        mock_get_tags_string.assert_called_once()
        mock_os.environ.__setitem__.assert_called_once_with("glue_tags", '{"key": "value"}')
        mock_os.execvp.assert_called_once_with(sys.argv[0], sys.argv)
        mock_get_tags_string.assert_called_once_with(
            mock_tag_retriever_instance, "domain-123", "myspace"
        )
