.. _scheduler tasks option:

======================
Scheduler tasks option
======================

The :momotor:option:`tasks@scheduler` option is processed by the scheduler when scheduling tasks. It makes it possible
to create multiple tasks from a single step. For example, this can be used to run multiple test cases on the
same input files. If not provided, a single task is generated for the step.

This option can directly define the number of tasks, but the actual number of tasks can also be defined
in the top-level options of the recipe or the options of the configuration bundle.

This option does not have to be defined in the checklet's meta options as it is enabled by default for all checklets,
but it is recommended to explicitly define this for checklets supporting multiple tasks.

The following table describes the various values that are valid for this option:

============ ============================
Tasks option Recipe/config option allowed
============ ============================
``*``        At least one dimension required (e.g. ``2``, ``2.2`` etc)
``*?``       Zero or more dimensions allowed.
``?``        A single dimension required (e.g. ``1``, ``2``)
``?.?``      Two dimensions required (e.g. ``1.1``, ``2.2``)
``?.?.?``    Three dimensions required (e.g. ``1.2.3``, ``2.2.2``)
``?.*``      At least two dimensions required (e.g. ``1.2``, ``1.2.3``)
``?.??``     One dimension required, two dimensions allowed.
``?.??.??``  One dimension required, two or three dimensions allowed.
``4.?``      Exactly two dimensions required, and the first must be ``4`` (e.g. ``4.1``, ``4.2``)
``4.*``      At least two dimensions required, and the first must be ``4`` (e.g. ``4.1``, ``4.2.3``)
``4.4``      A fixed dimension. Config option not required, but if provided, MUST equal ``4.4``
``?.*?``     Allowed but identical to ``*``, so not recommended.
``?.??.*?``  Allowed but identical to ``?.*``, so not recommended.
============ ============================

There is no limit to the number of dimensions allowed.

The ``?`` and ``*`` wildcards indicate required dimensions. The ``??`` and ``*?`` wildcards indicate optional
dimensions. The optional requirements must be the last dimensions in the option, e.g. ``??.?`` is not valid,
but ``?.??`` is. There can only be one ``*`` or ``*?`` wildcard in the option, and it must be the last one.
