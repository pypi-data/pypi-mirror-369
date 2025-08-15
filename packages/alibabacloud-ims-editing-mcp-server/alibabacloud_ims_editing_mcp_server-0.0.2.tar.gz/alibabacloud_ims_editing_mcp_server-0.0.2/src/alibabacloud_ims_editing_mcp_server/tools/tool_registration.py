basic_tools = []
standard_tools = []
premium_tools = []
trial_tools = []


def register_level_tools(*tool_lists, tool_info: dict = {}):
    def decorator(func):
        for tool_list in tool_lists:
            tool_list(func, tool_info)
        return func

    return decorator


def basic_tool(func, tool_info: dict):
    func_dict = {
        'tool_info': tool_info,
        'tool_func': func
    }
    basic_tools.append(func_dict)
    standard_tools.append(func_dict)
    premium_tools.append(func_dict)
    return func


def standard_tool(func, tool_info: dict):
    func_dict = {
        'tool_info': tool_info,
        'tool_func': func
    }
    standard_tools.append(func_dict)
    premium_tools.append(func_dict)
    return func


def premium_tool(func, tool_info: dict):
    func_dict = {
        'tool_info': tool_info,
        'tool_func': func
    }
    premium_tools.append(func_dict)
    return func


def trial_tool(func, tool_info: dict):
    func_dict = {
        'tool_info': tool_info,
        'tool_func': func
    }
    trial_tools.append(func_dict)
    return func
