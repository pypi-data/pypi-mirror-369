# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: Apache-2.0

"""tag related logic module"""

import logging

logging.basicConfig()
logger = logging.getLogger("sm_resource_tag")
logger.setLevel(logging.INFO)


class ResourceTagRetriever:
    """Class used to retrieve different types of tags."""

    def __init__(self, client):
        self._client = client

    # this method will propagate the exception for client to handle
    def get_space_tags(self, domain_id, space_name):
        """Get shared space tags for specific space.

        :param domain_id: domain id
        :param space_name: space name
        :return: tags dict
        """
        response = self._client.describe_space(DomainId=domain_id, SpaceName=space_name)
        res_arn = response["SpaceArn"]
        tags = self._get_resource_tags(res_arn)

        # add user profile arn as internal tag.
        tags["sagemaker:space-arn"] = res_arn
        return tags

    # this method will propagate the exception for client to handle
    def get_domain_tags(self, domain_id):
        """Get domain level tags.

        :param domain_id: domain id
        :return: tags dict.
        """
        response = self._client.describe_domain(DomainId=domain_id)
        domain_arn = response["DomainArn"]

        # We will enable the domain level customer tagging along with an opt-in mechanism.
        # For now we only attach the domain arn.
        # tags = self._get_resource_tags(domain_arn)
        tags = {}

        # add domain arn as internal tag.
        tags["sagemaker:domain-arn"] = domain_arn
        return tags

    # return map of key and value
    def _get_resource_tags(self, res_arn):
        """Internal logic to get tags for specific resource arn"""
        tags_response = self._client.list_tags(ResourceArn=res_arn)

        tags = tags_response.get("Tags", {})

        # filter any "aws:" internal tags, this is needed because Looseleaf adds aws: tags for
        # beta & gamma stacks
        sanitized_tags = [tag for tag in tags if not tag["Key"].startswith("aws:")]
        logger.info("Sanitized resource tags for %s - %s", res_arn, sanitized_tags)

        return self._convert_to_flatten_dict(sanitized_tags)

    def _convert_to_flatten_dict(self, list_of_dicts):
        """Flatten the tag dict

        Method to convert from:
           [{"Key": "tag1", "Value": "value1"}, {"Key": "tag2", "Value": "value2"}]
        to:
           {"tag1": "value1", "tag2":"value2"}
        """

        result_dict = {}
        for entry in list_of_dicts:
            key = entry["Key"]
            value = entry["Value"]
            result_dict[key] = value
        return result_dict
