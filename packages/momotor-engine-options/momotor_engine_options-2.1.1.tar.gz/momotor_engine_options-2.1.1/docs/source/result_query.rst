.. _result query:

Result query
============

A result query references one or more results in a results bundle. Each result has an id, consisting of the
id of the step that generated that result, and optionally one or more task number for steps with multiple tasks.
The id and task numbers are separated with a dot (``.``)

For example, the following result ids are valid: ``step1``, ``step.1``, ``step.1.2.3.4.5``

Result queries allows selection of these result ids using wildcards and with a replacement for some of the task
numbers based on another task number.

The syntax for a result query is

.. productionlist:: result-query
   queries: `query` ( "," `query` )*
   query: `step_id` [ `task_query` ]
        : | [ `step_id` ] "*" [ `task_query` ]
        : | [ `step_id` ] "**"
   task_query: ( "." `task_number` )* | ".$@"
   task_number: `integer` | `task_wildcard` | `task_reference`
   task_wildcard: "*" | "?"
   task_reference: "$" `integer` [ `oper` `integer` ]
   oper: "+" | "-" | "*" | "/" | "%"

Where `step-id` is a (XML) id without periods (``.``), and `integer` is a positive natural number
(including zero).

The most simple result queries are just the result id and will match that single result id:

+-----------------------------------------+----------------------------------------------------------------------------+
| result query                            |                                                                            |
+=========================================+============================================================================+
| ``step1``                               | Matches exactly one result, with id ``step1``                              |
+-----------------------------------------+----------------------------------------------------------------------------+
| ``step.1``                              | Matches exactly one result, with id ``step.1``                             |
+-----------------------------------------+----------------------------------------------------------------------------+
| ``step.1.2.3.4.5``                      | Matches exactly one result, with id ``step.1.2.3.4.5``                     |
+-----------------------------------------+----------------------------------------------------------------------------+

Multiple queries are possible by separating them with a comma (``,``)

+-----------------------------------------+----------------------------------------------------------------------------+
| result query                            |                                                                            |
+=========================================+============================================================================+
| ``step1,step.1``                        | Matches exactly two results: ``step1`` and ``step.1``                      |
+-----------------------------------------+----------------------------------------------------------------------------+

A ``*`` is a wildcard character that matches one or more elements and is allowed in both the
`step-id` and `task-number` sections. In the `step-id`, the ``*`` wildcard does not have to be used only at the end:

+-----------------------------------------+----------------------------------------------------------------------------+
| result query                            |                                                                            |
+=========================================+============================================================================+
| ``st*p``                                | Matches ``step``, ``stap``, ``steeeeeep``, etc.                            |
+-----------------------------------------+----------------------------------------------------------------------------+
| ``step*``                               | Matches any step whose id starts with ``step``, but without task number    |
+-----------------------------------------+----------------------------------------------------------------------------+
| ``step.*``                              | Matches any step whose id equals ``step`` followed by a task number,       |
|                                         | e.g. ``step.1`` and ``step.1.2.3.4.5`` match, but ``step`` does not        |
+-----------------------------------------+----------------------------------------------------------------------------+
| ``step*.*``                             | Combination of the above two: matches ``step.1``, ``stepxyz.2``, but not   |
|                                         | `step`                                                                     |
+-----------------------------------------+----------------------------------------------------------------------------+
| ``step**``                              | Matches any step whose id starts with ``step``, with or without            |
|                                         | any task number                                                            |
+-----------------------------------------+----------------------------------------------------------------------------+

The `task-number` section can also contain a ``?`` wildcard, which will match exactly one element:

+-----------------------------------------+----------------------------------------------------------------------------+
| result query                            |                                                                            |
+=========================================+============================================================================+
| ``step.?``                              | Matches ``step.1``, but not ``step`` or ``step.1.2.3.4.5``                 |
+-----------------------------------------+----------------------------------------------------------------------------+
| ``step.1.?``                            | Matches ``step.1.1``, ``step.1.42`` but not                                |
|                                         | ``step``, ``step.1`` or ``step.1.2.3.4.5``                                 |
+-----------------------------------------+----------------------------------------------------------------------------+
| ``step.?.1``                            | Matches ``step.1.1``, ``step.42.1`` but not                                |
|                                         | ``step``, ``step.1`` or ``step.1.2.3.4.5``                                 |
+-----------------------------------------+----------------------------------------------------------------------------+

It is also possible to reference a specific task number based on a current task number. For example, when executing
task ``step.2.3`` it would be useful to reference another based on the current task number ``2.3``. This is done using
a ``$`` reference. Where ``$0`` references the first task number element (``2`` in this example), ``$1`` references
the second element (``3``), etc.

The following examples all use current task number ``2.3``:

+-----------------------------------------+----------------------------------------------------------------------------+
| result query                            |                                                                            |
+=========================================+============================================================================+
| ``task.$0``                             | References result id ``task.2``                                            |
+-----------------------------------------+----------------------------------------------------------------------------+
| ``task.$1``                             | References result id ``task.3``                                            |
+-----------------------------------------+----------------------------------------------------------------------------+
| ``task.$0.$1``                          | References result id ``task.2.3``                                          |
+-----------------------------------------+----------------------------------------------------------------------------+
| ``task.$1.$0``                          | References result id ``task.3.2``                                          |
+-----------------------------------------+----------------------------------------------------------------------------+
| ``task.$@``                             | Special "shortcut" to replace the full task number, here ``task.2.3``      |
+-----------------------------------------+----------------------------------------------------------------------------+

Simple arithmetic is possible on the task number references. Available operations
are ``+`` (addition), ``-`` (subtraction), ``*`` (multiplication), ``/`` (integer floor division) and
``%`` (modulo). The right-hand side of the operator has to be an integer, it cannot be another reference.

+-----------------------------------------+----------------------------------------------------------------------------+
| result query                            |                                                                            |
+=========================================+============================================================================+
| ``task.$0-1``                           | References result id ``task.1``                                            |
+-----------------------------------------+----------------------------------------------------------------------------+
| ``task.$0+1``                           | References result id ``task.3``                                            |
+-----------------------------------------+----------------------------------------------------------------------------+
| ``task.$0*2``                           | References result id ``task.4``                                            |
+-----------------------------------------+----------------------------------------------------------------------------+
| ``task.$0/2.$1/2``                      | References result id ``task.1.1``                                          |
+-----------------------------------------+----------------------------------------------------------------------------+
| ``task.$0%2.$1%2``                      | References result id ``task.0.1``                                          |
+-----------------------------------------+----------------------------------------------------------------------------+

If a subtraction results in a negative number the value is replaced with ``#NEG``, and if a division results in
a division by zero the value is replaced with ``#INF``. Both of these result in invalid result id.

+-----------------------------------------+----------------------------------------------------------------------------+
| result query                            |                                                                            |
+=========================================+============================================================================+
| ``task.$0-3``                           | References result id ``task.#NEG``                                         |
+-----------------------------------------+----------------------------------------------------------------------------+
| ``task.$0/0``                           | References result id ``task.#INF``                                         |
+-----------------------------------------+----------------------------------------------------------------------------+

.. automodule:: momotor.options.result_query
   :members:
   :inherited-members:
   :undoc-members:
