import pytest

from momotor.bundles import ResultsBundle, RecipeBundle, ConfigBundle, ProductBundle
from momotor.bundles.elements.files import File
from momotor.bundles.elements.options import Option
from momotor.bundles.elements.properties import Property
from momotor.bundles.elements.result import Result, Outcome
from momotor.bundles.elements.steps import Step
from momotor.options.parser.placeholders import replace_placeholders
from momotor.options.providers import Providers
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
            step_id='passed',
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
            step_id='failed',
            outcome=Outcome.FAIL
        ),
        Result(test_results).create(
            step_id='skipped',
            outcome=Outcome.SKIP
        ),
        Result(test_results).create(
            step_id='error',
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


@pytest.mark.parametrize(['template', 'expected'], [
    pytest.param('', ''),
    pytest.param('no placeholder', 'no placeholder'),
    pytest.param('escaped $${template}', 'escaped ${template}'),
    pytest.param('score ${prop[:score]}', 'score 1,2'),
    pytest.param('score ${%min prop[:score]}', 'score 1'),
    pytest.param('score ${%max prop[:score]}', 'score 2'),
    pytest.param('score ${%sum prop[:score]}', 'score 3'),
    pytest.param('score ${%first prop[:score]}', 'score 1'),
    pytest.param('score ${%last prop[:score]}', 'score 2'),
    pytest.param('score ${%join prop[:score]}', 'score 1,2'),
    pytest.param('score ${%joinc prop[:score]}', 'score 1,2'),
    pytest.param('score ${%joins prop[:score]}', 'score 1 2'),
    pytest.param('score ${%joincs prop[:score]}', 'score 1, 2'),
    pytest.param('score ${%json prop[:score]}', 'score [1,2,null,null,null]'),
    pytest.param('score ${%cat prop[:score]}', 'score 12'),
    pytest.param('score ${%all prop[:score]}', 'score False'),
    pytest.param('score ${%any prop[:score]}', 'score True'),
    pytest.param('score ${%notall prop[:score]}', 'score True'),
    pytest.param('score ${%notany prop[:score]}', 'score False'),

    pytest.param('passed: ${pass}', "passed: step,passed"),
    pytest.param('all passed: ${%all pass}', "all passed: False"),
    pytest.param('any passed: ${%any pass}', "any passed: True"),
    pytest.param('notall passed: ${%notall pass}', "notall passed: True"),
    pytest.param('notany passed: ${%notany pass}', "notany passed: False"),

    pytest.param('files: ${file[@recipe:classA#*]}', "files: 'recipe file1.txt','recipe file2.cfg'"),
    pytest.param('files: ${%json file[@recipe:classA#*]}', 'files: ["recipe file1.txt","recipe file2.cfg"]'),

    # If the template is not an `str`, it is returned unmodified
    pytest.param(42, 42),
    pytest.param(True, True),
    pytest.param(None, None),
    pytest.param(b'${pass}', b'${pass}'),
])
def test_replace_placeholders(template, expected):
    result = replace_placeholders(template, test_bundles)
    assert result == expected
