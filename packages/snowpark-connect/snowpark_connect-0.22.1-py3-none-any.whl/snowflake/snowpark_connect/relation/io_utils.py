#
# Copyright (c) 2012-2025 Snowflake Computing Inc. All rights reserved.
#

from urllib.parse import urlparse

CLOUD_PREFIX_TO_CLOUD = {
    "abfss": "azure",
    "wasbs": "azure",
}


def get_cloud_from_url(
    url: str,
):
    """
    Google Cloud Storage : 'gcs://<bucket>[/<path>/]'
    Microsoft Azure : 'azure://<account>.blob.core.windows.net/<container>[/<path>/]'
    """
    url_parts = url.split("://")
    if len(url_parts) < 2:
        return None

    cloud_domain = url_parts[0].lower()
    return CLOUD_PREFIX_TO_CLOUD.get(cloud_domain, cloud_domain)


def split_url_paths(url):
    return url.split("://")[1].split("/")


def parse_gcp_url(url: str):
    """

    Args:
        url: 'gcs://<bucket>[/<path>/]'

    """
    path_parts = split_url_paths(url)
    bucket_name = path_parts[0]
    path = "/".join(path_parts[1:])
    return bucket_name, path


def parse_azure_url(url: str):
    """

    Args:
        url: 'azure://<account>.blob.core.windows.net/<container>[/<path>/]'
        url: "abfss://<container-name>@<storage-account-name>.dfs.core.windows.net/<path-to-data>"

    """
    path_parts = split_url_paths(url)
    prefix = path_parts[0].split(".")[0].split("@")
    account = prefix[1]
    bucket_name = prefix[0]
    path = "/".join(path_parts[1:])
    return account, bucket_name, path


def is_cloud_path(path: str) -> bool:
    return (
        path.startswith("@")  # Snowflake Stage
        or path.startswith("s3://")
        or path.startswith("s3a://")  # AWS S3
        or path.startswith("azure://")
        or path.startswith("abfss://")
        or path.startswith("wasbs://")  # Azure
        or path.startswith("gcs://")  # GCP
    )


def convert_file_prefix_path(path: str) -> str:
    if path.startswith("file:/"):
        return urlparse(path).path
    return path
