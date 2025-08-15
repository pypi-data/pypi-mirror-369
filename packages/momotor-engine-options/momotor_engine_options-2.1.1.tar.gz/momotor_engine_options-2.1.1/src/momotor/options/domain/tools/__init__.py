from __future__ import annotations

import collections.abc
import logging
import typing
from dataclasses import dataclass
from textwrap import dedent

from momotor.options.doc import annotate_docstring
from momotor.options.option import OptionDefinition, OptionNameDomain
from momotor.options.parser.placeholders import replace_placeholders
from momotor.options.providers import Providers
from momotor.options.split import multi_split
from momotor.options.tools import ToolName, Tool, resolve_tool
from momotor.options.types import SubDomainDefinitionType
from ._domain import DOMAIN as TOOLS_DOMAIN

if typing.TYPE_CHECKING:
    from os import PathLike
    PathList = typing.Optional[collections.abc.Iterable[typing.Union[str, PathLike]]]


__all__ = ['ToolOptionDefinition', 'ToolOptionName', 'TOOLS_DOMAIN']


logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class ToolOptionName(OptionNameDomain):
    domain: str = TOOLS_DOMAIN


TOOLS_OPTION_LOCATION = 'config', 'step', 'recipe'


@annotate_docstring(TOOLS_DOMAIN=TOOLS_DOMAIN)
@dataclass(frozen=True)
class ToolOptionDefinition(OptionDefinition):
    """ A specialization of :py:class:`~momotor.options.OptionDefinition` for tool dependency definitions.

    The option value can be a space or comma separated list of version requirements to indicate alternative
    version preferences of a single tool (in order of most to least preferred).

    Provides appropriate defaults for :py:attr:`domain`, :py:attr:`default` and :py:attr:`location` fields:

    * the default for :py:attr:`domain` is ``{TOOLS_DOMAIN}``
    * the default for :py:attr:`default` is the option name, i.e. if no option for the given name is in any bundle,
      the default version as defined in the registry will be used.
    * :py:attr:`location` is ``config, step, recipe`` and cannot be changed.

    Other differences compared to :py:class:`~momotor.options.OptionDefinition`:

    * :py:attr:`multiple` must be `False` (setting it to `True` will throw a :py:class:`ValueError`),
    * :py:meth:`resolve` returns an iterable of :py:class:`~momotor.options.tools.ToolName` objects,
    * additional method :py:meth:`resolve_tool` resolves the tool using the tool registry, it resolves to a single tool,
      matching the most preferred tool available.
    * auto-generates suitable :py:attr:`doc` if none is provided
    """
    type = 'str'

    def __post_init__(self):
        if isinstance(self.name, OptionNameDomain):
            name, domain = self.name.name, self.name.domain
        else:
            name, domain = self.name, self.domain

        if ToolName.SEPARATOR in name:
            raise ValueError(f'ToolOptionDefinition.name cannot contain {ToolName.SEPARATOR}')

        if domain is None:
            object.__setattr__(self, 'domain', TOOLS_DOMAIN)

        if self.default is self.NO_DEFAULT:
            object.__setattr__(self, 'default', name)

        super().__post_init__()

        if self.location is None or self.location == TOOLS_OPTION_LOCATION:
            object.__setattr__(self, 'location', TOOLS_OPTION_LOCATION)
        else:
            raise ValueError(f"ToolOptionDefinition.location cannot be changed {self.location!r}")

        if self.multiple:
            raise ValueError("ToolOptionDefinition.multiple must be False")

        if not self.doc:
            object.__setattr__(
                self, 'doc',
                dedent(f"""\
                    {name.capitalize()} version(s) to use. 
                    
                    Can be a space or comma separated list of version requirements to indicate alternative
                    version preferences (in order of most to least preferred).
                    
                    See the :external+momotor-engine-options:ref:`tool registry documentation <tool registry>` for
                    details.                      
                """)
            )

    def resolve(
            self,
            providers: Providers,
            subdomains: SubDomainDefinitionType | bool | None = None
    ) -> collections.abc.Iterable[ToolName]:
        result = super().resolve(providers, subdomains)
        if result is None:
            raise FileNotFoundError

        if isinstance(result, bytes):
            result = result.decode('utf-8', errors='replace')

        if not isinstance(result, str):
            raise TypeError

        result = replace_placeholders(result, providers)

        for name in multi_split(result, ','):
            yield ToolName(name)

    def resolve_tool(
            self,
            providers: Providers,
            subdomains: SubDomainDefinitionType | bool | None = None, *,
            paths: "PathList" = None,
            include_default_paths: bool = True
    ) -> Tool | None:
        """ Resolve a tool option into a single :py:class:`~momotor.options.tools.Tool` using the tool registry.
        If multiple options are provided, the first existing tool will be returned. If none of the
        requested tools exist, raises :py:class:`FileNotFoundError`

        If `include_default_paths` is True (default), this reads the tool registry from `.toolregistry.d` in
        the current user's home directory and `/etc/toolregistry.d`. If `paths` is provided, registry will be read from
        all paths in the path list as well.

        `providers` and `subdomain` arguments are the same as for :py:meth:`resolve`, and
        `paths` and `include_default_paths` arguments are the same as for
        :py:func:`~momotor.options.tools.registry.resolve_tool`

        :param providers: the providers to resolve
        :param subdomains: the subdomains
        :param paths: the paths
        :param include_default_paths: include the default paths
        :return: the tool
        """
        logger.debug(f'resolving "{self.name}" tool')

        for name in self.resolve(providers, subdomains):
            try:
                return resolve_tool(
                    name, paths=paths, include_default_paths=include_default_paths
                )
            except FileNotFoundError:
                pass

        logger.warning(f'unable to resolve "{self.name}" tool')
        raise FileNotFoundError
