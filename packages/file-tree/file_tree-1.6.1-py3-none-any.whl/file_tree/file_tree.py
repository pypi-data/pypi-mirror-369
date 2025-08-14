"""Defines the main FileTree object, which will be the main point of interaction."""

import os
import string
import warnings
from collections import defaultdict
from difflib import get_close_matches
from functools import cmp_to_key
from pathlib import Path
from shutil import copyfile
from typing import Any, Collection, Dict, Generator, Optional, Sequence, Set, Union
from warnings import warn

import numpy as np
import rich
import xarray

from .template import DuplicateTemplate, Placeholders, Template, is_singular


class FileTree:
    """Represents a structured directory.

    The many methods can be split into 4 categories

        1. The template interface. Each path (file or directory) is represented by a :class:`Template <file_tree.template.Template>`,
           which defines the filename with any unknown parts (e.g., subject ID) marked by placeholders.
           Templates are accessed based on their key.

            - :meth:`get_template`: used to access a template based on its key.
            - :meth:`template_keys`: used to list all the template keys.
            - :meth:`add_template`: used to add a new template or overwrite an existing one.
            - :meth:`add_subtree`: can be used to add all the templates from a different tree to this one.
            - :meth:`override`: overrides some of the templates in this FileTree with that of another FileTree.
            - :meth:`filter_templates`: reduce the filetree to a user-provided list of templates and its parents

        2. The placeholder interface. Placeholders represent values to be filled into the placeholders.
           Each placeholder can be either undefined, have a singular value, or have a sequence of possible values.

            - You can access the :class:`placeholders dictionary-like object <file_tree.template.Placeholders>` directly through `FileTree.placeholders`
            - :meth:`update`: returns a new FileTree with updated placeholders or updates the placeholders in the current one.
            - :meth:`update_glob`: sets the placeholder values based on which files/directories exist on disk.
            - :meth:`iter_vars`: iterate over all possible values for the selected placeholders.
            - :meth:`iter`: iterate over all possible values for the placeholders that are part of a given template.

        3. Getting the actual filenames based on filling the placeholder values into the templates.

            - :meth:`get`: Returns a valid path by filling in all the placeholders in a template.
              For this to work all placeholder values should be defined and singular.
            - :meth:`get_mult`: Returns array of all possible valid paths by filling in the placeholders in a template.
              Placeholder values can be singular or a sequence of possible values.
            - :meth:`get_mult_glob`: Returns array with existing paths on disk.
              Placeholder values can be singular, a sequence of possible values, or undefined.
              In the latter case possible values for that placeholder are determined by checking the disk.
            - :meth:`fill`: Returns new FileTree with any singular values filled into the templates and removed from the placeholder dict.

        4. Input/output

            - :meth:`report`: create a pretty overview of the filetree
            - :meth:`run_app`: opens a terminal-based App to explore the filetree interactively
            - :meth:`empty`: creates empty FileTree with no templates or placeholder values.
            - :meth:`read`: reads a new FileTree from a file.
            - :meth:`from_string`: reads a new FileTree from a string.
            - :meth:`write`: writes a FileTree to a file.
            - :meth:`to_string`: writes a FileTree to a string.
    """

    def __init__(
        self,
        templates: Dict[str, Template],
        placeholders: Union[Dict[str, Any], Placeholders],
        return_path=False,
        glob=True,
    ):
        """Create a new FileTree with provided templates/placeholders."""
        self._templates = templates
        self.placeholders = Placeholders(placeholders)
        self.return_path = return_path
        self.glob = glob
        if not (glob in (False, True, "default", "first", "last") or callable(glob)):
            raise ValueError(
                f"Invalid value for `glob` ({glob}). Please note that from v1.6 `glob` is now a setting in `FileTree` and can no longer be used as a placeholder name."
            )

    # create new FileTree objects
    @classmethod
    def empty(
        cls, top_level: Union[str, Template] = ".", return_path=False, glob=True
    ) -> "FileTree":
        """Create a new empty FileTree containing only a top-level directory.

        Args:
            top_level: Top-level directory that other templates will use as a reference. Defaults to current directory.
            return_path: if True, returns filenames as Path objects rather than strings.
            glob: determines whether to allow filename pattern matching in the templates. Globbing is only applied if there are `*` or `?` characters in the template. Possible values are:
                - `False`: do not do any pattern matching (identical to <= v1.5 behaviour).
                - `True`/"default": return filename if there is a single match. Raise an error otherwise. This is the default behaviour in v1.6 or later.
                - "first"/"last": return the first or last match (based on alphabetical ordering). An error is raised if there are no matches.
                - callable: return the match returned by the callable. The input to the callable is a list of all the matching filenames (possibly of zero length).

        Returns:
            empty FileTree
        """
        if not isinstance(top_level, Template):
            top_level = Template(None, top_level)
        return cls({"": top_level}, {}, return_path=return_path, glob=glob)

    @classmethod
    def read(
        cls,
        name: str,
        top_level: Union[str, Template] = ".",
        return_path=False,
        glob=True,
        **placeholders,
    ) -> "FileTree":
        """Read a filetree based on the given name.

        # noqa DAR101

        Args:
            name: name of the filetree. Interpreted as:

                - a filename containing the tree definition if "name" or "name.tree" exist on disk
                - one of the trees in `tree_directories` if one of those contains "name" or "name.tree"
                - one of the tree in the plugin FileTree modules

            top_level: top-level directory name. Defaults to current directory. Set to parent template for sub-trees.
            return_path: if True, returns filenames as Path objects rather than strings.
            glob: determines whether to allow filename pattern matching in the templates. Globbing is only applied if there are `*` or `?` characters in the template. Possible values are:
                - `False`: do not do any pattern matching (identical to <= v1.5 behaviour).
                - `True`/"default": return filename if there is a single match. Raise an error otherwise. This is the default behaviour in v1.6 or later.
                - "first"/"last": return the first or last match (based on alphabetical ordering). An error is raised if there are no matches.
                - callable: return the match returned by the callable. The input to the callable is a list of all the matching filenames (possibly of zero length).
            placeholders: maps placeholder names to their values

        Raises:
            ValueError: if FileTree is not found.

        Returns:
            FileTree: tree matching the definition in the file
        """
        from . import parse_tree

        if "directory" in placeholders:
            warnings.warn(
                f"Setting the 'directory' placeholder to {placeholders['directory']}. "
                + "This differs from the behaviour of the old filetree in fslpy, which used the `directory` keyword to set the top-level directory. "
                + "If you want to do that, please use the new `top_level` keyword instead of `directory`."
            )
        found_tree = parse_tree.search_tree(name)
        if isinstance(found_tree, Path):
            with open(found_tree, "r") as f:
                text = f.read()
            with parse_tree.extra_tree_dirs([found_tree.parent]):
                return cls.from_string(
                    text, top_level, return_path=return_path, glob=glob, **placeholders
                )
        elif isinstance(found_tree, str):
            return cls.from_string(
                found_tree,
                top_level,
                return_path=return_path,
                glob=glob,
                **placeholders,
            )
        elif isinstance(found_tree, FileTree):
            new_tree = cls.empty(top_level, return_path, glob=glob)
            new_tree.add_subtree(found_tree, fill=False)
            return new_tree.update(**placeholders)
        raise ValueError(
            f"Type of object ({type(found_tree)}) returned when searching for FileTree named '{name}' was not recognised"
        )

    @classmethod
    def from_string(
        cls,
        definition: str,
        top_level: Union[str, Template] = ".",
        return_path=False,
        glob=True,
        **placeholders,
    ) -> "FileTree":
        """Create a FileTree based on the given definition.

        Args:
            definition: A FileTree definition describing a structured directory
            top_level: top-level directory name. Defaults to current directory. Set to parent template for sub-trees.
            return_path: if True, returns filenames as Path objects rather than strings.
            glob: determines whether to allow filename pattern matching in the templates. Globbing is only applied if there are `*` or `?` characters in the string. Possible values are:
                - `False`: do not do any pattern matching (identical to <= v1.5 behaviour).
                - `True`/"default": return filename if there is a single match. Raise an error otherwise. This is the default behaviour in v1.6 or later.
                - "first"/"last": return the first or last match (based on alphabetical ordering). An error is raised if there are no matches.
                - callable: return the match returned by the callable. The input to the callable is a list of all the matching filenames (possibly of zero length).
            placeholders: key->value pairs setting initial value for any placeholders.

        Returns:
            FileTree: tree matching the definition in the file
        """
        from . import parse_tree

        res = parse_tree.read_file_tree_text(definition.splitlines(), top_level).update(
            inplace=True, **placeholders
        )
        res.return_path = return_path
        res.glob = glob
        return res

    def copy(
        self,
    ) -> "FileTree":
        """Create a copy of the tree.

        The dictionaries (templates, placeholders) are copied, but the values within them are not.

        Returns:
            FileTree: new tree object with identical templates, sub-trees and placeholders
        """
        new_tree = type(self)(
            dict(self._templates),
            Placeholders(self.placeholders),
            self.return_path,
            self.glob,
        )
        return new_tree

    # template interface
    def get_template(self, key: str, error_duplicate=True) -> Template:
        """Return the template corresponding to `key`.

        Raises:
            KeyError: if no template with that identifier is available  # noqa DAR402
            ValueError: if multiple templates with that identifier are available (suppress using `error_duplicate=False`)

        Args:
            key (str): key identifying the template.
            error_duplicate (bool): set to False to return a `DuplicateTemplate` object rather than raising an error

        Returns:
            Template: description of pathname with placeholders not filled in
        """
        try:
            value = self._templates[key]
            if error_duplicate and isinstance(value, DuplicateTemplate):
                templates = ", ".join([str(t.as_path) for t in value.templates])
                raise ValueError(
                    f"There are multiple templates matching key '{key}': {templates}"
                )
            return value
        except KeyError:
            pass
        matches = get_close_matches(key, self.template_keys())
        if len(matches) == 0:
            raise KeyError(f"Template key '{key}' not found in FileTree.")
        else:
            raise KeyError(
                f"Template key '{key}' not found in FileTree; did you mean {' or '.join(sorted(matches))}?"
            )

    @property
    def top_level(
        self,
    ):
        """Top-level directory.

        Within the template dictionary this top-level directory is represented with an empty string
        """
        as_string = self.get_template("").unique_part
        if self.return_path:
            return Path(as_string)
        return str(as_string)

    @top_level.setter
    def top_level(self, value: str):
        self.get_template("").unique_part = str(value)

    def add_template(
        self,
        template_path: str,
        key: Optional[Union[str, Sequence[str]]] = None,
        parent: Optional[str] = "",
        overwrite=False,
    ) -> Template:
        """Update the FileTree with the new template.

        Args:
            template_path: path name with respect to the parent (or top-level if no parent provided)
            key: key(s) to access this template in the future. Defaults to result from :meth:`Template.guess_key <file_tree.template.Template.guess_key>`
                (i.e., the path basename without the extension).
            parent: if defined, `template_path` will be interpreted as relative to this template.
                By default the top-level template is used as reference.
                To create a template unaffiliated with the rest of the tree, set `parent` to None.
                Such a template should be an absolute path or relative to the current directory and can be used as parent for other templates
            overwrite: if True, overwrites any existing template rather than raising a ValueError. Defaults to False.

        Returns:
            Template: the newly added template object
        """
        if parent is None:
            parent_template = None
        elif isinstance(parent, Template):
            parent_template = parent
        else:
            parent_template = self.get_template(parent)
        new_template = Template(parent_template, template_path)
        if (
            parent_template is not None
            and new_template.as_path == parent_template.as_path
        ):
            new_template = parent_template
        return self._add_actual_template(new_template, key, overwrite=overwrite)

    def _add_actual_template(
        self,
        template: Template,
        keys: Optional[Union[str, Sequence[str]]] = None,
        overwrite=False,
    ):
        if keys is None:
            keys = template.guess_key()
        if isinstance(keys, Path):
            keys = str(keys)
        if isinstance(keys, str):
            keys = [keys]
        for key in keys:
            if key in self._templates:
                old_template = self.get_template(key, error_duplicate=overwrite)
                if not overwrite:
                    if isinstance(old_template, DuplicateTemplate):
                        old_template.add_template(template)
                    else:
                        self._templates[key] = DuplicateTemplate(old_template, template)
                    continue

                for potential_child in self._templates.values():
                    if potential_child.parent is old_template:
                        potential_child.parent = template
            self._templates[key] = template
        return template

    def override(
        self,
        new_filetree: "FileTree",
        required: Collection[str] = (),
        optional: Collection[str] = (),
    ):
        """Overide some templates and all placeholders in this filetree with templates from `new_filetree`.

        A new `FileTree` is returned with all the template keys in `required` replaced or added.
        Template keys in `optional` will also be replaced or added if they are present in `new_filetree`.

        Any placeholders defined in `new_filetree` will be transfered as well.

        Without supplying any keys to `required` or `optional` the new `FileTree` will be identical to this one.
        """
        if isinstance(required, str):
            required = [required]
        if isinstance(optional, str):
            optional = [optional]
        all_keys = set(required).union(optional)

        old_duplicate_keys = self.template_keys(skip_duplicates=False).difference(
            self.template_keys(skip_duplicates=True)
        )
        duplicates = [key for key in all_keys if key in old_duplicate_keys]
        if len(duplicates) > 0:
            raise ValueError(
                "Some of the keys to be replaced in the original FileTree are duplicates: %s",
                ", ".join(duplicates),
            )

        new_available_keys = new_filetree.template_keys(skip_duplicates=False)
        undefined = [key for key in required if key not in new_available_keys]
        if len(undefined) > 0:
            raise ValueError(
                "Some required keys are missing from the input FileTree: %s",
                ", ".join(undefined),
            )

        new_duplicate_keys = new_available_keys.difference(
            new_filetree.template_keys(skip_duplicates=True)
        )
        duplicates = [key for key in all_keys if key in new_duplicate_keys]
        if len(duplicates) > 0:
            raise ValueError(
                "Some of the keys to be used in the input FileTree are duplicates: %s",
                ", ".join(duplicates),
            )

        res_filetree = self.copy()
        res_filetree.placeholders.update(new_filetree.placeholders)
        for key in all_keys:
            if key in new_available_keys:
                res_filetree._add_actual_template(
                    new_filetree.get_template(key), key, overwrite=True
                )
        return res_filetree

    @property
    def _iter_templates(
        self,
    ) -> Dict[Template, Set[str]]:
        result = defaultdict(set)

        def add_parent(t: Template):
            if t.parent is None or t.parent in result:
                return
            result[t.parent]
            add_parent(t.parent)

        for key, possible in self._templates.items():
            if isinstance(possible, DuplicateTemplate):
                for template in possible.templates:
                    result[template].add(key)
                    add_parent(template)
            else:
                result[possible].add(key)
                add_parent(possible)
        return dict(result)

    def template_keys(self, only_leaves=False, skip_duplicates=True):
        """Return the keys of all the templates in the FileTree.

        Each key will be returned for templates with multiple keys.

        Args
            only_leaves (bool, optional): set to True to only return templates that do not have any children.
            skip_duplicates (bool, optional): set to False to include keys that point to multiple templates.
        """
        if skip_duplicates:
            keys = {k for (k, v) in self._templates.items() if isinstance(v, Template)}
        else:
            keys = set(self._templates.keys())
        if not only_leaves:
            return keys
        elif not skip_duplicates:
            raise ValueError("Cannot select only leaves when not skipping duplicates.")

        parents = {
            t.parent for t in self._iter_templates.keys() if t.parent is not None
        }
        return {key for key in keys if self.get_template(key) not in parents}

    def add_subtree(
        self,
        sub_tree: "FileTree",
        precursor: Union[Optional[str], Sequence[Optional[str]]] = (None,),
        parent: Optional[Union[str, Template]] = "",
        fill=None,
    ) -> None:
        """Update the templates and the placeholders in place with those in sub_tree.

        The top-level directory of the sub-tree will be replaced by the `parent` (unless set to None).
        The sub-tree templates will be available with the key "<precursor>/<original_key>",
        unless the precursor is None in which case they will be unchanged (which can easily lead to errors due to naming conflicts).

        What happens with the placeholder values of the sub-tree depends on whether the precursor is None or not:

            - if the precursor is None, any singular values are directly filled into the sub-tree templates.
              Any placeholders with multiple values will be added to the top-level variable list (error is raised in case of conflicts).
            - if the precursor is a string, the templates are updated to look for "<precursor>/<original_placeholder>" and
              all sub-tree placeholder values are also prepended with this precursor.
              Any template values with "<precursor>/<key>" will first look for that full key, but if that is undefined
              they will fall back to "<key>" (see :class:`Placeholders <file_tree.template.Placeholders>`).

        The net effect of either of these procedures is that the sub-tree placeholder values will be used in that sub-tree,
        but will not affect templates defined elsewhere in the parent tree.
        If a placeholder is undefined in a sub-tree, it will be taken from the parent placeholder values (if available).

        Args:
            sub_tree: tree to be added to the current one
            precursor: name(s) of the sub-tree. Defaults to just adding the sub-tree to the main tree without precursor
            parent: key of the template used as top-level directory for the sub tree.
                Defaults to top-level directory of the main tree.
                Can be set to None for an independent tree.
            fill: whether any defined placeholders should be filled in before adding the sub-tree. By default this is True if there is no precursor and false otherwise

        Raises:
            ValueError: if there is a conflict in the template names.
        """
        if isinstance(precursor, str) or precursor is None:
            precursor = [precursor]
        for name in precursor:
            sub_tree_fill = sub_tree
            if name is None:
                add_string = ""
                if (fill is None) or fill:
                    sub_tree_fill = sub_tree.fill()
            else:
                add_string = name + "/"
                if fill:
                    sub_tree_fill = sub_tree.fill()

            to_assign = dict(sub_tree_fill._iter_templates)
            sub_top_level = [k for (k, v) in to_assign.items() if "" in v][0]

            if parent is None:
                new_top_level = Template(None, sub_top_level.unique_part)
            elif isinstance(parent, Template):
                new_top_level = parent
            else:
                new_top_level = self.get_template(parent)
            if name is None:
                if parent is None:
                    for letter in string.ascii_letters:
                        label = f"tree_top_{letter}"
                        if (
                            label not in sub_tree_fill.template_keys()
                            and label not in self.template_keys()
                        ):
                            self._add_actual_template(new_top_level, label)
                            break
            else:
                self._add_actual_template(new_top_level, add_string)

            been_assigned = {sub_top_level: new_top_level}
            del to_assign[sub_top_level]
            while len(to_assign) > 0:
                for old_template, keys in list(to_assign.items()):
                    if old_template.parent is None:
                        parent_template = None
                    elif old_template.parent in been_assigned:
                        parent_template = been_assigned[old_template.parent]
                    else:
                        continue
                    new_template = Template(
                        parent_template, old_template.unique_part
                    ).add_precursor(add_string)
                    for key in keys:
                        self._add_actual_template(new_template, add_string + key)
                    been_assigned[old_template] = new_template
                    del to_assign[old_template]

            if name is None:
                conflict = {
                    key
                    for key in sub_tree_fill.placeholders.keys()
                    if key in self.placeholders
                }
                if len(conflict) > 0:
                    raise ValueError(
                        f"Sub-tree placeholder values for {conflict} conflict with those set in the parent tree."
                    )
            for old_key, old_value in sub_tree_fill.placeholders.items():
                if isinstance(old_key, str):
                    self.placeholders[add_string + old_key] = old_value
                else:
                    self.placeholders[frozenset(add_string + k for k in old_key)] = {
                        add_string + k: v for k, v in old_value.items()
                    }

    def filter_templates(
        self, template_names: Collection[str], check=True
    ) -> "FileTree":
        """Create new FileTree containing just the templates in `template_names` and their parents.

        Args:
            template_names: names of the templates to keep.
            check: if True, check whether all template names are actually part of the FileTree

        Raises:
            KeyError: if any of the template names are not in the FileTree (unless `check` is set to False).

        Returns:
            FileTree containing requested subset of templates.
        """
        all_keys = self.template_keys()
        if check:
            undefined = {name for name in template_names if name not in all_keys}
            if len(undefined) > 0:
                raise KeyError("Undefined template names found in filter: ", undefined)

        new_filetree = FileTree(
            {}, self.placeholders.copy(), return_path=self.return_path, glob=self.glob
        )

        already_added = set()

        def add_template(template: Template):
            if template in already_added:
                return
            if template.parent is not None:
                add_template(template.parent)
            new_filetree._add_actual_template(template, self._iter_templates[template])
            already_added.add(template)

        for name in template_names:
            if name not in all_keys:
                continue
            add_template(self.get_template(name))

        return new_filetree

    # placeholders interface
    def update(self, inplace=False, **placeholders) -> "FileTree":
        """Update the placeholder values to be filled into the templates.

        Args:
            inplace (bool): if True change the placeholders in-place (and return the FileTree itself);
                by default a new FileTree is returned with the updated values without altering this one.
            **placeholders (Dict[str, Any]): maps placeholder names to their new values (None to mark placeholder as undefined)

        Returns:
            FileTree: Tree with updated placeholders (same tree as the current one if inplace is True)
        """
        new_tree = self if inplace else self.copy()
        new_tree.placeholders.update(placeholders)
        return new_tree

    def update_glob(
        self,
        template_key: Union[str, Sequence[str]],
        inplace=False,
        link: Union[None, Sequence[str], Sequence[Sequence[str]]] = None,
    ) -> "FileTree":
        """Update any undefined placeholders based on which files exist on disk for template.

        Args:
            template_key (str or sequence of str): key(s) of the template(s) to use
            inplace (bool): if True change the placeholders in-place (and return the FileTree itself);
                by default a new FileTree is returned with the updated values without altering this one.
            link (sequences of str): template keys that should be linked together in the output.

        Returns:
            FileTree: Tree with updated placeholders (same tree as the current one if inplace is True)
        """
        if link is None:
            link = []
        elif len(link) > 0 and isinstance(link[0], str):
            link = [link]
        link_as_frozenset = [frozenset(link_value) for link_value in link]

        if isinstance(template_key, str):
            template_key = [template_key]
        new_placeholders: Dict[str, Set[str]] = defaultdict(set)
        new_links = [set() for _ in range(len(link))]
        for key in template_key:
            template = self.get_template(key)
            from_template = template.get_all_placeholders(self.placeholders, link=link)
            for name, values in from_template.items():
                if isinstance(name, frozenset):
                    index = link_as_frozenset.index(name)
                    values_as_tuples = zip(*[values[key] for key in link[index]])
                    new_links[index].update(values_as_tuples)
                else:
                    new_placeholders[name] = new_placeholders[name].union(values)

        def cmp(item1, item2):
            if item1 is None:
                return -1
            if item2 is None:
                return 1
            if item1 < item2:
                return -1
            if item1 > item2:
                return 1
            return 0

        new_tree = self if inplace else self.copy()
        new_tree.placeholders.update(
            {k: sorted(v, key=cmp_to_key(cmp)) for k, v in new_placeholders.items()},
        )
        for key, value in zip(link, new_links):
            new_tree.placeholders[tuple(key)] = list(zip(*sorted(value)))
        return new_tree

    # Extract paths
    def get(self, key: str, make_dir=False, glob=None) -> Union[str, Path]:
        """Return template with placeholder values filled in.

        Args:
            key (str): identifier for the template
            make_dir (bool, optional): If set to True, create the parent directory of the returned path.
            glob: determines whether to allow filename pattern matching in the templates. By default the value set when creating the file-tree is used (see `FileTree.glob`). Globbing is only applied if there are `*` or `?` in the template. Possible values are:
                - `False`: do not do any pattern matching (identical to <= v1.5 behaviour). Use this to get the raw string including any `*` or `?` characters
                - `True`/"default": return filename if there is a single match. Raise an error otherwise.
                - "first"/"last": return the first or last match (based on alphabetical ordering). An error is raised if there are no matches.
                - callable: return the match returned by the callable. The input to the callable is a list of all the matching filenames (possibly of zero length).

        Returns:
            Path: Filled in template as Path object.
                Returned as a `pathlib.Path` object if `FileTree.return_path` is True.
                Otherwise a string is returned.
        """
        path = self.get_template(key).format_single(
            self.placeholders, glob=self.glob if glob is None else glob
        )
        if make_dir:
            Path(path).parent.mkdir(parents=True, exist_ok=True)
        if self.return_path:
            return Path(path)
        return path

    def get_mult(
        self, key: Union[str, Sequence[str]], filter=False, make_dir=False, glob=None
    ) -> Union[xarray.DataArray, xarray.Dataset]:
        """Return array of paths with all possible values filled in for the placeholders.

        Singular placeholder values are filled into the template directly.
        For each placeholder with multiple values a dimension is added to the output array.
        This dimension will have the name of the placeholder and labels corresponding to the possible values (see http://xarray.pydata.org/en/stable/).
        The precense of required, undefined placeholders will lead to an error
        (see :meth:`get_mult_glob` or :meth:`update_glob` to set these placeholders based on which files exist on disk).

        Args:
            key (str, Sequence[str]): identifier(s) for the template.
            filter (bool, optional): If Set to True, will filter out any non-existent files.
                If the return type is strings, non-existent entries will be empty strings.
                If the return type is Path objects, non-existent entries will be None.
                Note that the default behaviour is opposite from :meth:`get_mult_glob`.
            make_dir (bool, optional): If set to True, create the parent directory for each returned path.
            glob: determines whether to allow filename pattern matching in the templates. By default the value set when creating the file-tree is used (see `FileTree.glob`). Globbing is only applied if there are `*` or `?` in the template. Possible values are:
                - `False`: do not do any pattern matching (identical to <= v1.5 behaviour). Use this to get the raw string including any `*` or `?` characters
                - `True`/"default": return filename if there is a single match. Raise an error otherwise.
                - "first"/"last": return the first or last match (based on alphabetical ordering). An error is raised if there are no matches.
                - callable: return the match returned by the callable. The input to the callable is a list of all the matching filenames (possibly of zero length).

        Returns:
            xarray.DataArray, xarray.Dataset: For a single key returns all possible paths in an xarray DataArray.
                For multiple keys it returns the combination of them in an xarray Dataset.
                Each element of in the xarray is a `pathlib.Path` object if `FileTree.return_path` is True.
                Otherwise the xarray will contain the paths as strings.
        """
        if isinstance(key, str):
            paths = self.get_template(key).format_mult(
                self.placeholders,
                filter=filter,
                glob=self.glob if glob is None else glob,
            )
            paths.name = key
            if make_dir:
                for path in paths.data.flat:
                    if path is not None:
                        Path(path).parent.mkdir(parents=True, exist_ok=True)
            if self.return_path:
                return xarray.apply_ufunc(
                    lambda p: None if p == "" else Path(p), paths, vectorize=True
                )
            return paths
        else:
            return xarray.merge(
                [self.get_mult(k, filter=filter, make_dir=make_dir) for k in key],
                join="exact",
            )

    def get_mult_glob(
        self, key: Union[str, Sequence[str]], glob=None
    ) -> Union[xarray.DataArray, xarray.Dataset]:
        """Return array of paths with all possible values filled in for the placeholders.

        Singular placeholder values are filled into the template directly.
        For each placeholder with multiple values a dimension is added to the output array.
        This dimension will have the name of the placeholder and labels corresponding to the possible values (see http://xarray.pydata.org/en/stable/).
        The possible values for undefined placeholders will be determined by which files actually exist on disk.

        The same result can be obtained by calling `self.update_glob(key).get_mult(key, filter=True)`.
        However calling this method is more efficient, because it only has to check the disk for which files exist once.

        Args:
            key (str, Sequence[str]): identifier(s) for the template.
            glob: determines whether to allow filename pattern matching in the templates. By default the value set when creating the file-tree is used (see `FileTree.glob`). Globbing is only applied if there are `*` or `?` in the template. Possible values are:
                - `False`: do not do any pattern matching (identical to <= v1.5 behaviour). Use this to get the raw string including any `*` or `?` characters
                - `True`/"default": return filename if there is a single match. Raise an error otherwise.
                - "first"/"last": return the first or last match (based on alphabetical ordering). An error is raised if there are no matches.
                - callable: return the match returned by the callable. The input to the callable is a list of all the matching filenames (possibly of zero length).

        Returns:
            xarray.DataArray, xarray.Dataset: For a single key returns all possible paths in an xarray DataArray.
                For multiple keys it returns the combination of them in an xarray Dataset.
                Each element of in the xarray is a `pathlib.Path` object if `FileTree.return_path` is True.
                Otherwise the xarray will contain the paths as strings.
        """
        if isinstance(key, str):
            template = self.get_template(key)
            matches = template.all_matches(self.placeholders)

            new_placeholders = Placeholders(self.placeholders)
            updates, matches = template.get_all_placeholders(
                self.placeholders, return_matches=True
            )
            new_placeholders.update(updates)

            paths = template.format_mult(
                new_placeholders,
                filter=True,
                matches=matches,
                glob=self.glob if glob is None else glob,
            )
            paths.name = key
            if self.return_path:
                return paths
            res = xarray.apply_ufunc(
                lambda p: "" if p is None else str(p), paths, vectorize=True
            )
            return res
        else:
            return xarray.merge(
                [self.get_mult_glob(k, glob) for k in key],
                join="outer",
                fill_value=None if self.return_path else "",
            )

    def fill(self, keep_optionals=True) -> "FileTree":
        """Fill in singular placeholder values.

        Args:
            keep_optionals: if True keep optional parameters that have not been set

        Returns:
            FileTree: new tree with singular placeholder values filled into the templates and removed from the placeholder dict
        """
        new_tree = FileTree(
            {}, self.placeholders.split()[1], self.return_path, glob=self.glob
        )
        to_assign = dict(self._iter_templates)
        template_mappings = {None: None}
        while len(to_assign) > 0:
            for old_template, keys in list(to_assign.items()):
                if old_template.parent in template_mappings:
                    new_parent = template_mappings[old_template.parent]
                else:
                    continue
                new_template = Template(
                    new_parent,
                    str(
                        Template(None, old_template.unique_part).format_single(
                            self.placeholders,
                            check=False,
                            keep_optionals=keep_optionals,
                            glob=False,
                        )
                    ),
                )
                template_mappings[old_template] = new_template
                new_tree._add_actual_template(new_template, keys)
                del to_assign[old_template]
        return new_tree

    # iteration
    def iter_vars(
        self, placeholders: Sequence[str]
    ) -> Generator["FileTree", None, None]:
        """Iterate over the user-provided placeholders.

        A single file-tree is yielded for each possible value of the placeholders.

        Args:
            placeholders (Sequence[str]): sequence of placeholder names to iterate over

        Yields:
            FileTrees, where each placeholder only has a single possible value
        """
        for sub_placeholders in self.placeholders.iter_over(placeholders):
            yield FileTree(
                self._templates, sub_placeholders, self.return_path, glob=self.glob
            )

    def iter(
        self, template: str, check_exists: bool = False
    ) -> Generator["FileTree", None, None]:
        """Iterate over trees containng all possible values for template.

        Args:
            template (str): short name identifier of the template
            check_exists (bool): set to True to only return trees for which the template actually exists

        Yields:
            FileTrees, where each placeholder in given template only has a single possible value
        """
        placeholders = self.get_template(template).placeholders(
            valid=self.placeholders.keys()
        )
        for tree in self.iter_vars(placeholders):
            if not check_exists or Path(tree.get(template)).exists:
                yield tree

    # convert to string
    def to_string(self, indentation=4) -> str:
        """Convert FileTree into a valid filetree definition.

        An identical FileTree can be created by running :meth:`from_string` on the resulting string.

        Args:
            indentation (int, optional): Number of spaces to use for indendation. Defaults to 4.

        Returns:
            String representation of FileTree.
        """
        lines = [self.placeholders.to_string()]

        top_level = sorted(
            [
                template
                for template in self._iter_templates.keys()
                if template.parent is None
            ],
            key=lambda k: ",".join(self._iter_templates[k]),
        )
        already_done = set()
        for t in top_level:
            if t not in already_done:
                lines.append(
                    t.as_multi_line(self._iter_templates, indentation=indentation)
                )
                already_done.add(t)
        return "\n\n".join(lines)

    def write(self, filename, indentation=4):
        """Write the FileTree to a disk as a text file.

        The first few lines will contain the placeholders.
        The remaining lines will contain the actual FileTree with all the templates (including sub-trees).
        The top-level directory is not stored in the file and hence will need to be provided when reading the tree from the file.

        Args:
            filename (str or Path): where to store the file (directory should exist already)
            indentation (int, optional): Number of spaces to use in indendation. Defaults to 4.
        """
        with open(filename, "w") as f:
            f.write(self.to_string(indentation=indentation))

    def report(self, fill=True, pager=False):
        """Print a formatted report of the filetree to the console.

        Prints a report of the file-tree to the terminal with:
        - table with placeholders and their values
        - tree of templates with template keys marked in cyan

        Args:
            fill (bool, optional): by default any fixed placeholders are filled in before printing the tree (using :meth:`fill`). Set to False to disable this.
            pager (bool, optional): if set to True, the report will be filed into a pager (recommended if the output is very large)
        """
        if fill:
            self = self.fill()

        if pager:
            from rich.console import Console

            printer = Console()
            with printer.pager():
                for part in self._generate_rich_report():
                    printer.print(part)
        else:
            for part in self._generate_rich_report():
                rich.print(part)

    def _generate_rich_report(self):
        """Generate a sequence of Rich renderables to produce report."""
        from rich.table import Table
        from rich.tree import Tree

        single_vars = {}
        multi_vars = {}
        linked_vars = []
        for key, value in self.placeholders.items():
            if value is None:
                continue
            if isinstance(key, frozenset):
                linked_vars.append(sorted(key))
                for linked_key, linked_value in value.items():
                    multi_vars[linked_key] = linked_value
            elif np.array(value).ndim == 1:
                multi_vars[key] = value
            else:
                single_vars[key] = value
        if len(single_vars) > 0:
            single_var_table = Table("name", "value", title="Defined placeholders")
            for key in sorted(single_vars.keys()):
                single_var_table.add_row(key, single_vars[key])
            yield single_var_table
        if len(multi_vars) > 0:
            multi_var_table = Table(
                "name", "value", title="Placeholders with multiple options"
            )
            for key in sorted(multi_vars.keys()):
                multi_var_table.add_row(key, ", ".join(str(v) for v in multi_vars[key]))
            yield multi_var_table

        if len(linked_vars) > 0:
            yield "Linked variables:\n" + (
                "\n".join([", ".join(v) for v in linked_vars])
            )

        def add_children(t: Template, tree: Optional[Tree]):
            for child in sorted(
                t.children(self._iter_templates.keys()), key=lambda t: t.as_string
            ):
                child_tree = tree.add(child.rich_line(self._iter_templates))
                add_children(child, child_tree)

        top_level = sorted(
            [
                template
                for template in self._iter_templates.keys()
                if template.parent is None
            ],
            key=lambda t: ",".join(self._iter_templates[t]),
        )
        already_done = set()
        for t in top_level:
            if t not in already_done:
                base_tree = Tree(t.rich_line(self._iter_templates))
                add_children(t, base_tree)
                yield base_tree

    def run_app(
        self,
    ):
        """
        Open a terminal-based App to explore the filetree interactively.

        The resulting app runs directly in the terminal,
        so it should work when ssh'ing to some remote cluster.

        There will be two panels:

            - The left panel will show all the templates in a tree format.
              Template keys are shown in cyan.
              For each template the number of files that exist on disc out of the total number is shown
              colour coded based on completeness (red: no files; yellow: some files; blue: all files).
              Templates can be selected by hovering over them.
              Clicking on directories with hide/show their content.
            - The right panel will show for the selected template the complete template string
              and a table showing for which combination of placeholders the file is present/absent
              (rows for absent files are colour-coded red).
        """
        from . import app

        app.FileTreeViewer(self).run()


def convert(
    src_tree: FileTree,
    target_tree: Optional[FileTree] = None,
    keys=None,
    symlink=False,
    overwrite=False,
    glob_placeholders=None,
):
    """
    Copy or link files defined in `keys` from the `src_tree` to the `target_tree`.

    Given two example trees

        - source::

            subject = A,B

            sub-{subject}
                data
                    T1w.nii.gz
                    FLAIR.nii.gz

        - target::

            subject = A,B

            data
                sub-{subject}
                    {subject}-T1w.nii.gz (T1w)
                    {subject}-T2w.nii.gz (T2w)

    And given pre-existing data matching the source tree::

        .
        ├── sub-A
        │   └── data
        │       ├── FLAIR.nii.gz
        │       └── T1w.nii.gz
        └── sub-B
            └── data
                ├── FLAIR.nii.gz
                └── T1w.nii.gz

    We can do the following conversions:

        - `convert(source, target)`:
            copies all matching keys from `source` to `target`.
            This will only copy the "T1w.nii.gz" files, because they are the only match in the template keys.
            Note that the `data` template key also matches between the two trees, but this template is not a leaf, so is ignored.
        - `convert(source, target, keys=['T1w', ('FLAIR', 'T2w')])`:
            copies the "T1w.nii.gz" files from `source` to `target` and
            copies the "FLAIR.nii.gz" in `source` to "T2w..nii.gz" in `target`.
        - `convert(source.update(subject='B'), source.update(subject='C'))`:
            creates a new "data/sub-C" directory and
            copies all the data from "data/sub-B" into that directory.
        - `convert(source, keys=[('FLAIR', 'T1w')], overwrite=True)`:
            copies the "FLAIR.nii.gz" into the "T1w.nii.gz" files overwriting the originals.

    Warnings are raised in two cases:

        - if a source file is missing
        - if a target file already exists and `overwrite` is False

    Args:
        src_tree: prepopulated filetree with the source files
        target_tree: filetree that will be populated. Defaults to same as `src_tree`.
        keys: collection of template keys to transfer from `src_tree` to `target_tree`. Defaults to all templates keys shared between `src_tree` and `target_tree`.
        symlink: if set to true links the files rather than copying them
        overwrite: if set to True overwrite any existing files
        glob_placeholders: Placeholders that should be treated as wildcards. This is meant for placeholders that have different values for each filename.

    Raises:
        ValueError: if the conversion can not be carried out.  If raised no data will be copied/linked.
    """
    if target_tree is None and keys is None:
        raise ValueError("Conversion requires either `target_tree` or `keys` to be set")
    src_tree = src_tree.copy()
    if target_tree is None:
        target_tree = src_tree
    target_tree = target_tree.copy()
    if keys is None:
        keys = set(src_tree.template_keys(only_leaves=True)).intersection(
            target_tree.template_keys(only_leaves=True)
        )
    if glob_placeholders is None:
        glob_placeholders = set()
    for p in glob_placeholders:
        if p in src_tree.placeholders:
            raise ValueError(
                f"Placeholder {p} has been selected for globbing, however values were set for it in source tree"
            )
        if p in target_tree.placeholders:
            raise ValueError(
                f"Placeholder {p} has been selected for globbing, however values were set for it in target tree"
            )

    full_keys = {
        (
            (key_definition, key_definition)
            if isinstance(key_definition, str)
            else key_definition
        )
        for key_definition in keys
    }
    for src_key, target_key in full_keys:
        # ensure template placeholders are consistent between source and target tree
        for placeholder in (
            src_tree.get_template(src_key).placeholders()
            + target_tree.get_template(target_key).placeholders()
        ):
            if placeholder in glob_placeholders:
                continue
            if placeholder not in src_tree.placeholders:
                if placeholder not in target_tree.placeholders:
                    raise ValueError(
                        f"Can not convert template {src_key}, because no values have been set for {placeholder}"
                    )
                src_tree.placeholders[placeholder] = target_tree.placeholders[
                    placeholder
                ]
            elif placeholder not in target_tree.placeholders:
                target_tree.placeholders[placeholder] = src_tree.placeholders[
                    placeholder
                ]
            nsrc = (
                -1
                if is_singular(src_tree.placeholders[placeholder])
                else len(src_tree.placeholders[placeholder])
            )
            ntarget = (
                -1
                if is_singular(target_tree.placeholders[placeholder])
                else len(target_tree.placeholders[placeholder])
            )
            if nsrc != ntarget:
                raise ValueError(
                    f"Number of possible values for {placeholder} do not match between source and target tree"
                )

        # ensure non-singular placeholders match
        src_non_singular = {
            p
            for p in src_tree.get_template(src_key).placeholders()
            if p not in glob_placeholders and not is_singular(src_tree.placeholders[p])
        }
        target_non_singular = {
            p
            for p in target_tree.get_template(target_key).placeholders()
            if p not in glob_placeholders
            and not is_singular(target_tree.placeholders[p])
        }

        diff = src_non_singular.difference(target_non_singular).difference(
            glob_placeholders
        )
        if len(diff) > 0:
            raise ValueError(
                f"Placeholders {diff} in source template {src_key} has no equivalent in target template {target_key}"
            )
        diff = target_non_singular.difference(src_non_singular)
        if len(diff) > 0:
            raise ValueError(
                f"Placeholders {diff} in target template {target_key} has no equivalent in source template {src_key}"
            )

    # all checks have passed; let's get to work
    to_warn_about = ([], [])

    transfer_filenames = []

    for src_key, target_key in sorted(full_keys):
        iter_placeholders = sorted(
            {
                p
                for p in src_tree.get_template(src_key).placeholders()
                if p not in glob_placeholders
                and not is_singular(src_tree.placeholders[p])
            }
        )
        for single_src_tree, single_target_tree in zip(
            src_tree.iter_vars(iter_placeholders),
            target_tree.iter_vars(iter_placeholders),
        ):
            if len(glob_placeholders) == 0:
                src_fn = single_src_tree.get(src_key)
                target_fn = single_target_tree.get(target_key)
            else:
                try:
                    src_trees = list(single_src_tree.update_glob(src_key).iter(src_key))
                except ValueError:
                    to_warn_about[0].append(
                        single_src_tree.get_template(src_key).format_single(
                            single_src_tree.placeholders, check=False
                        )
                    )
                    continue
                if len(src_trees) > 1:
                    raise ValueError(
                        f"Multiple matching filenames were found when globbing {src_key} ({single_src_tree.get(src_key)})"
                    )

                keys = {
                    key: src_trees[0].placeholders[key]
                    for key in glob_placeholders
                    if key in src_trees[0].placeholders
                }
                src_fn = single_src_tree.update(**keys).get(src_key)
                target_fn = single_target_tree.update(**keys).get(src_key)

            transfer_filenames.append((Path(src_fn), Path(target_fn)))
    if len(to_warn_about[0]) > 0:
        warn(
            f"Following source files were not found during FileTree conversion: {to_warn_about[0]}"
        )
    if len(to_warn_about[1]) > 0:
        warn(
            f"Following target files already existed during FileTree conversion: {to_warn_about[1]}"
        )
    for fn1, fn2 in transfer_filenames:
        _convert_file(
            fn1,
            fn2,
            to_warn_about,
            symlink=symlink,
            overwrite=overwrite,
        )


def _convert_file(
    source: Path, target: Path, to_warn_about, symlink=False, overwrite=False
):
    """
    Copy or link `source` file to `target` file.

    Helper function for :func:`convert`
    """
    if not source.exists():
        to_warn_about[0].append(str(source))
        return
    if target.exists():
        if not overwrite:
            to_warn_about[1].append(str(target))
            return
        os.remove(target)
    target.parent.mkdir(parents=True, exist_ok=True)
    if not symlink:
        copyfile(source, target, follow_symlinks=False)
    elif source.is_absolute():
        target.symlink_to(source)
    else:
        target.symlink_to(os.path.relpath(source, target.parent))
