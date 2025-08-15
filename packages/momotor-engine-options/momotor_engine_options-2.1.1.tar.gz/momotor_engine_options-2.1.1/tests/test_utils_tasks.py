import pytest

from momotor.bundles import RecipeBundle, ConfigBundle, BundleFormatError
from momotor.bundles.elements.options import Option
from momotor.bundles.elements.steps import Step
from momotor.bundles.utils.domain import merge_domains
from momotor.options.domain.scheduler.tasks import TASKS_OPTION_NAME, get_scheduler_tasks_option


def create_options(bundle, options):
    return [
        Option(bundle).create(
            name=TASKS_OPTION_NAME.name,
            domain=merge_domains(TASKS_OPTION_NAME.domain, f'#{step_id}' if step_id else None),
            value=value
        ) for step_id, value in options.items()
    ] if options else None


def create_recipe(definitions, options=None):
    recipe = RecipeBundle(None, None)
    return recipe.create(
        options=create_options(recipe, options),
        steps=[
            Step(recipe).create(
                id=step_id,
                options=[
                    Option(recipe).create(
                        name=TASKS_OPTION_NAME.name,
                        domain=TASKS_OPTION_NAME.domain,
                        value=step_option_definition
                    )
                ] if step_option_definition else None
            )
            for step_id, step_option_definition in definitions.items()
        ],
    )


def create_config(options):
    config = ConfigBundle(None, None)
    return config.create(
        options=create_options(config, options)
    )


@pytest.mark.parametrize(['recipe', 'config', 'expected_tasks'], [
    pytest.param(
        create_recipe({
            'step': None
        }),
        None,
        {
            'step': None
        },
        id='No tasks option'
    ),
    pytest.param(
        create_recipe({
            'step': '??'
        }),
        None,
        {
            'step': None
        },
        id='Unused task option'
    ),
    pytest.param(
        create_recipe({
            'step': '*?'
        }),
        None,
        {
            'step': None
        },
        id='Unused task option (wildcard)'
    ),
    pytest.param(
        create_recipe({
            'step': '*'
        }),
        create_config({
            'step': '2'
        }),
        {
            'step': (2,)
        },
        id='Wildcard tasks option, value provided in config'
    ),
    pytest.param(
        create_recipe({
            'step': '*'
        }, {
            'step': '2.2'
        }),
        None,
        {
            'step': (2, 2)
        },
        id='Wildcard tasks option, value provided in recipe'
    ),
    pytest.param(
        create_recipe({
            'step': '*?'
        }),
        create_config({
            'step': '2'
        }),
        {
            'step': (2,)
        },
        id='Wildcard tasks option, value provided in config'
    ),
    pytest.param(
        create_recipe({
            'step': '*?'
        }, {
            'step': '2.2'
        }),
        None,
        {
            'step': (2, 2)
        },
        id='Wildcard tasks option, value provided in recipe'
    ),
    pytest.param(
        create_recipe({
            'step': '?'
        }),
        create_config({
            'step': '2'
        }),
        {
            'step': (2,)
        },
        id='Single dimension tasks option, value provided in config'
    ),
    pytest.param(
        create_recipe({
            'step': '?.??'
        }),
        create_config({
            'step': '2'
        }),
        {
            'step': (2,)
        },
        id='Single or double dimension tasks option, single value provided in config'
    ),
    pytest.param(
        create_recipe({
            'step': '?.??'
        }),
        create_config({
            'step': '2.3'
        }),
        {
            'step': (2, 3)
        },
        id='Single or double dimension tasks option, double value provided in config'
    ),
    pytest.param(
        create_recipe({
            'step': '2.2'
        }),
        None,
        {
            'step': (2, 2)
        },
        id='Fixed dimension option, no value provided'
    ),
    pytest.param(
        create_recipe({
            'step': '2.2'
        }),
        create_config({
            'step': '2.2'
        }),
        {
            'step': (2, 2)
        },
        id='Fixed dimension option, value provided in config'
    ),
    pytest.param(
        create_recipe({
            'step': '?.2'
        }),
        create_config({
            'step': '3.2'
        }),
        {
            'step': (3, 2)
        },
        id='Partially fixed dimension option, value provided in config'
    ),
    pytest.param(
        create_recipe({
            'step1': '*',
            'step2': "*",
        }),
        create_config({
            'step1': '1',
            'step2': '2',
        }),
        {
            'step1': (1,),
            'step2': (2,)
        },
        id='Multiple steps with task option'
    ),
    pytest.param(
        create_recipe({
            'step': '12345.67890'
        }),
        None,
        {
            'step': (12345, 67890)
        },
        id='Fixed dimension option, big numbers'
    ),
])
def test_get_step_tasks_options(recipe, config, expected_tasks):
    tasks = {}
    for step_id in recipe.steps.keys():
        tasks[step_id] = get_scheduler_tasks_option(recipe, config, step_id)

    assert tasks == expected_tasks


@pytest.mark.parametrize(['recipe', 'config', 'expected_error'], [
    pytest.param(
        create_recipe({
            'step': '*'
        }),
        None,
        rf"Step 'step': missing required tasks@{TASKS_OPTION_NAME.domain} option",
        id="Missing tasks option"
    ),
    pytest.param(
        create_recipe({
            'step': None
        }),
        create_config({
            'step': '1'
        }),
        rf"Step 'step': tasks@{TASKS_OPTION_NAME.domain} option not supported",
        id="Step not supporting task option"
    ),
    pytest.param(
        create_recipe({
            'step': '*.?'
        }),
        None,
        rf"Step 'step': invalid tasks@{TASKS_OPTION_NAME.domain} option definition '\*\.\?'",
        id="Invalid wildcard placement *.?"
    ),
    pytest.param(
        create_recipe({
            'step': '*?.?'
        }),
        None,
        rf"Step 'step': invalid tasks@{TASKS_OPTION_NAME.domain} option definition '\*\?\.\?'",
        id="Invalid wildcard placement *?.?"
    ),
    pytest.param(
        create_recipe({
            'step': '??.?'
        }),
        None,
        rf"Step 'step': invalid tasks@{TASKS_OPTION_NAME.domain} option definition '\?\?\.\?'",
        id="Invalid wildcard placement ??.?"
    ),
    pytest.param(
        create_recipe({
            'step': 'X.?'
        }),
        None,
        rf"Step 'step': invalid tasks@{TASKS_OPTION_NAME.domain} option definition 'X\.\?'",
        id="Invalid character in definition"
    ),
    pytest.param(
        create_recipe({
            'step': '1.0'
        }),
        None,
        rf"Step 'step': invalid tasks@{TASKS_OPTION_NAME.domain} option definition '1\.0'",
        id="Zero element in definition"
    ),
    pytest.param(
        create_recipe({
            'step': '1.01'
        }),
        None,
        rf"Step 'step': invalid tasks@{TASKS_OPTION_NAME.domain} option definition '1\.01'",
        id="Leading zero in definition"
    ),
    pytest.param(
        create_recipe({
            'step': '2.2'
        }, {
            'step': '3.3'
        }),
        None,
        rf"Step 'step': tasks@{TASKS_OPTION_NAME.domain} option value '3\.3' does not match definition '2\.2'",
        id="Wrong fixed dimension"
    ),
    pytest.param(
        create_recipe({
            'step': '?.2'
        }, {
            'step': '3.3'
        }),
        None,
        rf"Step 'step': tasks@{TASKS_OPTION_NAME.domain} option value '3\.3' does not match definition '\?\.2'",
        id="Wrong partially fixed dimension"
    ),
    pytest.param(
        create_recipe({
            'step': '?'
        }, {
            'step': '3.3'
        }),
        None,
        rf"Step 'step': tasks@{TASKS_OPTION_NAME.domain} option value '3\.3' does not match definition '\?'",
        id="Invalid dimension (1->2)"
    ),
    pytest.param(
        create_recipe({
            'step': '?.?'
        }, {
            'step': '3'
        }),
        None,
        rf"Step 'step': tasks@{TASKS_OPTION_NAME.domain} option value '3' does not match definition '\?\.\?'",
        id="Invalid dimension (2->1)"
    ),
    pytest.param(
        create_recipe({
            'step': '*'
        }, {
            'step': '*'
        }),
        None,
        rf"Step 'step': tasks@{TASKS_OPTION_NAME.domain} option value '\*' does not match definition '\*'",
        id="Invalid value"
    ),
])
def test_invalid_step_tasks_options(recipe, config, expected_error):
    with pytest.raises(BundleFormatError, match=expected_error):
        get_scheduler_tasks_option(recipe, config, 'step')
