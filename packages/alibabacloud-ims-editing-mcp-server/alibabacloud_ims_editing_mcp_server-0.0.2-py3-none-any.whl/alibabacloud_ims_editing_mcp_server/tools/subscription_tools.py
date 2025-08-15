from alibabacloud_ims_editing_mcp_server.tools.tool_registration import *
from alibabacloud_ims_editing_mcp_server.client import get_ice_client, invoke_api


@register_level_tools(basic_tool, trial_tool, tool_info={
    'tags': {'获取会员订阅版本'}
})
def get_user_subscription_level():
    """
        <tags>'获取会员订阅版本'</tags>
        <toolDescription>该工具主要功能是获取客户当前的会员订阅版本。Basic: 入门版，Standard: 标准版，Premium：旗舰版，TrialPlan：试用版。权限范围：入门版 < 标准版 < 试用版 < 旗舰版</toolDescription>
        <return>当前用户订阅等级</return>
    """

    payload = {
        "ServiceCode": "mediaservice",
        "CommodityCode": "ice_subscribe_spn_public_cn",
        "Status": "Normal"
    }
    ice_client = get_ice_client()
    response = invoke_api("GetPrepaidServiceInfo", payload, ice_client)
    subscription_list = response["PrepaidServiceInfoList"]

    max_level = None
    max_level_int = -1
    level_map = {"None": -1, "Basic": 0, "Standard": 1, "TrialPlan": 2, "Premium": 3}
    if subscription_list:
        for subscription in subscription_list:
            level = subscription["Level"]
            if level and level in level_map:
                subscription_level_int = level_map[level]
                if subscription_level_int > max_level_int:
                    max_level_int = subscription_level_int
                    max_level = subscription["Level"]

    if max_level_int == -1:
        return "No subscription found. Please refer to https://help.aliyun.com/zh/ims/commercial-upgrade-announcement to purchase proper subscription."
    else:
        return max_level
