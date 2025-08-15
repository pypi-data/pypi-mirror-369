""" Sphinx extension for documenting checklet option definitions. """
from __future__ import annotations

import collections.abc
import textwrap
import typing

from momotor.bundles.elements.options import Option
from momotor.options import OptionDefinition, OptionNameDomain

try:
    from docutils import nodes
    from docutils.nodes import make_id
    from docutils.parsers.rst import directives
    from docutils.parsers.rst.states import RSTState
    from docutils.statemachine import ViewList, StringList
    from sphinx import addnodes
    from sphinx.addnodes import desc_signature
    from sphinx.application import Sphinx
    from sphinx.directives import ObjectDescription
    from sphinx.domains import Domain, ObjType
    from sphinx.domains.python import PyVariable, ObjectEntry
    from sphinx.environment import BuildEnvironment
    from sphinx.ext.autodoc import DataDocumenter
    from sphinx.roles import XRefRole
    from sphinx.util import nested_parse_with_titles, logging
    from sphinx.util.docfields import Field
    from sphinx.util.docstrings import prepare_docstring
    from sphinx.util.nodes import make_refnode
    from sphinx.util.typing import OptionSpec

except ImportError:
    has_sphinx = False
else:
    has_sphinx = True

if has_sphinx:
    logger = logging.getLogger(__name__)

    def meta_option_ref(checklet, option):
        return f'{checklet}.Meta.options.{option}'

    def step_option_ref(step, option):
        return f'{step}:{option}'

    def qualified_option_sig(sig: str) -> tuple[str, str]:
        default_domain = '@' + Option.DEFAULT_DOMAIN

        if '@' not in sig:
            qualsig = f'{sig}{default_domain}'
        elif sig.endswith(default_domain):
            qualsig = sig
            sig = sig.split('@')[0]
        else:
            qualsig = sig

        return sig, qualsig

    # Show control characters in the output.
    CONTROL_TRANS = str.maketrans({
        '\x00': '\u2400',
        '\x01': '\u2401',
        '\x02': '\u2402',
        '\x03': '\u2403',
        '\x04': '\u2404',
        '\x05': '\u2405',
        '\x06': '\u2406',
        '\x07': '\u2407',
        '\x08': '\u2408',
        '\x09': '\u2409',
        '\x0A': '\u240A',
        '\x0B': '\u240B',
        '\x0C': '\u240C',
        '\x0D': '\u240D',
        '\x0E': '\u240E',
        '\x0F': '\u240F',
        '\x10': '\u2410',
        '\x11': '\u2411',
        '\x12': '\u2412',
        '\x13': '\u2413',
        '\x14': '\u2414',
        '\x15': '\u2415',
        '\x16': '\u2416',
        '\x17': '\u2417',
        '\x18': '\u2418',
        '\x19': '\u2419',
        '\x1A': '\u241A',
        '\x1B': '\u241B',
        '\x1C': '\u241C',
        '\x1D': '\u241D',
        '\x1E': '\u241E',
        '\x1F': '\u241F',
        '\x7F': '\u2421',
    })

    def format_value(typ: str | None, value: typing.Any) -> str:
        if typ in {'bool', 'boolean'} or isinstance(value, bool):
            return repr(value)
        elif typ in {'str', 'string'} or isinstance(value, str):
            if value:
                return f'``{value.translate(CONTROL_TRANS)}``'
            else:
                return '*Empty string*'

        return repr(value)

    def document_option_definition(
            option: OptionDefinition, tab_width: int = 8, style: str = 'checklet', *,
            checklet: str | None = None,
            canonical: str | None = None,
            step: str | None = None,
            no_index_entry: bool = False,
            no_contents_entry: bool = False,
            values: list[typing.Any] | None = None,
            default: typing.Any = OptionDefinition.NO_DEFAULT,
    ) -> collections.abc.Generator[str, None, None]:
        """ Generate a reStructuredText description for the given option definition.

        :param option: The option definition to document.
        :param tab_width: The tab width to use for indentation.
        :param style: The style to use for the option ('checklet' or 'step').
        :param no_index_entry: Whether to suppress the index entry for this option.
        :param no_contents_entry: Whether to suppress the contents entry for this option.
        :param checklet: The checklet name (full path including module) to use for the option.
        :param canonical: The canonical checklet (full path including module) that defines this option.
        :param step: The step name to use for the option.
        :param values: The values to use for the option. If provided, the option's default value is ignored.
        :param default: Alternate default value to use for the option. Overrides the option's default value.
        :return: A generator yielding the lines of the reStructuredText description.
        """
        yield f'.. momotor:option:: {option.fullname}'

        if checklet:
            yield f'   :checklet: {checklet}'
        if canonical:
            yield f'   :canonical: {canonical}'
        if step:
            yield f'   :step: {step}'
        if no_index_entry:
            yield '   :no-index-entry:'
        if no_contents_entry:
            yield '   :no-contents-entry:'

        if option.deprecated:
            if isinstance(option.deprecated, str):
                prefix = '   :deprecated: '
                for line in prepare_docstring(option.deprecated, tab_width):
                    yield prefix + line
                    prefix = '                '
            else:
                yield '   :deprecated:'
                yield ''
        else:
            yield ''

        if option.doc is not None:
            for line in prepare_docstring(option.doc, tab_width):
                yield f'   {line}'

        yield f'   :type: {"Any" if option.type is None else option.type}'
        yield f'   :required: {option.required!r}'
        yield f'   :multiple: {option.multiple!r}'
        if option.multiple:
            yield f'   :all: {option.all!r}'
        if style == 'checklet':
            yield f'   :location: {", ".join(option.location)}'

        if values is not None:
            if len(values) == 0:
                yield '   :value: *No values*'
            elif len(values) == 1:
                yield '   :value: ' + format_value(option.type, values[0])
            else:
                yield '   :value:'
                for value in values:
                    yield f'      - {format_value(option.type, value)}'
        else:
            if default is OptionDefinition.NO_DEFAULT:
                default = option.default

            if default is OptionDefinition.NO_DEFAULT:
                yield '   :default: *No default*'
            else:
                yield '   :default: ' + format_value(option.type, default)

        yield ''

    def parse_rst(rst: str, state: RSTState) -> list[nodes.Node]:
        vl = ViewList(textwrap.dedent(rst).splitlines(), source='')
        node = nodes.paragraph()
        # noinspection PyTypeChecker
        nested_parse_with_titles(state, vl, node)

        return [node]

    def option_deprecation_note(state: RSTState, note: str | None = None) -> list[nodes.Node]:
        if not note:
            note = 'This option is deprecated.'

        note_nodes = parse_rst(textwrap.dedent(note), state=state)

        return [
            nodes.admonition(
                '',
                nodes.title(
                    '',
                    'Deprecated'
                ),
                *note_nodes,
                classes=['attention']
            )
        ]

    class OptionField(Field):
        pass

    class CheckletOptionDirective(ObjectDescription[str]):
        # noinspection PyClassVar
        option_spec: typing.ClassVar[OptionSpec] = {
            **ObjectDescription.option_spec,
            'deprecated': directives.unchanged,
            'checklet': directives.unchanged,
            'step': directives.unchanged,
            'canonical': directives.unchanged,
        }

        doc_field_types = [
            OptionField('type', label='Type', names=('type',), has_arg=False),
            OptionField('required', label='Required', names=('required',), has_arg=False),
            OptionField('multiple', label='Multiple', names=('multiple',), has_arg=False),
            OptionField('all', label='All', names=('all',), has_arg=False),
            OptionField('location', label='Location', names=('location',), has_arg=False),
            OptionField('default', label='Default', names=('default',), has_arg=False),
        ]

        def _get_option_or_context(self, name) -> str | None:
            return self.options.get(name, self.env.ref_context.get(f'momotor:{name}'))

        def _full_name(self, sig: str) -> str:
            if step := self._get_option_or_context('step'):
                sig = step_option_ref(step, sig)

            if checklet := self._get_option_or_context('checklet'):
                sig = meta_option_ref(checklet, sig)

            return sig

        def handle_signature(self, sig: str, signode: desc_signature) -> str:
            sig, qualsig = qualified_option_sig(sig)

            checklet = self._get_option_or_context('checklet')
            fullname = self._full_name(sig)
            node_id = make_id(self._full_name(qualsig))

            signode['checklet'] = checklet
            signode['fullname'] = fullname
            signode['name'] = sig
            signode['qualname'] = qualsig
            signode['ids'].append(node_id)

            option_name = OptionNameDomain.from_qualified_name(sig)

            signode += addnodes.desc_name(option_name.name, option_name.name)

            if option_name.domain != Option.DEFAULT_DOMAIN:
                nodetext = f'@{option_name.domain}'
                signode += addnodes.desc_addname(nodetext, nodetext)

            signode += addnodes.desc_annotation(' option', ' option')

            return fullname

        def get_index_text(self, sig: str) -> str:
            if step := self._get_option_or_context('step'):
                return f'{sig} (option of {step} step)'

            if checklet := self._get_option_or_context('checklet'):
                return f'{sig} ({checklet} option)'

            return f'{sig} (option)'

        def add_target_and_index(self, name: str, sig: str, signode: desc_signature) -> None:
            sig, qualsig = qualified_option_sig(sig)

            super().add_target_and_index(name, qualsig, signode)
            node_id = signode['ids'][0]

            domain = typing.cast(MomotorDomain, self.env.get_domain('momotor'))
            domain.note_object(self._full_name(qualsig), self.objtype, node_id, location=signode)

            if 'no-index-entry' not in self.options:
                index_text = self.get_index_text(sig)

                self.indexnode['entries'].append(
                    # (entrytype, entryname, target, ignored, key)
                    ('single', index_text, node_id, '', None),
                )

        def transform_content(self, contentnode: addnodes.desc_content) -> None:
            if deprecated := self.options.get('deprecated'):
                contentnode[0:0] = option_deprecation_note(self.state, deprecated)

            if canonical := self.options.get('canonical'):
                contentnode.extend(parse_rst(
                    f'Provided by: :momotor:checklet:`~{canonical}`',
                    state=self.state
                ))

        def _object_hierarchy_parts(self, sig_node: desc_signature) -> tuple[str, ...]:
            if 'name' not in sig_node:
                return ()

            parts = (sig_node['qualname'],)

            if step := sig_node.get('step'):
                return *(step.rsplit('.', 1)), *parts

            if checklet := sig_node.get('checklet'):
                return *(checklet.rsplit('.', 1)), *parts

            return parts

        def _toc_entry_name(self, sig_node: desc_signature) -> str:
            if not sig_node.get('_toc_parts'):
                return ''

            config = self.env.app.config
            *parents, name = sig_node['_toc_parts']
            if config.toc_object_entries_show_parents == 'domain':
                name = sig_node.get('fullname', name)
            elif config.toc_object_entries_show_parents == 'hide':
                pass
            elif config.toc_object_entries_show_parents == 'all':
                name = '.'.join(parents + [name])
            else:
                return ''

            if name.endswith('@' + Option.DEFAULT_DOMAIN):
                name = name[:-len('@' + Option.DEFAULT_DOMAIN)]

            return name + ' option'


    class OptionDefinitionVariableDirective(PyVariable):
        pass

    class OptionXRefRole(XRefRole):
        def process_link(self, env: BuildEnvironment, refnode: nodes.Element,
                         has_explicit_title: bool, title: str, target: str) -> tuple[str, str]:
            for field in ['py:module', 'py:class', 'momotor:step']:
                refnode[field] = env.ref_context.get(field)

            if not has_explicit_title:
                title = title.lstrip('.')    # only has a meaning for the target
                target = target.lstrip('~')  # only has a meaning for the title
                # if the first character is a tilde, don't display the module/class
                # parts of the contents
                if title[0:1] == '~':
                    title = title[1:]
                    dot = title.rfind('.')
                    if dot != -1:
                        title = title[dot + 1:]

            # if the first character is a dot, search more specific namespaces first
            # else search builtins first
            if target[0:1] == '.':
                target = target[1:]
                refnode['refspecific'] = True

            return title, target

    class MomotorDomain(Domain):
        name = 'momotor'
        label = 'Momotor'

        object_types: dict[str, ObjType] = {
            'option': ObjType('option', 'option'),
            'optiondefvar': ObjType('optiondef', 'optiondef'),
        }

        directives = {
            'option': CheckletOptionDirective,
            'optiondefvar': OptionDefinitionVariableDirective,
        }

        roles = {
            'option': OptionXRefRole(),
        }

        @property
        def objects(self) -> dict[str, ObjectEntry]:
            return self.data.setdefault('objects', {})  # fullname -> ObjectEntry

        def note_object(self, name: str, objtype: str, node_id: str,
                        aliased: bool = False, location: typing.Any = None) -> None:
            if other := self.objects.get(name):
                if other.aliased and aliased is False:
                    # The original definition found. Override it!
                    pass
                elif other.aliased is False and aliased:
                    # The original definition is already registered.
                    return
                else:
                    # duplicated
                    logger.warning('duplicate object description of %s, '
                                   'other instance in %s, use :no-index: for one of them',
                                   name, other.docname, location=location)

            self.objects[name] = ObjectEntry(self.env.docname, node_id, objtype, aliased)

        def get_objects(self) -> collections.abc.Iterator[tuple[str, str, str, str, str, int]]:
            for refname, obj in self.objects.items():
                yield refname, refname, obj.objtype, obj.docname, obj.node_id, (-1 if obj.aliased else 1)

        def resolve_xref(self, env, fromdocname, builder, typ, target, node, contnode) -> nodes.reference | None:
            if typ == 'option':
                target = qualified_option_sig(target)[1]  # option refs are always qualified with domain
                targets = [target]

                if py_class := node.attributes.get('py:class'):
                    if py_module := node.attributes.get('py:module'):
                        full_target = meta_option_ref(f'{py_module}.{py_class}', target)
                    else:
                        full_target = meta_option_ref(py_class, target)

                    if node.attributes.get('refspecific'):
                        targets.insert(0, full_target)
                    else:
                        targets.append(full_target)

                if momotor_step := node.attributes.get('momotor:step'):
                    full_target = step_option_ref(momotor_step, target)
                    if node.attributes.get('refspecific'):
                        targets.insert(0, full_target)
                    else:
                        targets.append(full_target)

            else:
                targets = [target]

            for sig in targets:
                for name, objsig, objtyp, todocname, anchor, prio in self.get_objects():
                    if objsig == sig and objtyp == typ:
                        return make_refnode(builder, fromdocname, todocname, anchor, contnode, sig)

            return None

    class OptionDefinitionVariableDocumenter(DataDocumenter):
        objtype = 'optiondefvar'
        domain = 'momotor'

        @classmethod
        def can_document_member(
                cls,
                member: typing.Any, membername: str, isattr: bool, parent: typing.Any
        ) -> bool:
            return isinstance(member, OptionDefinition) and isattr

        def should_suppress_value_header(self) -> bool:
            return True

        def add_content(self, more_content: StringList | None) -> None:
            super().add_content(more_content)

            sourcename = self.get_sourcename()
            tab_width = self.directive.state.document.settings.tab_width

            for line in document_option_definition(self.object, tab_width):
                self.add_line(line, sourcename)

    def setup(app: Sphinx) -> dict[str, typing.Any]:
        from importlib.metadata import version

        app.setup_extension('sphinx.ext.autodoc')
        app.add_autodocumenter(OptionDefinitionVariableDocumenter)
        app.add_domain(MomotorDomain)

        return {
            'version': version('momotor-engine-options'),
            'parallel_read_safe': True,
            'parallel_write_safe': True,
        }
