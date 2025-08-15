.. _tool registry:

Tool registry
=============

Tools like Java and Python are not always installed in the same location on different installations.

The tool registry provides a way for Momotor checklets to find the external tools needed in a system independent way.
Additionally, the registry is used to indicate to the scheduler which tools a worker has available. This allows
use of workers with different configurations without running the risk of a job getting scheduled on a worker
which does not have a specific tool (or version of that tool) available.

.. _tool registry structure:

Registry structure
------------------

The registry itself is a directory structure containing text files, making it easy to generate these files
during setup of the tools. The registry also supports multiple versions of tools to be installed and
selectable, and also further variants within these versions.

Example of a registry structure::

    ├── anaconda3/
    │   ├── 2021.05/
    │   │   ├── base
    │   │   ├── python38 ➔ base
    │   │   └── _default ➔ base
    │   ├── 2021.11/
    │   │   ├── base
    │   │   ├── python38
    │   │   └── _default ➔ base
    │   └── _default/ ➔ 2021.11/
    ├── java/
    │   ├── 8
    │   ├── 17
    │   ├── 18
    │   ├── latest ➔ 18
    │   ├── lts ➔ 17
    │   └── _default ➔ 17
    └── python/
        ├── 2.7.18
        ├── 3.8.10
        ├── 3.8.11
        └── 3.9.7

The first level of the registry contains the tool names as they will be used by the checklets. The next level
contains version numbers and the (optional) third directory level contains variants. It's possible to have
even more directory levels. Files contain the information about a tool, which is documented
:ref:`below <tool registry file>`.
Soft links (shown in the example above using ``➔``) are allowed and create an alias.

The most basic way to select a tool is to use the path of the tool file name, e.g. ``anaconda3/2021.11/python38``

If parts of the path are not provided, the ``_default`` file (or, preferably, link) will be used if this is available,
otherwise the highest available version will be selected. So, for the example above, tool name ``java`` will
select `Java 17`, whereas tool name ``python`` will select `Python 3.9.7`.

For tools with multiple sub-directories, an underscore can be used to indicated the default,
e.g. ``anaconda/_/python38`` will select the `python38` variant of the default `anaconda3` installation.

Dotted version numbers can be abbreviated, and if multiple versions match, the highest version is selected, i.e.
tool name ``python/3.8`` will select `Python 3.8.11` in the example above, ``python/2`` selects `Python 2.7.18`,
and ``python/3`` selects `Python 3.9.7`. Version number abbreviation is checked by "dot", i.e. ``3.8.1`` would
not match ``3.8.10`` or ``3.8.11``.

It's possible to create named versions, e.g. ``java/lts`` will select `Java 17`. Numeric versions have priority over
named versions, so in case of the `python` tree above, if there would have been a named version, `3.9.7` would still
be the `default`. When a directory only contains names, no numeric versions and no ``_default``, the alphabetically
highest name will be considered the default. Version numbers are correctly ordered numerically, so if the ``_default``
file did not exist in the ``java`` tree, `Java 18` would have been the default version, not `Java 8`

File and directory names starting with a dot (``.``) or ending with a tilde (``~``) are ignored while scanning
the registry.

.. _tool registry file:

Registry file
-------------

A registry file contains environment variables required for the tool, and the path to the tool itself.
The tool path is usually the executable, but it could also be a directory. How the environment variables
and tool path are interpreted is up to the checklets using the tool registry.

An example registry file is:

.. code-block:: shell

  PYTHONHOME=${HOME}/python38
  PYTHONPATH=${PYTHONHOME}/extra-packages/
  ${PYTHONHOME}/bin/python

As shown in the example above, environment variables can refer to other variables in the current environment,
including variables defined on earlier lines in the tool definition file.
They will be resolved when the tool file is read.

The tool path is always on the last non-empty line of the file, and the other lines should be valid environment
variable definitions.

If the tool path or the value of an environment variable is quoted, any text after the end quote is ignored:

.. code-block:: shell

  SOMEVARIABLE='this text is part of the variable' this text is ignored
  '/quoted/path' this text is also ignored

The value of ``SOMEVARIABLE`` will be ``this text is part of the variable``, and the path will be ``/quoted/path``.
Both single and double quotes are supported.

The variable expansion is done using Python :ref:`python:template-strings`.

.. _tool registry location:

Registry location
-----------------

By default, the registry is read from the `/etc/toolregistry.d` and `~/toolregistry.d` directories,
where entries in the latter override entries in the first.

The environment variable ``TOOLREGISTRY`` can be used to change the defaults. It is a colon (``:``) separated
list of paths, similar to the standard ``PATH`` environment variable.

The :py:func:`~momotor.options.tools.registry.registered_tools` and
:py:func:`~momotor.options.tools.registry.resolve_tool` functions allow extending or overriding the defaults.

Usage in bundles
----------------

To configure a checklet to use a certain tool version, two options are needed: the
:momotor:option:`tools@scheduler option <tools@scheduler>` in each step that requires external tools,
to indicate to the scheduler which tools are required by the step's checklet, and options in the
:ref:`tools domain <tools domain>` to define the actual tool versions to use.

The options in the :ref:`tools domain <tools domain>` can be defined in the recipe or config bundles,
and can contain :ref:`placeholders <placeholder>`. This makes it possible to define
the tool version based a on property generated by earlier executed steps, for example:

.. code-block:: xml

   <options domain="tools">
     <option name="java" value="${prop[#build-java:exectool]}" />
   </options>

where the ``build-java`` step generates a property ``exectool`` which contains a proper tool name to use to
execute the generated class files.

Tool and registry functions and classes
---------------------------------------

.. automodule:: momotor.options.tools.registry
   :members:
   :inherited-members:
   :undoc-members:

.. automodule:: momotor.options.tools.tool
   :members:
   :inherited-members:
   :undoc-members:

.. automodule:: momotor.options.tools.version
   :members:
   :inherited-members:
   :undoc-members:
