import os
import pathlib

import pytest
from momotor.options.task_id import StepTaskId

from momotor.options.providers import Providers

from momotor.bundles import RecipeBundle
from momotor.bundles.elements.options import Option
from momotor.bundles.elements.steps import Step
from momotor.options.domain.tools import ToolOptionDefinition, TOOLS_DOMAIN


TEST_REGISTRY = pathlib.Path(__file__).parent / 'files' / 'toolregistry.d'


test_recipe = RecipeBundle()

test_step = Step(test_recipe).create(id='step', options=[
    Option(test_recipe).create(name='tool1', domain=TOOLS_DOMAIN, value='tool1'),
    Option(test_recipe).create(name='tool2', domain=TOOLS_DOMAIN, value='tool2/2.0 tool2/1.0'),
    Option(test_recipe).create(name='variant', domain=TOOLS_DOMAIN, value='variant/2.0/b'),
])
test_recipe.create(
    steps=[test_step]
)

test_providers = Providers(
    recipe=test_recipe,
    task_id=StepTaskId('step', None),
)


@pytest.mark.parametrize(
    ['name', 'default', 'expected'],
    [
        pytest.param('tool0', None, ['tool0']),
        pytest.param('tool0', 'tool0/0.0', ['tool0/0.0']),
        pytest.param('tool1', None, ['tool1']),
        pytest.param('tool1', 'tool1/1.0', ['tool1']),
        pytest.param('tool2', None, ['tool2/2.0', 'tool2/1.0']),
        pytest.param('tool2', 'tool2/2.1', ['tool2/2.0', 'tool2/1.0']),
    ]
)
def test_tool_option(name, default, expected):
    kwargs = {
        'name': name,
    }
    if default is not None:
        kwargs['default'] = default

    option = ToolOptionDefinition(**kwargs)
    assert option.name == name
    assert option.default == default or name
    assert list(option.resolve(test_providers)) == expected


@pytest.mark.skipif(os.name != 'posix', reason='Tool registry does not support non-posix environments')
@pytest.mark.parametrize(
    ['name', 'default', 'expected_env'],
    [
        pytest.param('tool', None, {'VERSION': 'default'}),
        pytest.param('tool', 'tool/1', {'VERSION': '1'}),
        pytest.param('tool', 'tool/2.1', {'VERSION': '2.1'}),
        pytest.param('tool', 'tool/2', {'VERSION': '2.2'}),
        pytest.param('tool', 'tool/2', {'VERSION': '2.2'}),
        pytest.param('tool', 'tool/1 tool/2', {'VERSION': '1'}),
        pytest.param('tool', 'tool/2 tool/1', {'VERSION': '2.2'}),
        pytest.param('tool', 'tool/3 tool/2 tool/1', {'VERSION': '2.2'}),
        pytest.param('variant', None,  {'VERSION': '2.0', 'VARIANT': 'b'}),
        pytest.param('variant', 'variant/2.1/c',  {'VERSION': '2.0', 'VARIANT': 'b'}),
    ]
)
def test_tool_option_registry_resolve(name, default, expected_env):
    kwargs = {
        'name': name,
    }
    if default is not None:
        kwargs['default'] = default

    option = ToolOptionDefinition(**kwargs)
    tool = option.resolve_tool(test_providers, paths=[TEST_REGISTRY], include_default_paths=False)
    assert tool.path == pathlib.Path('/bin/true').resolve()
    assert tool.environment == expected_env


def test_tool_option_invalid_name():
    with pytest.raises(ValueError):
        ToolOptionDefinition(name='test/1')


def test_tool_option_no_multiple():
    with pytest.raises(ValueError):
        ToolOptionDefinition(name='test', multiple=True)
