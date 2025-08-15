import pytest

from momotor.options.parser.modifier import apply_combiner_modifier


@pytest.mark.parametrize(['mod', 'values', 'expected'], [
    pytest.param('all', [], None),
    pytest.param('all', [True], True),
    pytest.param('all', [False], False),
    pytest.param('all', [True, False], False),
    pytest.param('all', [None], False),
    pytest.param('all', ['test'], True),

    pytest.param('any', [], None),
    pytest.param('any', [True], True),
    pytest.param('any', [False], False),
    pytest.param('any', [True, False], True),
    pytest.param('any', [None], False),
    pytest.param('any', ['test'], True),

    pytest.param('notall', [], None),
    pytest.param('notall', [True], False),
    pytest.param('notall', [False], True),
    pytest.param('notall', [True, False], True),
    pytest.param('notall', [None], True),
    pytest.param('notall', ['test'], False),

    pytest.param('not', [], None),
    pytest.param('not', [True], False),
    pytest.param('not', [False], True),
    pytest.param('not', [True, False], False),
    pytest.param('not', [None], True),
    pytest.param('not', ['test'], False),

    pytest.param('notany', [], None),
    pytest.param('notany', [True], False),
    pytest.param('notany', [False], True),
    pytest.param('notany', [True, False], False),
    pytest.param('notany', [None], True),
    pytest.param('notany', ['test'], False),

    pytest.param('sum', [], None),
    pytest.param('sum', [1], 1),
    pytest.param('sum', [1, 2], 3),
    pytest.param('sum', [None], None),
    pytest.param('sum', ['test'], None),

    pytest.param('max', [], None),
    pytest.param('max', [1], 1),
    pytest.param('max', [1, 2], 2),
    pytest.param('max', [None], None),
    pytest.param('max', ['test'], None),

    pytest.param('min', [], None),
    pytest.param('min', [1], 1),
    pytest.param('min', [1, 2], 1),
    pytest.param('min', [None], None),
    pytest.param('min', ['test'], None),

    pytest.param('cat', [], ''),
    pytest.param('cat', [1], '1'),
    pytest.param('cat', [1, 2], '12'),
    pytest.param('cat', ['lorem'], 'lorem'),
    pytest.param('cat', ['lorem ipsum'], 'lorem ipsum'),
    pytest.param('cat', ['lorem', 'ipsum'], 'loremipsum'),
    pytest.param('cat', ['"lorem"', "'ipsum'"], '"lorem"\'ipsum\''),
    pytest.param('cat', [None], ''),

    pytest.param('join', [], ''),
    pytest.param('join', [1], '1'),
    pytest.param('join', [1, 2], '1,2'),
    pytest.param('join', ['lorem'], 'lorem'),
    pytest.param('join', ['lorem ipsum'], "'lorem ipsum'"),
    pytest.param('join', ['lorem', 'ipsum'], 'lorem,ipsum'),
    pytest.param('join', ['"lorem"', "'ipsum'"], '\'"lorem"\',"\'ipsum\'"'),
    pytest.param('join', [None], ''),

    pytest.param('joinc', [], ''),
    pytest.param('joinc', [1], '1'),
    pytest.param('joinc', [1, 2], '1,2'),
    pytest.param('joinc', ['lorem'], 'lorem'),
    pytest.param('joinc', ['lorem ipsum'], "'lorem ipsum'"),
    pytest.param('joinc', ['lorem', 'ipsum'], 'lorem,ipsum'),
    pytest.param('joinc', ['"lorem"', "'ipsum'"], '\'"lorem"\',"\'ipsum\'"'),
    pytest.param('joinc', [None], ''),

    pytest.param('joincs', [], ''),
    pytest.param('joincs', [1], '1'),
    pytest.param('joincs', [1, 2], '1, 2'),
    pytest.param('joincs', ['lorem'], 'lorem'),
    pytest.param('joincs', ['lorem ipsum'], "'lorem ipsum'"),
    pytest.param('joincs', ['lorem', 'ipsum'], 'lorem, ipsum'),
    pytest.param('joincs', ['"lorem"', "'ipsum'"], '\'"lorem"\', "\'ipsum\'"'),
    pytest.param('joincs', [None], ''),

    pytest.param('json', [], 'null'),
    pytest.param('json', [1], '1'),
    pytest.param('json', [1, 2], '[1,2]'),
    pytest.param('json', ['lorem'], '"lorem"'),
    pytest.param('json', ['lorem', 'ipsum'], '["lorem","ipsum"]'),
    pytest.param('json', [True], 'true'),
    pytest.param('json', [None], 'null'),

    pytest.param('first', [], None),
    pytest.param('first', [1], 1),
    pytest.param('first', [1, 2], 1),
    pytest.param('first', [None], None),
    pytest.param('first', ['one', 'two'], 'one'),

    pytest.param('last', [], None),
    pytest.param('last', [1], 1),
    pytest.param('last', [1, 2], 2),
    pytest.param('last', [None], None),
    pytest.param('last', ['one', 'two'], 'two'),
])
def test_combiner_modifier(mod, values, expected):
    assert apply_combiner_modifier(mod, values) == expected
