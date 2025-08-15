import os
from collections import Counter, defaultdict
from collections.abc import Callable, Iterable, Mapping
from typing import TYPE_CHECKING, TypeAlias, cast

import polars as pl
from typing_extensions import TypeAliasType

if TYPE_CHECKING:
    Hierarchy: TypeAlias = "list[str] | Mapping[str, Hierarchy]"
else:
    Hierarchy = TypeAliasType("Hierarchy", list[str] | Mapping[str, "Hierarchy"])


def check_unique_hierarchy(
    v: Mapping[str, Mapping[str, Hierarchy]],
) -> Mapping[str, Mapping[str, Hierarchy]]:
    errors = []
    for hierarchy_name, hierarchy in v.items():
        flat_hierarchy = flatten(hierarchy)
        dupes = [item for item, count in Counter(flat_hierarchy).items() if count > 1]

        if dupes:
            errors.append(
                f"""
                There are duplicate elements in hierarchy {hierarchy_name}:
                {', '.join(dupes)}
                """,
            )
    if errors:
        raise ValueError(os.linesep.join(errors))
    else:
        return v


def check_nonempty_hierarchy(
    v: Mapping[str, Mapping[str, Hierarchy]],
) -> Mapping[str, Mapping[str, Hierarchy]]:
    errors = []
    if len(v) == 0:
        errors.append("Hierarchy cannot be empty.")
    else:
        for hierarchy_name, hierarchy in v.items():
            if len(hierarchy) == 0:
                errors.append(f"Hierarchy {hierarchy_name} cannot be empty.")

    if errors:
        raise ValueError(os.linesep.join(errors))
    else:
        return v


def check_all_codes_have_labels(
    hierarchies: Mapping[str, Hierarchy],
    labels: Mapping[str, Mapping[str, str]],
) -> list[str]:
    missing_hierarchies = []
    missing_codes = defaultdict(list)
    extra_codes = defaultdict(list)

    for hierarchy_name, hierarchy in hierarchies.items():
        if hierarchy_name not in labels:
            missing_hierarchies.append(hierarchy_name)
            break

        all_codes = set(flatten(hierarchy))
        all_label_codes = set(labels[hierarchy_name].keys())
        missing_codes[hierarchy_name].extend(list(all_codes - all_label_codes))
        extra_codes[hierarchy_name].extend(list(all_label_codes - all_codes))

    error_messages = []
    if missing_hierarchies:
        missing_str = ", ".join(missing_hierarchies)
        error_messages.append(
            f"The following hierarchies do not have mappings: {missing_str}",
        )

    for hierarchy_name, codes in missing_codes.items():
        if codes:
            missing_str = ", ".join(codes)
            error_messages.append(
                f"Hierarchies {hierarchy_name} has missing mappings: {missing_str}",
            )

    for hierarchy_name, codes in extra_codes.items():
        if codes:
            xtr_str = ", ".join(codes)
            error_messages.append(
                f"Hierarchies {hierarchy_name} has superfluous mappings: {xtr_str}",
            )

    return error_messages


def flatten(
    hierarchy: Hierarchy,
    only_leaves: bool = False,
) -> list[str]:
    if isinstance(hierarchy, list):
        return hierarchy

    items = []
    for k, v in hierarchy.items():
        if not only_leaves:
            items.append(k)
        if isinstance(v, dict):
            items.extend(flatten(v, only_leaves=only_leaves))
        else:
            items.extend(v)
    return items


def validate_hierarchy_schema(
    available_schemas: Iterable[str],
    hierarchy_schema: str,
) -> None:
    if hierarchy_schema not in available_schemas:
        raise ValueError(
            f"""
            Schema {hierarchy_schema} does not exist.
            Only {', '.join(available_schemas)} exist.
            """,
        )


def map_hierarchy(
    hierarchy: Mapping[str, Hierarchy],
    fn: Callable[[str], str],
) -> Mapping[str, Hierarchy]:
    return {
        fn(k): (map_hierarchy(v, fn) if not isinstance(v, list) else [fn(e) for e in v])
        for k, v in hierarchy.items()
    }


def filter_leaves(
    hierarchy: Mapping[str, Hierarchy],
    fn: Callable[[str], bool],
) -> Mapping[str, Hierarchy]:
    result: Mapping[str, Hierarchy] = {}
    for k, v in hierarchy.items():
        if isinstance(v, dict):
            survivors1 = filter_leaves(v, fn)
            if survivors1:
                result[k] = survivors1  # type: ignore
        else:
            survivors2 = [e for e in v if fn(e)]
            if survivors2:
                result[k] = survivors2  # type: ignore
    return result


def find_in_hierarchy(
    hierarchy: Mapping[str, Hierarchy],
    needle: str,
    *,
    return_depth: bool = False,
    depth: int = 0,
) -> Hierarchy | int | None:
    for k, v in hierarchy.items():
        if k == needle:
            return {k: v} if not return_depth else depth + 1
        if isinstance(v, list):
            if needle in v:
                return [needle] if not return_depth else depth + 2
        elif isinstance(v, dict):
            match = find_in_hierarchy(
                v,
                needle,
                return_depth=return_depth,
                depth=depth + 1,
            )
            if match:
                return match if not return_depth else match

    if depth == 0:
        return None if not return_depth else -1
    else:
        return []


def trim_to_depth(hierarchy: Hierarchy, depth: int) -> Hierarchy:
    if depth < 0:
        raise AssertionError(f"Depth must be >= 0., {depth}")
    if depth == 1:
        return list(hierarchy.keys()) if isinstance(hierarchy, dict) else hierarchy
    elif isinstance(hierarchy, list):
        return hierarchy
    else:
        return {k: trim_to_depth(v, depth - 1) for k, v in hierarchy.items()}


def filter_labels_to_hierarchy(
    hierarchy: Mapping[str, Hierarchy],
    labels: Mapping[str, str],
) -> Mapping[str, str]:
    return {k: v for k, v in labels.items() if k in flatten(hierarchy)}


def get_depth(hierarchy: Mapping[str, Hierarchy] | list[str]) -> int:
    if isinstance(hierarchy, list):
        d = 0
    else:
        depths = []
        for value in hierarchy.values():
            depths.append(get_depth(value))
        d = max(depths)
    return d + 1


def check_all_leafcodes_exist(
    hierarchy: Mapping[str, Hierarchy], leaf_codes: set[str]
) -> None:
    missing_codes = set(flatten(hierarchy, only_leaves=True)) - leaf_codes
    if missing_codes:
        raise ValueError(f"There are missing codes: {', '.join(missing_codes)}")


# TODO: move somewhere else
def unnest(hierarchy: Mapping[str, Hierarchy] | list[str]) -> list[list[str]]:
    """Convert a nested hierarchy to a list of lists."""
    if isinstance(hierarchy, list):
        return [[v] for v in hierarchy]
    elif isinstance(hierarchy, dict):
        return sum([[[k, *v] for v in unnest(h)] for k, h in hierarchy.items()], [])
    else:
        raise ValueError("Hierarchy must be either a list or a dictionary.")


def prune_leaves(
    hierarchy: Mapping[str, Hierarchy],
) -> Mapping[str, Hierarchy]:
    return {
        k: prune_leaves(v) if not isinstance(v, list) else []
        for k, v in hierarchy.items()
    }


def hierarchy_to_df(
    hierarchy: Mapping[str, Hierarchy] | list[str], hierarchy_labels: Mapping[str, str]
) -> pl.DataFrame:
    rows = []

    def recurse(
        node: Mapping[str, Hierarchy] | list[str], level: int, parent_code: str | None
    ) -> None:
        if isinstance(node, dict):
            for key, subtree in node.items():
                # Add the current key (an intermediate node)
                rows.append({"code": key, "level": level, "parent_code": parent_code})
                # Recurse into its value
                recurse(subtree, level + 1, key)
        elif isinstance(node, list):
            # If we hit a list, each element is a leaf code
            for leaf in node:
                rows.append({"code": leaf, "level": level, "parent_code": parent_code})

    recurse(hierarchy, level=0, parent_code=None)

    return (
        pl.DataFrame(rows)
        .select(
            pl.col("level").cast(pl.Int32),
            "code",
            pl.col("code").replace_strict(hierarchy_labels).alias("label"),
            pl.col("parent_code").cast(pl.String),
        )
        .sort("level", maintain_order=True)
    )


def hierarchy_df_to_wide(
    hierarchy: Mapping[str, Hierarchy] | list[str], hierarchy_labels: Mapping[str, str]
) -> pl.DataFrame:
    df = hierarchy_to_df(hierarchy, hierarchy_labels)

    df_wide = df.filter(pl.col("level") == 0).select(
        pl.col("code").alias("level_1"), pl.col("label").alias("level_1_label")
    )
    for lvl in range(cast(int, df.get_column("level").max())):
        df_wide = (
            df_wide.join(
                df.filter(pl.col("level") == lvl + 1),
                left_on=f"level_{lvl + 1}",
                right_on="parent_code",
                how="left",
            )
            .drop("level")
            .rename({"code": f"level_{lvl + 2}", "label": f"level_{lvl + 2}_label"})
        )
    return df_wide
