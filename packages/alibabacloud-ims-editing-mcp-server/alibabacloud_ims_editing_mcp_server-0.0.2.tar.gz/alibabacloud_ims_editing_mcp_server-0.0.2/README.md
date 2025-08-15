# Alibaba Cloud IMS Editing MCP Server

## 简介
Alibaba Cloud IMS Editing MCP Server是一个[模型上下文协议（MCP）](https://modelcontextprotocol.io/introduction)服务器，提供和阿里云智能媒体服务智能剪辑制作相关的工具，支持通过自然语言对话方式进行智能剪辑。


## 准备
- 安装 [uv](https://docs.astral.sh/uv/getting-started/installation/) 
- Python 3.12+
- 提供对应阿里云账号的access key id和access key secret，或者是security token
- 开通[智能媒体服务](https://help.aliyun.com/zh/ims/getting-started/opening-service?spm=a2c4g.11186623.help-menu-193643.d_1_0.6334f56eqZZppb&scm=20140722.H_440168._.OR_help-T_cn~zh-V_1)，并提前购买企业订阅服务才能使用对应的能力，具体参考[智能媒体服务计费概述 ](https://help.aliyun.com/zh/ims/billing-overview?spm=a2c4g.11186623.help-menu-193643.d_0_2_0.65a54970djwiSe&scm=20140722.H_439260._.OR_help-T_cn~zh-V_1)


## 配置
在 mcp client 中配置MCP Server，配置如下：

```json
{
  "mcpServers": {
    "alibabacloud-ims-editing-mcp-server": {
      "command": "uvx",
      "args": [
        "alibabacloud-ims-editing-mcp-server@latest",
        "--level",
        "Premium"
      ],
      "env": {
        "ALIBABA_CLOUD_ACCESS_KEY_ID": "your access key id",
        "ALIBABA_CLOUD_ACCESS_KEY_SECRET": "your access key secret",
        "ALIBABA_CLOUD_SECURITY_TOKEN": "sts_security_token optional, required when using STS Token",
        "ALIBABA_CLOUD_REGION": "your region"
      }
    }
  }
}
```

其中，可以通过--level参数配置使用的订阅版本支持的能力，订阅版本参数对应关系如下：
- Basic：基础版
- Standard：标准版
- TrialPlan: 试用版
- Premium：旗舰版（默认，能力最全）


## 功能点（Tool）

| **工具**                                | **功能描述**                                                               | **订阅制版本要求** |
|---------------------------------------|------------------------------------------------------------------------|-------------|
| register_editing_media                        | 注册媒资，当前仅支持输入OSS地址注册媒资，返回媒资MediaId                                      | Basic       |
| get_editing_media_info                             | 获取媒资信息，包括媒资状态status、标题title、时长duration、文件地址file_url、文件宽width、文件高height | Basic       |
| search_editing_media                          | 媒资搜索，支持通过自然语言搜索搜索库中的媒资文件。如果用户开通的是旗舰版或者试用版，则使用混合搜索，其他订阅版本使用普通搜索         | Basic       |
| submit_media_comprehension_job        | 提交内容理解任务，获取剧情事件分镜结果                                                    | Standard    |
| get_media_comprehension_job           | 查询内容理解任务                                                               | Standard    |
| generate_timeline | 提交生成时间线任务                                                              | Basic       |
| modify_timeline  | 提交修改时间线任务                                                              | Basic       |
| get_timeline_project_result  | 根据输入的时间线任务job_id来获取生成时间线对应的云剪辑工程的project_id                            | Basic       |
| get_timeline_from_project  | 根据输入的剪辑工程project_id来获取对应的时间线                                           | Basic       |
| submit_media_producing_job              | 提交剪辑任务                                                                 | Basic       |
| get_media_producing_job                 | 查询剪辑任务                                                                 | Basic       |
| submit_batch_editing_script_job             | 提交脚本化混剪一键成片任务                                                          | Basic       |
| submit_batch_editing_general_match_job         | 提交图文匹配一键成片任务                                                           | Standard    |
| get_batch_editing_job                 | 查询一键成片任务结果                                                             | Basic       |
| get_user_subscription_level                 | 获取用户订阅版本                                                               | Basic       |
| get_oss_bucket_list                 | 获取用户当前区域的OSS文件列表，用于配置剪辑输出oss bucket                                    | None        |


## 使用场景

1. 简单拼接

帮我将mediaId=xxx的0～10s和mediaId=xxx的15～25s剪辑拼接成新视频

2. 图文匹配

基于mediaId=xx1,xx2,xx3等，帮我撰写100字左右和保护海洋，清理垃圾相关的文案，剪辑生成一个宣传片

3. 高光提取+普通剪辑

帮我挑选出https://test_bucket.oss-cn-shanghai.aliyuncs.com/test_1.mp4和https://test_bucket.oss-cn-shanghai.aliyuncs.com/test_2.mp4里面的剧情精彩的高光片段，然后中间添加一些转场特效拼接成片











