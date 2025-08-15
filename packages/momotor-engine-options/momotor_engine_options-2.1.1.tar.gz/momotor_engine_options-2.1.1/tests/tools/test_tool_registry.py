import os
import pathlib

import pytest

from momotor.options.tools import resolve_tool, registered_tools, ToolName

TEST_REGISTRY = pathlib.Path(__file__).parent / 'files' / 'toolregistry.d'


@pytest.mark.skipif(os.name != 'posix', reason='Tool registry does not support non-posix environments')
def test_tool_registry_read():
    tools = registered_tools(paths=[TEST_REGISTRY], include_default_paths=False)
    data = {
        tool_name: (tool.name, tool.environment.get('VERSION'), tool.environment.get('VARIANT'))
        for tool_name, tool in tools.items()
    }
    assert data == {
        ToolName('nodefault/1'): ('nodefault/1', '1', None),
        ToolName('nodefault/2.1'): ('nodefault/2.1', '2.1', None),
        ToolName('nodefault/named'): ('nodefault/named', 'named', None),
        ToolName('tool/_'): ('tool/_', 'default', None),
        ToolName('tool/1'): ('tool/1', '1', None),
        ToolName('tool/2.1'): ('tool/2.1', '2.1', None),
        ToolName('tool/2.2'): ('tool/2.2', '2.2', None),
        ToolName('tool/envs'): ('tool/envs', None, None),
        ToolName('variant/2.0/a'): ('variant/2.0/a', '2.0', 'a'),
        ToolName('variant/2.0/b'): ('variant/2.0/b', '2.0', 'b'),
        ToolName('variant/2.1/b'): ('variant/2.1/b', '2.1', 'b'),
        ToolName('variant/2.1/c'): ('variant/2.1/c', '2.1', 'c'),
    }


@pytest.mark.skipif(os.name != 'posix', reason='Tool registry does not support non-posix environments')
@pytest.mark.parametrize(
    ['tool', 'expected_env'],
    [
        pytest.param('nodefault', {'VERSION': '2.1'}),
        pytest.param('nodefault/1', {'VERSION': '1'}),
        pytest.param('nodefault/named', {'VERSION': 'named'}),
        pytest.param('tool', {'VERSION': 'default'}),
        pytest.param('tool/_', {'VERSION': 'default'}),
        pytest.param('tool/1', {'VERSION': '1'}),
        pytest.param('tool/2.1', {'VERSION': '2.1'}),
        pytest.param('tool/2', {'VERSION': '2.2'}),
        pytest.param('tool/envs', {'BIN': '/bin', 'BIN2': '/bin2', 'HOME': os.environ.get('HOME')}),
        pytest.param('variant', {'VERSION': '2.1', 'VARIANT': 'c'}),
        pytest.param('variant/2', {'VERSION': '2.1', 'VARIANT': 'c'}),
        pytest.param('variant/2.0', {'VERSION': '2.0', 'VARIANT': 'b'}),
        pytest.param('variant/2.1', {'VERSION': '2.1', 'VARIANT': 'c'}),
        pytest.param('variant/2/a', {'VERSION': '2.0', 'VARIANT': 'a'}),
        pytest.param('variant/2/b', {'VERSION': '2.1', 'VARIANT': 'b'}),
        pytest.param('variant/2/c', {'VERSION': '2.1', 'VARIANT': 'c'}),
        pytest.param('variant/2.0/a', {'VERSION': '2.0', 'VARIANT': 'a'}),
        pytest.param('variant/2.1/b', {'VERSION': '2.1', 'VARIANT': 'b'}),
        pytest.param('variant/_/a', {'VERSION': '2.0', 'VARIANT': 'a'}),
        pytest.param('variant/_/b', {'VERSION': '2.1', 'VARIANT': 'b'}),
        pytest.param('variant/_/c', {'VERSION': '2.1', 'VARIANT': 'c'}),
        pytest.param('variant/_/_', {'VERSION': '2.1', 'VARIANT': 'c'}),
    ]
)
def test_tool_registry_resolve(tool, expected_env):
    tool = resolve_tool(tool, paths=[TEST_REGISTRY], include_default_paths=False)
    assert tool.path == pathlib.Path('/bin/true').resolve()
    assert tool.environment == expected_env


@pytest.mark.skipif(os.name != 'posix', reason='Tool registry does not support non-posix environments')
def test_tool_registry_not_found():
    with pytest.raises(FileNotFoundError):
        resolve_tool('lorem', paths=[TEST_REGISTRY], include_default_paths=False)


@pytest.mark.skipif(os.name == 'posix', reason='Tool registry does not support non-posix environments')
def test_tool_registry_posix_needed():
    with pytest.raises(AssertionError, match=r'Tool registry only supported on Posix systems'):
        resolve_tool('lorem', paths=[TEST_REGISTRY], include_default_paths=False)
