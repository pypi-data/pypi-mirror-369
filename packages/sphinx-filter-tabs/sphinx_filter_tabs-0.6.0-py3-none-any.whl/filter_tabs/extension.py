#
# extension.py: The core logic for the sphinx-filter-tabs Sphinx extension.
#

# --- Imports ---
# Ensures that all type hints are treated as forward references, which is standard practice.
from __future__ import annotations

import re
import uuid
import copy
import shutil
from pathlib import Path
from docutils import nodes
from docutils.parsers.rst import Directive
from sphinx.application import Sphinx
from sphinx.util import logging
from sphinx.writers.html import HTML5Translator

# Used for type hinting to avoid circular imports and improve code clarity.
from typing import TYPE_CHECKING, Any, Dict, List

# Imports the package version, dynamically read from the installed package's metadata.
from . import __version__

# A block that only runs when a type checker is running, not at runtime.
# This avoids potential runtime errors from importing types that may not be available.
if TYPE_CHECKING:
    from sphinx.config import Config
    from sphinx.environment import BuildEnvironment

# --- Constants ---
# A dedicated UUID namespace ensures that the same tab name will always produce
# the same unique identifier. This is a crucial security measure to prevent CSS injection.
_CSS_NAMESPACE = uuid.UUID('d1b1b3e8-5e7c-48d6-a235-9a4c14c9b139')

# Centralizing CSS class names makes them easy to manage and prevents typos.
SFT_CONTAINER = "sft-container"
SFT_FIELDSET = "sft-fieldset"
SFT_LEGEND = "sft-legend"
SFT_TAB_BAR = "sft-tab-bar"
SFT_CONTENT = "sft-content"
SFT_PANEL = "sft-panel"
SFT_TEMP_PANEL = "sft-temp-panel"
COLLAPSIBLE_SECTION = "collapsible-section"
COLLAPSIBLE_CONTENT = "collapsible-content"
CUSTOM_ARROW = "custom-arrow"

# --- Logger ---
# A dedicated logger for this extension, following Sphinx's best practices.
# This allows for clean, configurable logging output.
logger = logging.getLogger(__name__)

# --- Custom Nodes ---
# Each custom node corresponds to a specific part of the component's HTML structure.
# This allows for fine-grained control over the final HTML output via visitor functions.

# The ContainerNode is essential for applying CSS Custom Properties via the 'style' attribute.
# The default docutils container doesn't reliably render the style attribute, so this
# custom node and its visitor function ensure the theming mechanism works correctly.
class ContainerNode(nodes.General, nodes.Element):
    pass

class FieldsetNode(nodes.General, nodes.Element): pass # For semantic grouping.
class LegendNode(nodes.General, nodes.Element): pass # For accessibility.
class RadioInputNode(nodes.General, nodes.Element): pass # The functional core for tab switching.
class LabelNode(nodes.General, nodes.Element): pass # The visible, clickable tab titles.
class PanelNode(nodes.General, nodes.Element): pass # The containers for tab content.
class DetailsNode(nodes.General, nodes.Element): pass # For collapsible sections.
class SummaryNode(nodes.General, nodes.Element): pass # The clickable title of a collapsible section.


# --- Renderer Class ---
class FilterTabsRenderer:
    """
    Handles the primary logic of converting the parsed directive content
    into a final node structure for both HTML and fallback formats (like LaTeX).
    """
    def __init__(self, directive: Directive, tab_names: list[str], default_tab: str, temp_blocks: list[nodes.Node]):
        """Initializes the renderer with all necessary context from the directive."""
        self.directive: Directive = directive
        self.env: BuildEnvironment = directive.state.document.settings.env
        self.tab_names: list[str] = tab_names
        self.default_tab: str = default_tab
        self.temp_blocks: list[nodes.Node] = temp_blocks

    def render_html(self) -> list[nodes.Node]:
        """Constructs the complete docutils node tree for the HTML output."""
        # Ensure a unique ID for each filter-tabs instance on a page.
        if not hasattr(self.env, 'filter_tabs_counter'):
            self.env.filter_tabs_counter = 0
        self.env.filter_tabs_counter += 1
        group_id = f"filter-group-{self.env.filter_tabs_counter}"

        config = self.env.app.config

        # Create a dictionary of CSS Custom Properties from conf.py settings.
        style_vars = {
            "--sft-border-radius": str(config.filter_tabs_border_radius),
            "--sft-tab-background": str(config.filter_tabs_tab_background_color),
            "--sft-tab-font-size": str(config.filter_tabs_tab_font_size),
            "--sft-tab-highlight-color": str(config.filter_tabs_tab_highlight_color),
            "--sft-collapsible-accent-color": str(config.filter_tabs_collapsible_accent_color),
        }
        style_string = "; ".join([f"{key}: {value}" for key, value in style_vars.items()])

        # If debug mode is on, log the generated ID and styles for easier troubleshooting.
        if config.filter_tabs_debug_mode:
            logger.info(f"[sphinx-filter-tabs] ID: {group_id}, Styles: '{style_string}'")

        # Create the main container node with the inline style for theming.
        container = ContainerNode(classes=[SFT_CONTAINER], style=style_string)

        # Build the semantic structure using fieldset and a hidden legend for accessibility.
        fieldset = FieldsetNode()
        legend = LegendNode()
        legend += nodes.Text(f"Filter by: {', '.join(self.tab_names)}")
        fieldset += legend

        # Generate the dynamic CSS that handles the core filtering logic.
        css_rules = []
        for tab_name in self.tab_names:
            radio_id = f"{group_id}-{self._css_escape(tab_name)}"
            # This CSS rule shows a panel only when its corresponding radio button is checked.
            # The modern :has() selector makes this possible without any JavaScript.
            css_rules.append(
                f".{SFT_TAB_BAR}:has(#{radio_id}:checked) ~ "
                f".{SFT_CONTENT} > .{SFT_PANEL}[data-filter='{tab_name}'] {{ display: block; }}"
            )
        # Embed the generated CSS directly into the HTML.
        style_node = nodes.raw(text=f"<style>{''.join(css_rules)}</style>", format="html")

        # Create the tab bar with radio inputs and labels.
        tab_bar = nodes.container(classes=[SFT_TAB_BAR], role='tablist')
        for tab_name in self.tab_names:
            radio_id = f"{group_id}-{self._css_escape(tab_name)}"
            # The radio buttons are functionally necessary but visually hidden.
            radio = RadioInputNode(type='radio', name=group_id, ids=[radio_id])
            if tab_name == self.default_tab:
                radio['checked'] = 'checked' # Set the default tab.
            tab_bar += radio

            # The labels are the visible, clickable tabs.
            label = LabelNode(for_id=radio_id, role='tab')
            label += nodes.Text(tab_name)
            tab_bar += label
        fieldset += tab_bar

        # Create the content area where all panels will reside.
        content_area = nodes.container(classes=[SFT_CONTENT])
        # Map tab names to their content blocks for easy lookup.
        content_map = {block['filter-name']: block.children for block in self.temp_blocks}
        # Ensure we create panels for all declared tabs plus the "General" tab.
        all_tab_names = self.tab_names + ["General"]
        for tab_name in all_tab_names:
            panel = PanelNode(classes=[SFT_PANEL], **{'data-filter': tab_name, 'role': 'tabpanel'})
            if tab_name in content_map:
                # Use deepcopy to prevent docutils node mutation bugs. Since the same content
                # might be referenced or processed multiple times, a deep copy ensures that
                # each panel gets a completely independent set of nodes.
                panel.extend(copy.deepcopy(content_map[tab_name]))
            content_area += panel
        fieldset += content_area
        container.children = [fieldset]

        # The final structure is the dynamic style block followed by the main container.
        return [style_node, container]

    def render_fallback(self) -> list[nodes.Node]:
        """Renders content as a series of simple admonitions for non-HTML builders (e.g., LaTeX/PDF)."""
        output_nodes: list[nodes.Node] = []
        content_map = {block['filter-name']: block.children for block in self.temp_blocks}
        # "General" content is rendered first, without a title.
        if "General" in content_map:
            output_nodes.extend(copy.deepcopy(content_map["General"]))
        # Each specific tab's content is placed inside a titled admonition block.
        for tab_name in self.tab_names:
            if tab_name in content_map:
                admonition = nodes.admonition()
                admonition += nodes.title(text=tab_name)
                admonition.extend(copy.deepcopy(content_map[tab_name]))
                output_nodes.append(admonition)
        return output_nodes

    @staticmethod
    def _css_escape(name: str) -> str:
        """
        Generates a deterministic, CSS-safe identifier from any given tab name string.
        This uses uuid.uuid5 to create a hashed value, which robustly prevents
        CSS injection vulnerabilities that could arise from special characters in tab names.
        """
        return str(uuid.uuid5(_CSS_NAMESPACE, name.strip().lower()))


class TabDirective(Directive):
    """Handles the `.. tab::` directive, capturing its content."""
    has_content = True
    required_arguments = 1
    final_argument_whitespace = True

    def run(self) -> list[nodes.Node]:
        """
        Parses the content of a tab and stores it in a temporary container.
        This method validates that the directive is used within a `filter-tabs` block.
        """
        env = self.state.document.settings.env
        # Ensure `tab` is only used inside `filter-tabs`.
        if not hasattr(env, 'sft_context') or not env.sft_context:
            raise self.error("`tab` can only be used inside a `filter-tabs` directive.")
        # Store the tab name and parsed content in a temporary node.
        container = nodes.container(classes=[SFT_TEMP_PANEL])
        container['filter-name'] = self.arguments[0].strip()
        self.state.nested_parse(self.content, self.content_offset, container)
        return [container]


class FilterTabsDirective(Directive):
    """Handles the main `.. filter-tabs::` directive, which orchestrates the entire component."""
    has_content = True
    required_arguments = 1
    final_argument_whitespace = True

    def run(self) -> list[nodes.Node]:
        """
        Parses the list of tabs, manages the parsing context for its content,
        and delegates the final rendering to the FilterTabsRenderer.
        """
        env = self.state.document.settings.env
        # Prevent nesting of filter-tabs directives.
        if hasattr(env, 'sft_context') and env.sft_context:
            raise self.error("Nesting `filter-tabs` is not supported.")

        # Set a context flag to indicate that we are inside a filter-tabs block.
        if not hasattr(env, 'sft_context'):
            env.sft_context = []
        env.sft_context.append(True)

        # Parse the content of the directive to find all `.. tab::` blocks.
        temp_container = nodes.container()
        self.state.nested_parse(self.content, self.content_offset, temp_container)
        env.sft_context.pop() # Unset the context flag.

        # Find all the temporary panel nodes created by the TabDirective.
        temp_blocks = temp_container.findall(lambda n: isinstance(n, nodes.Element) and SFT_TEMP_PANEL in n.get('classes', []))
        if not temp_blocks:
            # Raise a clear error if the directive is empty, instead of failing silently.
            self.error("No `.. tab::` directives found inside `filter-tabs`. Content will not be rendered.")
            return []

        # Parse the tab names from the directive's arguments.
        tabs_raw = [t.strip() for t in self.arguments[0].split(',')]
        tab_names_only = [re.sub(r'\s*\(\s*default\s*\)$', '', t, re.IGNORECASE).strip() for t in tabs_raw]

        if len(set(tab_names_only)) != len(tab_names_only):
            raise self.error(f"Duplicate tab names found: {tab_names_only}")

        # Identify the default tab.
        default_tab, tab_names = "", []
        for tab in tabs_raw:
            match = re.match(r"^(.*?)\s*\(\s*default\s*\)$", tab, re.IGNORECASE)
            tab_name = match.group(1).strip() if match else tab
            if match and not default_tab:
                default_tab = tab_name
            tab_names.append(tab_name)

        # If no default is specified, the first tab becomes the default.
        if not default_tab and tab_names:
            default_tab = tab_names[0]

        # Instantiate the renderer and call the appropriate render method based on the builder.
        renderer = FilterTabsRenderer(self, tab_names, default_tab, temp_blocks)
        if env.app.builder.name == 'html':
            return renderer.render_html()
        else:
            return renderer.render_fallback()


def setup_collapsible_admonitions(app: Sphinx, doctree: nodes.document, docname: str):
    """
    Finds any admonition with the `:class: collapsible` option and transforms it
    into an HTML `<details>`/`<summary>` element for a native collapsible effect.
    This hook runs after the document tree is resolved.
    """
    if not app.config.filter_tabs_collapsible_enabled or app.builder.name != 'html':
        return

    # Iterate over a copy of the list of nodes to allow for safe modification.
    for node in list(doctree.findall(nodes.admonition)):
        if 'collapsible' not in node.get('classes', []):
            continue

        is_expanded = 'expanded' in node.get('classes', [])
        title_node = next(iter(node.findall(nodes.title)), None)
        summary_text = title_node.astext() if title_node else "Details"
        if title_node:
            title_node.parent.remove(title_node) # Remove the old title.

        # Create the new <details> node.
        details_node = DetailsNode(classes=[COLLAPSIBLE_SECTION])
        if is_expanded:
            details_node['open'] = 'open'

        # Create the new <summary> node with a custom arrow.
        summary_node = SummaryNode()
        arrow_span = nodes.inline(classes=[CUSTOM_ARROW])
        arrow_span += nodes.Text("►")
        summary_node += arrow_span
        summary_node += nodes.Text(summary_text)
        details_node += summary_node

        # Move the original content of the admonition into a new container.
        content_node = nodes.container(classes=[COLLAPSIBLE_CONTENT])
        content_node.extend(copy.deepcopy(node.children))
        details_node += content_node
        # Replace the original admonition node with the new details node.
        node.replace_self(details_node)

def _get_html_attrs(node: nodes.Element) -> Dict[str, Any]:
    """Helper to get a clean dictionary of HTML attributes from a docutils node."""
    attrs = node.attributes.copy()
    # Remove docutils-internal attributes to avoid rendering them in the HTML.
    for key in ('ids', 'backrefs', 'dupnames', 'names', 'classes', 'id', 'for_id'):
        attrs.pop(key, None)
    return attrs

# --- HTML Visitor Functions ---
# These functions translate the custom docutils nodes into HTML tags.

def visit_container_node(self: HTML5Translator, node: ContainerNode) -> None:
    self.body.append(self.starttag(node, 'div', **_get_html_attrs(node)))
def depart_container_node(self: HTML5Translator, node: ContainerNode) -> None:
    self.body.append('</div>')

def visit_fieldset_node(self: HTML5Translator, node: FieldsetNode) -> None:
    self.body.append(self.starttag(node, 'fieldset', CLASS=SFT_FIELDSET))
def depart_fieldset_node(self: HTML5Translator, node: FieldsetNode) -> None:
    self.body.append('</fieldset>')

def visit_legend_node(self: HTML5Translator, node: LegendNode) -> None:
    self.body.append(self.starttag(node, 'legend', CLASS=SFT_LEGEND))
def depart_legend_node(self: HTML5Translator, node: LegendNode) -> None:
    self.body.append('</legend>')

def visit_radio_input_node(self: HTML5Translator, node: RadioInputNode) -> None:
    self.body.append(self.starttag(node, 'input', **_get_html_attrs(node)))
def depart_radio_input_node(self: HTML5Translator, node: RadioInputNode) -> None:
    pass # No closing tag for <input>.

def visit_label_node(self: HTML5Translator, node: LabelNode) -> None:
    attrs = _get_html_attrs(node)
    attrs['for'] = node['for_id'] # Connect the label to its radio button.
    self.body.append(self.starttag(node, 'label', **attrs))
def depart_label_node(self: HTML5Translator, node: LabelNode) -> None:
    self.body.append('</label>')

def visit_panel_node(self: HTML5Translator, node: PanelNode) -> None:
    self.body.append(self.starttag(node, 'div', CLASS=SFT_PANEL, **_get_html_attrs(node)))
def depart_panel_node(self: HTML5Translator, node: PanelNode) -> None:
    self.body.append('</div>')

def visit_details_node(self: HTML5Translator, node: DetailsNode) -> None:
    self.body.append(self.starttag(node, 'details', **_get_html_attrs(node)))
def depart_details_node(self: HTML5Translator, node: DetailsNode) -> None:
    self.body.append('</details>')

def visit_summary_node(self: HTML5Translator, node: SummaryNode) -> None:
    self.body.append(self.starttag(node, 'summary', **_get_html_attrs(node)))
def depart_summary_node(self: HTML5Translator, node: SummaryNode) -> None:
    self.body.append('</summary>')


def copy_static_files(app: Sphinx):
    """
    Copies the extension's static CSS file to the build output directory.
    This hook runs when the builder is initialized, ensuring the CSS file is
    always available for HTML builds without complex packaging maneuvers.
    """
    if app.builder.name != 'html':
        return
    source_css = Path(__file__).parent / "static" / "filter_tabs.css"
    dest_dir = Path(app.outdir) / "_static"
    dest_dir.mkdir(parents=True, exist_ok=True)
    shutil.copy(source_css, dest_dir)


def setup(app: Sphinx) -> Dict[str, Any]:
    """
    The main entry point for the Sphinx extension.
    This function registers all components with Sphinx.
    """
    # Register custom configuration values, allowing users to theme from conf.py.
    app.add_config_value('filter_tabs_tab_highlight_color', '#007bff', 'html', [str])
    app.add_config_value('filter_tabs_tab_background_color', '#f0f0f0', 'html', [str])
    app.add_config_value('filter_tabs_tab_font_size', '1em', 'html', [str])
    app.add_config_value('filter_tabs_border_radius', '8px', 'html', [str])
    app.add_config_value('filter_tabs_debug_mode', False, 'html', [bool])
    app.add_config_value('filter_tabs_collapsible_enabled', True, 'html', [bool])
    app.add_config_value('filter_tabs_collapsible_accent_color', '#17a2b8', 'html', [str])

    # Add the main stylesheet to the HTML output.
    app.add_css_file('filter_tabs.css')

    # Register all custom nodes and their HTML visitor/depart functions.
    app.add_node(ContainerNode, html=(visit_container_node, depart_container_node))
    app.add_node(FieldsetNode, html=(visit_fieldset_node, depart_fieldset_node))
    app.add_node(LegendNode, html=(visit_legend_node, depart_legend_node))
    app.add_node(RadioInputNode, html=(visit_radio_input_node, depart_radio_input_node))
    app.add_node(LabelNode, html=(visit_label_node, depart_label_node))
    app.add_node(PanelNode, html=(visit_panel_node, depart_panel_node))
    app.add_node(DetailsNode, html=(visit_details_node, depart_details_node))
    app.add_node(SummaryNode, html=(visit_summary_node, depart_summary_node))

    # Register the RST directives.
    app.add_directive('filter-tabs', FilterTabsDirective)
    app.add_directive('tab', TabDirective)

    # Connect to Sphinx events (hooks) to run custom functions at specific build stages.
    app.connect('doctree-resolved', setup_collapsible_admonitions)
    app.connect('builder-inited', copy_static_files)

    # Return metadata about the extension.
    return {
        'version': __version__,
        'parallel_read_safe': True,
        'parallel_write_safe': True,
    }
