import pytest

from momotor.options.dependencies import _get_direct_deps, _get_full_deps  # noqa
from momotor.options.exception import InvalidDependencies, CircularDependencies
from momotor.options.task_id import StepTaskId, task_number_from_id


@pytest.mark.parametrize(['step_dep_info', 'direct_deps', 'full_deps'], [
    pytest.param(
        {},
        {},
        {},
        id='empty'
    ),
    pytest.param(
        {
            'step': ([], None),
        },
        {
            'step': tuple(),
        },
        {
            'step': tuple(),
        },
        id='one step'
    ),
    pytest.param(
        {
            'step1': ([], None),
            'step2': ([], None),
        },
        {
            'step1': tuple(),
            'step2': tuple(),
        },
        {
            'step1': tuple(),
            'step2': tuple(),
        },
        id='two independent steps'
    ),
    pytest.param(
        {
            'step1': ([], None),
            'step2': (['step1'], None),
        },
        {
            'step1': tuple(),
            'step2': ('step1',),
        },
        {
            'step1': tuple(),
            'step2': ('step1',),
        },
        id='single dependency'
    ),
    pytest.param(
        {
            'step1': (['step2'], None),
            'step2': ([], None),
        },
        {
            'step1': ('step2',),
            'step2': tuple()
        },
        {
            'step1': ('step2',),
            'step2': tuple()
        },
        id='forward single dependency'
    ),
    pytest.param(
        {
            'step1': ([], None),
            'step2': (['step1'], None),
            'step3': (['step2'], None),
        },
        {
            'step1': tuple(),
            'step2': ('step1',),
            'step3': ('step2',),
        },
        {
            'step1': tuple(),
            'step2': ('step1',),
            'step3': ('step1', 'step2'),
        },
        id='line dependency'
    ),
    pytest.param(
        {
            'step1': (['step2'], None),
            'step2': (['step3'], None),
            'step3': ([], None)
        },
        {
            'step1': ('step2',),
            'step2': ('step3',),
            'step3': tuple(),
        },
        {
            'step1': ('step2', 'step3',),
            'step2': ('step3',),
            'step3': tuple(),
        },
        id='forward line dependency'
    ),
    pytest.param(
        {
            'step1': ([], None),
            'step2': (['step1'], None),
            'step3': (['step1'], None),
            'step4': (['step2', 'step3'], None)
        },
        {
            'step1': tuple(),
            'step2': ('step1',),
            'step3': ('step1',),
            'step4': ('step2', 'step3',),
        },
        {
            'step1': tuple(),
            'step2': ('step1',),
            'step3': ('step1',),
            'step4': ('step1', 'step2', 'step3',),
        },
        id='multiple dependency'
    ),
    pytest.param(
        {
            'step': ([], (2,))
        },
        {
            'step.0': tuple(),
            'step.1': tuple(),
        },
        {
            'step.0': tuple(),
            'step.1': tuple(),
        },
        id='one step, two tasks'
    ),
    pytest.param(
        {
            'step1': ([], (2,)),
            'step2': (['step1.*'], None)
        },
        {
            'step1.0': tuple(),
            'step1.1': tuple(),
            'step2': ('step1.0', 'step1.1',),
        },
        {
            'step1.0': tuple(),
            'step1.1': tuple(),
            'step2': ('step1.0', 'step1.1',),
        },
        id='two steps, two tasks for first'
    ),
    pytest.param(
        {
            'step1': ([], None),
            'step2': (['step1'], (2,))
        },
        {
            'step1': tuple(),
            'step2.0': ('step1',),
            'step2.1': ('step1',),
        },
        {
            'step1': tuple(),
            'step2.0': ('step1',),
            'step2.1': ('step1',),
        },
        id='two steps, two tasks for second'
    ),
    pytest.param(
        {
            'step1': ([], (2,)),
            'step2': (['step1.0'], None)
        },
        {
            'step1.0': tuple(),
            'step1.1': tuple(),
            'step2': ('step1.0',),
        },
        {
            'step1.0': tuple(),
            'step1.1': tuple(),
            'step2': ('step1.0',),
        },
        id='two steps, two tasks for first, dependency on single sub-task'
    ),
    pytest.param(
        {
            'step1': ([], (2,)),
            'step2': (['step1.$0'], (2,))
        },
        {
            'step1.0': tuple(),
            'step1.1': tuple(),
            'step2.0': ('step1.0',),
            'step2.1': ('step1.1',),
        },
        {
            'step1.0': tuple(),
            'step1.1': tuple(),
            'step2.0': ('step1.0',),
            'step2.1': ('step1.1',),
        },
        id='two steps, two tasks for first, dependency on sub-task reference'
    ),
    pytest.param(
        {
            'step1': ([], (2, 2,)),
            'step2': (['step1.$0-1.*'], (2,)),
        },
        {
            'step1.0.0': tuple(),
            'step1.0.1': tuple(),
            'step1.1.0': tuple(),
            'step1.1.1': tuple(),
            'step2.0': tuple(),
            'step2.1': ('step1.0.0', 'step1.0.1',),
        },
        {
            'step1.0.0': tuple(),
            'step1.0.1': tuple(),
            'step1.1.0': tuple(),
            'step1.1.1': tuple(),
            'step2.0': tuple(),
            'step2.1': ('step1.0.0', 'step1.0.1',),
        },
        id='two steps, arithmetic and wildcard dependencies'
    ),
    pytest.param(
        {
            'step1': ([], (2, 2,)),
            'step2': (['step1.?.0'], None),
        },
        {
            'step1.0.0': tuple(),
            'step1.0.1': tuple(),
            'step1.1.0': tuple(),
            'step1.1.1': tuple(),
            'step2': ('step1.0.0', 'step1.1.0',),
        },
        {
            'step1.0.0': tuple(),
            'step1.0.1': tuple(),
            'step1.1.0': tuple(),
            'step1.1.1': tuple(),
            'step2': ('step1.0.0', 'step1.1.0',),
        },
        id='two steps, ? wildcard dependency'
    ),
])
def test_validate_task_dependencies(step_dep_info, direct_deps, full_deps):
    def make_task_id(task_id_str) -> StepTaskId:
        if '.' in task_id_str:
            step_id, task_id = task_id_str.split('.', 1)
        else:
            step_id, task_id = task_id_str, None

        return StepTaskId(step_id, task_number_from_id(task_id))

    assert {
        task_id_str: tuple(str(dep_id) for dep_id in _get_direct_deps(make_task_id(task_id_str), step_dep_info))
        for task_id_str in direct_deps.keys()
    } == direct_deps

    assert {
        str(task_id): tuple(str(dep_id) for dep_id in dependencies)
        for task_id, dependencies in _get_full_deps(step_dep_info).items()
    } == full_deps


@pytest.mark.parametrize(['step_dep_info'], [
    pytest.param(
        {
            'step1': (['step2'], None),
            'step2': (['step1'], None),
        },
        id='cross dependency'
    ),
    pytest.param(
        {
            'step1': (['step3'], None),
            'step2': (['step1'], None),
            'step3': (['step2'], None),
        },
        id='deep dependency'
    ),
    pytest.param(
        {
            'step1': (['step2'], None),
            'step2': (['step3'], None),
            'step3': (['step1'], None)
        },
        id='forward deep dependency'
    ),
])
def test_validate_get_complete_step_dependencies_circular(step_dep_info):
    with pytest.raises(CircularDependencies):
        _get_full_deps(step_dep_info)


@pytest.mark.parametrize(['step_dep_info'], [
    pytest.param(
        {
            'step1': (['step0'], None),
        },
        id='non-existing dependency'
    )
])
def test_validate_get_complete_step_dependencies_invalid(step_dep_info):
    with pytest.raises(InvalidDependencies):
        _get_full_deps(step_dep_info)
