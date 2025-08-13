# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: Apache-2.0

"""client module"""
import boto3

STAGE_MAPPING = {"devo": "beta", "loadtest": "gamma"}


class SageMakerClient:
    """Sagemaker client wrapper provides convenient method for creating sagemaker client."""

    @staticmethod
    def create_instance(region_name=None, stage=None):
        """Static method to create sagemaker client.

        :param region_name: region name
        :param stage: stage which is used to support non-prod stages.
        :return: sagemaker client
        """
        create_client_args = {"service_name": "sagemaker", "region_name": region_name}

        if stage and region_name and stage != "prod":
            endpoint_stage = STAGE_MAPPING[stage.lower()]
            # fmt: off
            create_client_args["endpoint_url"] = (
                f"https://sagemaker.{endpoint_stage}.{region_name}.ml-platform.aws.a2z.com"
            )
            # fmt: on

        session = boto3.session.Session()
        return session.client(**create_client_args)
