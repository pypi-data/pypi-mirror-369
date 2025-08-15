import pytest

from momotor.options.tools import match_tool, match_tool_requirements


@pytest.mark.parametrize(
    ['name', 'tools', 'expected'],
    [
        pytest.param('test', ['test'], 'test'),
        pytest.param('other', ['test'], None),
        pytest.param('test', ['test/1'], 'test/1'),
        pytest.param('test', ['test/1', 'test/2'], 'test/2'),
        pytest.param('test', ['test/2', 'test/1.0', 'test/1.1'], 'test/2'),
        pytest.param('test/_', ['test/2', 'test/1.0', 'test/1.1'], 'test/2'),
        pytest.param('test/1', ['test/2', 'test/1.0', 'test/1.1'], 'test/1.1'),
        pytest.param('test/1.0', ['test/2', 'test/1.0', 'test/1.1'], 'test/1.0'),
        pytest.param('test/1.2', ['test/2', 'test/1.0', 'test/1.1'], None),
        pytest.param('test/_', ['test/2', 'test/2.0', 'test/2.0-0', 'test/2.0-1'], 'test/2.0-1'),
        pytest.param('test/2', ['test/2', 'test/2.0', 'test/2.0-0', 'test/2.0-1'], 'test/2.0-1'),
        pytest.param('test/2.0', ['test/2', 'test/2.0', 'test/2.0-0', 'test/2.0-1'], 'test/2.0-1'),
        pytest.param('test/2.0-0', ['test/2', 'test/2.0', 'test/2.0-0', 'test/2.0-1'], 'test/2.0-0'),
        pytest.param('test', ['test/2', 'test/1.0', 'test/1.1', 'test/_'], 'test/_'),
        pytest.param('test/_', ['test/2', 'test/1.0', 'test/1.1', 'test/_'], 'test/_'),
        pytest.param('test/1', ['test/2', 'test/1.0', 'test/1.1', 'test/_'], 'test/1.1'),
        pytest.param('test/1.0', ['test/2', 'test/1.0', 'test/1.1', 'test/_'], 'test/1.0'),
        pytest.param('test/1.2', ['test/2', 'test/1.0', 'test/1.1', 'test/_'], None),
    ]
)
def test_match_tool(name, tools, expected):
    assert match_tool(name, tools) == expected


@pytest.mark.parametrize(
    ['requirements', 'tools', 'expected'],
    [
        pytest.param(
            {'test': ['test']}, ['test'],
            {'test': 'test'}
        ),
        pytest.param(
            {'test': ['test'], 'other': ['other']}, ['test'],
            None
        ),
        pytest.param(
            {'test': ['test'], 'other': ['other']}, ['test', 'other'],
            {'test': 'test', 'other': 'other'}
        ),
        pytest.param(
            {'test': ['test/1'], 'other': ['other']}, ['test/1', 'test/2', 'other'],
            {'test': 'test/1', 'other': 'other'}
        ),
        pytest.param(
            {'test': ['test/2'], 'other': ['other']}, ['test/1', 'test/2', 'other'],
            {'test': 'test/2', 'other': 'other'}
        ),
        pytest.param(
            {'test': ['test/3'], 'other': ['other']}, ['test/1', 'test/2', 'other'],
            None,
        ),
        pytest.param(
            {'test': ['test/_'], 'other': ['other']}, ['test/1', 'test/2', 'other'],
            {'test': 'test/2', 'other': 'other'}
        ),
    ]
)
def test_match_tool_requirements(requirements, tools, expected):
    try:
        result = match_tool_requirements(requirements, tools)
    except ValueError:
        result = None

    assert result == expected
