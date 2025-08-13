import unittest
from unittest.mock import patch
from sagemaker_kernel_wrapper.client import SageMakerClient


class TestSageMakerClient(unittest.TestCase):
    @patch("boto3.session.Session.client")
    def test_create_instance(self, mock_client):
        # stage is None
        client = SageMakerClient.create_instance(region_name="us-west-2")
        self.assertTrue(mock_client.called)
        self.assertEqual(client, mock_client.return_value)

        # stage is 'prod'
        client = SageMakerClient.create_instance(region_name="us-west-2", stage="prod")
        self.assertTrue(mock_client.called)
        self.assertEqual(client, mock_client.return_value)

    @patch("boto3.session.Session.client")
    def test_create_instance_gamma(self, mock_client):
        # loadtest
        client = SageMakerClient.create_instance(region_name="us-west-2", stage="loadtest")
        self.assertTrue(mock_client.called)
        self.assertEqual(client, mock_client.return_value)
        mock_client.assert_called_once_with(
            service_name="sagemaker",
            region_name="us-west-2",
            endpoint_url="https://sagemaker.gamma.us-west-2.ml-platform.aws.a2z.com",
        )

    @patch("boto3.session.Session.client")
    def test_create_instance_devo(self, mock_client):
        # devo
        client = SageMakerClient.create_instance(region_name="us-west-2", stage="devo")
        self.assertTrue(mock_client.called)
        self.assertEqual(client, mock_client.return_value)
        mock_client.assert_called_once_with(
            service_name="sagemaker",
            region_name="us-west-2",
            endpoint_url="https://sagemaker.beta.us-west-2.ml-platform.aws.a2z.com",
        )
