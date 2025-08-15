.. _tools domain:

Tools domain
============

The *tools* domain contains options who's name should be a tool name, and the value of the option should
be a version requirement. For example:

.. code-block:: xml

  <option domain="tools" name="python" value="python/3.9" />

The option name and first part of the value should normally be the same, unless there is a very specific
reason for the checklet to require multiple versions of the same tool:

.. code-block:: xml

  <option domain="tools" name="python-legacy" value="python/2" />
  <option domain="tools" name="python" value="python/3.9" />


Checklets should use :py:class:`~momotor.options.domain.tools.ToolOptionDefinition` to define required tools
in their :py:attr:`~mtrchk.org.momotor.base.checklet.meta.CheckletOptions.options`


.. automodule:: momotor.options.domain.tools
   :members:
   :inherited-members:
   :undoc-members:
