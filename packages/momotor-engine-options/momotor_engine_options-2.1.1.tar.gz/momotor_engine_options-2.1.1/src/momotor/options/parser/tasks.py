from __future__ import annotations

from momotor.options.task_id import StepTaskId


def replace_task_placeholder(text: str | None, task_id: StepTaskId | None) -> str | None:
    """ Replace the :ref:`task id placeholders <task id placeholder>` in a string.

    Replaces the ``$#``, ``$0#``, and ``$1#`` placeholders in a string with the sub-task number.
    ``$#`` and ``$0#`` are replaced with the zero-based task number, ``$1#`` is replaced with the one-based task
    number.

    If the task id is ``None``, or has no sub-tasks, the placeholders are replaced with ``-``.

    >>> replace_task_placeholder('Text $#', StepTaskId('task', (0, 1)))
    'Text 0.1'

    >>> replace_task_placeholder('Text $0#', StepTaskId('task', (0, 1)))
    'Text 0.1'

    >>> replace_task_placeholder('Text $1#', StepTaskId('task', (0, 1)))
    'Text 1.2'

    >>> replace_task_placeholder('Text $#', StepTaskId('task', None))
    'Text -'

    >>> replace_task_placeholder('Text $#', None)
    'Text -'

    :param text: the string to replace the placeholders in
    :param task_id: the task id to use
    :return: the string with the placeholders replaced
    """
    if not text:
        return text

    if '$1#' in text:
        if task_id and task_id.task_number:
            task_nr = '.'.join(str(t + 1) for t in task_id.task_number)
        else:
            task_nr = '-'

        text = text.replace('$1#', task_nr)

    if '$0#' in text or '$#' in text:
        if task_id and task_id.task_number:
            task_nr = '.'.join(str(t) for t in task_id.task_number)
        else:
            task_nr = '-'

        text = text.replace('$0#', task_nr)
        text = text.replace('$#', task_nr)

    return text
