"""Define Placeholders and Template interface."""

import itertools
import os
import re
import string
from collections import defaultdict
from collections.abc import MutableMapping
from fnmatch import fnmatch
from functools import cmp_to_key, lru_cache
from glob import glob
from itertools import chain, combinations, product
from pathlib import Path
from typing import (
    Any,
    Collection,
    Dict,
    FrozenSet,
    Generator,
    Iterable,
    Iterator,
    List,
    Optional,
    Sequence,
    Set,
    Tuple,
)

import numpy as np
import pandas as pd
import xarray
from parse import compile, extract_format


def is_singular(value):
    """Whether a value is singular or has multiple options."""
    if isinstance(value, str):
        return True
    try:
        iter(value)
        return False
    except TypeError:
        return True


class Placeholders(MutableMapping):
    """Dictionary-like object containing the placeholder values.

    It understands about sub-trees
    (i.e., if "<sub_tree>/<placeholder>" does not exist it will return "<placeholder>" instead).
    """

    def __init__(self, *args, **kwargs):
        """Create a new Placeholders as any dictionary."""
        self.mapping = {}
        self.linkages: Dict[str, FrozenSet[str]] = {}
        self.update(dict(*args, **kwargs))

    def copy(self) -> "Placeholders":
        """Create copy of placeholder values."""
        p = Placeholders()
        p.mapping = dict(self.mapping)
        p.linkages = dict(self.linkages)
        return p

    def __getitem__(self, key: str):
        """Get placeholder values respecting sub-tree placeholders."""
        actual_key = self.find_key(key)
        if actual_key is None:
            raise KeyError(f"No parameter value available for {key}")
        if actual_key in self.linkages:
            return self.mapping[self.linkages[actual_key]][actual_key]
        return self.mapping[actual_key]

    def __delitem__(self, key):
        """Delete placeholder values represented by key."""
        if isinstance(key, tuple):
            key = frozenset(key)
        del self.mapping[key]
        if isinstance(key, frozenset):
            for k in key:
                del self.linkages[k]

    def __setitem__(self, key, value):
        """Overwrite placeholder value taking adjusting linked placeholders if needed."""
        if isinstance(key, tuple):  # create linked placeholders
            if len(key) != len(value):
                raise ValueError(
                    f"Attempting to set linked placeholders for {key}, "
                    + f"but {value} has a different number of elements than {key}"
                )
            if any([len(value[0]) != len(v) for v in value]):
                raise ValueError(
                    f"Attempting to set linked placeholders for {key}, "
                    + f"but not all elements in {value} have the same length."
                )
            value = {k: v for k, v in zip(key, value)}
            key = frozenset(key)
        if isinstance(key, frozenset):
            assert isinstance(value, dict)
            for k in list(key):
                if k in self.linkages:
                    unmatched_keys = [
                        unmatched
                        for unmatched in self.linkages[k]
                        if unmatched not in key
                    ]
                    if len(unmatched_keys) > 0:
                        matched_keys = [
                            matched for matched in self.linkages[k] if matched in key
                        ]
                        old_values = list(
                            zip(*[self[matched] for matched in matched_keys])
                        )
                        linked_values = {
                            new_key: [] for new_key in [*key, *unmatched_keys]
                        }
                        for index, new_value in enumerate(
                            zip(*[value[matched] for matched in matched_keys])
                        ):
                            already_seen_linked_matches = set()
                            for index2, old_value in enumerate(old_values):
                                if old_value != new_value:
                                    continue
                                linked_matches = tuple(
                                    self[unmatched][index2]
                                    for unmatched in unmatched_keys
                                )
                                print(f"Linked matches: {linked_matches}")

                                if linked_matches in already_seen_linked_matches:
                                    continue
                                already_seen_linked_matches.add(linked_matches)

                                for match, v in zip(matched_keys, new_value):
                                    linked_values[match].append(v)
                                for unmatch, v in zip(unmatched_keys, linked_matches):
                                    linked_values[unmatch].append(v)
                            if len(already_seen_linked_matches) == 0:
                                for match, v in zip(matched_keys, new_value):
                                    linked_values[match].append(v)
                                for unmatched in unmatched_keys:
                                    linked_values[unmatched].append(None)
                            for _ in range(max(1, len(already_seen_linked_matches))):
                                for k in key:
                                    if k in matched_keys:
                                        continue
                                    print(value[k])
                                    linked_values[k].append(value[k][index])

                        self[frozenset([*key, *unmatched_keys])] = linked_values
                        return
            self.mapping[key] = {k: tuple(v) for (k, v) in value.items()}
            for k in list(key):
                if k in self.mapping:
                    del self.mapping[k]
                if k in self.linkages:
                    if self.linkages[k] in self.mapping and self.linkages[k] != key:
                        del self.mapping[self.linkages[k]]
                    del self.linkages[k]
                self.linkages[k] = key
        elif key in self.linkages:
            old_values = self.mapping[self.linkages[key]]
            if is_singular(value):
                nvalue = old_values[key].count(value)
                self.unlink(*old_values.keys())
                if nvalue == 0:
                    for skey in old_values:
                        del self.mapping[skey]
                    self.mapping[key] = value
                elif nvalue == 1:
                    idx = old_values[key].index(value)
                    for skey in old_values:
                        self.mapping[skey] = old_values[skey][idx]
                else:
                    idx = [i for i, v in enumerate(old_values[key]) if v == value]
                    for skey in old_values:
                        if key == skey:
                            self.mapping[key] = value
                        else:
                            self.mapping[skey] = tuple(old_values[skey][i] for i in idx)
                    self.link(*[skey for skey in old_values if skey != key])
            else:
                self[frozenset([key])] = {key: value}
                return
        else:
            self.mapping[key] = value

    def __iter__(self):
        """Iterate over all placeholder keys that actually have values."""
        for key in self.mapping:
            if self.mapping[key] is not None:
                yield key

    def __len__(self):
        """Return number of keys in the mapping."""
        return len([k for k, v in self.mapping.items() if v is not None])

    def __repr__(self):
        """Text representation of placeholder values."""
        return f"Placeholders({self.mapping})"

    def find_key(self, key: str) -> Optional[str]:
        """Find the actual key containing the value.

        Will look for:

            - not None value for the key itself
            - not None value for any parent (i.e, for key "A/B", will look for "B" as well)
            - otherwise will return None

        Args:
            key (str): placeholder name

        Returns:
            None if no value for the key is available, otherwise the key used to index the value
        """
        if not isinstance(key, str):
            key = frozenset(key)
        elif key in self.linkages:
            return key
        if self.mapping.get(key, None) is not None:
            return key
        elif "/" in key:
            _, *parts = key.split("/")
            new_key = "/".join(parts)
            return self.find_key(new_key)
        else:
            return None

    def missing_keys(self, all_keys: Collection[str], top_level=True) -> Set[str]:
        """Identify any placeholder keys in `all_keys` that are not defined.

        If `top_level` is True (default), any sub-tree information is removed from the missing keys.
        """
        not_defined = {key for key in all_keys if self.find_key(key) is None}
        if not top_level:
            return not_defined
        return {key.split("/")[-1] for key in not_defined}

    def split(self) -> Tuple["Placeholders", "Placeholders"]:
        """Split all placeholders into those with a single value or those with multiple values.

        Placeholders are considered to have multiple values if they are equivalent to 1D-arrays (lists, tuples, 1D ndarray, etc.).
        Anything else is considered a single value (string, int, float, etc.).

        Returns:
            Tuple with two dictionaries:

                1. placeholders with single values
                2. placehodlers with multiple values
        """
        single_placeholders = Placeholders()
        multi_placeholders = Placeholders()
        for name, value in self.mapping.items():
            if isinstance(name, frozenset) or not is_singular(value):
                multi_placeholders[name] = value
            else:
                single_placeholders[name] = value
        return single_placeholders, multi_placeholders

    def iter_over(self, keys) -> Generator["Placeholders", None, None]:
        """Iterate over the placeholder names.

        Args:
            keys (Sequence[str]): sequence of placeholder names to iterate over

        Raises:
            KeyError: Raised if any of the provided `keys` does not have any value.

        Yields:
            yield Placeholders object, where each of the listed keys only has a single possible value
        """
        actual_keys = [self.linkages.get(self.find_key(key), key) for key in keys]
        unfilled = {orig for orig, key in zip(keys, actual_keys) if key is None}
        if len(unfilled) > 0:
            raise KeyError(f"Can not iterate over undefined placeholders: {unfilled}")

        unique_keys = []
        iter_values = {}
        for key in actual_keys:
            if key not in unique_keys:
                if isinstance(key, frozenset):  # linked placeholder
                    unique_keys.append(key)
                    iter_values[key] = [
                        {k: self[k][idx] for k in key}
                        for idx in range(len(self[list(key)[0]]))
                    ]
                elif not is_singular(self[key]):  # iterable placeholder
                    unique_keys.append(key)
                    iter_values[key] = self[key]

        for values in product(*[iter_values[k] for k in unique_keys]):
            new_vars = Placeholders(self)
            for key, value in zip(unique_keys, values):
                if isinstance(key, frozenset):
                    del new_vars[key]  # break the placeholders link
                    new_vars.update(value)
                else:
                    new_vars[key] = value
            yield new_vars

    def link(self, *keys):
        """
        Link the placeholders represented by `keys`.

        When iterating over linked placeholders the i-th tree
        will contain the i-th element from all linked placeholders,
        instead of the tree containing all possible combinations of placeholder values.

        This can be thought of using `zip` for linked variables and
        `itertools.product` for unlinked ones.
        """
        actual_keys = set()
        for key in keys:
            if key in self.linkages:
                actual_keys.update(self.linkages[key])
            else:
                actual_keys.add(key)
        self[frozenset(actual_keys)] = {key: self[key] for key in actual_keys}

    def unlink(self, *keys):
        """
        Unlink the placeholders represented by `keys`.

        See :meth:`link` for how linking affects the iteration
        through placeholders with multiple values.

        Raises a ValueError if the placeholders are not actually linked.
        """
        if keys not in self:
            raise ValueError(f"{keys} were not linked, so cannot unlink them")
        new_vars = {k: self[k] for k in keys}
        del self[keys]
        self.update(new_vars)

    def to_string(
        self,
    ):
        """Convert the placeholders to a string representation."""
        lines = []
        all_keys = sorted(
            [
                *self.linkages.keys(),
                *[k for k in self.mapping.keys() if not isinstance(k, frozenset)],
            ]
        )
        for key in sorted(all_keys):
            value = self[key]
            if value is None:
                continue
            if np.array(value).ndim == 1:
                lines.append(f"{key} = {', '.join([str(v) for v in value])}")
            else:
                lines.append(f"{key} = {value}")
        for key in self.mapping.keys():
            if isinstance(key, frozenset):
                lines.append(f"&LINK {', '.join(sorted(key))}")
        return "\n".join(lines)


class MyDataArray:
    """Wrapper around xarray.DataArray for internal usage.

    It tries to delay creating the DataArray object as long as possible
    (as using them for small arrays is slow...).
    """

    def __init__(self, data, coords=None):
        """Create a new DataArray look-a-like."""
        self.as_xarray = coords is None
        if self.as_xarray:
            assert isinstance(data, xarray.DataArray)
            self.data_array = data
        else:
            self.data = data
            self.coords = coords

    def map(self, func) -> "MyDataArray":
        """Apply `func` to each element of array."""
        if self.as_xarray:
            return MyDataArray(
                xarray.apply_ufunc(func, self.data_array, vectorize=True)
            )
        else:
            return MyDataArray(
                np.array([func(d) for d in self.data.flat]).reshape(self.data.shape),
                self.coords,
            )

    def to_xarray(
        self,
    ) -> xarray.DataArray:
        """Convert to a real xarray.DataArray."""
        if self.as_xarray:
            return self.data_array
        else:
            return xarray.DataArray(
                self.data, [_to_index(name, values) for name, values in self.coords]
            )

    @staticmethod
    def concat(parts, new_index) -> "MyDataArray":
        """Combine multiple DataArrays."""
        if len(parts) == 0:
            return MyDataArray(np.array([]), [])
        to_xarray = any(p.as_xarray for p in parts) or any(
            len(p.coords) != len(parts[0].coords)
            or any(
                np.all(name1 != name2)
                for (name1, _), (name2, _) in zip(p.coords, parts[0].coords)
            )
            for p in parts
        )
        if to_xarray:
            return MyDataArray(
                xarray.concat([p.to_xarray() for p in parts], _to_index(*new_index))
            )
        else:
            new_data = np.stack([p.data for p in parts], axis=0)
            new_coords = list(parts[0].coords)
            new_coords.insert(0, new_index)
            return MyDataArray(new_data, new_coords)


def _to_index(name, values):
    """Convert to index for MyDataArray."""
    if isinstance(name, str):
        return pd.Index(values, name=name)
    else:
        return ("-".join(sorted(name)), pd.MultiIndex.from_tuples(values, names=name))


class Template:
    """Represents a single template in the FileTree."""

    def __init__(self, parent: Optional["Template"], unique_part: str):
        """Create a new child template in `parent` directory with `unique_part` filename."""
        self.parent = parent
        self.unique_part = unique_part

    @property
    def as_path(self) -> Path:
        """Return the full path with no placeholders filled in."""
        if self.parent is None:
            return Path(self.unique_part)
        return self.parent.as_path.joinpath(self.unique_part)

    @property
    def as_string(self):
        """Return the full path with no placeholders filled in."""
        if self.parent is None:
            return str(self.unique_part)
        return os.path.join(self.parent.as_string, str(self.unique_part))

    def __str__(self):
        """Return string representation of template."""
        return f"Template({self.as_string})"

    def children(self, templates: Iterable["Template"]) -> List["Template"]:
        """Find children from a sequence of templates.

        Args:
            templates: sequence of possible child templates.

        Returns:
            list of children templates
        """
        res = []

        def add_if_child(possible_child):
            if isinstance(possible_child, DuplicateTemplate):
                for t in possible_child.templates:
                    add_if_child(t)
            elif possible_child.parent is self and possible_child not in res:
                res.append(possible_child)

        for t in templates:
            add_if_child(t)
        return sorted(res, key=lambda t: t.unique_part)

    def as_multi_line(
        self, other_templates: Dict["Template", Set[str]], indentation=4
    ) -> str:
        """Generate a string describing this and any child templates.

        Args:
            other_templates (Dict[Template, Set[str]]):
                templates including all the child templates and itself.
            indentation (int, optional):
                number of spaces to use as indentation. Defaults to 4.

        Returns:
            str: multi-line string that can be processed by :meth:`file_tree.FileTree.read`
        """
        result = self._as_multi_line_helper(other_templates, indentation)

        is_top_level = "" in other_templates[self]
        if not is_top_level and self.parent is None:
            return "!" + result
        else:
            return result

    def _as_multi_line_helper(
        self,
        other_templates: Dict["Template", Set[str]],
        indentation=4,
        _current_indentation=0,
    ) -> str:
        leaves = []
        branches = []
        for t in sorted(
            self.children(other_templates.keys()), key=lambda t: t.unique_part
        ):
            if len(t.children(other_templates.keys())) == 0:
                leaves.append(t)
            else:
                branches.append(t)

        is_top_level = "" in other_templates[self]
        if is_top_level:
            base_line = "."
            assert _current_indentation == 0 and self.parent is None
            _current_indentation = -indentation
        else:
            base_line = _current_indentation * " " + self.unique_part

        all_keys = set(other_templates[self])
        if is_top_level and all_keys == {""}:
            lines = []
        elif len(all_keys) == 1 and list(all_keys)[0] == self.guess_key():
            lines = [base_line]
        else:
            if is_top_level:
                all_keys.remove("")
            lines = [base_line + f" ({','.join(sorted(all_keys))})"]

        already_done = set()
        for t in leaves + branches:
            if t not in already_done:
                lines.append(
                    t._as_multi_line_helper(
                        other_templates, indentation, indentation + _current_indentation
                    )
                )
                already_done.add(t)
        return "\n".join(lines)

    @property
    def _parts(
        self,
    ):
        return TemplateParts.parse(self.as_string)

    def placeholders(self, valid=None) -> List[str]:
        """Return a list of the placeholder names.

        Args:
            valid: Collection of valid placeholder names.
                An error is raised if any other placeholder is detected.
                By default all placeholder names are fine.

        Returns:
            List[str]: placeholder names in order that they appear in the template
        """
        return self._parts.ordered_placeholders(valid)

    def format_single(
        self, placeholders: Placeholders, check=True, keep_optionals=False, glob=True
    ) -> str:
        """Format the template with the placeholders filled in.

        Only placeholders with a single value are considered.

        Args:
            placeholders (Placeholders): values to fill into the placeholder
            check (bool): check for missing placeholders if set to True
            keep_optionals: if True keep optional parameters that have not been set (will cause the check to fail)
            glob: setting for pattern matching

        Raises:
            KeyError: if any placeholder is missing

        Returns:
            str: filled in template
        """
        single_placeholders, _ = placeholders.split()
        template = self._parts.fill_single_placeholders(single_placeholders)
        if not keep_optionals:
            template = template.remove_optionals()
        if check:
            unfilled = template.required_placeholders()
            if len(unfilled) > 0:
                raise KeyError(f"Missing placeholder values for {unfilled}")
        return pattern_match(str(template), glob)

    def format_mult(
        self,
        placeholders: Placeholders,
        check=False,
        filter=False,
        matches=None,
        glob=False,
    ) -> xarray.DataArray:
        """Replace placeholders in template with the provided placeholder values.

        Args:
            placeholders: mapping from placeholder names to single or multiple vaalues
            check: skip check for missing placeholders if set to True
            filter: filter out non-existing files if set to True
            matches: Optional pre-generated list of any matches to the template.
            glob: keyword determining the pattern matching behaviour

        Raises:
            KeyError: if any placeholder is missing

        Returns:
            xarray.DataArray: array with possible resolved paths.
                If `filter` is set to True the non-existent paths are replaced by None
        """
        parts = self._parts
        resolved = parts.resolve(placeholders)
        if check:
            for template in resolved.data.flatten():
                unfilled = template.required_placeholders()
                if len(unfilled) > 0:
                    raise KeyError(f"Missing placeholder values for {unfilled}")

        def _match_single(t):
            try:
                return pattern_match(str(t), glob)
            except FileNotFoundError:
                if filter:
                    return ""
                raise

        paths = resolved.map(_match_single)
        if not filter:
            return paths.to_xarray()
        placeholder_dict = dict(placeholders)
        path_matches = [
            str(
                parts.fill_single_placeholders(
                    Placeholders({**placeholder_dict, **match})
                ).remove_optionals()
            )
            for match in (
                self.all_matches(placeholders) if matches is None else matches
            )
        ]
        return paths.map(
            lambda p: (
                p
                if any(
                    (fnmatch(p, m) if is_glob_pattern(m) else p == m)
                    for m in path_matches
                )
                else ""
            )
        ).to_xarray()

    def optional_placeholders(
        self,
    ) -> Set[str]:
        """Find all placeholders that are only within optional blocks (i.e., they do not require a value).

        Returns:
            Set[str]: names of optional placeholders
        """
        return self._parts.optional_placeholders()

    def required_placeholders(
        self,
    ) -> Set[str]:
        """Find all placeholders that are outside of optional blocks (i.e., they do require a value).

        Returns:
            Set[str]: names of required placeholders
        """
        return self._parts.required_placeholders()

    def guess_key(
        self,
    ) -> str:
        """Propose a short name for the template.

        The proposed short name is created by:

            - taking the basename (i.e., last component) of the path
            - removing the first '.' and everything beyond (to remove the extension)

        .. warning::

            If there are multiple dots within the path's basename,
            this might remove far more than just the extension.

        Returns:
            str: proposed short name for this template (used if user does not provide one)
        """
        parts = self.as_path.parts
        if len(parts) == 0:
            return ""
        else:
            return parts[-1].split(".")[0]

    def add_precursor(self, text) -> "Template":
        """Return a new Template with any placeholder names in the unique part now preceded by `text`.

        Used for adding sub-trees
        """
        parts = TemplateParts.parse(self.unique_part).parts
        updated = "".join([str(p.add_precursor(text)) for p in parts])
        return Template(self.parent, updated)

    def get_all_placeholders(
        self, placeholders: Placeholders, link=None, return_matches=False
    ) -> Placeholders:
        """Fill placeholders with possible values based on what is available on disk.

        Args:
            placeholders: New values for undefined placeholders in template.
            link: template keys that should be linked together in the output.
            return_matches: if True, also returns any matches to the template, which can be passed on to `format_mult`.

        Returns:
            Set of placeholders updated based on filed existing on disk that match this template.
        """
        if link is None:
            link = []
        elif len(link) > 0 and isinstance(link[0], str):
            link = [link]
        # link is now a sequence of sequence of strings

        all_to_link = [name for single in link for name in single]
        template_keys = {
            *self.optional_placeholders(),
            *self.required_placeholders(),
        }

        undefined = set()
        placeholder_with_linked = placeholders.copy()
        for name in all_to_link:
            if placeholder_with_linked.find_key(name) is None:
                placeholder_with_linked[name] = ""
                undefined.add(name)
        undefined.update(placeholders.missing_keys(template_keys))

        matches = self.all_matches(placeholders, undefined)

        undefined_values = defaultdict(set)
        for match in matches:
            for name, value in match.items():
                if placeholders.find_key(name) is None and name not in all_to_link:
                    undefined_values[name].add(value)

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

        res = Placeholders(
            {k: sorted(v, key=cmp_to_key(cmp)) for k, v in undefined_values.items()}
        )
        for to_link in link:
            res[tuple(to_link)] = list(
                zip(
                    *sorted(
                        {
                            tuple(Placeholders(match).get(key, None) for key in to_link)
                            for match in matches
                        }
                    )
                )
            )
        if return_matches:
            return (res, matches)
        return res

    def all_matches(
        self, placeholders: Placeholders, keys_to_fill: Optional[Collection[str]] = None
    ) -> List[Dict[str, Any]]:
        """Return a sequence of all possible variable values for `keys_to_fill` matching existing files on disk.

        Only variable values matching existing placeholder values (in `placeholders`) are returned
        (undefined placeholders are unconstrained).
        """
        if keys_to_fill is None:
            keys_to_fill = placeholders.missing_keys(
                {
                    *self.required_placeholders(),
                    *self.optional_placeholders(),
                }
            )

        single_vars, multi_vars = placeholders.split()
        res = []

        def check_name_with_edit(match, name):
            value = match[name]
            if name in single_vars and single_vars.find_key(name) == name:
                return value == single_vars[name]
            if name in multi_vars and multi_vars.find_key(name) == name:
                return value in multi_vars[name]
            if name in keys_to_fill:
                return True
            del match[name]
            _, *parts = name.split("/")
            parent_name = "/".join(parts)
            if parent_name in match:
                return match[parent_name] == value
            match[parent_name] = value
            return check_name_with_edit(match, parent_name)

        for match in self._parts.fill_single_placeholders(single_vars).all_matches(
            multi_vars
        ):
            match.update(single_vars)
            if not all(
                check_name_with_edit(match, name) for name in list(match.keys())
            ):
                continue
            res.append(match)
        return res

    def rich_line(self, all_keys):
        """Produce a line for rendering using rich."""
        keys = all_keys[self]
        base = self.guess_key()
        unique_part = str(self.unique_part)
        if base in keys:
            keys.remove(base)
            unique_part = str.replace(unique_part, base, f"[cyan]{base}[/cyan]")
            if len(keys) == 0:
                return unique_part
        return (
            unique_part
            + " ("
            + ", ".join("[cyan]" + key + "[/cyan]" for key in sorted(keys))
            + ")"
        )


class DuplicateTemplate:
    """Represents the case where a single key points to multiple templates."""

    def __init__(self, *templates: Template):
        """Create a new DuplicateTemplate with the provided templates."""
        self._templates = list(templates)

    def add_template(self, template: Template):
        """Add another conflicting template."""
        self._templates.append(template)

    @property
    def templates(
        self,
    ):
        """Return the list of templates matching the given key."""
        return tuple(self._templates)


def extract_placeholders(template, filename, known_vars=None):
    """
    Extract the placeholder values from the filename.

    :param template: template matching the given filename
    :param filename: filename
    :param known_vars: already known placeholders
    :return: dictionary from placeholder names to string representations
        (unused placeholders set to None)
    """
    return TemplateParts.parse(template).extract_placeholders(filename, known_vars)


class Part:
    """
    Individual part of a template.

    3 subclasses are defined:

        - :class:`Literal`:
            piece of text
        - :class:`Required`:
            required placeholder to fill in
            (between curly brackets)
        - :class:`OptionalPart`:
            part of text containing optional placeholders
            (between square brackets)
    """

    def fill_single_placeholders(
        self, placeholders: Placeholders, ignore_type=False
    ) -> Sequence["Part"]:
        """Fill in the given placeholders."""
        return (self,)

    def optional_placeholders(
        self,
    ) -> Set[str]:
        """Return all placeholders in optional parts."""
        return set()

    def required_placeholders(
        self,
    ) -> Set[str]:
        """Return all required placeholders."""
        return set()

    def contains_optionals(self, placeholders: Optional[Set["Part"]] = None):
        """Return True if this part contains the optional placeholders."""
        return False

    def append_placeholders(self, placeholders: List[str], valid=None):
        """Append the placeholders in this part to the provided list in order."""
        pass

    def add_precursor(self, text: str) -> "Part":
        """Prepend any placeholder names by `text`."""
        return self

    def for_defined(self, placeholder_names: Set[str]) -> List["Part"]:
        """Return the template string assuming the placeholders in `placeholder_names` are defined.

        Removes any optional parts, whose placeholders are not in `placeholder_names`.
        """
        return [self]

    def remove_precursors(self, placeholders=None):
        """Remove precursor from placeholder key."""
        return self


class Literal(Part):
    """Piece of text in template without placeholders."""

    def __init__(self, text: str):
        """
        Literal part is defined purely by the text it contains.

        :param text: part of the template
        """
        self.text = text

    def __str__(self):
        """Return this part of the template as a string."""
        return self.text

    def __eq__(self, other):
        """Check if text matches other `Literal`."""
        if not isinstance(other, Literal):
            return NotImplemented
        return self.text == other.text


class Required(Part):
    """Placeholder part of template that requires a value."""

    def __init__(self, var_name, var_formatting=None):
        """
        Create required part of template (between curly brackets).

        Required placeholder part of template is defined by placeholder name and its format

        :param var_name: name of placeholder
        :param var_formatting: how to format the placeholder
        """
        self.var_name = var_name
        self.var_formatting = var_formatting

    def __str__(self):
        """Return this part of the template as a string."""
        if self.var_formatting is None or len(self.var_formatting) == 0:
            return "{" + self.var_name + "}"
        else:
            return "{" + self.var_name + ":" + self.var_formatting + "}"

    def fill_single_placeholders(self, placeholders: Placeholders, ignore_type=False):
        """Fill placeholder values into template obeying typing."""
        value = placeholders.get(self.var_name, None)
        if value is None:
            return (self,)
        else:
            if not ignore_type and len(self.var_formatting) > 0:
                format_type = extract_format(self.var_formatting, [])["type"]
                if format_type in list(r"dnbox"):
                    value = int(value)
                elif format_type in list(r"f%eg"):
                    value = float(value)
                elif format_type in ["t" + ft for ft in "iegachs"] and isinstance(
                    value, str
                ):
                    from dateutil import parser

                    value = parser(value)
            res = TemplateParts.parse(
                format(value, "" if ignore_type else self.var_formatting)
            )
            if len(res.parts) == 1:
                return res.parts
            return res.fill_single_placeholders(
                placeholders, ignore_type=ignore_type
            ).parts

    def required_placeholders(
        self,
    ):
        """Return variable names."""
        return {self.var_name}

    def append_placeholders(self, placeholders, valid=None):
        """Add placeholder name to list of placeholders in template."""
        if valid is not None and self.var_name not in valid:
            raise ValueError(f"Placeholder {self.var_name} is not defined")
        placeholders.append(self.var_name)

    def add_precursor(self, text: str) -> "Required":
        """Prepend any placeholder names by `text`."""
        return Required(text + self.var_name, self.var_formatting)

    def remove_precursors(self, placeholders=None):
        """Remove precursor from placeholder key."""
        if placeholders is None:
            new_name = self.var_name.split("/")[-1]
        else:
            key = placeholders.find_key(self.var_name)
            new_name = self.var_name if key is None else key
        return Required(new_name, self.var_formatting)

    def __eq__(self, other):
        """Check whether `other` placeholder matches this one."""
        if not isinstance(other, Required):
            return NotImplemented
        return (self.var_name == other.var_name) & (
            self.var_formatting == other.var_formatting
        )


class OptionalPart(Part):
    """Optional part of a template (i.e., between square brackets)."""

    def __init__(self, sub_template: "TemplateParts"):
        """
        Create optional part of template (between square brackets).

        Optional part can contain literal and required parts

        :param sub_template: part of the template within square brackets
        """
        self.sub_template = sub_template

    def __str__(self):
        """Return string representation of optional part."""
        return "[" + str(self.sub_template) + "]"

    def fill_single_placeholders(self, placeholders: Placeholders, ignore_type=False):
        """Fill placeholders into text within optional part."""
        new_opt = self.sub_template.fill_single_placeholders(
            placeholders, ignore_type=ignore_type
        )
        if len(new_opt.required_placeholders()) == 0:
            return (Literal(str(new_opt)),)
        return (OptionalPart(new_opt),)

    def optional_placeholders(self):
        """Return sequence of any placeholders in the optional part of the template."""
        return self.sub_template.required_placeholders()

    def contains_optionals(self, placeholders=None):
        """Check if this optional part contains any placeholders not listed in `placeholders`."""
        if placeholders is None and len(self.optional_placeholders()) > 0:
            return True
        return len(self.optional_placeholders().intersection(placeholders)) > 0

    def append_placeholders(self, placeholders, valid=None):
        """Add any placeholders in the optional part to `placeholders` list."""
        try:
            placeholders.extend(self.sub_template.ordered_placeholders(valid=valid))
        except ValueError:
            pass

    def add_precursor(self, text: str) -> "OptionalPart":
        """Prepend precursor `text` to any placeholders in the optional part."""
        return OptionalPart(
            TemplateParts([p.add_precursor(text) for p in self.sub_template.parts])
        )

    def for_defined(self, placeholder_names: Set[str]) -> List["Part"]:
        """
        Return the template string assuming the placeholders in `placeholder_names` are defined.

        Removes any optional parts, whose placeholders are not in `placeholder_names`.
        """
        if len(self.optional_placeholders().difference(placeholder_names)) > 0:
            return []
        return list(self.sub_template.parts)

    def remove_precursors(self, placeholders=None):
        """Remove precursor from placeholder key."""
        return OptionalPart(self.sub_template.remove_precursors(placeholders))

    def __eq__(self, other):
        """Check whether two optional parts match."""
        if not isinstance(other, OptionalPart):
            return NotImplemented
        return self.sub_template == other.sub_template


class TemplateParts:
    """Representation of full template as sequence of `Part` objects."""

    optional_re = re.compile(r"(\[.*?\])")
    requires_re = re.compile(r"(\{.*?\})")

    def __init__(self, parts: Sequence[Part]):
        """Create new TemplateParts based on sequence."""
        if isinstance(parts, str):
            raise ValueError(
                "Input to Template should be a sequence of parts; "
                + "did you mean to call `TemplateParts.parse` instead?"
            )
        self.parts = tuple(parts)

    @staticmethod
    @lru_cache(1000)
    def parse(text: str) -> "TemplateParts":
        """Parse a template string into its constituent parts.

        Args:
            text: template as string.

        Raises:
            ValueError: raised if a parsing error is

        Returns:
            TemplateParts: object that contains the parts of the template
        """
        parts: List[Part] = []
        for optional_parts in TemplateParts.optional_re.split(text):
            if (
                len(optional_parts) > 0
                and optional_parts[0] == "["
                and optional_parts[-1] == "]"
            ):
                if "[" in optional_parts[1:-1] or "]" in optional_parts[1:-1]:
                    raise ValueError(
                        f"Can not parse {text}, because unmatching square brackets were found"
                    )
                parts.append(OptionalPart(TemplateParts.parse(optional_parts[1:-1])))
            else:
                for required_parts in TemplateParts.requires_re.split(optional_parts):
                    if (
                        len(required_parts) > 0
                        and required_parts[0] == "{"
                        and required_parts[-1] == "}"
                    ):
                        if ":" in required_parts:
                            var_name, var_type = required_parts[1:-1].split(":")
                        else:
                            var_name, var_type = required_parts[1:-1], ""
                        parts.append(Required(var_name, var_type))
                    else:
                        parts.append(Literal(required_parts))
        return TemplateParts(parts)

    def __str__(self):
        """Return the template as a string."""
        return os.path.normpath("".join([str(p) for p in self.parts]))

    def optional_placeholders(
        self,
    ) -> Set[str]:
        """Set of optional placeholders."""
        if len(self.parts) == 0:
            return set()
        optionals = set.union(*[p.optional_placeholders() for p in self.parts])
        return optionals.difference(self.required_placeholders())

    def required_placeholders(
        self,
    ) -> Set[str]:
        """Set of required placeholders."""
        if len(self.parts) == 0:
            return set()
        return set.union(*[p.required_placeholders() for p in self.parts])

    def ordered_placeholders(self, valid=None) -> List[str]:
        """Sequence of all placeholders in order (can contain duplicates)."""
        ordered_vars: List[str] = []
        for p in self.parts:
            p.append_placeholders(ordered_vars, valid=valid)
        return ordered_vars

    def fill_known(self, placeholders: Placeholders, ignore_type=False) -> MyDataArray:
        """Fill in the known placeholders.

        Any optional parts, where all placeholders have been filled
        will be automatically replaced.
        """
        single, multi = placeholders.split()
        return self.remove_precursors(placeholders)._fill_known_helper(
            single, multi, ignore_type=ignore_type
        )

    def _fill_known_helper(
        self, single: Placeholders, multi: Placeholders, ignore_type=False
    ) -> MyDataArray:
        """Do work for `fill_known`."""
        new_template = self.fill_single_placeholders(single, ignore_type=ignore_type)
        for name in new_template.ordered_placeholders():
            use_name = multi.find_key(name)
            if use_name is None:
                continue
            new_multi = multi.copy()
            if use_name in multi.linkages:
                values = multi[multi.linkages[use_name]]
                keys = tuple(sorted(values.keys()))
                index = (keys, zip(*[values[k] for k in keys]))
                del new_multi[new_multi.linkages[use_name]]
            else:
                values = {use_name: list(multi[name])}
                index = (use_name, values[use_name])
                del new_multi[use_name]
            assert use_name is not None

            parts = []
            new_single = single.copy()
            for idx in range(len(values[use_name])):
                new_vals = {n: v[idx] for n, v in values.items()}
                new_single.mapping.update(new_vals)
                parts.append(
                    new_template._fill_known_helper(
                        new_single, new_multi, ignore_type=ignore_type
                    )
                )

            return MyDataArray.concat(parts, index)
        return MyDataArray(np.array(new_template), [])

    def fill_single_placeholders(
        self, placeholders: Placeholders, ignore_type=False
    ) -> "TemplateParts":
        """
        Fill in placeholders with singular values.

        Assumes that all placeholders are in fact singular.
        """
        res = [
            p.fill_single_placeholders(placeholders, ignore_type=ignore_type)
            for p in self.parts
        ]
        return TemplateParts(list(chain(*res)))

    def remove_optionals(self, optionals=None) -> "TemplateParts":
        """
        Remove any optionals containing the provided placeholders.

        By default all optionals are removed.
        """
        return TemplateParts(
            [p for p in self.parts if not p.contains_optionals(optionals)]
        )

    def all_matches(self, placeholders_values: Placeholders) -> List[Dict[str, Any]]:
        """Find all potential matches to existing templates.

        It accepts a list of placeholders that have multiple possible values.

        Returns a list with the possible combination of values for the placeholders.
        """
        required = self.required_placeholders()
        optional = self.optional_placeholders()
        matches = []
        already_globbed = {}

        fill_keys = [
            key
            for key in [*required, *optional]
            if (
                key in placeholders_values
                and any(os.path.sep in str(value) for value in placeholders_values[key])
            )
        ]
        for all_iter in placeholders_values.iter_over(fill_keys):
            already_filled, _ = all_iter.split()

            for defined_optionals in [
                c for n in range(len(optional) + 1) for c in combinations(optional, n)
            ]:
                glob_placeholders = Placeholders(
                    **{req: "*" for req in required},
                    **{opt: "*" for opt in defined_optionals},
                )
                glob_placeholders.update(already_filled)
                new_glob = str(
                    self.fill_single_placeholders(
                        glob_placeholders, ignore_type=True
                    ).remove_optionals()
                )
                while "**" in new_glob:
                    new_glob = new_glob.replace("**", "*")
                if new_glob not in already_globbed:
                    already_globbed[new_glob] = glob(new_glob)
                res = []
                vars = required.union(defined_optionals)
                for p in self.fill_single_placeholders(already_filled).parts:
                    res.extend(p.for_defined(vars))
                parser = TemplateParts(res).get_parser()
                for fn in already_globbed[new_glob]:
                    try:
                        placeholders = parser(fn)
                    except ValueError:
                        continue
                    placeholders.update(already_filled)
                    for var_name in optional:
                        if var_name not in placeholders:
                            placeholders[var_name] = None
                    matches.append(placeholders)
        return matches

    def resolve(self, placeholders, ignore_type=False) -> MyDataArray:
        """
        Resolve the template given a set of placeholders.

        :param placeholders: mapping of placeholder names to values
        :param ignore_type: if True, ignore the type formatting when
                            filling in placeholders
        :return: cleaned string
        """
        return self.fill_known(placeholders, ignore_type=ignore_type).map(
            lambda t: t.remove_optionals()
        )

    def optional_subsets(
        self,
    ) -> Iterator["TemplateParts"]:
        """Yield template sub-sets with every combination optional placeholders."""
        optionals = self.optional_placeholders()
        for n_optional in range(len(optionals) + 1):
            for exclude_optional in itertools.combinations(optionals, n_optional):
                yield self.remove_optionals(exclude_optional)

    def extract_placeholders(self, filename, known_vars=None):
        """
        Extract the placeholder values from the filename.

        :param filename: filename
        :param known_vars: already known placeholders
        :return: dictionary from placeholder names to string representations
                 (unused placeholders set to None)
        """
        if known_vars is not None:
            template = self.fill_known(known_vars)
        else:
            template = self
        while "//" in filename:
            filename = filename.replace("//", "/")

        required = template.required_placeholders()
        optional = template.optional_placeholders()
        results = []
        for to_fill in template.optional_subsets():
            sub_re = str(
                to_fill.fill_known(
                    {var: r"(\S+)" for var in required.union(optional)},
                )
            )
            while "//" in sub_re:
                sub_re = sub_re.replace("//", "/")
            sub_re = sub_re.replace(".", r"\.")
            match = re.match(sub_re, filename)
            if match is None:
                continue

            extracted_value = {}
            ordered_vars = to_fill.ordered_placeholders()
            assert len(ordered_vars) == len(match.groups())

            failed = False
            for var, value in zip(ordered_vars, match.groups()):
                if var in extracted_value:
                    if value != extracted_value[var]:
                        failed = True
                        break
                else:
                    extracted_value[var] = value
            if failed or any("/" in value for value in extracted_value.values()):
                continue
            for name in template.optional_placeholders():
                if name not in extracted_value:
                    extracted_value[name] = None
            if known_vars is not None:
                extracted_value.update(known_vars)
            results.append(extracted_value)
        if len(results) == 0:
            raise ValueError("{} did not match {}".format(filename, template))

        def score(placeholders):
            """
            Assign score to possible reconstructions of the placeholder values.

            The highest score is given to the set of placeholders that:

                1. has used the largest amount of optional placeholders
                2. has the shortest text within the placeholders (only used if equal at 1
            """
            number_used = len([v for v in placeholders.values() if v is not None])
            length_hint = sum([len(v) for v in placeholders.values() if v is not None])
            return number_used * 1000 - length_hint

        best = max(results, key=score)
        for var in results:
            if best != var and score(best) == score(var):
                raise KeyError(
                    "Multiple equivalent ways found to parse {} using {}".format(
                        filename, template
                    )
                )
        return best

    def get_parser(self):
        """Create function that will parse a filename based on this template."""
        if any(isinstance(p, OptionalPart) for p in self.parts):
            raise ValueError(
                "Can not parse filename when there are optional parts in the template"
            )
        mapping = {
            old_key: "".join(new_key)
            for old_key, new_key in zip(
                self.required_placeholders(),
                itertools.product(*[string.ascii_letters] * 3),
            )
        }
        reverse = {new_key: old_key for old_key, new_key in mapping.items()}
        cleaned = str(
            TemplateParts(
                [
                    (
                        Required(mapping[p.var_name], p.var_formatting)
                        if isinstance(p, Required)
                        else p
                    )
                    for p in self.parts
                ]
            )
        ).replace("?", "{:1}")

        if is_glob_pattern(cleaned):
            nreplace = cleaned.count("*")
            parsers = []

            for replace_with in product(*([["", "{}"]] * nreplace)):
                this_string = cleaned
                for r in replace_with:
                    this_string = this_string.replace("*", r, 1)
                parsers.append(compile(this_string, case_sensitive=True).parse)

            def parser(filename):
                for p in parsers:
                    result = p(filename)
                    if result is not None:
                        return result
                return None

        else:
            parser = compile(cleaned, case_sensitive=True).parse

        def parse_filename(filename):
            """Parse filename based on template."""
            result = parser(filename)
            if result is None:
                raise ValueError(
                    f"template string ({str(self)}) does not mach filename ({filename})"
                )
            named = result.named
            if any(isinstance(value, str) and "/" in value for value in named.values()):
                raise ValueError("Placeholder can not span directories")
            return {reverse[key]: value for key, value in named.items()}

        return parse_filename

    def remove_precursors(self, placeholders=None):
        """Replace keys to those existing in the placeholders.

        If no placeholders provided all precursors are removed.
        """
        return TemplateParts([p.remove_precursors(placeholders) for p in self.parts])

    def __eq__(self, other):
        """Check whether other template matches this one."""
        if not isinstance(other, TemplateParts):
            return NotImplemented
        return (len(self.parts) == len(other.parts)) and all(
            p1 == p2 for p1, p2 in zip(self.parts, other.parts)
        )


def is_glob_pattern(path):
    """Check if the given path is a glob-like pattern."""
    return "*" in path or "?" in path


def pattern_match(path, glob_cmd):
    """
    Apply glob-like pattern matching to given `path`.

    The `path` will be returned directly if `path` does not contain any `*`, `?`, or `[]` or `glob_cmd` is False.
    Otherwise pattern matching using the python `glob` library is used.
    """
    if not (glob_cmd and is_glob_pattern(path)):
        return path

    matches = sorted(glob(path))
    if callable(glob_cmd):
        try:
            res = glob_cmd(matches)
        except Exception:
            if len(matches) == 0:
                raise FileNotFoundError(
                    f"No file was found to match pattern `{path}`. The `FileTree.glob` function raised the underlying error."
                )
            if len(matches) > 1:
                raise FileNotFoundError(
                    f"Multiple ({len(matches)}) files were found to match pattern `{path}`. The `FileTree.glob` function raised the underlying error."
                )
            raise
        if not isinstance(res, str):
            raise ValueError(
                f"The `FileTree.glob` function should return a single path as a string, not `{res}`."
            )
        return res
    else:
        if len(matches) == 0:
            raise FileNotFoundError(
                f"No file was found to match pattern `{path}`. Set `FileTree.glob` to False to return the pattern rather than a file matching the pattern."
            )
        if glob_cmd in (True, "default"):
            if len(matches) > 1:
                raise FileNotFoundError(
                    f"Multiple ({len(matches)}) files were found to match pattern `{path}`. Set `FileTree.glob` to False to return the pattern rather than a file matching the pattern. You can also set it to 'first' or 'last' to get the first or last match."
                )
            return matches[0]
        elif glob_cmd == "first":
            return matches[0]
        elif glob_cmd == "last":
            return matches[-1]
        raise ValueError(
            "`FileTree.glob` should be set to callable or one of `False`, `True`, 'default', 'first', or 'last'. Invalid value of `{glob_cmd}` given."
        )
