from .tool import ToolName, Tool, match_tool, match_tool_requirements
from .registry import registered_tools, resolve_tool, tool_registry_paths


def _print_registry():
    print("Registered tools:")
    print('-----------------')

    tools = registered_tools(include_missing=True)
    for alias_name, tool_info in sorted(tools.items()):
        print(f'{alias_name} => {tool_info.path}')

    print()


def _print_tool(tool_name: str):
    tool_info = resolve_tool(tool_name)

    print('name:')
    print(f'  {tool_info.name}')

    print('path:')
    print(f'  {tool_info.path}')

    if tool_info.environment:
        print('environment:')
        for env_name, env_value in sorted(tool_info.environment.items()):
            print(f'  {env_name}={env_value}')

    print()


if __name__ == '__main__':
    import sys

    if len(sys.argv) > 1:
        _print_tool(sys.argv[1])
    else:
        _print_registry()
