import json
import os
from alibabacloud_ims_editing_mcp_server.tools.tool_registration import *
from alibabacloud_ims_editing_mcp_server.client import get_oss_client
import alibabacloud_oss_v2 as oss
import re
from urllib.parse import urlparse
from datetime import timedelta
import logging

logger = logging.getLogger("ims-editing-mcp.log")

oss_client = get_oss_client()


@register_level_tools(basic_tool, trial_tool, tool_info={
    'tags': {'获取用户当前区域bucket列表'}
})
def get_oss_bucket_list() -> str:
    """
        <tags>'获取用户当前区域bucket列表'</tags>
        <toolDescription>
            该工具主要功能是获取用户当前区域的bucket列表，用于设置剪辑成片的输出地址。
            需要用户授权调用账号的ak有OSS相关权限才能获取，如果没有权限，先建议用户给调用ak授权OSS权限，客户也可以选择自行指定输出oss bucket。
        </toolDescription>
        <return>用户当前区域bucket列表</return>
    """
    try:
        results = []
        paginator = oss_client.list_buckets_paginator()
        region_id = os.getenv('ALIBABA_CLOUD_REGION')

        for page in paginator.iter_page(oss.ListBucketsRequest()):
            for o in page.buckets:
                if o.location == "oss-" + region_id:
                    results.append(o.name)
        return json.dumps({"bucket_list": results})
    except oss.exceptions.OperationError as err:
        logger.error(err)
        return "you are forbidden to list oss bucket because access denied, please specify the output oss bucket yourself."
    except Exception as error:
        logger.exception(error)
        return "get_oss_bucket_list failed, please specify the output oss bucket yourself."


def get_signed_oss_url(media_url: str) -> str:
    try:
        bucket, key = parse_oss_url(media_url)
        if not oss_client.is_object_exist(bucket, key):
            return media_url
        else:
            pre_result = oss_client.presign(
                oss.GetObjectRequest(
                    bucket=bucket,
                    key=key,
                ),
                expires=timedelta(hours=1)
            )
            return pre_result.url
    except Exception as e:
        logger.error(e)
        return media_url


def parse_oss_url(url: str):
    parsed = urlparse(url)

    host = parsed.netloc
    bucket_match = re.match(r'([^.]+)\.oss-[^.]+\.aliyuncs\.com', host)
    if not bucket_match:
        return None, None
    bucket_name = bucket_match.group(1)

    path = parsed.path.strip('/')
    object_key = path or None

    return bucket_name, object_key
