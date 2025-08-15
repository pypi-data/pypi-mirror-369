""" Methods for resolving result dependencies
"""
from __future__ import annotations

import collections.abc
from collections import deque

from momotor.bundles import ConfigBundle, RecipeBundle

from momotor.options.domain.scheduler.tasks import get_scheduler_tasks_option
from momotor.options.exception import CircularDependencies, InvalidDependencies
from momotor.options.result_query import make_result_id_re
from momotor.options.task_id import StepTaskId, apply_task_number, \
    get_task_id_lookup, iter_task_ids, iter_task_numbers
from momotor.options.types import StepTasksType

__all__ = [
    'get_full_task_dependencies', 'reverse_task_dependencies', 'get_task_dependencies'
]


def _extract_deps(recipe: RecipeBundle, config: ConfigBundle | None) \
        -> collections.abc.Mapping[str, tuple[collections.abc.Sequence[str], StepTasksType | None]]:
    """ Extract step dependency info from recipe and config
    """
    return {
        step_id: (
            tuple(step.get_dependencies_ids()),
            get_scheduler_tasks_option(recipe, config, step_id)
        )
        for step_id, step in recipe.steps.items()
    }


def _collect_dependency_matches(depend_id_str: str, task_id: StepTaskId, task_ids_map: dict[str, StepTaskId]) \
        -> collections.abc.Generator[StepTaskId, None, None]:

    applied_id = apply_task_number(depend_id_str, task_id)
    if '#' in applied_id:
        # A `#` in the applied_id indicates an arithmetic error
        # Ignoring this allows tasks to depend on a previous task, with the first task not having such
        # dependency
        return

    if '*' in applied_id or '?' in applied_id:
        applied_id_re = make_result_id_re(applied_id)
        for task_id_str, task_id in task_ids_map.items():
            if applied_id_re.fullmatch(task_id_str):
                yield task_id

    else:
        dep_task_id = task_ids_map.get(applied_id)
        if dep_task_id:
            yield dep_task_id
        elif applied_id == depend_id_str:
            raise InvalidDependencies(
                f"Task {str(task_id)!r} depends on non-existent task(s) {depend_id_str!r}"
            )


def _reorder_taskids(task_ids: collections.abc.Container[StepTaskId], ordering: collections.abc.Iterable[StepTaskId]) \
        -> tuple[StepTaskId, ...]:

    # Convert a container of StepTaskIds into a tuple, using the order given by `ordering`
    return tuple(
        task_id
        for task_id in ordering
        if task_id in task_ids
    )


def _get_full_deps(
            step_dep_info: collections.abc.Mapping[str, tuple[collections.abc.Sequence[str], StepTasksType | None]]
        ) -> dict[StepTaskId, tuple[StepTaskId, ...]]:

    # collect all step and task ids
    # step_ids: frozenset[str] = frozenset(step_dep_info.keys())  # all step ids
    step_task_ids: dict[str, collections.abc.Sequence[StepTaskId]] = {}  # task ids for each step

    task_ids = deque()  # all task ids
    for step_id, (depends, tasks) in step_dep_info.items():
        ids = list(iter_task_ids(step_id, tasks))
        step_task_ids[step_id] = ids
        task_ids.extend(ids)

    task_ids_str: dict[str, StepTaskId] = get_task_id_lookup(task_ids)

    # collect all task ids and collect direct dependencies for all steps and tasks
    dependencies: dict[StepTaskId, frozenset[StepTaskId]] = {}  # direct dependencies of each task
    for step_id, (depends, tasks) in step_dep_info.items():
        step_dependencies = deque()  # dependencies of all tasks for this step

        for task_number in iter_task_numbers(tasks):
            task_id = StepTaskId(step_id, task_number)
            task_dependencies = deque()  # dependencies of this task
            for depend_id_str in depends:
                task_dependencies.extend(
                    _collect_dependency_matches(depend_id_str, task_id, task_ids_str)
                )

            dependencies[task_id] = frozenset(task_dependencies)
            step_dependencies.extend(task_dependencies)

        dependencies[StepTaskId(step_id, None)] = frozenset(step_dependencies)

    # collect the full dependencies
    deps_cache: dict[StepTaskId, tuple[StepTaskId, ...]] = {}

    def _collect(tid: StepTaskId, previous: frozenset[StepTaskId]) -> tuple[StepTaskId, ...]:
        if tid not in deps_cache:
            previous = previous | {tid}
            full_task_deps = set(dependencies[tid])
            for full_dep_id in dependencies[tid]:
                if full_dep_id in previous:
                    raise CircularDependencies("Recipe contains circular reference in task dependencies")

                full_task_deps.update(_collect(full_dep_id, previous))

            deps_cache[tid] = _reorder_taskids(full_task_deps, task_ids)

        return deps_cache[tid]

    return {
        task_id: _collect(task_id, frozenset())
        for task_id in task_ids
    }


def _get_direct_deps(
    task_id: StepTaskId,
    step_dep_info: collections.abc.Mapping[str, tuple[collections.abc.Sequence[str], StepTasksType | None]]
) -> tuple[StepTaskId, ...]:

    # collect all step and task ids
    # step_ids: frozenset[str] = frozenset(step_dep_info.keys())  # all step ids
    step_task_ids: dict[str, frozenset[StepTaskId]] = {}  # task ids for each step
    task_ids = deque()  # all task ids
    for step_id, (step_deps, tasks) in step_dep_info.items():
        ids = list(iter_task_ids(step_id, tasks))
        step_task_ids[step_id] = frozenset(ids)
        task_ids.extend(ids)

    task_ids_str: dict[str, StepTaskId] = get_task_id_lookup(task_ids)

    task_dependencies: set[StepTaskId] = set()
    for depend_id_str in step_dep_info[task_id.step_id][0]:
        task_dependencies.update(
            _collect_dependency_matches(depend_id_str, task_id, task_ids_str)
        )

    return _reorder_taskids(task_dependencies, task_ids)


def get_full_task_dependencies(recipe: RecipeBundle, config: ConfigBundle | None) \
        -> dict[StepTaskId, tuple[StepTaskId, ...]]:
    """ Generate the full dependency tree for all steps in the recipe.
    For each task, it lists the all tasks that it depends on, including dependencies of dependencies

    Task ordering is preserved: the tasks listed in the result, both the dict keys and the tuple values,
    are in the same order as the definitions in the recipe.

    :param recipe: the recipe containing the steps
    :param config: (optionally) the config containing step options
    :return: the tasks to tasks mapping. the ordering is guaranteed to be same as the order of the steps in the recipe
    :raises CircularDependencies: if the recipe contains circular dependencies
    :raises InvalidDependencies: if the recipe contains invalid dependencies
    """

    return _get_full_deps(_extract_deps(recipe, config))


def get_task_dependencies(recipe: RecipeBundle, config: ConfigBundle | None, task_id: StepTaskId) \
        -> tuple[StepTaskId, ...]:
    """ Get direct dependencies for a single task.

    Task ordering is preserved: the tasks listed in the result are in the same order as the definitions in the recipe.

    :param recipe: the recipe containing the steps
    :param config: (optionally) the config containing step options
    :param task_id: the task to generate the dependencies of
    :return: the dependencies
    :raises CircularDependencies: if the recipe contains circular dependencies
    :raises InvalidDependencies: if the recipe contains invalid dependencies
    """

    return _get_direct_deps(task_id, _extract_deps(recipe, config))


def reverse_task_dependencies(dependencies: collections.abc.Mapping[StepTaskId, collections.abc.Iterable[StepTaskId]]) \
        -> dict[StepTaskId, tuple[StepTaskId, ...]]:
    """ Reverses the dependency tree generated by :py:func:`get_task_dependencies`,
    i.e. for each step it lists which other steps depend on it.

    Task ordering is preserved: the tasks listed in the result, both the dict keys and the tuple values,
    are in the same order as in the `dependencies` argument.

    :param dependencies: the task dependencies
    :return: the reverse dependencies
    """
    rdeps = {
        task_id: deque()
        for task_id in dependencies.keys()
    }

    for dep_id, deps in dependencies.items():
        for dep in deps:
            rdeps[dep].append(dep_id)

    return {
        rdep_id: _reorder_taskids(deps, dependencies.keys())
        for rdep_id, deps in rdeps.items()
    }
