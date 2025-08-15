.. _references:

========================
Element reference syntax
========================

Element reference syntax is used by Momotor checklets to allow recipes and config bundles to easily and consistently
refer to elements of a bundle using a standardized syntax.
Usually these references are used in the recipe and config bundle options.

.. _reference:

Reference
=========

A *reference* refers to one or more
:py:class:`~momotor.bundles.elements.result.Result`,
:py:class:`~momotor.bundles.elements.properties.Property`,
:py:class:`~momotor.bundles.elements.files.File` or
:py:class:`~momotor.bundles.elements.options.Option` elements in bundles.

The syntax for a *reference* is:

.. productionlist:: reference
   typed_reference: `type` "[" `reference` [ "," `reference` ]* "]"
   type: "file" | "prop" | "opt" | "result" | `outcome` | `not_outcome`
   outcome: "pass" | "fail" | "error" | "skip"
   not_outcome: "not-" `outcome`
   reference: ( `provider_id` [ ":" `typeref` ] ) | `typeref`
   provider_id: "@" `provider` ] [ "#" `id` ( "," `id` )* ]
   provider: "recipe" | "config" | "product" | "step" | "result"
   typeref: `propref` | `fileref` | `optref`
   propref: `name`
   fileref: `class` | [ `class` ] "#" `name`
   optref: `name` [ "@" `domain` ]

The :token:`~reference:type` defines the element type which is referenced. Choices are

+----------------------------------------------+---------------------------------------------------------------------+
| :token:`~reference:type`                     | element referenced                                                  |
+==============================================+=====================================================================+
| :token:`prop <reference:type>`               | One or more                                                         |
|                                              | :py:class:`~momotor.bundles.elements.properties.Property` elements  |
+----------------------------------------------+---------------------------------------------------------------------+
| :token:`file <reference:type>`               | One or more                                                         |
|                                              | :py:class:`~momotor.bundles.elements.files.File` elements           |
+----------------------------------------------+---------------------------------------------------------------------+
| :token:`opt <reference:type>`                | One or more                                                         |
|                                              | :py:class:`~momotor.bundles.elements.options.Option` elements       |
+----------------------------------------------+---------------------------------------------------------------------+
| :token:`result <reference:type>`             | One or more                                                         |
|                                              | :py:class:`~momotor.bundles.elements.result.Result` elements        |
+----------------------------------------------+---------------------------------------------------------------------+
| :token:`pass <reference:outcome>` /          | All :py:class:`~momotor.bundles.elements.result.Result`             |
| :token:`fail <reference:outcome>` /          | elements with given outcome, e.g. :token:`pass <reference:outcome>` |
| :token:`skip <reference:outcome>` /          | selects all passed results                                          |
| :token:`error <reference:outcome>`           |                                                                     |
+----------------------------------------------+---------------------------------------------------------------------+
| :token:`not-pass <reference:not_outcome>` /  | All :py:class:`~momotor.bundles.elements.result.Result`             |
| :token:`not-fail <reference:not_outcome>` /  | elements with a different outcome, e.g.                             |
| :token:`not-skip <reference:not_outcome>` /  | :token:`not-pass <reference:not_outcome>` selects all results that  |
| :token:`not-error <reference:not_outcome>`   | did not pass                                                        |
+----------------------------------------------+---------------------------------------------------------------------+

The :token:`~reference:provider` selects the bundle from which these elements are referenced. Choices are

+--------------------------------------------+---------------------------------------------------------------------+
| :token:`~reference:provider`               | element referenced                                                  |
+============================================+=====================================================================+
| :token:`@recipe <reference:provider>`      | The :py:class:`~momotor.bundles.RecipeBundle` bundle                |
+--------------------------------------------+---------------------------------------------------------------------+
| :token:`@config <reference:provider>`      | The :py:class:`~momotor.bundles.ConfigBundle` bundle                |
+--------------------------------------------+---------------------------------------------------------------------+
| :token:`@product <reference:provider>`     | The :py:class:`~momotor.bundles.ProductBundle` bundle               |
+--------------------------------------------+---------------------------------------------------------------------+
| :token:`@result <reference:provider>`      | :py:class:`~momotor.bundles.elements.result.Result` elements in a   |
|                                            | :py:class:`~momotor.bundles.RecipeBundle` bundle                    |
+--------------------------------------------+---------------------------------------------------------------------+
| :token:`@step <reference:provider>`        | The current :py:class:`~momotor.bundles.elements.steps.Step` in the |
|                                            | :py:class:`~momotor.bundles.RecipeBundle` bundle                    |
+--------------------------------------------+---------------------------------------------------------------------+

Not all :token:`~reference:type` / :token:`~reference:provider` combinations are valid.
For the :token:`prop <reference:type>`, :token:`result <reference:type>`, :token:`~reference:outcome`
and :token:`~reference:not_outcome` types, only the :token:`@result <reference:provider>` provider is valid.
Since there is only one provider valid for these types, specifying the provider is optional in this case.
For the :token:`opt <reference:type>` and :token:`file <reference:type>` types, all providers are valid.

Since :py:class:`~momotor.bundles.ResultsBundle` bundles contain multiple results, one or more ``id`` tokens
can be specified to limit the list of results. If no ``id`` is given, all results in the bundle are referenced.
``id`` is not used with other providers. The ``id`` can contain :ref:`task id <task_id>` placeholders and these
will be expanded with the task numbers for the currently active task.

The :token:`file <reference:type>` reference type requires an additional :token:`name and/or class <reference:fileref>`
to select the file(s). The name can contain glob-like wildcards and can be quoted if it contains space or any
other special characters.

The :token:`prop <reference:type>` reference type requires an additional :token:`name <reference:propref>` to
select the property.

The :token:`opt <reference:type>` reference type requires an additional
:token:`name with optional domain <reference:optref>` to select the option.
If domain is not provided it defaults to ``checklet``.

Similar to ``id``, :ref:`task id <task_id>` placeholders will be expanded in references too.

Examples of references are:

=========================================== =============================================================================================
reference                                   result
------------------------------------------- ---------------------------------------------------------------------------------------------
``prop[:name1]``                            Selects properties with name ``name1`` from all results in the results bundle
``prop[#id1:name1]``                        Selects properties with name ``name1`` from result with result id ``#id1``
``prop[@result#id1:name1]``                 Same as above (``@result`` is optional and implied)
``file[@config:class1#name1]``              Selects the file with class ``class1`` and exact name ``name1`` from the config
``file[@config:class1#*.txt]``              Selects all files with class ``class1`` and name ending with ``.txt`` from the config
``file[@recipe:class1#doc.txt]``            Selects all files with class ``class1`` and exact name ``doc.txt`` from the recipe
``file[@recipe:class1#"doc 1.txt"]``        Selects all files with class ``class1`` and exact name ``doc 1.txt`` from the recipe.
                                            Because of the whitespace, the name has to be quoted
``opt[@step:name1]``                        Selects the option with name ``name1`` in (default) domain ``checklet`` of the current step
``opt[@step:name1@domain1]``                Selects the option with name ``name1`` in domain ``domain1`` of the current step
``result``                                  Select all results from the results bundle
``result[#id1]``                            Select result with id ``id1`` from the results bundle
``pass``                                    Select all passed results from the results bundle
``pass[#id1,#id2]``                         Select results with result id ``id1`` and ``id2``, if they passed
``pass[@result#id1,#id2]``                  Same as above (``@result`` is optional and implied)
``not-pass[@result#id1,#id2]``              Select results with result id ``id1`` and ``id2``, if they did not pass
=========================================== =============================================================================================

.. _reference value:

Reference value
===============

A *reference value* is a single value generated from a :ref:`reference <reference>`.
Checklets can use *reference values* in options to resolve those options into values.
*Reference values* are also used as part of the :ref:`placeholder <placeholder>` syntax.

A *reference value* is a :ref:`reference <reference>`, optionally prefixed with a modifier:

.. productionlist:: reference_value
   value_reference: [ "%" `mod` ] `~reference:typed_reference`
   mod: "all" | "any" | "notall" | "notany" | "not" | "sum"
      : | "sumf" | "sumr" | "max" | "min" | "cat" | "join"
      : | "joinc" | "joins" | "joincs" | "json" | "first" | "last"

.. _reference type value:

What value is produced by a *reference value* is determined by the reference :token:`~reference:type`:

+------------------------------------------------+---------------------------------------------------------------------+
| :token:`~reference:type`                       | value                                                               |
+================================================+=====================================================================+
| :token:`prop <reference:type>` /               | The :attr:`value` attribute of the referenced                       |
| :token:`opt <reference:type>`                  | :py:class:`~momotor.bundles.elements.properties.Property` or        |
|                                                | :py:class:`~momotor.bundles.elements.options.Option` elements       |
+------------------------------------------------+---------------------------------------------------------------------+
| :token:`file <reference:type>`                 | The :attr:`name` attribute of the referenced                        |
|                                                | :py:class:`~momotor.bundles.elements.files.File` elements           |
+------------------------------------------------+---------------------------------------------------------------------+
| :token:`result <reference:type>`               | The :attr:`outcome` attribute of the referenced                     |
|                                                | :py:class:`~momotor.bundles.elements.result.Result` elements        |
|                                                | [#resultvalue]_                                                     |
+------------------------------------------------+---------------------------------------------------------------------+
| | :token:`pass <reference:outcome>` /          | The :attr:`step_id` attribute of the referenced                     |
|   :token:`fail <reference:outcome>` /          | :py:class:`~momotor.bundles.elements.result.Result` elements        |
|   :token:`skip <reference:outcome>` /          | [#resultvalue]_                                                     |
|   :token:`error <reference:outcome>` /         |                                                                     |
| | :token:`not-pass <reference:not_outcome>` /  |                                                                     |
|   :token:`not-fail <reference:not_outcome>` /  |                                                                     |
|   :token:`not-skip <reference:not_outcome>` /  |                                                                     |
|   :token:`not-error <reference:not_outcome>`   |                                                                     |
+------------------------------------------------+---------------------------------------------------------------------+

.. [#resultvalue]

   The :token:`result <reference:type>` and :token:`~reference:outcome` / :token:`~reference:not_outcome` types
   produce different values, although they both reference :py:class:`~momotor.bundles.elements.result.Result` elements.

.. _reference value modifier:

The :token:`~reference_value:mod` modifier indicates how the list of values produced by the :ref:`reference <reference>`
is converted into a *reference value*.
The default modifier is :token:`join <reference_value:mod>`, but this can be changed by the
caller of the :py:meth:`~momotor.options.parser.reference.resolve_reference_value` method.

+------------------------------------------------+---------------------------------------------------------------------+
| :token:`~reference_value:mod`                  | result                                                              |
+================================================+=====================================================================+
| :token:`%all <reference_value:mod>`            | `True` if all values are considered `True` [#anyall]_               |
+------------------------------------------------+---------------------------------------------------------------------+
| :token:`%any <reference_value:mod>`            | `True` if at least one value is considered `True` [#anyall]_        |
+------------------------------------------------+---------------------------------------------------------------------+
| :token:`%notall <reference_value:mod>`         | `False` if all values are considered `True` [#anyall]_              |
+------------------------------------------------+---------------------------------------------------------------------+
| :token:`%notany <reference_value:mod>`         | `False` if at least one value is considered `True` [#anyall]_       |
+------------------------------------------------+---------------------------------------------------------------------+
| :token:`%not <reference_value:mod>`            | Alias for :token:`%notany <reference_value:mod>`                    |
+------------------------------------------------+---------------------------------------------------------------------+
| :token:`%sum <reference_value:mod>`            | The sum of the values [#summaxmin]_                                 |
+------------------------------------------------+---------------------------------------------------------------------+
| :token:`%sumf <reference_value:mod>`           | The sum of the values, rounded down to `int` [#summaxmin]_          |
+------------------------------------------------+---------------------------------------------------------------------+
| :token:`%sumr <reference_value:mod>`           | The sum of the values, rounded to the nearest `int` [#summaxmin]_   |
+------------------------------------------------+---------------------------------------------------------------------+
| :token:`%max <reference_value:mod>`            | The maximum of the values [#summaxmin]_                             |
+------------------------------------------------+---------------------------------------------------------------------+
| :token:`%min <reference_value:mod>`            | The minimum of the values [#summaxmin]_                             |
+------------------------------------------------+---------------------------------------------------------------------+
| :token:`%cat <reference_value:mod>`            | All values concatenated without any separator                       |
+------------------------------------------------+---------------------------------------------------------------------+
| :token:`%join <reference_value:mod>`           | All values concatenated with a single comma, without spaces         |
+------------------------------------------------+---------------------------------------------------------------------+
| :token:`%joinc <reference_value:mod>`          | Alias for :token:`%join <reference_value:mod>`                      |
+------------------------------------------------+---------------------------------------------------------------------+
| :token:`%joins <reference_value:mod>`          | All values concatenated with a space character                      |
+------------------------------------------------+---------------------------------------------------------------------+
| :token:`%joincs <reference_value:mod>`         | All values concatenated with a comma followed by a space            |
+------------------------------------------------+---------------------------------------------------------------------+
| :token:`%json <reference_value:mod>`           | The values converted into a json list [#json]_                      |
+------------------------------------------------+---------------------------------------------------------------------+
| :token:`%first <reference_value:mod>`          | The first value [#firstlast]_                                       |
+------------------------------------------------+---------------------------------------------------------------------+
| :token:`%last <reference_value:mod>`           | The last value [#firstlast]_                                        |
+------------------------------------------------+---------------------------------------------------------------------+

.. [#anyall]

   For the :token:`all <reference_value:mod>`, :token:`any <reference_value:mod>`, :token:`not <reference_value:mod>`,
   :token:`notall <reference_value:mod>` and :token:`notany <reference_value:mod>` the values are interpreted
   as booleans in the same way Python does: a 0 (zero), `None` or empty string is considered to be `False`, and
   anything else is considered to be `True`. Empty sequences result in `None`.

.. [#summaxmin]

   For the :token:`sum <reference_value:mod>`,  :token:`sumf <reference_value:mod>`, :token:`sumr <reference_value:mod>`,
   :token:`max <reference_value:mod>` and :token:`min <reference_value:mod>`
   modifiers, string values will be cast into `float` or `int` if possible, or ignored otherwise. If all values
   resolve to integers, the result of these modifiers will be an integer. If at least one of the values is a floating
   point value, the result will be a float, except for :token:`sumf <reference_value:mod>` and
   :token:`sumr <reference_value:mod>` which will resolve to an integer. Empty sequences result in `None`.

.. [#json]

   The :token:`json <reference_value:mod>` modifier returns a json list with the values converted to equivalent
   JSON types.

.. [#firstlast]

   The :token:`first <reference_value:mod>` and :token:`last <reference_value:mod>` modifiers return the first or last
   value and keep the type intact. Empty sequences result in `None`.

All other modifiers convert the values to a string before joining.

.. _selector:

Selector
========

A *selector* filters :ref:`references <reference>` on the value. The value is one of the attributes of the referenced
elements, the same attribute as used for :ref:`value references <reference type value>`.

A *selector* has the following syntax:

.. productionlist:: selector
   selector: `~reference:typed_reference` [ `selection` ]
   selection: `unary_oper` | `binary_oper` `value`
   unary_oper: "?" | "!"
   binary_oper: "==" | "!=" | ">" | ">=" | "<" | "<="

+------------------------------------------------+---------------------------------------------------------------------+
| operator                                       | action                                                              |
+================================================+=====================================================================+
| (no selector)                                  | Selects all elements (i.e. same as the reference)                   |
+------------------------------------------------+---------------------------------------------------------------------+
| :token:`? <selector:unary_oper>`               | Unary operator which selects the elements whose value is            |
|                                                | considered `True` [#queexl]_                                        |
+------------------------------------------------+---------------------------------------------------------------------+
| :token:`\! <selector:unary_oper>`              | Unary operator which selects the elements whose value is            |
|                                                | considered `False` [#queexl]_                                       |
+------------------------------------------------+---------------------------------------------------------------------+
| :token:`== <selector:binary_oper>` /           | Binary operators.                                                   |
| :token:`\!= <selector:binary_oper>` /          | Selects the elements whose value matches the equation.              |
| :token:`> <selector:binary_oper>` /            | String values to compare with need to be quoted.                    |
| :token:`>= <selector:binary_oper>` /           |                                                                     |
| :token:`< <selector:binary_oper>` /            |                                                                     |
| :token:`<= <selector:binary_oper>`             |                                                                     |
+------------------------------------------------+---------------------------------------------------------------------+

.. [#queexl]

   For the :token:`? <selector:unary_oper>` and :token:`\! <selector:unary_oper>` operators the values are interpreted
   as booleans in the same way Python does: a 0 (zero), `None` or empty string is considered to be `False`, and
   anything else is considered to be `True`.

Example selectors:

+------------------------------------------------+---------------------------------------------------------------------+
| selector                                       |                                                                     |
+================================================+=====================================================================+
| ``pass``                                       | Selects all passed results                                          |
+------------------------------------------------+---------------------------------------------------------------------+
| ``result=="pass"``                             | Also selects all passed results                                     |
+------------------------------------------------+---------------------------------------------------------------------+
| ``prop[score]``                                | Selects all results containing a score property                     |
+------------------------------------------------+---------------------------------------------------------------------+
| ``prop[score]>1``                              | Selects all results with a score property greater than 1            |
+------------------------------------------------+---------------------------------------------------------------------+

.. _match:

Match
=====

.. productionlist:: match
   match: [ "%" `mod` ] `~selector:selector`
   mod: "all" | "any" | "not" | "notall" | "notany"

A *match* takes a :ref:`selector <selector>` and collapses it into a boolean, depending on the :token:`~match:mod`
modifier.

+-----------------------------------------------------------+--------------------------------------------------------------+
| :token:`~match:mod`                                       | match                                                        |
+===========================================================+==============================================================+
| No modifier or :token:`%all <match:mod>`                  | Matches if the selector is "true" for all referenced elements|
+-----------------------------------------------------------+--------------------------------------------------------------+
| :token:`%any <match:mod>`                                 | Matches if there is at least one selected element "true"     |
+-----------------------------------------------------------+--------------------------------------------------------------+
| :token:`%notall <match:mod>`                              | Matches if not all of the selected elements are "true"       |
+-----------------------------------------------------------+--------------------------------------------------------------+
| :token:`%not <match:mod>` or :token:`%notany <match:mod>` | Matches if not any of the selected elements is "true"        |
+-----------------------------------------------------------+--------------------------------------------------------------+

+--------------+-----------------------------+---------------------------+------------------------------+--------------------------------+
| elements     | | no modifier or            | :token:`%any <match:mod>` | :token:`%notall <match:mod>` | | :token:`%not <match:mod>`    |
|              | | :token:`%all <match:mod>` |                           |                              | | :token:`%notany <match:mod>` |
+==============+=============================+===========================+==============================+================================+
| all true     | true                        |  true                     | false                        | false                          |
+--------------+-----------------------------+---------------------------+------------------------------+--------------------------------+
| all false    | false                       |  false                    | true                         | true                           |
+--------------+-----------------------------+---------------------------+------------------------------+--------------------------------+
| mixed        | false                       |  true                     | true                         | false                          |
+--------------+-----------------------------+---------------------------+------------------------------+--------------------------------+


Example matches:

+------------------------------------------------+---------------------------------------------------------------------+
| match                                          |                                                                     |
+================================================+=====================================================================+
| ``pass``                                       | Matches if all results passed                                       |
+------------------------------------------------+---------------------------------------------------------------------+
| ``%any pass``                                  | Matches if at least one result passed                               |
+------------------------------------------------+---------------------------------------------------------------------+
| ``%notall pass``                               | Matches if not all results passed                                   |
+------------------------------------------------+---------------------------------------------------------------------+
| ``%notany pass``                               | Matches if at least one result did not pass                         |
+------------------------------------------------+---------------------------------------------------------------------+
| ``prop[score]``                                | Matches if all results contain a score property                     |
+------------------------------------------------+---------------------------------------------------------------------+
| ``%any prop[score]``                           | Matches if at least one result contains a score property            |
+------------------------------------------------+---------------------------------------------------------------------+
| ``prop[score]>1``                              | Matches if all results contain a score of more than 1               |
+------------------------------------------------+---------------------------------------------------------------------+

.. _placeholder:
.. _reference placeholder:

Reference placeholder
=====================

*Reference placeholders* can be used inside a longer string. The placeholder will be replaced by the value produced by
the :ref:`reference value <reference value>`.

.. productionlist:: placeholder
   placeholder: "${" `~reference_value:value_reference` "}"

Placeholders are :ref:`reference values <reference value>` wrapped inside a ``${...}``.
To include a literal ``${`` in the string, use ``$${`` to escape the placeholder syntax.

.. _task id placeholder:

Task id placeholder
===================

*Task id placeholders* can be used inside a longer string. The placeholder will be replaced by the
sub-task number of the currently active task, either zero-based or one-based.

.. productionlist:: task_id_placeholder
   task_id_placeholder: "$" [ `task_id_base` ] "#"
   task_id_base: "0" | "1"

Task id placeholders are ``$#``, ``$0#`` and ``$1#``. The ``0`` and ``1`` indicate whether the task id is zero-based or
one-based. If no base is given, the default is zero-based. If there is no task, the placeholder will be
replaced by a ``-``.

Examples, for a task with id ``task.0.1``:

+-------------------+-------------------+
| placeholder       | replacement       |
+===================+===================+
| ``$#``            | ``0.1``           |
+-------------------+-------------------+
| ``$0#``           | ``0.1``           |
+-------------------+-------------------+
| ``$1#``           | ``1.2``           |
+-------------------+-------------------+
