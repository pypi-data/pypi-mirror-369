# -*- coding: utf-8 -*-

"""
Bucket related API.

.. _bsm: https://github.com/aws-samples/boto-session-manager-project
.. _create_bucket: https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/s3/client/create_bucket.html

"""

import typing as T

from func_args import NOTHING, resolve_kwargs

from ..aws import context
from ..marker import warn_beta
from ..validate import validate_s3_bucket
from .resolve_s3_client import resolve_s3_client


if T.TYPE_CHECKING:  # pragma: no cover
    from .s3path import S3Path
    from boto_session_manager import BotoSesManager
    from mypy_boto3_s3 import S3Client


class BucketAPIMixin:
    """
    A mixin class that implements the bucket related methods.
    """

    @classmethod
    def from_bucket(
        cls: T.Type["S3Path"],
        bucket: str,
    ) -> "S3Path":
        """
        Create an S3Path object from a bucket name.
        """
        validate_s3_bucket(bucket)
        return cls(f"s3://{bucket}/")

    def create_bucket(
        self: "S3Path",
        region: str = "us-east-1",
        acl: str = NOTHING,
        grant_full_control: str = NOTHING,
        grant_read: str = NOTHING,
        grant_read_acp: str = NOTHING,
        grant_write: str = NOTHING,
        grant_write_acp: str = NOTHING,
        object_lock_enabled_for_bucket: bool = NOTHING,
        object_ownership: str = NOTHING,
        bsm: T.Optional[T.Union["BotoSesManager", "S3Client"]] = None,
    ) -> dict:
        """
        Create an S3 bucket.
        """
        warn_beta("S3Path.create_bucket")
        self.ensure_bucket()
        if region == "us-east-1":
            create_bucket_configuration = NOTHING
        else:
            create_bucket_configuration = dict(LocationConstraint=region)
        s3_client = resolve_s3_client(context, bsm)
        response = s3_client.create_bucket(
            **resolve_kwargs(
                Bucket=self.bucket,
                ACL=acl,
                CreateBucketConfiguration=create_bucket_configuration,
                GrantFullControl=grant_full_control,
                GrantRead=grant_read,
                GrantReadACP=grant_read_acp,
                GrantWrite=grant_write,
                GrantWriteACP=grant_write_acp,
                ObjectLockEnabledForBucket=object_lock_enabled_for_bucket,
                ObjectOwnership=object_ownership,
            ),
        )
        return response

    def delete_bucket(
        self: "S3Path",
        expected_bucket_owner: str = NOTHING,
        bsm: T.Optional[T.Union["BotoSesManager", "S3Client"]] = None,
    ):
        """
        Delete an S3 bucket.
        """
        self.ensure_bucket()
        s3_client = resolve_s3_client(context, bsm)
        response = s3_client.delete_bucket(
            **resolve_kwargs(
                Bucket=self.bucket,
                ExpectedBucketOwner=expected_bucket_owner,
            ),
        )
        self.clear_cache()
        return response

    def get_bucket_versioning(
        self: "S3Path",
        expected_bucket_owner: str = NOTHING,
        bsm: T.Optional[T.Union["BotoSesManager", "S3Client"]] = None,
    ) -> dict:
        """
        Get the versioning state of an S3 bucket.
        """
        self.ensure_bucket()
        s3_client = resolve_s3_client(context, bsm)
        response = s3_client.get_bucket_versioning(
            **resolve_kwargs(
                Bucket=self.bucket,
                ExpectedBucketOwner=expected_bucket_owner,
            ),
        )
        return response

    def is_versioning_enabled(
        self: "S3Path",
        bsm: T.Optional[T.Union["BotoSesManager", "S3Client"]] = None,
    ) -> bool:
        """
        Check if the versioning of an S3 bucket is enabled.
        """
        res = self.get_bucket_versioning(bsm=bsm)
        return res.get("Status", "UNKNOWN") == "Enabled"

    def is_versioning_suspended(
        self: "S3Path",
        bsm: T.Optional[T.Union["BotoSesManager", "S3Client"]] = None,
    ) -> bool:
        """
        Check if the versioning of an S3 bucket is suspended.
        """
        res = self.get_bucket_versioning(bsm=bsm)
        return res.get("Status", "UNKNOWN") == "Suspended"

    def put_bucket_versioning(
        self: "S3Path",
        enable_versioning: bool,
        enable_mfa_delete: bool = NOTHING,
        check_sum_algorithm: str = NOTHING,
        mfa: str = NOTHING,
        expected_bucket_owner: str = NOTHING,
        bsm: T.Optional[T.Union["BotoSesManager", "S3Client"]] = None,
    ) -> dict:
        """
        Enable or suspend S3 bucket versioning.
        """
        self.ensure_bucket()
        s3_client = resolve_s3_client(context, bsm)
        if enable_versioning:
            enable_versioning = "Enabled"
        else:
            enable_versioning = "Suspended"
        if enable_mfa_delete is not NOTHING:  # pragma: no cover
            if enable_mfa_delete:
                enable_versioning = "Enabled"
            else:
                enable_versioning = "Disabled"
        versioning_configuration = resolve_kwargs(
            MFADelete=enable_mfa_delete,
            Status=enable_versioning,
        )
        response = s3_client.put_bucket_versioning(
            **resolve_kwargs(
                Bucket=self.bucket,
                ChecksumAlgorithm=check_sum_algorithm,
                VersioningConfiguration=versioning_configuration,
                MFA=mfa,
                ExpectedBucketOwner=expected_bucket_owner,
            ),
        )
        return response

    @classmethod
    def list_buckets(
        cls: T.Type["S3Path"],
        bsm: T.Optional[T.Union["BotoSesManager", "S3Client"]] = None,
    ) -> T.List["S3Path"]:
        """
        List all S3 buckets.
        """
        s3_client = resolve_s3_client(context, bsm)
        response = s3_client.list_buckets()
        s3bucket_list = list()
        for dct in response.get("Buckets", []):
            s3bucket = cls.from_bucket(dct["Name"])
            s3bucket._meta = {"LastModified": dct["CreationDate"]}
            s3bucket_list.append(s3bucket)
        return s3bucket_list
