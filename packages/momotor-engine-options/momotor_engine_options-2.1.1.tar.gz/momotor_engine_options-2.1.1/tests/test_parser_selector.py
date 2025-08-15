from momotor.bundles import ResultsBundle, RecipeBundle, ConfigBundle, ProductBundle
from momotor.bundles.elements.files import File
from momotor.bundles.elements.options import Option
from momotor.bundles.elements.properties import Property
from momotor.bundles.elements.result import Result, Outcome
from momotor.bundles.elements.steps import Step

import pytest

from momotor.options.providers import Providers
from momotor.options.parser.selector import filter_by_selector, match_by_selector
from momotor.options.task_id import StepTaskId

test_recipe = RecipeBundle()

test_recipe.create(
    id='recipe',
    options=[
        Option(test_recipe).create(
            name='recipe-opt1',
            value=5
        ),
        Option(test_recipe).create(
            domain='test_domain',
            name='recipe-opt2',
            value='option'
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
        ),
    ]
)

test_config = ConfigBundle()
test_config.create(
    id='config',
    options=[
        Option(test_config).create(
            name='config-opt'
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


@pytest.mark.parametrize(['selector', 'expected'], [
    pytest.param('pass', ['step', 'passed-step']),
    pytest.param('fail', ['failed-step']),
    pytest.param('skip', ['skipped-step']),
    pytest.param('error', ['error-step']),
    pytest.param('pass[#step]', ['step']),
    pytest.param('not-pass', ['failed-step', 'skipped-step', 'error-step']),

    pytest.param('result=="pass"', ['step', 'passed-step']),
    pytest.param('result=="fail"', ['failed-step']),
    pytest.param('result=="skip"', ['skipped-step']),
    pytest.param('result=="error"', ['error-step']),
    pytest.param('result[#step]=="pass"', ['step']),
    pytest.param('result!="pass"', ['failed-step', 'skipped-step', 'error-step']),

    pytest.param('prop[:score]', ['step', 'passed-step']),
    pytest.param('prop[:score]?', ['step', 'passed-step']),
    pytest.param('prop[:score]>0', ['step', 'passed-step']),
    pytest.param('prop[:score]>1', ['passed-step']),
    pytest.param('prop[:score]==3', []),

    pytest.param('file[@recipe:classA#*]', ['recipe']),
    pytest.param('file[@recipe]=="recipe file1.txt"', ['recipe']),
    pytest.param('file[@recipe]=="other.txt"', []),
])
def test_resolve_selector(selector, expected):
    elements, remainder = filter_by_selector(selector, test_bundles)
    assert remainder == ''
    ids = [
        getattr(el, 'id', getattr(el, 'step_id', None))
        for el in elements
    ]
    assert ids == expected


@pytest.mark.parametrize(['selector', 'expected'], [
    pytest.param('pass', False),
    pytest.param('%all pass', False),
    pytest.param('%any pass', True),
    pytest.param('%notall pass', True),
    pytest.param('%notany pass', False),

    pytest.param('not-pass', False),
    pytest.param('%any not-pass', True),
    pytest.param('%notall not-pass', True),
    pytest.param('%notany not-pass', False),

    pytest.param('pass[#nonexistant]', False),
    pytest.param('%any pass[#nonexistant]', False),
    pytest.param('not-pass[#nonexistant]', False),
    pytest.param('%any not-pass[#nonexistant]', False),
    pytest.param('%notall pass[#nonexistant]', True),
    pytest.param('%notany pass[#nonexistant]', True),

    pytest.param('%all pass[#step,passed-step]', True),
    pytest.param('%any pass[#step,passed-step]', True),
    pytest.param('%notall pass[#failed-step,skipped-step,error-step]', True),
    pytest.param('%notany pass[#failed-step,skipped-step,error-step]', True),

    pytest.param('not-pass[#step,passed-step]', False),
    pytest.param('%any not-pass[#step,passed-step]', False),

    pytest.param('skip', False),
    pytest.param('%any skip', True),
    pytest.param('not-skip', False),
    pytest.param('%any not-skip', True),

    pytest.param('prop[:score]?', False),  # all results have a score?
    pytest.param('prop[#step,passed-step:score]?', True),  # all listed results have a score?
    pytest.param('prop[#step,passed-step,failed-step:score]?', False),  # all listed results have a score?
    pytest.param('prop[:score]>1', False),
    pytest.param('%any prop[:score]>1', True),

    pytest.param('file[@recipe:classA]', True),
    pytest.param('file[@recipe:classB]', True),
    pytest.param('file[@recipe:classX]', False),
    pytest.param('file[@recipe:classY]', False),
    pytest.param('%notall file[@recipe:classA]', False),
    pytest.param('%notall file[@recipe:classX]', True),

    # files classA and classB exist, files classX and classY don't
    pytest.param('file[@recipe:classA,@recipe:classB]', True),
    pytest.param('file[@recipe:classA,@recipe:classX]', False),
    pytest.param('file[@recipe:classX,@recipe:classY]', False),
    pytest.param('%any file[@recipe:classA,@recipe:classB]', True),
    pytest.param('%any file[@recipe:classA,@recipe:classX]', True),
    pytest.param('%any file[@recipe:classX,@recipe:classY]', False),
    pytest.param('%notall file[@recipe:classA,@recipe:classB]', False),
    pytest.param('%notall file[@recipe:classA,@recipe:classX]', True),
    pytest.param('%notall file[@recipe:classX,@recipe:classY]', True),
    pytest.param('%notany file[@recipe:classA,@recipe:classB]', False),
    pytest.param('%notany file[@recipe:classA,@recipe:classX]', False),
    pytest.param('%notany file[@recipe:classX,@recipe:classY]', True),
])
def test_match_selector(selector, expected):
    result, remainder = match_by_selector(selector, test_bundles)
    assert remainder == ''
    assert result == expected
