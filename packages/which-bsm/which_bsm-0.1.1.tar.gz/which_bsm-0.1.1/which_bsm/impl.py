# -*- coding: utf-8 -*-

"""
This module provides the entry point to access all boto session related logic
for managing AWS authentication across different environments and runtime contexts.

The ``BaseBotoSesEnum`` class serves as a factory for creating environment-specific
boto session managers, automatically selecting the appropriate authentication method
based on runtime detection (local, CI/CD, or AWS compute services).

All methods and properties use lazy loading for optimal performance.
"""

import typing as T
import os
import dataclasses
from functools import cached_property

from boto_session_manager import BotoSesManager


def get_aws_account_id_in_ci(env_name: str) -> str:
    """
    Retrieve the AWS account ID for the specified environment in CI.
    """
    key = f"{env_name.upper()}_AWS_ACCOUNT_ID"
    try:
        value = os.environ[key]
    except KeyError:
        raise KeyError(
            f"Environment variable '{key}' is not set. "
            "Make sure to set it in your CI environment to store the AWS account ID."
        )
    if len(value) != 12:
        raise ValueError(
            f"Invalid AWS account ID '{value}' for environment '{env_name}'. "
            "It should be a 12-digit number."
        )
    if not value.isdigit():
        raise ValueError(
            f"Invalid AWS account ID '{value}' for environment '{env_name}'. "
            "It should contain only digits."
        )
    return value


@dataclasses.dataclass
class BaseBotoSesEnum:
    """
    Base class for boto session enumeration.

    Provides configuration mapping between environments and AWS settings
    for managing boto sessions across different runtime contexts (local vs CI).
    Supports multiple AWS execution environments and runtime detection.

    :param env_to_aws_profile_mapper: Mapping from environment names to AWS CLI profile names
    :param env_to_aws_region_mapper: Mapping from environment names to AWS regions
    :param default_app_env_name: Default application environment name
    :param devops_env_name: DevOps environment name (cannot be same as default_app_env_name)
    :param workload_role_name_prefix_in_ci: Prefix for workload IAM role names in CI
    :param workload_role_name_suffix_in_ci: Suffix for workload IAM role names in CI
    :param is_local_runtime_group: Whether this configuration is for local development
    :param is_ci_runtime_group: Whether this configuration is for CI environment
    :param is_local: Whether running in local development environment
    :param is_cloud9: Whether running in AWS Cloud9 IDE environment
    :param is_ec2: Whether running on AWS EC2 instance
    :param is_lambda: Whether running in AWS Lambda function
    :param is_batch: Whether running in AWS Batch job
    :param is_esc: Whether running in AWS ECS (Elastic Container Service)
    :param is_glue: Whether running in AWS Glue job

    Example:
        Configuration for multi-environment setup::

            {
                "env_to_aws_profile_mapper": {"dev": "my-dev-profile", "prod": "my-prod-profile"},
                "env_to_aws_region_mapper": {"dev": "us-east-1", "prod": "us-west-2"},
                "default_app_env_name": "dev",
                "devops_env_name": "devops",
                "workload_role_name_prefix_in_ci": "WorkloadRole-",
                "workload_role_name_suffix_in_ci": "-Role",
                "is_local_runtime_group": true,
                "is_ci_runtime_group": false,
                "is_local": true,
                "is_cloud9": false,
                "is_ec2": false,
                "is_lambda": false,
                "is_batch": false,
                "is_esc": false,
                "is_glue": false
            }

    .. note::
        The devops_env_name must be different from default_app_env_name to maintain
        proper separation between application and operations environments.

        The runtime detection flags (is_local, is_cloud9, etc.) help determine
        the appropriate authentication method and session configuration for
        different AWS execution environments.
    """

    env_to_aws_profile_mapper: dict[str, str] = dataclasses.field()
    env_to_aws_region_mapper: dict[str, str] = dataclasses.field()
    default_app_env_name: str = dataclasses.field()
    devops_env_name: str = dataclasses.field()
    workload_role_name_prefix_in_ci: str = dataclasses.field()
    workload_role_name_suffix_in_ci: str = dataclasses.field()
    is_local_runtime_group: bool = dataclasses.field()
    is_ci_runtime_group: bool = dataclasses.field()
    is_local: bool = dataclasses.field()
    is_cloud9: bool = dataclasses.field()
    is_ec2: bool = dataclasses.field()
    is_lambda: bool = dataclasses.field()
    is_batch: bool = dataclasses.field()
    is_ecs: bool = dataclasses.field()
    is_glue: bool = dataclasses.field()

    def __post_init__(self):
        if self.default_app_env_name == self.devops_env_name:
            raise ValueError(
                f"default_app_env_name cannot be devops_env_name! "
                f"'{self.devops_env_name}' is NOT an app environment."
            )

    def get_workload_role_arn_in_ci(self, env_name: str) -> str:
        """
        Generate the workload IAM role ARN for the specified environment in CI.

        Constructs the full ARN for the workload role that should be assumed
        in CI environments for deployment operations. The role name is built
        using the configured prefix, environment name, and suffix.

        :param env_name: Target environment name for the workload role

        :returns: Complete IAM role ARN for the workload environment

        :raises ValueError: If env_name is the devops environment
        :raises KeyError: If AWS account ID environment variable is not set

        .. note::
            This method is primarily used in CI environments where AWS CLI
            profiles are not available. In local development, use AWS CLI
            named profiles instead.
        """
        if env_name == self.devops_env_name:
            raise ValueError(
                f"You cannot use the devops environment '{self.devops_env_name}' "
                f"to get workload role ARN in CI."
            )
        aws_account_id = os.environ[f"{env_name.upper()}_AWS_ACCOUNT_ID"]
        return (
            f"arn:aws:iam::{aws_account_id}:role/"
            f"{self.workload_role_name_prefix_in_ci}{env_name}{self.workload_role_name_suffix_in_ci}"
        )

    def get_workfload_role_session_name(self, env_name: str) -> str:  # pragma: no cover
        """
        Generate a session name for the workload role assumption.

        Creates a standardized session name format for role assumption operations.
        This helps with tracking and auditing role usage in AWS CloudTrail.

        :param env_name: Environment name to include in the session name

        :returns: Formatted session name for role assumption
        """
        return f"{env_name}_role_session"

    def get_aws_profile(self, env_name: str) -> str:
        try:
            return self.env_to_aws_profile_mapper[env_name]
        except KeyError:  # pragma: no cover
            raise KeyError(
                f"Environment '{env_name}' is not configured in env_to_aws_profile_mapper."
            )

    def get_aws_region(self, env_name: str) -> str:
        try:
            return self.env_to_aws_region_mapper[env_name]
        except KeyError:
            raise KeyError(
                f"Environment '{env_name}' is not configured in env_to_aws_region_mapper."
            )

    def get_devops_bsm_in_local(self) -> "BotoSesManager":  # pragma: no cover
        """
        Get the boto session manager for the DevOps environment in local runtime.
        """
        if self.is_cloud9:
            return BotoSesManager(
                region_name=self.get_aws_region(self.devops_env_name),
            )
        else:
            return BotoSesManager(
                profile_name=self.get_aws_profile(self.devops_env_name),
                region_name=self.get_aws_region(self.devops_env_name),
            )

    def get_devops_bsm_in_ci(self) -> "BotoSesManager":  # pragma: no cover
        """
        Get the boto session manager for the DevOps environment in CI runtime.
        """
        return BotoSesManager(
            region_name=self.get_aws_region(self.devops_env_name),
        )

    def get_devops_bsm(self) -> "BotoSesManager":  # pragma: no cover
        """
        Get the boto session manager for the DevOps environment based on the runtime group.
        """
        if self.is_local_runtime_group:
            return self.get_devops_bsm_in_local()
        elif self.is_ci_runtime_group:
            return self.get_devops_bsm_in_ci()
        else:  # pragma: no cover
            raise RuntimeError(
                "get_devops_bsm() should only be called in local or CI runtime groups."
            )

    @cached_property
    def bsm_devops(self) -> "BotoSesManager":  # pragma: no cover
        """
        Get the boto session manager for the DevOps environment.
        """
        return self.get_devops_bsm()

    def get_env_bsm_in_local(
        self,
        env_name: str,
    ) -> "BotoSesManager":  # pragma: no cover
        """
        Get the boto session manager for a specific environment in local runtime.
        """
        return BotoSesManager(
            profile_name=self.get_aws_profile(env_name),
            region_name=self.get_aws_region(env_name),
        )

    def get_env_bsm_in_ci(
        self,
        env_name: str,
        assume_role_kwargs: T.Optional[dict[str, T.Any]] = None,
    ) -> "BotoSesManager":  # pragma: no cover
        bsm_devops = self.get_devops_bsm()
        role_arn = self.get_workload_role_arn_in_ci(env_name)
        role_session_name = self.get_workfload_role_session_name(env_name)
        if assume_role_kwargs is None:
            assume_role_kwargs = {}
        bsm_workload = bsm_devops.assume_role(
            role_arn=role_arn,
            role_session_name=role_session_name,
            **assume_role_kwargs,
        )
        return bsm_workload

    def get_env_bsm(
        self,
        env_name: str,
        assume_role_kwargs: T.Optional[dict[str, T.Any]] = None,
    ) -> "BotoSesManager":
        """
        Get the boto session manager for a specific environment based on the runtime group.
        """
        if self.is_local_runtime_group:
            return self.get_env_bsm_in_local(env_name)
        elif self.is_ci_runtime_group:
            return self.get_env_bsm_in_ci(env_name, assume_role_kwargs)
        else:  # pragma: no cover
            raise RuntimeError(
                "get_env_bsm() should only be called in local or CI runtime groups."
            )

    def get_app_bsm(self) -> "BotoSesManager":
        """
        Get the boto session manager for the application environment.
        """
        return self.get_env_bsm(env_name=self.default_app_env_name)

    @cached_property
    def bsm_app(self) -> "BotoSesManager":
        """
        Get the boto session manager for the application environment.
        """
        return self.get_app_bsm()
