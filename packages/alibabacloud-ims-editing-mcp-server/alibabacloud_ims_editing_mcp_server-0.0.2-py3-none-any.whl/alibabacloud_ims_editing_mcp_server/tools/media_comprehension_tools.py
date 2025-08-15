import json
import logging
from alibabacloud_ice20201109 import models as ice20201109_models
from alibabacloud_tea_util import models as util_models
from alibabacloud_ims_editing_mcp_server.tools.tool_registration import *
from alibabacloud_ims_editing_mcp_server.client import get_ice_client
from typing import Annotated
from pydantic import Field

logger = logging.getLogger("ims-editing-mcp.log")


@register_level_tools(standard_tool, trial_tool, tool_info={
    'tags': {'分析素材阶段', '提交任务', '内容理解'}
})
def submit_media_comprehension_job(media_id_list: Annotated[list, Field(description="媒资Id列表")]) -> str:
    """
    <tags>'分析素材阶段','提交任务','内容理解'</tags>
    <subscriptionLevel>Standard</subscriptionLevel>
    <toolDescription>对输入媒资进行视频内容理解，主要是通过理解字幕、画面按剧情维度对输入视频进行分段划分，结果可以用于后续高光分析，素材挑选等</toolDescription>
    <return>任务id</return>
    Args:
        media_id_list (list): 视频媒资Id列表
    """
    job_info_list = []
    for media_id in media_id_list:
        job_ret = submit_smart_tag_job(media_id)
        job_info_list.append(job_ret)
    return json.dumps(job_info_list, ensure_ascii=False)


@register_level_tools(standard_tool, trial_tool, tool_info={
    'tags': {'分析素材阶段', '查询任务', '内容理解'}
})
def get_media_comprehension_job(job_info_list: Annotated[list, Field(description="任务信息列表")]) -> str:
    """
    <tags>'分析素材阶段','查询任务','内容理解'</tags>
    <subscriptionLevel>Standard</subscriptionLevel>
    <toolDescription>查询内容理解结果，输入job_info_list，并返回任务结果</toolDescription>
    <return>如果任务失败或者还在处理，会返回任务状态，如果任务成功，则会返回视频理解结果，说明任务完成。</return>

    获取查询结果之后，因为查询结果比较多，所以不需要在回答里面罗列，仅展示即可。
    Args:
        job_info_list (list): 任务信息列表，包含以下字段：
            job_id (string): 任务id
            media_id (string): 媒资id
    """
    job_result = {}
    logger.info(f'get_media_comprehension_job, input: {job_info_list}')
    for job_info in job_info_list:
        media_id = job_info["media_id"]
        job_id = job_info["job_id"]
        query_smart_tag_job_request = ice20201109_models.QuerySmarttagJobRequest(
            job_id=job_id
        )
        runtime = util_models.RuntimeOptions()
        ice_client = get_ice_client()
        try:
            resp = ice_client.query_smarttag_job_with_options(query_smart_tag_job_request, runtime)
            logger.info(f'get_media_comprehension_job, job_id: {job_id}, response: {resp.body}')
            job_status = resp.body.job_status
            if job_status == "Success":
                result = resp.body.results.result
                for res in result:
                    if res.type == "EventSplit":
                        job_result[media_id] = {"EventInfoList": json.loads(res.data)}
            elif job_status == "Submitted" or job_status == "Processing":
                job_result[media_id] = f"the job {job_id} is processing"
            else:
                job_result[media_id] = f"the job {job_id} is failed because of " + resp.body.results.result[0].data
        except Exception as error:
            logger.exception(error)
            return str(error)

    return json.dumps(job_result, ensure_ascii=False)


def submit_smart_tag_job(media_id: str) -> dict:
    job_input = ice20201109_models.SubmitSmarttagJobRequestInput(
        type='Media',
        media=media_id
    )
    submit_smart_tag_job_request = ice20201109_models.SubmitSmarttagJobRequest(
        input=job_input,
        template_id='S00000103-000003',
        params='{"clipSplitParams":{"splitType":"event"}}'
    )
    logger.info(f'submit_media_comprehension_job, the input of submit_smart_tag_job: {submit_smart_tag_job_request}')
    runtime = util_models.RuntimeOptions()
    ice_client = get_ice_client()
    try:
        resp = ice_client.submit_smarttag_job_with_options(submit_smart_tag_job_request, runtime)
        logger.info(f'submit_media_comprehension_job, the response of submit_smart_tag_job: {resp.body}')
        ret = {"media_id": media_id, "job_id": resp.body.job_id}
        return ret
    except Exception as error:
        logger.exception(error)
        ret = {"media_id": media_id, "error_message": str(error)}
        return ret
