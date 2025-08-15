.. _scheduler preflight option:

==========================
Scheduler preflight option
==========================

The :momotor:option:`preflight@scheduler` option is processed by the scheduler during the scheduling of the
tasks. The option allows recipes to indicate situations in which the task does not have to be executed,
for example when an input precondition fails.

This option does not have to be defined in the checklet's meta options as it is enabled by default for all checklets.,
but it can be defined to change the default preflight check for this checklet.

The expected format for the option value is:

.. productionlist:: preflight-option
   preflight_option: [ `~selector:selector` ] "=>" `action` [ `preflight_status` | `preflight_props` ]
   preflight_status: text status message
   preflight_props: "{" `prop` ":" `value` ( "," `prop` ":" `value` )* "}"
   action: "run" | "pass" | "pass-secret" | "pass-hidden"
         : | "fail" | "fail-secret" | "fail-hidden" | "skip"
         : | "error" | "skip-error"

If a :ref:`selector <selector>` matches or is empty, a results bundle based on the action and status message
is created (unless the action is :token:`run <preflight-option:action>`).
If no selectors match, or a selector matches with action :token:`run <preflight-option:action>`,
no result is created and the step should execute as normal.

Possible values for :token:`~preflight-option:action` are:

* :token:`run <preflight-option:action>`: runs the checklet. When a :token:`run <preflight-option:action>`
  action is encountered, no further preflight options are processed.
* :token:`pass <preflight-option:action>`, :token:`pass-secret <preflight-option:action>`, and
  :token:`pass-hidden <preflight-option:action>`: will return a `pass` outcome without running the checklet.
* :token:`fail <preflight-option:action>`, :token:`fail-secret <preflight-option:action>`, and
  :token:`fail-hidden <preflight-option:action>`: will return a `fail` outcome without running the checklet.
* :token:`skip <preflight-option:action>` and :token:`skip-error <preflight-option:action>`: will return a
  `skip` outcome without running the checklet.
* :token:`error <preflight-option:action>`: will return an `error` outcome without running the checklet.

If a result is created, the properties will contain a `preflight-trigger` property with the selector
that triggered the action, a `source` property with the name of this module. If `status` is provided
and does not start with a ``{``, a `status` property with the status message is added. If `status` starts
with a ``{``, it is parsed as a (json style) dictionary of properties and added to the result properties.

Some of the actions will add additional properties to the result:

* :token:`pass-secret <preflight-option:action>` and :token:`fail-secret <preflight-option:action>` will
  also add a `secret` property with value ``True``.
* :token:`pass-hidden <preflight-option:action>` and :token:`fail-hidden <preflight-option:action>` will
  add `secret` and `hidden` properties with value ``True``.
* :token:`skip <preflight-option:action>` and :token:`skip-error <preflight-option:action>` adds a `skipped`
  property with value ``True``.
* :token:`skip-error <preflight-option:action>` additionally adds a `deps-error` property with value ``True``.

The default preflight check is:

.. code-block:: text

   %any error => skip-error

This default check is always executed before any other preflight checks provided in the options *unless*
an explicit preflight action for the ``error`` outcome exists. So, by default tasks are skipped if any of
their dependencies result in an error, but this default behaviour can be overridden by providing an explicit
rule with the ``error`` outcome.
