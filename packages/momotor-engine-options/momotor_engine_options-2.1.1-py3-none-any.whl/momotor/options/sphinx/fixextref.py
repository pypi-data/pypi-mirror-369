""" Transformer that converts external references to the local package into normal references

This makes it possible to write documentation that is reused in other packages, and still
have the references work correctly regardless of whether the documentation is parsed in the
local package or in the external package.
"""
from __future__ import annotations

import logging
import typing

try:
    from docutils.nodes import system_message
    from docutils.utils import Reporter
    from sphinx.application import Sphinx
    from sphinx.errors import ConfigError
    from sphinx.util.docutils import CustomReSTDispatcher
    from sphinx.util.typing import RoleFunction
except ImportError:
    has_sphinx = False
else:
    has_sphinx = True

if has_sphinx:
    logger = logging.getLogger(__name__)


    class IntersphinxTransformer(CustomReSTDispatcher):
        """ Replace ':external+<local_package:xxx:' references with ':xxx:' references
        """
        def __init__(self, local_package: str):
            self.local_ref = f'external+{local_package}:'
            super().__init__()

        def role(self, role_name: str, language_module: "typing.ModuleType", lineno: int, reporter: Reporter) \
                -> tuple[RoleFunction, list[system_message]]:
            if len(role_name) > 9 and role_name.startswith(self.local_ref):
                new_role = role_name[len(self.local_ref):]
                logger.debug('Transforming :%s: into :%s:', role_name, new_role)
                role_name = new_role

            return super().role(role_name, language_module, lineno, reporter)


    def install_external_ref_xform(app: Sphinx, docname: str, source: list[str]) -> None:
        """ Install a transformer that converts external references to the local package into
        normal references """
        package_name = getattr(app.config, 'package_name', None)
        if not package_name:
            raise ConfigError('`package_name` not set in Sphinx config, '
                              'required by the `momotor.options.sphinx.fixextref` extension')

        dispatcher = IntersphinxTransformer(package_name)
        dispatcher.enable()


    def setup(app: Sphinx) -> dict[str, typing.Any]:
        from importlib.metadata import version

        app.add_config_value('package_name', None, 'env')
        app.connect('source-read', install_external_ref_xform)

        return {
            'version': version('momotor-engine-options'),
            'parallel_read_safe': True,
            'parallel_write_safe': True,
        }
