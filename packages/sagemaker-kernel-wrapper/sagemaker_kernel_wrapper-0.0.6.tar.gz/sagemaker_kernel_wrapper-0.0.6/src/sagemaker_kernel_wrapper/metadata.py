# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: Apache-2.0

"""metadata module used to read Sagemaker's metadata"""
import json

# This is a public contract - https://docs.aws.amazon.com/sagemaker/latest/dg/notebooks-run-and
# -manage-metadata.html#notebooks-run-and-manage-metadata-app
APP_METADATA_FILE_LOCATION = "/opt/ml/metadata/resource-metadata.json"

# Internal metadata which is not part of public contract.
SAGEMAKER_INTERNAL_METADATA_FILE = "/opt/.sagemakerinternal/internal-metadata.json"


class AppMetadata:
    """Singleton App metadata access class."""

    _instance = None

    def __init__(self, app_metadata=APP_METADATA_FILE_LOCATION):
        with open(app_metadata, "r") as file:
            self.metadata = json.load(file)

    # singleton to avoid unnecessary reloading
    def __new__(cls, *args, **kwargs):
        """Static new method to enable singleton."""
        if cls._instance is None:
            cls._instance = super().__new__(cls, *args, **kwargs)
        return cls._instance

    def _get_app_arn(self) -> str:
        """Get app arn

        :return: application arn id.
        """
        return self.metadata["ResourceArn"]

    def get_partition(self):
        """Get aws partition value.

        :return: partition string value.
        """
        return self._get_app_arn().split(":")[1]

    def get_region_name(self):
        """Get region name

        :return: region string value
        """
        return self._get_app_arn().split(":")[3]

    def get_aws_account_id(self):
        """Get aws account id from the metadata file.

        :return: account id string.
        """
        return self._get_app_arn().split(":")[4]

    def get_space_name(self):
        """Get space name.

        :return: space name as string
        """
        return self.metadata.get("SpaceName", "")

    def get_domain_id(self):
        """Get domain id

        :return: domain value as string
        """
        return self.metadata.get("DomainId")

    def get_exec_role_arn(self):
        """Get execution role arn

        :return: execution role arn value as string
        """
        return self.metadata.get("ExecutionRoleArn", None)


class InternalMetadata:
    """Internal metadata access class."""

    _instance = None

    def __init__(self, app_metadata=SAGEMAKER_INTERNAL_METADATA_FILE):
        with open(app_metadata, "r") as file:
            self.metadata = json.load(file)

    def __new__(cls, *args, **kwargs):
        """Static new method to enable singleton."""
        if cls._instance is None:
            cls._instance = super().__new__(cls, *args, **kwargs)
        return cls._instance

    def get_stage(self) -> str:
        """Get stage internal field.

        :return: string value of the stage
        """
        return self.metadata["Stage"]
