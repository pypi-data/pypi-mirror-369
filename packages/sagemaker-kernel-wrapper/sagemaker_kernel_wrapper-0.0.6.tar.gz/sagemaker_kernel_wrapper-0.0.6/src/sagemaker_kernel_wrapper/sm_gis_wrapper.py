# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: Apache-2.0

"""gis wrapper logic"""

import os
import sys

import json
import logging
import boto3

from sagemaker_kernel_wrapper.client import SageMakerClient
from sagemaker_kernel_wrapper.metadata import AppMetadata, InternalMetadata
from sagemaker_kernel_wrapper.resource_tag import ResourceTagRetriever


AWS_GLUE_TAGS = "glue_tags"

logging.basicConfig()
logger = logging.getLogger("sm_gis_wrapper")
logger.setLevel(logging.INFO)


def _get_tags_string(tag_retriever, domain_id, space_name):
    """Get tags and format into the string needed by GIS."""
    try:
        user_or_space_tags = {}
        if len(space_name) > 0:
            user_or_space_tags = tag_retriever.get_space_tags(
                domain_id=domain_id, space_name=space_name
            )

        domain_tags = tag_retriever.get_domain_tags(domain_id=domain_id)

        # lower level take precedence
        tags = {**domain_tags, **user_or_space_tags}

        return json.dumps(tags)
    except Exception as error:  # pylint: disable=W0703
        # catch all possible exceptions. Tagging related failure should not affect GIS kernel
        # creation
        err_msg = (
            f"Error while preparing SageMaker Studio tags. No tags from domain, "
            f"user profile or space are propagated. This does not block Glue Interactive "
            f"Session kernel launch and Glue session still functions. Error: {error}"
        )
        logger.warning(err_msg)
        # return empty map string so that no tag gets propagated to Glue
        return "{}"


def get_sagemaker_client(app_medata):
    region = app_medata.get_region_name()
    stage = InternalMetadata().get_stage()
    return SageMakerClient.create_instance(region_name=region, stage=stage)


def exec_kernel():
    """Wrapper kernel entry."""
    # only run if the notebook is running within studio, otherwise AppMetadata call will fail
    if "SM_JOB_DEF_VERSION" not in os.environ:
        app_medata = AppMetadata()

        try:
            client = get_sagemaker_client(app_medata)
            tag_retriever = ResourceTagRetriever(client)

            tags_str = _get_tags_string(
                tag_retriever,
                app_medata.get_domain_id(),
                app_medata.get_space_name(),
            )
            os.environ[AWS_GLUE_TAGS] = tags_str
            logger.info("AWS_GLUE_TAGS from SageMaker Studio: %s.", tags_str)

            # Set execution role arn as environment variable AWS_GLUE_ROLE_ARN
            aws_glue_role_arn = app_medata.get_exec_role_arn()
            if aws_glue_role_arn is not None:
                logger.info(
                    "Setting environment variable named glue_role_arn with value %s",
                    aws_glue_role_arn,
                )
                os.environ["glue_role_arn"] = aws_glue_role_arn
            else:
                logger.warning(
                    "Unable to set environment variable named glue_role_arn. "
                    "The value is None or empty string."
                )
        except Exception as error:
            err_msg = (
                f"Error creating SageMaker client. This does not block Glue Interactive "
                f"Session kernel launch and Glue session still functions. Error: {error}"
            )
            logger.warning(err_msg)

    sys.argv[0] = sys.executable
    logger.info("Running Glue Kernel: %s boto3 version: %s", sys.argv, boto3.__version__)
    os.execvp(sys.argv[0], sys.argv)


if __name__ == "__main__":
    exec_kernel()
