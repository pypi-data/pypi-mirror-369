"""
Set up and runs the textual app for some FileTree.

It is not recommended to run any of the functions in this module.
Instead load a :class:`FileTree <file_tree.file_tree.FileTree>` and
then run :meth:`FileTree.run_app <file_tree.file_tree.FileTree.run_app>` and
"""

import itertools
from argparse import ArgumentParser
from functools import lru_cache

try:
    from rich.style import Style
    from rich.text import Text
    from textual.app import App, ComposeResult
    from textual.binding import Binding
    from textual.containers import Horizontal, Vertical
    from textual.message import Message
    from textual.widgets import DataTable, Footer, Header, Static, Tree
    from textual.widgets.tree import TreeNode
except ImportError:
    raise ImportError(
        "Running the file-tree app requires rich and textual to be installed. Please install these using `pip/conda install textual`."
    )

from .file_tree import FileTree, Template


class TemplateSelect(Message, bubble=True):
    """Message sent when a template in the sidebar gets selected."""

    def __init__(self, sender, template: Template):
        """Create template selector."""
        self.template = template
        super().__init__(sender)


class TemplateTreeControl(Tree):
    """Sidebar containing all template definitions in FileTree."""

    current_node = None
    BINDINGS = [
        Binding("space", "toggle_node", "Collapse/Expand Node", show=True),
        Binding("up", "cursor_up", "Move Up", show=True),
        Binding("down", "cursor_down", "Move Down", show=True),
    ]

    def __init__(self, file_tree: FileTree, parent_app, name: str = None):
        """
        Create a new template sidebar based on given FileTree.

        Args:
            file_tree: FileTree to interact with
            parent_app: parent app to send message to update the template
            name: name of the sidebar within textual
        """
        self.file_tree = file_tree
        super().__init__("-", name=name)
        self.show_root = False
        self.find_children(self.root, self.file_tree.get_template(""))
        self.root.expand_all()
        self.parent_app = parent_app
        self.select_node(self.get_node_at_line(0))

    def on_mount(
        self,
    ):
        """Focus on tree when app is loaded."""
        self.focus()

    def find_children(self, parent_node: TreeNode, template: Template):
        """
        Find all the children of a template and add them to the node.

        Calls itself recursively.
        """
        all_children = template.children(self.file_tree._templates.values())
        if len(all_children) == 0:
            parent_node.add_leaf(template.unique_part, template)
        else:
            this_node = parent_node.add(template.unique_part, template)
            children = set()
            for child in all_children:
                if child not in children:
                    self.find_children(this_node, child)
                    children.add(child)

    def render_label(self, node: TreeNode[Template], base_style, style):
        """Render the label for a template node in the tree."""
        if node.data is None:
            return node.label
        label = _render_node_helper(self.file_tree, node).copy()
        if node is self.cursor_node:
            label.stylize("reverse")
        if not node.is_expanded and len(node.children) > 0:
            label = Text("📁 ") + label
        return label

    def on_tree_node_highlighted(self):
        """Update tempalte in parent app when a node is highlighted."""
        if self.current_node is not self.cursor_node:
            self.current_node = self.cursor_node
            self.parent_app.update_template(self.current_node.data)


@lru_cache(None)
def _render_node_helper(tree: FileTree, node: TreeNode[Template]):
    meta = {
        "@click": f"click_label({node.id})",
        "tree_node": node.id,
    }
    paths = node.data.format_mult(
        tree.placeholders, filter=True, glob=True
    ).data.flatten()
    existing = [p for p in paths if p != ""]
    color = "blue" if len(existing) == len(paths) else "yellow"
    if len(existing) == 0:
        color = "red"
    counter = f" [{color}][{len(existing)}/{len(paths)}][/{color}]"
    res = Text.from_markup(
        node.data.rich_line(tree._iter_templates) + counter, overflow="ellipsis"
    )
    res.apply_meta(meta)
    return res


class FileTreeViewer(App):
    """FileTree viewer app."""

    TITLE = "FileTree viewer"
    CSS_PATH = "css/app.css"

    def __init__(self, file_tree: FileTree):
        """Create a new FileTree viewer app."""
        self.file_tree = file_tree.fill().update_glob(
            file_tree.template_keys(only_leaves=True)
        )
        super().__init__()

    def compose(self) -> ComposeResult:
        """Compose the app layout."""
        self.table = TemplateTable(self.file_tree)
        controller = TemplateTreeControl(self.file_tree, self)
        self.template_keys = Static()
        yield Header()
        yield Horizontal(
            controller,
            Vertical(
                self.template_keys,
                self.table,
            ),
        )
        yield Footer()

    async def handle_template_select(self, message: TemplateSelect):
        """User has selected a template."""
        self.update_template(message.template)

    def update_template(self, template: Template):
        """Update the template keys and table based on the selected template."""
        self.app.sub_title = template.as_string
        keys = sorted(
            [
                key
                for (key, value) in self.file_tree._templates.items()
                if value == template
            ]
        )
        if len(keys) == 0:
            self.template_keys.update("No keys found for this template.")
        elif keys == [""]:
            self.template_keys.update(
                "Please select a template to see its possible values.",
            )
        else:
            self.template_keys.update(f"Keys: {', '.join(keys)}")
        self.table.update_template(template)


class TemplateTable(DataTable):
    """
    Table showing all possible placeholder values for a template.

    Any rows that do not exist in the file system are shaded red.
    """

    def __init__(self, file_tree: FileTree):
        """Create new renderer for template."""
        self.file_tree = file_tree
        super().__init__(fixed_rows=1, zebra_stripes=True, cursor_type="none")

    def update_template(self, template: Template):
        """Update the table to show the values for a new template."""
        self.clear(columns=True)
        xr = template.format_mult(self.file_tree.placeholders, filter=True, glob=True)
        coords = sorted(xr.coords.keys())
        self.add_columns(*coords)
        for values in itertools.product(*[xr.coords[c].data for c in coords]):
            path = xr.sel(**{c: v for c, v in zip(coords, values)}).item()
            style = Style(bgcolor=None if path != "" else "red")
            self.add_row(*[Text(v, style) for v in values])


def run():
    """Start CLI interface to app."""
    parser = ArgumentParser(
        description="Interactive terminal-based interface with file-trees"
    )
    parser.add_argument("file_tree", help="Which file-tree to visualise")
    parser.add_argument("-d", "--directory", default=".", help="top-level directory")
    args = parser.parse_args()
    FileTree.read(args.file_tree, args.directory).run_app()
