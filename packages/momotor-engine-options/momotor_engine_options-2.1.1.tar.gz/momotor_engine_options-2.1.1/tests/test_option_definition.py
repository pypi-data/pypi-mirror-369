import pytest

from momotor.bundles import RecipeBundle
from momotor.bundles.elements.options import Option
from momotor.bundles.elements.steps import Step
from momotor.options import OptionDefinition
from momotor.options.providers import Providers
from momotor.options.task_id import StepTaskId

test_recipe = RecipeBundle()
step_option_1 = Option(test_recipe).create(name='option', value='s1')
step_option_2 = Option(test_recipe).create(name='option', value='s2')
step_option_3 = Option(test_recipe).create(name='option', domain='test', value='s3')

recipe_option_1 = Option(test_recipe).create(name='option', value='r1')
recipe_option_2 = Option(test_recipe).create(name='option', value='r2')
recipe_option_3 = Option(test_recipe).create(name='option', domain='test', value='r3')
recipe_option_4 = Option(test_recipe).create(name='option', domain='#sub', value='r4')
recipe_option_5 = Option(test_recipe).create(name='option', domain='test#sub', value='r5')

test_step = Step(test_recipe).create(id='step', options=[
    step_option_1,
    step_option_2,
    step_option_3,
])
test_recipe.create(
    options=[
        recipe_option_1,
        recipe_option_2,
        recipe_option_3,
        recipe_option_4,
        recipe_option_5,
    ],
    steps=[test_step]
)

test_providers = Providers(
    recipe=test_recipe,
    task_id=StepTaskId('step', None),
)


REQUIRED_ARGS = {
    'name': 'option',
    'domain': 'unspecified',
    'location': tuple()
}


def test_option_name_required():
    with pytest.raises(TypeError, match=r"missing 1 required positional argument: 'name'"):
        OptionDefinition()  # noqa


def test_option_subdomain_not_allowed():
    kwargs = {
        **REQUIRED_ARGS,
        'domain': 'domain#subdomain',
    }
    with pytest.raises(TypeError, match=r"domain cannot contain a subdomain"):
        OptionDefinition(**kwargs)  # noqa


def test_option_defaults():
    """ Test defaults
    """
    checklet_option = OptionDefinition(**REQUIRED_ARGS)

    assert checklet_option.name == REQUIRED_ARGS['name']
    assert checklet_option.location == REQUIRED_ARGS['location']
    assert checklet_option.doc is None
    assert checklet_option.required is False
    assert checklet_option.multiple is False
    assert checklet_option.default is OptionDefinition.NO_DEFAULT


@pytest.mark.parametrize(
    ['required', 'multiple', 'default', 'expected'],
    [
        pytest.param(False, False, False, None),
        pytest.param(False, False, True, 'default'),
        pytest.param(False, True, False, tuple()),
        pytest.param(False, True, True, tuple(['default'])),
        pytest.param(True, False, False, ValueError),
        pytest.param(True, False, True, ValueError),
        pytest.param(True, True, False, ValueError),
        pytest.param(True, True, True, ValueError),
    ]
)
def test_option_resolve_not_provided(required, multiple, default, expected):
    kwargs = {
        **REQUIRED_ARGS,
        'required': required,
        'multiple': multiple,
    }

    if default:
        kwargs['default'] = 'default'

    checklet_option = OptionDefinition(**kwargs)

    if expected is ValueError:
        with pytest.raises(ValueError):
            checklet_option.resolve(Providers())
    else:
        assert checklet_option.resolve(Providers()) == expected


@pytest.mark.parametrize(
    ['location', 'multiple', 'all', 'expected'],
    [
        pytest.param('step,recipe', False, False, 's1'),
        pytest.param('recipe,step', False, False, 'r1'),
        pytest.param('step,recipe', False, True,  's1'),
        pytest.param('recipe,step', False, True,  'r1'),
        pytest.param('step,recipe', True,  False, ('s1', 's2')),
        pytest.param('recipe,step', True,  False, ('r1', 'r2')),
        pytest.param('step,recipe', True,  True,  ('s1', 's2', 'r1', 'r2')),
        pytest.param('recipe,step', True,  True,  ('r1', 'r2', 's1', 's2')),
    ]
)
def test_option_result_location_multiple_all(location, multiple, all, expected):
    kwargs = {
        **REQUIRED_ARGS,
        'domain': Option.DEFAULT_DOMAIN,
        'location': location,
        'multiple': multiple,
        'all': all,
    }

    option = OptionDefinition(**kwargs)
    assert option.resolve(test_providers) == expected


@pytest.mark.parametrize(
    ['location'],
    [
        pytest.param('recipe,step'),
        pytest.param('recipe, step'),
        pytest.param(' recipe, step '),
        pytest.param(('recipe', 'step')),
        pytest.param(['recipe', 'step']),
        pytest.param(iter(['recipe', 'step'])),
    ]
)
def test_option_result_location_formats(location):
    kwargs = {
        **REQUIRED_ARGS,
        'location': location,
    }
    option = OptionDefinition(**kwargs)
    assert option.location == ('recipe', 'step')


@pytest.mark.parametrize(
    ['option_domain', 'all', 'resolve_subdomains', 'expected'],
    [
        pytest.param(Option.DEFAULT_DOMAIN, True,  {},                        ('s1', 's2', 'r1', 'r2')),
        pytest.param(Option.DEFAULT_DOMAIN, True,  {'recipe': None},          ('s1', 's2', 'r1', 'r2')),
        pytest.param(Option.DEFAULT_DOMAIN, True,  {'recipe': ''},            ('s1', 's2', 'r1', 'r2')),
        pytest.param(Option.DEFAULT_DOMAIN, True,  {'recipe': []},            ('s1', 's2', 'r1', 'r2')),
        pytest.param(Option.DEFAULT_DOMAIN, True,  {'recipe': [None]},        ('s1', 's2', 'r1', 'r2')),
        pytest.param(Option.DEFAULT_DOMAIN, True,  {'recipe': ['']},          ('s1', 's2', 'r1', 'r2')),

        pytest.param(Option.DEFAULT_DOMAIN, True,  {'recipe': 'sub'},         ('r4', 's1', 's2')),
        pytest.param(Option.DEFAULT_DOMAIN, True,  {'recipe': ['sub', None]}, ('r4', 's1', 's2', 'r1', 'r2')),

        pytest.param('test',                True,  {},                        ('s3', 'r3')),
        pytest.param('test',                True,  {'recipe': 'sub'},         ('r5', 's3')),
        pytest.param('test',                True,  {'recipe': ['sub', None]}, ('r5', 's3', 'r3')),

        pytest.param(Option.DEFAULT_DOMAIN, False, {},                        ('s1', 's2')),
        pytest.param(Option.DEFAULT_DOMAIN, False, {'recipe': 'sub'},         ('r4',)),
        pytest.param(Option.DEFAULT_DOMAIN, False, {'recipe': ['sub', None]}, ('r4',)),

        pytest.param('test',                False, {},                        ('s3',)),
        pytest.param('test',                False, {'recipe': 'sub'},         ('r5',)),
        pytest.param('test',                False, {'recipe': ['sub', None]}, ('r5',)),
    ]
)
def test_option_result_subdomains(option_domain, all, resolve_subdomains, expected):
    kwargs = {
        **REQUIRED_ARGS,
        'domain': option_domain,
        'location': 'step, recipe',
        'multiple': True,
        'all': all,
    }
    option = OptionDefinition(**kwargs)
    assert option.resolve(test_providers, resolve_subdomains) == expected


@pytest.mark.parametrize(
    ['name', 'default', 'expected'],
    [
        pytest.param('option', None, 's1'),
        pytest.param('option', 'def', 's1'),
        pytest.param('other', None, None),
        pytest.param('other', 'def', 'def'),
    ]
)
def test_option_default(name, default, expected):
    kwargs = {
        **REQUIRED_ARGS,
        'name': name,
        'domain': Option.DEFAULT_DOMAIN,
        'location': 'step',
    }
    if default is not None:
        kwargs['default'] = default

    option = OptionDefinition(**kwargs)
    assert option.resolve(test_providers) == expected
