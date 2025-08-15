from __future__ import annotations

import typing

from momotor.bundles import RecipeBundle, ConfigBundle, ResultsBundle
from momotor.options.doc import annotate_docstring
from momotor.options.domain.tools import ToolOptionDefinition, TOOLS_DOMAIN
from momotor.options.option import OptionDefinition, OptionNameDomain
from momotor.options.parser.placeholders import replace_placeholders
from momotor.options.providers import Providers
from momotor.options.split import multi_split
from momotor.options.task_id import StepTaskId
from ._domain import DOMAIN

if typing.TYPE_CHECKING:
    from momotor.options.tools.types import ToolRequirements

TOOLS_OPTION_NAME = OptionNameDomain('tools', DOMAIN)

#: The :momotor:option:`tools@scheduler` option defines the tools required for a step.
TOOLS_OPTION = OptionDefinition(
    name=TOOLS_OPTION_NAME,
    type='string',
    doc=f"""\
        .. role:: xml(code)
           :language: xml
   
        List of tools required for the step. Can only be provided by :xml:`<step>` nodes.
        
        Multiple tools can be provided by using multiple {TOOLS_OPTION_NAME} options, or using a single
        {TOOLS_OPTION_NAME} option with multiple tool names. Multiple tool names on a single option should 
        be space or comma separated.
        
        The list of tools should only contain tool names. Any detailed version requirements should
        be defined with options in the :external+momotor-engine-options:ref:`tools domain <tools domain>`.
        
        See the :external+momotor-engine-options:ref:`tool registry documentation <tool registry>` on how 
        this option is used to resolve a tool.
    """,
    multiple=True,
    location='step',
)


@annotate_docstring(
    TOOLS_OPTION_NAME=TOOLS_OPTION_NAME,
    TOOLS_DOMAIN=TOOLS_DOMAIN,
)
def get_scheduler_tools_option(
        recipe: RecipeBundle,
        config: ConfigBundle | None,
        results: ResultsBundle | None,
        *, task_id: StepTaskId
) -> "ToolRequirements":
    """ Evaluate the tool requirements by parsing the :momotor:option:`{TOOLS_OPTION_NAME}` option
    for a single step in the given bundles.

    This gets the value of the :momotor:option:`{TOOLS_OPTION_NAME}` option for the step, and subsequently gets the
    specific tool version requirements (if any) from the options in the
    :py:ref:`{TOOLS_DOMAIN} domain <{TOOLS_DOMAIN} domain>`.

    A step requiring tools must define the :momotor:option:`{TOOLS_OPTION_NAME}` in the recipe.
    The tool version options are defined in the :py:ref:`{TOOLS_DOMAIN} domain <{TOOLS_DOMAIN} domain>`
    in the normal locations: *config*, *recipe*, *step*.

    Example of a step defining some tool requirements:

    .. code-block::

      <recipe ...>
        ...
        <step ...>
          ...
          <options domain="{TOOLS_OPTION_NAME.domain}">
            <option name="{TOOLS_OPTION_NAME.name}" value="anaconda3" />
          </options>
          <options domain="{TOOLS_DOMAIN}">
            <option name="anaconda3" value="anaconda3/_/momotor anaconda3" />
          </options>
          ...
        </step>
        ...
      </recipe>

    This indicates to the scheduler that this step requires the ``anaconda3`` tool. It also indicates
    to both the scheduler and to the checklet that will execute this step that the ``anaconda3/_/momotor`` version
    is preferred, but if not available any ``anaconda3`` will do.

    For the format of the tool version requirements, see :py:ref:`tool registry`.

    :param recipe: The recipe bundle.
    :param config: The config bundle.
    :param results: The results bundle.
    :param task_id: The task id.
    :return: The tool requirements for the requested step and task.
    """
    requirement_providers = Providers(
        recipe=recipe,
        task_id=task_id
    )

    version_providers = Providers(
        recipe=recipe,
        config=config,
        results=results,
        task_id=task_id
    )

    tools = {}
    for tool_req in TOOLS_OPTION.resolve(requirement_providers, False):
        tool_req = replace_placeholders(tool_req, version_providers)
        for name in multi_split(tool_req, ','):
            if name not in tools:
                tools[name] = frozenset(
                    ToolOptionDefinition(name=name).resolve(version_providers)
                )

    return tools
