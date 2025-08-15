import os
from alibabacloud_ice20201109.client import Client as ICE20201109Client
from alibabacloud_tea_openapi import models as open_api_models
from alibabacloud_openapi_util.client import Client as OpenApiUtilClient
from alibabacloud_tea_util import models as util_models
import alibabacloud_oss_v2 as oss


def create_client() -> ICE20201109Client:
    access_key_id = os.getenv('ALIBABA_CLOUD_ACCESS_KEY_ID')
    access_key_secret = os.getenv('ALIBABA_CLOUD_ACCESS_KEY_SECRET')
    security_token = os.getenv('ALIBABA_CLOUD_SECURITY_TOKEN')
    region = os.getenv('ALIBABA_CLOUD_REGION')

    config = open_api_models.Config(
        access_key_id=access_key_id,
        access_key_secret=access_key_secret,
        security_token=security_token,
        region_id=region
    )

    config.endpoint = f'ice.{region}.aliyuncs.com'
    return ICE20201109Client(config)


def invoke_api(api_name: str, pay_load: dict, ice_client: ICE20201109Client):
    params = open_api_models.Params(
        action=api_name,
        version='2020-11-09',
        protocol='HTTPS',
        pathname='/',
        method='POST',
        auth_type='AK',
        style='RPC',
        req_body_type='formData',
        body_type='json'
    )
    req = open_api_models.OpenApiRequest(
        query=OpenApiUtilClient.query(pay_load)
    )
    response = ice_client.call_api(params=params, request=req, runtime=util_models.RuntimeOptions())
    if response['statusCode'] != 200:
        print(response)
        raise Exception(f"API {api_name} 调用失败，请检查入参")
    return response['body']


def create_oss_client():
    access_key_id = os.getenv('ALIBABA_CLOUD_ACCESS_KEY_ID')
    access_key_secret = os.getenv('ALIBABA_CLOUD_ACCESS_KEY_SECRET')
    security_token = os.getenv('ALIBABA_CLOUD_SECURITY_TOKEN')
    region = os.getenv('ALIBABA_CLOUD_REGION')

    credentials_provider = oss.credentials.StaticCredentialsProvider(access_key_id, access_key_secret, security_token)
    config = oss.config.load_default()
    config.credentials_provider = credentials_provider
    config.region = region
    config.endpoint = f"https://oss-{region}.aliyuncs.com"
    return oss.Client(config)


def get_ice_client():
    ice_client = create_client()
    return ice_client


def get_oss_client():
    oss_client = create_oss_client()
    return oss_client
