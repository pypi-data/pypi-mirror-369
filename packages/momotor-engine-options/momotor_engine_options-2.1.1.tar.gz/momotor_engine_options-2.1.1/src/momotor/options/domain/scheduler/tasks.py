from __future__ import annotations

import re

from momotor.bundles import RecipeBundle, ConfigBundle, BundleFormatError
from momotor.options.doc import annotate_docstring
from momotor.options.option import OptionDefinition, OptionNameDomain
from momotor.options.parser.placeholders import replace_placeholders
from momotor.options.providers import Providers
from momotor.options.task_id import task_number_from_id, StepTaskId
from momotor.options.types import StepTasksType
from ._domain import DOMAIN

TASKS_OPTION_NAME = OptionNameDomain('tasks', DOMAIN)

#: The :momotor:option:`tasks@scheduler` option defines the number of sub-tasks for a step.
TASKS_OPTION = OptionDefinition(
    name=TASKS_OPTION_NAME,
    type='string',
    doc="""\
        Enable multiple tasks for this step. If not provided, a single task is generated for this step.

        See :external+momotor-engine-options:ref:`scheduler tasks option` for the documentation of this option.
    """,
    location=('config', 'recipe', 'step')
)

TASKS_DEF_RE = re.compile(r'^((([1-9]\d*)|[?])\.)*((([1-9]\d*)|[?*])|((\?\?\.)*([*?]\?)))$')


@annotate_docstring(TASKS_OPTION_NAME=TASKS_OPTION_NAME)
def get_scheduler_tasks_option(recipe: RecipeBundle, config: ConfigBundle | None, step_id: str) \
        -> StepTasksType | None:
    """ Get the :momotor:option:`{TASKS_OPTION_NAME}` option for a single step from the step, recipe or config.

    :param recipe: the recipe bundle
    :param config: (optional) the config bundle
    :param step_id: the id of the step
    :return: the tasks option, parsed into a tuple of ints
    """
    value_def_providers = Providers(
        recipe=recipe,
        task_id=StepTaskId(step_id, None)
    )
    value_def = TASKS_OPTION.resolve(value_def_providers, False)
    value_def = replace_placeholders(value_def, value_def_providers)
    if value_def is not None:
        value_def = value_def.strip()

    value_providers = Providers(
        recipe=recipe,
        config=config
    )
    value = TASKS_OPTION.resolve(
        value_providers, {
            'recipe': step_id,
            'config': step_id
        }
    )
    value = replace_placeholders(value, value_providers)
    if value is not None:
        value = value.strip()

    if not value_def:
        if value is None:
            return None
        else:
            raise BundleFormatError(f"Step {step_id!r}: {TASKS_OPTION_NAME} option not supported")

    if not TASKS_DEF_RE.match(value_def):
        raise BundleFormatError(f"Step {step_id!r}: invalid {TASKS_OPTION_NAME} option"
                                f" definition {value_def!r}")

    value_def_parts = value_def.split('.')
    if value_def_parts[-1] == '*?':
        wildcard = True
        value_def_parts.pop()
    elif value_def_parts[-1] == '*':
        wildcard = True
        value_def_parts[-1] = '?'
    else:
        wildcard = False

    min_length = 0
    for p in value_def_parts:
        if p == '??':
            break
        min_length += 1

    if not wildcard and '?' not in value_def_parts and '??' not in value_def_parts:
        # Fixed dimension -- value is optional but must be equal to value_def if provided
        if value and value != value_def:
            raise BundleFormatError(f"Step {step_id!r}: {TASKS_OPTION_NAME} option value {value!r} "
                                    f"does not match definition {value_def!r}")

        return task_number_from_id(value_def)

    elif not value:
        if min_length > 0:
            # Missing value option
            raise BundleFormatError(f"Step {step_id!r}: missing required {TASKS_OPTION_NAME} option")

        return None

    else:
        try:
            step_tasks = []
            for pos, part in enumerate(value.split('.')):
                try:
                    part_def = value_def_parts[pos]
                except IndexError:
                    if not wildcard:
                        raise ValueError
                else:
                    if part_def not in {'?', '??', part}:
                        raise ValueError

                step_tasks.append(int(part))

        except ValueError:
            step_tasks = None

        if step_tasks is None or len(step_tasks) < min_length:
            raise BundleFormatError(f"Step {step_id!r}: {TASKS_OPTION_NAME} option value {value!r} "
                                    f"does not match definition {value_def!r}")

        return tuple(step_tasks) if step_tasks else None
