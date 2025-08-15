import pytest

from momotor.bundles import RecipeBundle, ConfigBundle, ProductBundle, ResultsBundle
from momotor.bundles.elements.files import File
from momotor.bundles.elements.options import Option
from momotor.bundles.elements.properties import Property
from momotor.bundles.elements.result import Result, Outcome
from momotor.bundles.elements.steps import Step
from momotor.options.providers import Providers
from momotor.options.parser.reference import select_by_reference, select_by_prop_reference, select_by_file_reference, \
    select_by_opt_reference
from momotor.options.task_id import StepTaskId

test_recipe = RecipeBundle()
test_recipe.create(
    id='recipe',
    options=[
        Option(test_recipe).create(
            name='recipe-opt1'
        ),
        Option(test_recipe).create(
            domain='domain',
            name='recipe-opt2'
        ),
    ],
    files=[
        File(test_recipe).create(
            name='recipe file1.txt',
            class_='classA'
        ),
        File(test_recipe).create(
            name='recipe file2.cfg',
            class_='classA'
        ),
        File(test_recipe).create(
            name='recipe file3.cfg',
            class_='classB'
        ),
    ],
    steps=[
        Step(test_recipe).create(
            id='step',
            options=[
                Option(test_recipe).create(
                    name='step-opt'
                ),
            ],
            files=[
                File(test_recipe).create(
                    name='step file.txt',
                    class_='classB'
                ),
            ],
        )
    ]
)

test_config = ConfigBundle()
test_config.create(
    id='config',
    options=[
        Option(test_config).create(
            name='config-opt',
            value='default-domain'
        ),
        Option(test_config).create(
            name='config-opt',
            domain='domain',
            value='domain',
        ),
        Option(test_config).create(
            name='config-opt',
            domain='#sub',
            value='subdomain',
        ),
        Option(test_config).create(
            name='config-opt',
            domain='domain#sub',
            value='domain-subdomain'
        ),
    ],
    files=[
        File(test_config).create(
            name='config file.txt',
            class_='classB'
        ),
    ],
)

test_product = ProductBundle()
test_product.create(
    id='product',
    options=[
        Option(test_product).create(
            name='product-opt'
        ),
    ],
    files=[
        File(test_product).create(
            name='product file.txt',
            class_='classB'
        ),
    ],
)

test_results = ResultsBundle()
test_results.create(
    results=[
        Result(test_results).create(
            step_id='step',
            outcome=Outcome.PASS,
            options=[
                Option(test_results).create(
                    name='result-opt'
                ),
            ],
            files=[
                File(test_results).create(
                    name='result file.txt',
                    class_='classB'
                ),
            ],
            properties=[
                Property(test_results).create(
                    name='result-prop1',
                    value='prop1'
                ),
                Property(test_results).create(
                    name='result-prop2',
                    value='prop2'
                ),
                Property(test_results).create(
                    name='score',
                    value=1
                ),
            ]
        ),
        Result(test_results).create(
            step_id='passed-step',
            outcome=Outcome.PASS,
            files=[
                File(test_results).create(
                    name='result file2.txt',
                    class_='classB'
                ),
            ],
            properties=[
                Property(test_results).create(
                    name='score',
                    value=2
                ),
            ]
        ),
        Result(test_results).create(
            step_id='failed-step',
            outcome=Outcome.FAIL
        ),
        Result(test_results).create(
            step_id='skipped-step',
            outcome=Outcome.SKIP
        ),
        Result(test_results).create(
            step_id='error-step',
            outcome=Outcome.ERROR
        ),
    ]
)

test_bundles = Providers(
    test_recipe,
    test_config,
    test_product,
    test_results,
    StepTaskId('step', None),
)


@pytest.mark.parametrize(['reference', 'expect_attr', 'expected'], [
    pytest.param('pass', 'step_id', [['step'], ['passed-step'], [], [], []]),
    pytest.param('fail', 'step_id', [[], [], ['failed-step'], [], []]),
    pytest.param('skip', 'step_id', [[], [], [], ['skipped-step'], []]),
    pytest.param('error', 'step_id', [[], [], [], [], ['error-step']]),
    pytest.param('pass[#step]', 'step_id', [['step']]),
    pytest.param('result', 'step_id', [['step'], ['passed-step'], ['failed-step'], ['skipped-step'], ['error-step']]),
    pytest.param('result[#step,skipped-step]', 'step_id', [['step'], ['skipped-step']]),
    pytest.param('result[#*-step]', 'step_id', [['passed-step'], ['failed-step'], ['skipped-step'], ['error-step']]),
    pytest.param('not-pass', 'step_id', [[], [], ['failed-step'], ['skipped-step'], ['error-step']]),
    pytest.param('prop[:score]', 'value', [[1], [2], [], [], []]),
    pytest.param('prop[#step:score]', 'value', [[1]]),
    pytest.param('file[@recipe]', 'name', [['recipe file1.txt', 'recipe file2.cfg', 'recipe file3.cfg']]),
    pytest.param('file[@recipe:#*.txt]', 'name', [['recipe file1.txt']]),
    pytest.param('file[@recipe:classA#*]', 'name', [['recipe file1.txt', 'recipe file2.cfg']]),
    pytest.param('file[@recipe:#"recipe file*"]', 'name', [['recipe file1.txt', 'recipe file2.cfg', 'recipe file3.cfg']]),
    pytest.param('file[@product]', 'name', [['product file.txt']]),
    pytest.param('file[@config]', 'name', [['config file.txt']]),
    pytest.param('file[@step]', 'name', [['step file.txt']]),
    pytest.param('file[@result]', 'name', [['result file.txt'], ['result file2.txt'], [], [], []]),
    pytest.param('opt[@recipe:recipe-opt1]', 'name', [['recipe-opt1']]),
    pytest.param('opt[@recipe:recipe-opt2]', 'name', [[]]),
    pytest.param('opt[@recipe:recipe-opt2@domain]', 'name', [['recipe-opt2']]),
    pytest.param('opt[@product:product-opt]', 'name', [['product-opt']]),
    pytest.param('opt[@config:config-opt]', 'name', [['config-opt']]),
    pytest.param('opt[@step:step-opt]', 'name', [['step-opt']]),
    pytest.param('opt[@result:result-opt]', 'name', [['result-opt'], [], [], [], []]),
    pytest.param('opt[@config:config-opt]', 'value', [['default-domain']]),
    pytest.param('opt[@config:config-opt@domain]', 'value', [['domain']]),
    pytest.param('opt[@config:config-opt@#sub]', 'value', [['subdomain']]),
    pytest.param('opt[@config:config-opt@domain#sub]', 'value', [['domain-subdomain']]),
])
def test_resolve_reference(reference, expect_attr, expected):
    type_, matches, remainder = select_by_reference(reference, test_bundles)

    result = []
    for match in matches:
        result.append([
            getattr(obj, expect_attr, None)
            for obj in match.values
        ])

    assert result == expected


@pytest.mark.parametrize(['reference', 'expected'], [
    pytest.param(':score => test', [1, 2]),
    pytest.param('#step:score', [1]),
])
def test_resolve_prop_reference(reference, expected):
    matches, remainder = select_by_prop_reference(reference, test_results)

    result = []
    for match in matches:
        result.extend(
            getattr(obj, 'value', None)
            for obj in match.values
        )

    assert result == expected


@pytest.mark.parametrize(['reference', 'expected'], [
    pytest.param('@recipe', ['recipe file1.txt', 'recipe file2.cfg', 'recipe file3.cfg']),
    pytest.param('@recipe:#*.txt', ['recipe file1.txt']),
    pytest.param('@recipe:classA#*', ['recipe file1.txt', 'recipe file2.cfg']),
    pytest.param('@recipe:#"recipe file*"', ['recipe file1.txt', 'recipe file2.cfg', 'recipe file3.cfg']),
    pytest.param('@product', ['product file.txt']),
    pytest.param('@config', ['config file.txt']),
    pytest.param('@step', ['step file.txt']),
    pytest.param('@result', ['result file.txt', 'result file2.txt']),
])
def test_resolve_file_reference(reference, expected):
    matches, remainder = select_by_file_reference(reference, test_bundles)

    result = []
    for match in matches:
        result.extend(
            getattr(obj, 'name', None)
            for obj in match.values
        )

    assert result == expected


@pytest.mark.parametrize(['reference', 'expected'], [
    pytest.param('@recipe:recipe-opt1', ['recipe-opt1']),
    pytest.param('@recipe:recipe-opt2', []),
    pytest.param('@recipe:recipe-opt2@domain', ['recipe-opt2']),
    pytest.param('@product:product-opt', ['product-opt']),
    pytest.param('@config:config-opt', ['config-opt']),
    pytest.param('@step:step-opt', ['step-opt']),
    pytest.param('@result:result-opt', ['result-opt']),
])
def test_resolve_opt_reference(reference, expected):
    matches, remainder = select_by_opt_reference(reference, test_bundles)

    result = []
    for match in matches:
        result.extend(
            getattr(obj, 'name', None)
            for obj in match.values
        )

    assert result == expected
