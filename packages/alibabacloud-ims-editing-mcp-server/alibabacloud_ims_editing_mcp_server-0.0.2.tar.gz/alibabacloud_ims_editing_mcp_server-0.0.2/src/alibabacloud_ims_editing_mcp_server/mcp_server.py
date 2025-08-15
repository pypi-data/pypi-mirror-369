import click
from fastmcp import FastMCP
from alibabacloud_ims_editing_mcp_server.tools.tool_registration import *
import logging
from dotenv import load_dotenv
import asyncio
import sys
import os
import re
from logging.handlers import TimedRotatingFileHandler


BASE_DIR = os.path.dirname(os.path.abspath(__file__))
logdir = os.path.join(BASE_DIR, "logs")
if not os.path.exists(logdir):
    os.makedirs(logdir)


def setup_log(log_name):
    logger = logging.getLogger(log_name)
    log_path = os.path.join(logdir, log_name)
    logger.setLevel(logging.INFO)
    file_handler = TimedRotatingFileHandler(
        filename=log_path, when="MIDNIGHT", interval=1, backupCount=3
    )
    file_handler.suffix = "%Y-%m-%d.log"
    file_handler.extMatch = re.compile(r"^\d{4}-\d{2}-\d{2}.log$")
    file_handler.setFormatter(
        logging.Formatter(
            "%(asctime)s %(levelname)s - %(message)s"
        )
    )
    logger.addHandler(file_handler)
    return logger


logger = setup_log("ims-editing-mcp.log")


def create_new_mcp_server(level, host, port):
    mcp = FastMCP(
        name="IMS Editing MCP",
        port=port,
        host=host
    )

    if level:
        if level == "Basic":
            for tool in basic_tools:
                mcp.tool(tool['tool_func'], **tool['tool_info'])
        elif level == "Standard":
            for tool in standard_tools:
                mcp.tool(tool['tool_func'], **tool['tool_info'])
        elif level == "Premium":
            for tool in premium_tools:
                mcp.tool(tool['tool_func'], **tool['tool_info'])
        elif level == "TrialPlan":
            for tool in trial_tools:
                mcp.tool(tool['tool_func'], **tool['tool_info'])
        else:
            raise ValueError("level value is invalid.")
    else:
        for tool in premium_tools:
            mcp.tool(tool['tool_func'], **tool['tool_info'])

    print(" - In basic_tools:", [f['tool_func'].__name__ for f in basic_tools])
    print(" - In standard_tools:", [f['tool_func'].__name__ for f in standard_tools])
    print(" - In premium_tools:", [f['tool_func'].__name__ for f in premium_tools])
    print(" - In trial_tools:", [f['tool_func'].__name__ for f in trial_tools])

    return mcp


@click.command()
@click.option(
    "--level",
    type=str,
    default=None,
    help="Subscription level, i.e. Basic or Standard or Premium or TrialPlan",
)
@click.option(
    "--transport",
    type=click.Choice(["stdio", "sse", "streamable-http"]),
    default="stdio",
    help="Transport type",
)
@click.option(
    "--host",
    type=str,
    default="127.0.0.1",
    help="Host",
)
@click.option(
    "--port",
    type=int,
    default=8000,
    help="Port number",
)
def main(level: str, transport: str, host: str, port: int):
    """命令行入口点，用于启动 IMS Video Editing MCP 服务器"""
    # 加载环境变量
    load_dotenv()

    try:
        # 创建MCP服务器
        mcp = create_new_mcp_server(level, port=port, host=host)
        print("start mcp server")
        asyncio.run(mcp.run(transport=transport))
    except Exception as e:
        print(f"启动服务器时出错: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
