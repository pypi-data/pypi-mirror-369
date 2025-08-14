import difflib
import io
import json
import os
import re
from copy import deepcopy
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional, Set, Tuple

import yamllint.config
import yamllint.linter
from rich.console import Console
from ruamel.yaml import YAML
from ruamel.yaml.compat import StringIO
from yaml import safe_load
from jinja2 import Undefined


from dbt_common.clients.jinja import get_template, render_template
from dbt_autofix.jinja import statically_parse_unrendered_config
from dbt_autofix.deprecations import DeprecationType
from dbt_autofix.retrieve_schemas import (
    DbtProjectSpecs,
    SchemaSpecs,
)

NUM_SPACES_TO_REPLACE_TAB = 2

COMMON_PROPERTY_MISSPELLINGS = {
    "desciption": "description",
    "descrption": "description",
    "descritption": "description",
    "desscription": "description",
}

console = Console()
error_console = Console(stderr=True)

config = """
rules:
  key-duplicates: enable
"""

yaml_config = yamllint.config.YamlLintConfig(config)


class DbtYAML(YAML):
    """dbt-compatible YAML class."""

    def __init__(self):
        super().__init__(typ=["rt", "string"])
        self.preserve_quotes = True
        self.width = 4096
        self.indent(mapping=2, sequence=4, offset=2)
        self.default_flow_style = False

    def dump(self, data, stream=None, **kw):
        inefficient = False
        if stream is None:
            inefficient = True
            stream = StringIO()
        super().dump(data, stream, **kw)
        if inefficient:
            return stream.getvalue()

    def dump_to_string(self, data: Any, add_final_eol: bool = False) -> str:
        buf = io.BytesIO()
        self.dump(data, buf)
        if add_final_eol:
            return buf.getvalue().decode("utf-8")
        else:
            return buf.getvalue()[:-1].decode("utf-8")


def read_file(path: Path) -> Dict:
    yaml = DbtYAML()
    return yaml.load(path)


def dict_to_yaml_str(content: Dict[str, Any]) -> str:
    """Write a dict value to a YAML string"""
    yaml = DbtYAML()
    file_text = yaml.dump_to_string(content)  # type: ignore
    return file_text


@dataclass
class DbtDeprecationRefactor:
    log: str
    deprecation: Optional[str] = None

    def to_dict(self) -> dict:
        ret_dict = {
            "deprecation": self.deprecation,
            "log": self.log
        }

        return ret_dict

@dataclass
class YMLRuleRefactorResult:
    rule_name: str
    refactored: bool
    refactored_yaml: str
    original_yaml: str
    deprecation_refactors: list[DbtDeprecationRefactor]

    @property
    def refactor_logs(self):
        return [refactor.log for refactor in self.deprecation_refactors]

    def to_dict(self) -> dict:
        ret_dict = {
            "deprecation_refactors": [deprecation_refactor.to_dict() for deprecation_refactor in self.deprecation_refactors]
        }
        return ret_dict


@dataclass
class YMLRefactorResult:
    dry_run: bool
    file_path: Path
    refactored: bool
    refactored_yaml: str
    original_yaml: str
    refactors: list[YMLRuleRefactorResult]

    def update_yaml_file(self) -> None:
        """Update the YAML file with the refactored content"""
        Path(self.file_path).write_text(self.refactored_yaml)

    def print_to_console(self, json_output: bool = True):
        if not self.refactored:
            return

        if json_output:
            flattened_refactors = []
            for refactor in self.refactors:
                if refactor.refactored:
                    flattened_refactors.extend(refactor.to_dict()["deprecation_refactors"])

            to_print = {
                "mode": "dry_run" if self.dry_run else "applied",
                "file_path": str(self.file_path),
                "refactors": flattened_refactors,
            }
            print(json.dumps(to_print))  # noqa: T201
            return

        console.print(
            f"\n{'DRY RUN - NOT APPLIED: ' if self.dry_run else ''}Refactored {self.file_path}:",
            style="green",
        )
        for refactor in self.refactors:
            if refactor.refactored:
                console.print(f"  {refactor.rule_name}", style="yellow")
                for log in refactor.refactor_logs:
                    console.print(f"    {log}")


@dataclass
class SQLRuleRefactorResult:
    rule_name: str
    refactored: bool
    refactored_content: str
    original_content: str
    deprecation_refactors: list[DbtDeprecationRefactor]
    refactored_file_path: Optional[Path] = None
    refactor_warnings: list[str] = field(default_factory=list)

    @property
    def refactor_logs(self):
        return [refactor.log for refactor in self.deprecation_refactors]

    def to_dict(self) -> dict:
        ret_dict = {
            "rule_name": self.rule_name,
            "deprecation_refactors": [refactor.to_dict() for refactor in self.deprecation_refactors],
        }
        return ret_dict


@dataclass
class SQLRefactorResult:
    dry_run: bool
    file_path: Path
    refactored: bool
    refactored_file_path: Path
    refactored_content: str
    original_content: str
    refactors: list[SQLRuleRefactorResult]
    has_warnings: bool = False

    def update_sql_file(self) -> None:
        """Update the SQL file with the refactored content"""
        new_file_path = self.refactored_file_path or self.file_path
        if self.file_path != new_file_path:
            os.rename(self.file_path, self.refactored_file_path)

        Path(new_file_path).write_text(self.refactored_content)

    def print_to_console(self, json_output: bool = True):
        if not self.refactored and not self.has_warnings:
            return

        if json_output:
            flattened_refactors = []
            for refactor in self.refactors:
                if refactor.refactored:
                    flattened_refactors.extend(refactor.to_dict()["deprecation_refactors"])
            
            flattened_warnings = []
            for refactor in self.refactors:
                if refactor.refactor_warnings:
                    flattened_warnings.extend(refactor.refactor_warnings)

            to_print = {
                "mode": "dry_run" if self.dry_run else "applied",
                "file_path": str(self.file_path),
                "refactors": flattened_refactors,
                "warnings": flattened_warnings,
            }
            print(json.dumps(to_print))  # noqa: T201
            return

        console.print(
            f"\n{'DRY RUN - NOT APPLIED: ' if self.dry_run else ''}Refactored {self.file_path}:",
            style="green",
        )
        for refactor in self.refactors:
            if refactor.refactored:
                console.print(f"  {refactor.rule_name}", style="yellow")

                for log in refactor.refactor_logs:
                    console.print(f"    {log}")

                for warning in refactor.refactor_warnings:
                    console.print(f"    Warning: {warning}", style="red")
            elif refactor.refactor_warnings:
                console.print(f"  {refactor.rule_name}", style="yellow")
                for warning in refactor.refactor_warnings:
                    console.print(f"    Warning: {warning}", style="red")


def remove_unmatched_endings(sql_content: str) -> SQLRuleRefactorResult:  # noqa: PLR0912
    """Remove unmatched {% endmacro %} and {% endif %} tags from SQL content.

    Handles:
    - Multi-line tags
    - Whitespace control variants ({%- and -%})
    - Nested blocks

    Args:
        sql_content: The SQL content to process

    Returns: SQLRuleRefactorResult
    """
    # Regex patterns for Jinja tag matching
    JINJA_TAG_PATTERN = re.compile(r"{%-?\s*((?s:.*?))\s*-?%}", re.DOTALL)
    MACRO_START = re.compile(r"^macro\s+([^\s(]+)")  # Captures macro name
    IF_START = re.compile(r"^if[(\s]+.*")  # if blocks can also be {% if(...) %}
    MACRO_END = re.compile(r"^endmacro")
    IF_END = re.compile(r"^endif")

    deprecation_refactors: List[DbtDeprecationRefactor] = []
    # Track macro and if states with their positions
    macro_stack: List[Tuple[int, int, str]] = []  # [(start_pos, end_pos, macro_name), ...]
    if_stack: List[Tuple[int, int]] = []  # [(start_pos, end_pos), ...]

    # Track positions to remove
    to_remove: List[Tuple[int, int]] = []  # [(start_pos, end_pos), ...]

    # Find all Jinja tags
    for match in JINJA_TAG_PATTERN.finditer(sql_content):
        tag_content = match.group(1)
        start_pos = match.start()
        end_pos = match.end()

        # Check for macro start
        macro_match = MACRO_START.match(tag_content)
        if macro_match:
            macro_name = macro_match.group(1)
            macro_stack.append((start_pos, end_pos, macro_name))
            continue

        # Check for if start
        if IF_START.match(tag_content):
            if_stack.append((start_pos, end_pos))
            continue

        # Handle endmacro
        if MACRO_END.match(tag_content):
            if not macro_stack:
                to_remove.append((start_pos, end_pos))
                # Count lines, adjusting for content before first newline
                prefix = sql_content[:start_pos]
                first_newline = prefix.find("\n")
                if first_newline == -1:
                    line_num = 1
                else:
                    line_num = prefix.count("\n", first_newline) + 1
                deprecation_refactors.append(
                    DbtDeprecationRefactor(
                        log=f"Removed unmatched {{% endmacro %}} near line {line_num}",
                        deprecation=DeprecationType.UNEXPECTED_JINJA_BLOCK_DEPRECATION
                    )
                )
            else:
                macro_stack.pop()
            continue

        # Handle endif
        if IF_END.match(tag_content):
            if not if_stack:
                to_remove.append((start_pos, end_pos))
                # Count lines, adjusting for content before first newline
                prefix = sql_content[:start_pos]
                first_newline = prefix.find("\n")
                if first_newline == -1:
                    line_num = 1
                else:
                    line_num = prefix.count("\n", first_newline) + 1
                deprecation_refactors.append(
                    DbtDeprecationRefactor(
                        log=f"Removed unmatched {{% endif %}} near line {line_num}",
                        deprecation=DeprecationType.UNEXPECTED_JINJA_BLOCK_DEPRECATION
                        )
                )
            else:
                if_stack.pop()

    # Remove the unmatched tags from end to start to maintain correct positions
    result = sql_content
    for start, end in sorted(to_remove, reverse=True):
        result = result[:start] + result[end:]

    return SQLRuleRefactorResult(
        rule_name="remove_unmatched_endings",
        refactored=result != sql_content,
        refactored_content=result,
        original_content=sql_content,
        deprecation_refactors=deprecation_refactors,
    )


def move_custom_configs_to_meta_sql(sql_content: str, schema_specs: SchemaSpecs, node_type: str) -> SQLRuleRefactorResult:
    """Move custom configs to meta in SQL files.

    Args:
        sql_content: The SQL content to process
        schema_specs: The schema specifications to use
        node_type: The type of node to process
    """
    refactored = False
    deprecation_refactors: List[DbtDeprecationRefactor] = []
    refactor_warnings: list[str] = []

    # Capture original config macro calls
    original_sql_configs = {}
    def capture_config(*args, **kwargs):
        original_sql_configs.update(kwargs)

    ctx = {"config": capture_config}
    template = get_template(sql_content, ctx=ctx, capture_macros=True)

    # Crude way to avoid rendering the template if it doesn't contain 'config'
    if "config(" in sql_content:
        render_template(template, ctx=ctx)

    statically_parsed_config = statically_parse_unrendered_config(sql_content) or {}

    # Refactor config based on schema specs
    refactored_sql_configs = None
    contains_jinja = False
    try:
        refactored_sql_configs = deepcopy(original_sql_configs)
    except Exception:
        # config() macro calls with jinja requiring dbt context will result in deepcopy error due to Undefined values
        refactored_sql_configs = None
        contains_jinja = True

    moved_to_meta = []
    for sql_config_key, sql_config_value in original_sql_configs.items():
        # If the config key is not in the schema specs, move it to meta
        allowed_config_fields = schema_specs.yaml_specs_per_node_type[node_type].allowed_config_fields

        # Special casing snapshots because target_schema and target_database are renamed by another autofix rule
        if node_type == "snapshots":
            allowed_config_fields = allowed_config_fields.union({"target_schema", "target_database"})

        if sql_config_key not in allowed_config_fields:
            moved_to_meta.append(sql_config_key)
            if refactored_sql_configs is not None:
                if "meta" not in refactored_sql_configs:
                    refactored_sql_configs["meta"] = {}
                refactored_sql_configs["meta"].update({sql_config_key: sql_config_value})
                del refactored_sql_configs[sql_config_key]

    # Update {{ config(...) }} macro call with new configs if any were moved to meta
    refactored_content = None
    if refactored_sql_configs and refactored_sql_configs != original_sql_configs:
        # Determine if jinja rendering occurred as part of config macro call
        original_config_str = _serialize_config_macro_call(original_sql_configs)
        post_render_statically_parsed_config = statically_parse_unrendered_config(f"{{{{ config({original_config_str}) }}}}")
        if post_render_statically_parsed_config == statically_parsed_config:
            refactored = True
            deprecation_refactors.append(
                DbtDeprecationRefactor(
                    log=f"Moved custom config{'s' if len(moved_to_meta) > 1 else ''} {moved_to_meta} to 'meta'",
                    deprecation=DeprecationType.CUSTOM_KEY_IN_CONFIG_DEPRECATION
                )
            )
            config_pattern = re.compile(r"(\{\{\s*config\s*\()(.*?)(\)\s*\}\})", re.DOTALL)
            new_config_str = _serialize_config_macro_call(refactored_sql_configs)
            def replace_config(match):
                return f"{{{{ config({new_config_str}) }}}}"
            refactored_content = config_pattern.sub(replace_config, sql_content, count=1)
        else:
            contains_jinja = True
    
    if moved_to_meta and contains_jinja: 
        refactor_warnings.append(
            f"Detected custom config{'s' if len(moved_to_meta) > 1 else ''} {moved_to_meta}, "
            f"but autofix was unable to refactor {'them' if len(moved_to_meta) > 1 else 'it'} due to Jinja usage in the config macro call.\n\t"
            f"Please manually move the custom configs {moved_to_meta} to 'meta'.",
        )

    return SQLRuleRefactorResult(
        rule_name="move_custom_configs_to_meta_sql",
        refactored=refactored,
        refactored_content=refactored_content or sql_content,
        original_content=sql_content,
        deprecation_refactors=deprecation_refactors,
        refactor_warnings=refactor_warnings,
    )

def _serialize_config_macro_call(config_dict: dict) -> str:
    items = []
    for k, v in config_dict.items():
        if isinstance(v, str):
            v_str = f'"{v}"'
        else:
            v_str = str(v)
        items.append(f"{k}={v_str}")
    return ", ".join(items)

def move_custom_config_access_to_meta_sql(sql_content: str, schema_specs: SchemaSpecs, node_type: str) -> SQLRuleRefactorResult:
    """Move custom config access to meta in SQL files.

    Args:
        sql_content: The SQL content to process
        schema_specs: The schema specifications to use
        node_type: The type of node to process
    """
    refactored = False
    refactored_content = sql_content
    deprecation_refactors: List[DbtDeprecationRefactor] = []

    # Crude way to avoid refactoring the file if it contains any cusotm 'config' variable
    if "set config" in sql_content:
        return SQLRuleRefactorResult(
            rule_name="move_custom_config_access_to_meta_sql",
            refactored=False,
            refactored_content=sql_content,
            original_content=sql_content,
            deprecation_refactors=[],
        )
    
    # Find all instances of config.get(<config-key>, <default>) or config.get(<config-key>)
    pattern = re.compile(
        r"config\.get\(\s*([\"'])(?P<key>.+?)\1\s*(?:,\s*(?P<default>[^)]+))?\)"
    )
    # To safely replace multiple matches in a string, collect all replacements first,
    # then apply them in reverse order (from end to start) so indices remain valid.
    matches = list(pattern.finditer(refactored_content))
    replacements = []
    allowed_config_fields = set()
    for specs in schema_specs.yaml_specs_per_node_type.values():
        allowed_config_fields.update(specs.allowed_config_fields)

    for match in matches:
        config_key = match.group("key")
        default = match.group("default")

        if config_key in allowed_config_fields:
            continue

        start, end = match.span()
        if default is None:
            replacement = f"config.get('meta').{config_key}"
        else:
            replacement = f"(config.get('meta').{config_key} or {default})"
        replacements.append((start, end, replacement, match.group(0)))
        refactored = True

    # Apply replacements in reverse order to avoid messing up indices
    for start, end, replacement, original in reversed(replacements):
        refactored_content = refactored_content[:start] + replacement + refactored_content[end:]
        deprecation_refactors.append(
            DbtDeprecationRefactor(
                log=f'Refactored "{original}" to "{replacement}"',
                # Core does not explicitly raise a deprecation for usage of config.get() in SQL files
                deprecation=None
            )
        )

    return SQLRuleRefactorResult(
        rule_name="move_custom_config_access_to_meta_sql",
        refactored=refactored,
        refactored_content=refactored_content,
        original_content=sql_content,
        deprecation_refactors=deprecation_refactors,
    )



def rename_sql_file_names_with_spaces(sql_content: str, sql_file_path: Path):
    deprecation_refactors: List[DbtDeprecationRefactor] = []

    new_file_path = sql_file_path
    if " " in sql_file_path.name:
        new_file_path = sql_file_path.with_name(sql_file_path.name.replace(" ", "_"))
        deprecation_refactors.append(
            DbtDeprecationRefactor(
                log=f"Renamed '{sql_file_path.name}' to '{new_file_path.name}'",
                deprecation=DeprecationType.RESOURCE_NAMES_WITH_SPACES_DEPRECATION
            )
        )

    return SQLRuleRefactorResult(
        rule_name="rename_sql_files_with_spaces",
        refactored=sql_file_path != new_file_path,
        refactored_content=sql_content,
        original_content=sql_content,
        deprecation_refactors=deprecation_refactors,
        refactored_file_path=new_file_path,
    )


def restructure_owner_properties(
    node: Dict[str, Any], node_type: str, schema_specs: SchemaSpecs
) -> Tuple[Dict[str, Any], bool, List[str]]:
    """Restructure owner properties according to dbt conventions.

    Args:
        node: The node dictionary to process
        node_type: The type of node to process
        schema_specs: The schema specifications to use

    Returns:
        Tuple containing:
        - The processed node dictionary
        - Boolean indicating if changes were made
        - List of refactor logs
    """
    refactored = False
    refactor_logs: List[str] = []
    pretty_node_type = node_type[:-1].title()

    if "owner" in node and isinstance(node["owner"], dict):
        owner = node["owner"]
        owner_copy = owner.copy()

        for field in owner_copy:
            if field not in schema_specs.owner_properties:
                refactored = True
                if "config" not in node:
                    node["config"] = {"meta": {}}
                if "meta" not in node["config"]:
                    node["config"]["meta"] = {}
                node["config"]["meta"][field] = owner[field]
                del owner[field]
                refactor_logs.append(
                    f"{pretty_node_type} '{node['name']}' - Owner field '{field}' moved under config.meta."
                )

    return node, refactored, refactor_logs


def changeset_remove_tab_only_lines(yml_str: str) -> YMLRuleRefactorResult:
    """Remove lines that contain only tabs from YAML files.

    Args:
        yml_str: The YAML string to process

    Returns:
        YMLRuleRefactorResult containing the refactored YAML and any changes made
    """
    refactored = False
    deprecation_refactors: List[DbtDeprecationRefactor] = []

    # Process each line
    lines = yml_str.splitlines()
    new_lines = []
    for i, line in enumerate(lines):
        if "\t" in line and line.strip() == "":
            refactored = True
            deprecation_refactors.append(
                DbtDeprecationRefactor(
                    log=f"Removed line containing only tabs on line {i + 1}"
                )
            )
            new_lines.append("")
        else:
            new_lines.append(line)

    refactored_yaml = "\n".join(new_lines) if refactored else yml_str

    return YMLRuleRefactorResult(
        rule_name="remove_tab_only_lines",
        refactored=refactored,
        refactored_yaml=refactored_yaml,
        original_yaml=yml_str,
        deprecation_refactors=deprecation_refactors,
    )


def process_yaml_files_except_dbt_project(
    root_path: Path,
    model_paths: Iterable[str],
    schema_specs: SchemaSpecs,
    dry_run: bool = False,
    select: Optional[List[str]] = None,
    behavior_change: bool = False,
    all: bool = False,
) -> List[YMLRefactorResult]:
    """Process all YAML files in the project

    Args:
        path: Project root path
        model_paths: Paths to process
        schema_specs: The schema specifications to use
        dry_run: Whether to perform a dry run
        select: Optional list of paths to select
        behavior_change: Whether to apply fixes that may lead to behavior changes
        all: Whether to run all fixes, including those that may require a behavior change
    """
    yaml_results: List[YMLRefactorResult] = []

    for model_path in model_paths:
        yaml_files = set((root_path / Path(model_path)).resolve().glob("**/*.yml")).union(
            set((root_path / Path(model_path)).resolve().glob("**/*.yaml"))
        )
        for yml_file in yaml_files:
            if skip_file(yml_file, select):
                continue

            yml_str = yml_file.read_text()
            yml_refactor_result = YMLRefactorResult(
                dry_run=dry_run,
                file_path=yml_file,
                refactored=False,
                refactored_yaml=yml_str,
                original_yaml=yml_str,
                refactors=[],
            )

            # Define the changesets to apply in order
            behavior_change_rules = [
                (changeset_replace_non_alpha_underscores_in_name_values, schema_specs),
            ]
            safe_change_rules = [
                (changeset_remove_tab_only_lines, None),
                (changeset_remove_indentation_version, None),
                (changeset_remove_extra_tabs, None),
                (changeset_remove_duplicate_keys, None),
                (changeset_refactor_yml_str, schema_specs),
                (changeset_owner_properties_yml_str, schema_specs),
            ]
            all_rules = [*behavior_change_rules, *safe_change_rules]

            changesets = all_rules if all else behavior_change_rules if behavior_change else safe_change_rules

            # Apply each changeset in sequence
            try:
                for changeset_func, changeset_args in changesets:
                    if changeset_args is None:
                        changeset_result = changeset_func(yml_refactor_result.refactored_yaml)
                    else:
                        changeset_result = changeset_func(yml_refactor_result.refactored_yaml, changeset_args)

                    if changeset_result.refactored:
                        yml_refactor_result.refactors.append(changeset_result)
                        yml_refactor_result.refactored = True
                        yml_refactor_result.refactored_yaml = changeset_result.refactored_yaml

                    yaml_results.append(yml_refactor_result)

            except Exception as e:
                error_console.print(f"Error processing YAML at path {yml_file}: {e.__class__.__name__}: {e}", style="bold red")
                exit(1)

    return yaml_results


def process_dbt_project_yml(
    root_path: Path, schema_specs: SchemaSpecs, dry_run: bool = False, exclude_dbt_project_keys: bool = False, behavior_change: bool = False, all: bool = False
) -> YMLRefactorResult:
    """Process dbt_project.yml"""
    if not (root_path / "dbt_project.yml").exists():
        error_console.print(f"Error: dbt_project.yml not found in {root_path}", style="red")
        return YMLRefactorResult(
            dry_run=dry_run,
            file_path=root_path / "dbt_project.yml",
            refactored=False,
            refactored_yaml="",
            original_yaml="",
            refactors=[],
        )

    yml_str = (root_path / "dbt_project.yml").read_text()
    yml_refactor_result = YMLRefactorResult(
        dry_run=dry_run,
        file_path=root_path / "dbt_project.yml",
        refactored=False,
        refactored_yaml=yml_str,
        original_yaml=yml_str,
        refactors=[],
    )

    behavior_change_rules = [
        (changeset_dbt_project_flip_behavior_flags, None)
    ]
    safe_change_rules = [
        (changeset_remove_duplicate_keys, None),
        (changeset_dbt_project_flip_test_arguments_behavior_flag, None),
        (changeset_dbt_project_remove_deprecated_config, exclude_dbt_project_keys),
        (changeset_dbt_project_prefix_plus_for_config, root_path, schema_specs),
    ]
    all_rules = [*behavior_change_rules, *safe_change_rules]

    changesets = all_rules if all else behavior_change_rules if behavior_change else safe_change_rules

    for changeset_func, *changeset_args in changesets:
        if changeset_args[0] is None:
            changeset_result = changeset_func(yml_refactor_result.refactored_yaml)
        elif len(changeset_args) == 1:
            changeset_result = changeset_func(yml_refactor_result.refactored_yaml, changeset_args[0])
        else:
            changeset_result = changeset_func(yml_refactor_result.refactored_yaml, *changeset_args)

        if changeset_result.refactored:
            yml_refactor_result.refactors.append(changeset_result)
            yml_refactor_result.refactored = True
            yml_refactor_result.refactored_yaml = changeset_result.refactored_yaml

    return yml_refactor_result


def skip_file(file_path: Path, select: Optional[List[str]] = None) -> bool:
    """Skip a file if a select list is provided and the file is not in the select list"""
    if select:
        return not any([Path(select_path).resolve().as_posix() in file_path.as_posix() for select_path in select])
    else:
        return False


def process_sql_files(
    path: Path,
    sql_paths_to_node_type: Dict[str, str],
    schema_specs: SchemaSpecs,
    dry_run: bool = False,
    select: Optional[List[str]] = None,
    behavior_change: bool = False,
    all: bool = False,
) -> List[SQLRefactorResult]:
    """Process all SQL files in the given paths for unmatched endings.

    Args:
        path: Base project path
        sql_paths: Set of paths relative to project root where SQL files are located
        dry_run: Whether to perform a dry run
        select: Optional list of paths to select
        behavior_change: Whether to apply fixes that may lead to behavior change
        all: Whether to run all fixes, including those that may require a behavior change

    Returns:
        List of SQLRefactorResult for each processed file
    """
    results: List[SQLRefactorResult] = []

    behavior_change_rules = [
        (rename_sql_file_names_with_spaces, True, False)
    ]
    safe_change_rules = [
        (remove_unmatched_endings, False, False),
        (move_custom_configs_to_meta_sql, False, True),
        (move_custom_config_access_to_meta_sql, False, True)
    ]
    all_rules = [*behavior_change_rules, *safe_change_rules]

    process_sql_file_rules = all_rules if all else behavior_change_rules if behavior_change else safe_change_rules

    for sql_path, node_type in sql_paths_to_node_type.items():
        full_path = (path / sql_path).resolve()
        if not full_path.exists():
            error_console.print(f"Warning: Path {full_path} does not exist", style="yellow")
            continue

        sql_files = full_path.glob("**/*.sql")
        for sql_file in sql_files:
            if skip_file(full_path, select):
                continue

            try:
                file_refactors: List[SQLRefactorResult] = []

                original_content = sql_file.read_text()
                new_content = original_content

                new_file_path = sql_file
                for sql_file_rule, requires_file_path, requires_schema_specs in process_sql_file_rules:
                    if requires_file_path and requires_schema_specs:
                        sql_file_refactor_result = sql_file_rule(new_content, new_file_path, schema_specs, node_type)
                    elif requires_file_path:
                        sql_file_refactor_result = sql_file_rule(new_content, new_file_path)
                    elif requires_schema_specs:
                        sql_file_refactor_result = sql_file_rule(new_content, schema_specs, node_type)
                    else:
                        sql_file_refactor_result = sql_file_rule(new_content)

                    new_content = sql_file_refactor_result.refactored_content
                    new_file_path = sql_file_refactor_result.refactored_file_path or sql_file
                    file_refactors.append(sql_file_refactor_result)

                refactored = (new_content != original_content) or (new_file_path != sql_file)
                has_warnings = any([refactor.refactor_warnings for refactor in file_refactors])
                results.append(
                    SQLRefactorResult(
                        dry_run=dry_run,
                        file_path=sql_file,
                        refactored=refactored,
                        refactored_content=new_content,
                        original_content=original_content,
                        refactors=file_refactors,
                        refactored_file_path=new_file_path,
                        has_warnings=has_warnings,
                    )
                )
            except Exception as e:
                error_console.print(f"Error processing {sql_file}: {e}", style="bold red")

    return results


def restructure_yaml_keys_for_node(
    node: Dict[str, Any], node_type: str, schema_specs: SchemaSpecs
) -> Tuple[Dict[str, Any], bool, List[DbtDeprecationRefactor]]:
    """Restructure YAML keys according to dbt conventions.

    Args:
        node: The node dictionary to process
        node_type: The type of node to process
        schema_specs: The schema specifications to use

    Returns:
        Tuple containing:
        - The processed model dictionary
        - Boolean indicating if changes were made
        - List of refactor logs
    """
    refactored = False
    deprecation_refactors: List[DbtDeprecationRefactor] = []
    existing_meta = node.get("meta", {}).copy()
    existing_config = node.get("config", {}).copy()
    pretty_node_type = node_type[:-1].title()

    for field in existing_config:
        # Special casing target_schema and target_database because they are renamed by another autofix rule
        if field in schema_specs.yaml_specs_per_node_type[node_type].allowed_config_fields or field in ("target_schema", "target_database"):
            continue

        refactored = True
        deprecation_refactors.append(
            DbtDeprecationRefactor(
                log=f"{pretty_node_type} '{node.get('name', '')}' - Config '{field}' is not an allowed config - Moved under config.meta.",
                deprecation=DeprecationType.CUSTOM_KEY_IN_CONFIG_DEPRECATION
            )
        )
        node_config_meta = node.get("config", {}).get("meta", {})
        node_config_meta.update({field: node["config"][field]})
        node["config"] = node.get("config", {})
        node["config"].update({"meta": node_config_meta})
        del node["config"][field]

    # we can not loop node and modify it at the same time
    copy_node = node.copy()

    for field in copy_node:
        if field in schema_specs.yaml_specs_per_node_type[node_type].allowed_properties:
            continue
        # This is very hard-coded because it is a 'safe' fix and we don't want to break the user's code
        elif field.lower() in COMMON_PROPERTY_MISSPELLINGS.keys():
            refactored = True
            correct_field = COMMON_PROPERTY_MISSPELLINGS[field.lower()]
            deprecation_refactors.append(
                DbtDeprecationRefactor(
                    log=f"{pretty_node_type} '{node.get('name', '')}' - Field '{field}' is a common misspelling of '{correct_field}', it has been renamed.",
                    deprecation=DeprecationType.CUSTOM_KEY_IN_OBJECT_DEPRECATION
                )
            )
            node[correct_field] = node[field]
            del node[field]
            continue

        if field in schema_specs.yaml_specs_per_node_type[node_type].allowed_config_fields_without_meta:
            refactored = True
            node_config = node.get("config", {})

            # if the field is not under config, move it under config
            if field not in node_config:
                node_config.update({field: node[field]})
                deprecation_refactors.append(
                        DbtDeprecationRefactor(
                            log=f"{pretty_node_type} '{node.get('name', '')}' - Field '{field}' moved under config.",
                            deprecation=DeprecationType.PROPERTY_MOVED_TO_CONFIG_DEPRECATION
                        )
                    )
                node["config"] = node_config

            # if the field is already under config, it will take precedence there, so we remove it from the top level
            else:
                deprecation_refactors.append(
                    DbtDeprecationRefactor(
                        log=f"{pretty_node_type} '{node.get('name', '')}' - Field '{field}' is already under config, it has been removed from the top level.",
                        deprecation="PropertyMovedToConfigDeprecation"
                    )
                )
            del node[field]

        if field not in schema_specs.yaml_specs_per_node_type[node_type].allowed_config_fields:
            refactored = True
            closest_match = difflib.get_close_matches(
                str(field),
                schema_specs.yaml_specs_per_node_type[node_type].allowed_config_fields.union(
                    set(schema_specs.yaml_specs_per_node_type[node_type].allowed_properties)
                ),
                1,
            )
            if closest_match:
                deprecation_refactors.append(
                    DbtDeprecationRefactor(
                        log=f"{pretty_node_type} '{node.get('name', '')}' - Field '{field}' is not allowed, but '{closest_match[0]}' is. Moved as-is under config.meta but you might want to rename it and move it under config.",
                        deprecation=DeprecationType.CUSTOM_KEY_IN_OBJECT_DEPRECATION
                    )
                )
            else:
                deprecation_refactors.append(
                    DbtDeprecationRefactor(
                        log=f"{pretty_node_type} '{node.get('name', '')}' - Field '{field}' is not an allowed config - Moved under config.meta.",
                        deprecation=DeprecationType.CUSTOM_KEY_IN_OBJECT_DEPRECATION
                    )
                )
            node_meta = node.get("config", {}).get("meta", {})
            node_meta.update({field: node[field]})
            node["config"] = node.get("config", {})
            node["config"].update({"meta": node_meta})
            del node[field]

    if existing_meta:
        refactored = True
        deprecation_refactors.append(
                    DbtDeprecationRefactor(
                        log=f"{pretty_node_type} '{node.get('name', '')}' - Moved all the meta fields under config.meta and merged with existing config.meta.",
                        deprecation=DeprecationType.CUSTOM_KEY_IN_OBJECT_DEPRECATION
                    )
                )

        if "config" not in node:
            node["config"] = {"meta": {}}
        if "meta" not in node["config"]:
            node["config"]["meta"] = {}
        for key, value in existing_meta.items():
            node["config"]["meta"].update({key: value})
        del node["meta"]

    return node, refactored, deprecation_refactors


def restructure_yaml_keys_for_test(
    test: Dict[str, Any], schema_specs: SchemaSpecs
) -> Tuple[Dict[str, Any], bool, List[DbtDeprecationRefactor]]:
    """Restructure YAML keys for tests according to dbt conventions.
    Tests are separated from other nodes because
    - they don't support meta
    - they can be either a string or a dict
    - when they are a dict, the top level ist just the test name

    Args:
        test: The test dictionary to process
        schema_specs: The schema specifications to use

    Returns:
        Tuple containing:
        - The processed test dictionary
        - Boolean indicating if changes were made
        - List of refactor logs
    """
    deprecation_refactors: List[DbtDeprecationRefactor] = []

    # if the test is a string, we leave it as is
    if isinstance(test, str):
        return test, False, []

    # extract the test name and definition
    test_name = next(iter(test.keys()))
    if isinstance(test[test_name], dict):
        # standard test definition syntax
        test_definition = test[test_name]
    else:
        # alt syntax
        test_name = test["test_name"]
        test_definition = test

    deprecation_refactors.extend(refactor_test_common_misspellings(test_definition, test_name))
    deprecation_refactors.extend(refactor_test_config_fields(test_definition, test_name, schema_specs))
    deprecation_refactors.extend(refactor_test_args(test_definition, test_name))

    return test, len(deprecation_refactors) > 0, deprecation_refactors

def refactor_test_config_fields(test_definition: Dict[str, Any], test_name: str, schema_specs: SchemaSpecs) -> List[DbtDeprecationRefactor]:
    deprecation_refactors: List[DbtDeprecationRefactor] = []

    test_configs = schema_specs.yaml_specs_per_node_type["tests"].allowed_config_fields_without_meta
    test_properties = schema_specs.yaml_specs_per_node_type["tests"].allowed_properties

    copy_test_definition = deepcopy(test_definition)
    for field in copy_test_definition:
        # field is a config and not a property
        if field in test_configs and field not in test_properties:
            node_config = test_definition.get("config", {})

            # if the field is not under config, move it under config
            if field not in node_config:
                node_config.update({field: test_definition[field]})
                deprecation_refactors.append(
                    DbtDeprecationRefactor(
                        log=f"Test '{test_name}' - Field '{field}' moved under config.",
                        deprecation=DeprecationType.CUSTOM_KEY_IN_OBJECT_DEPRECATION
                    )
                )
                test_definition["config"] = node_config

            # if the field is already under config, overwrite it and remove from top level
            else:
                node_config[field] = test_definition[field]
                deprecation_refactors.append(
                    DbtDeprecationRefactor(
                        log=f"Test '{test_name}' - Field '{field}' is already under config, it has been overwritten and removed from the top level.",
                        deprecation=DeprecationType.CUSTOM_KEY_IN_OBJECT_DEPRECATION
                    )
                )
                test_definition["config"] = node_config
            del test_definition[field]

    return deprecation_refactors

def refactor_test_common_misspellings(test_definition: Dict[str, Any], test_name: str) -> List[DbtDeprecationRefactor]:
    deprecation_refactors: List[DbtDeprecationRefactor] = []

    for field in test_definition:
        if field.lower() in COMMON_PROPERTY_MISSPELLINGS.keys():
            deprecation_refactors.append(
                DbtDeprecationRefactor(
                    log=f"Test '{test_name}' - Field '{field}' is a common misspelling of '{COMMON_PROPERTY_MISSPELLINGS[field.lower()]}', it has been renamed.",
                    deprecation=DeprecationType.CUSTOM_KEY_IN_OBJECT_DEPRECATION
                )
            )
            test_definition[COMMON_PROPERTY_MISSPELLINGS[field.lower()]] = test_definition[field]
            del test_definition[field]

    return deprecation_refactors

def refactor_test_args(test_definition: Dict[str, Any], test_name: str) -> List[DbtDeprecationRefactor]:
    """Move non-config args under 'arguments' key
    This refactor is only necessary for custom tests, or tests making use of the alternative test definition syntax ('test_name')
    """
    deprecation_refactors: List[DbtDeprecationRefactor] = []

    copy_test_definition = deepcopy(test_definition)
    # Avoid refactoring if the test already has an arguments key that is not a dict
    if "arguments" in test_definition and not isinstance(test_definition["arguments"], dict):
        return deprecation_refactors

    for field in copy_test_definition:
        # TODO: pull from CustomTestMultiKey on schema_specs once available in jsonschemas
        if field in ("config", "arguments", "test_name", "name", "description", "column_name"):
            continue
        deprecation_refactors.append(
            DbtDeprecationRefactor(
                log=f"Test '{test_name}' - Custom test argument '{field}' moved under 'arguments'.",
                deprecation=DeprecationType.MISSING_GENERIC_TEST_ARGUMENTS_PROPERTY_DEPRECATION
            )
        )
        test_definition["arguments"] = test_definition.get("arguments", {})
        test_definition["arguments"].update({field: test_definition[field]})
        del test_definition[field]
    
    return deprecation_refactors

def changeset_owner_properties_yml_str(yml_str: str, schema_specs: SchemaSpecs) -> YMLRuleRefactorResult:
    """Generates a refactored YAML string from a single YAML file
    - moves all the owner fields that are not in owner_properties under config.meta
    """
    refactored = False
    deprecation_refactors: List[DbtDeprecationRefactor] = []
    yml_dict = DbtYAML().load(yml_str) or {}

    for node_type in schema_specs.nodes_with_owner:
        if node_type in yml_dict:
            for i, node in enumerate(yml_dict[node_type]):
                processed_node, node_refactored, node_refactor_logs = restructure_owner_properties(
                    node, node_type, schema_specs
                )
                if node_refactored:
                    refactored = True
                    yml_dict[node_type][i] = processed_node
                    for log in node_refactor_logs:
                        deprecation_refactors.append(
                            DbtDeprecationRefactor(
                                log=log,
                                deprecation=DeprecationType.CUSTOM_KEY_IN_OBJECT_DEPRECATION
                            )
                        )

    return YMLRuleRefactorResult(
        rule_name="restructure_owner_properties",
        refactored=refactored,
        refactored_yaml=dict_to_yaml_str(yml_dict) if refactored else yml_str,
        original_yaml=yml_str,
        deprecation_refactors=deprecation_refactors
    )


def changeset_refactor_yml_str(yml_str: str, schema_specs: SchemaSpecs) -> YMLRuleRefactorResult:  # noqa: PLR0912,PLR0915
    """Generates a refactored YAML string from a single YAML file
    - moves all the config fields under config
    - moves all the meta fields under config.meta and merges with existing config.meta
    - moves all the unknown fields under config.meta
    - provide some information if some fields don't exist but are similar to allowed fields
    - removes custom top-level keys
    """
    refactored = False
    deprecation_refactors: List[DbtDeprecationRefactor] = []
    yml_dict = DbtYAML().load(yml_str) or {}

    yml_dict_keys = list(yml_dict.keys())
    for key in yml_dict_keys:
        if key not in schema_specs.valid_top_level_yaml_fields:
            refactored = True
            deprecation_refactors.append(
                DbtDeprecationRefactor(
                    log=f"Removed custom top-level key: '{key}'",
                    deprecation=DeprecationType.CUSTOM_TOP_LEVEL_KEY_DEPRECATION
                )
            )
            yml_dict.pop(key)

    for node_type in schema_specs.yaml_specs_per_node_type:
        if node_type in yml_dict:
            for i, node in enumerate(yml_dict[node_type]):
                processed_node, node_refactored, node_deprecation_refactors = restructure_yaml_keys_for_node(
                    node, node_type, schema_specs
                )
                if node_refactored:
                    refactored = True
                    yml_dict[node_type][i] = processed_node
                    deprecation_refactors.extend(node_deprecation_refactors)

                if "columns" in processed_node:
                    for column_i, column in enumerate(node["columns"]):
                        processed_column, column_refactored, column_deprecation_refactors = restructure_yaml_keys_for_node(
                            column, "columns", schema_specs
                        )
                        if column_refactored:
                            refactored = True
                            yml_dict[node_type][i]["columns"][column_i] = processed_column
                            deprecation_refactors.extend(column_deprecation_refactors)

                        # there might be some tests, but they can be called tests or data_tests
                        some_tests = {"tests", "data_tests"} & set(processed_column)
                        if some_tests:
                            test_key = next(iter(some_tests))
                            for test_i, test in enumerate(node["columns"][column_i][test_key]):
                                processed_test, test_refactored, test_refactor_deprecations = restructure_yaml_keys_for_test(
                                    test, schema_specs
                                )
                                if test_refactored:
                                    refactored = True
                                    yml_dict[node_type][i]["columns"][column_i][test_key][test_i] = processed_test
                                    deprecation_refactors.extend(test_refactor_deprecations)

                # if there are tests, we need to restructure them
                some_tests = {"tests", "data_tests"} & set(processed_node)
                if some_tests:
                    test_key = next(iter(some_tests))
                    for test_i, test in enumerate(node[test_key]):
                        processed_test, test_refactored, test_refactor_deprecations = restructure_yaml_keys_for_test(
                            test, schema_specs
                        )
                        if test_refactored:
                            refactored = True
                            yml_dict[node_type][i][test_key][test_i] = processed_test
                            deprecation_refactors.extend(test_refactor_deprecations)

    # for sources, the config can be set at the table level as well, which is one level lower
    if "sources" in yml_dict:
        for i, source in enumerate(yml_dict["sources"]):
            if "tables" in source:
                for j, table in enumerate(source["tables"]):
                    processed_source_table, source_table_refactored, source_table_deprecation_refactors = (
                        restructure_yaml_keys_for_node(table, "tables", schema_specs)
                    )
                    if source_table_refactored:
                        refactored = True
                        yml_dict["sources"][i]["tables"][j] = processed_source_table
                        deprecation_refactors.extend(source_table_deprecation_refactors)

                    some_tests = {"tests", "data_tests"} & set(processed_source_table)
                    if some_tests:
                        test_key = next(iter(some_tests))
                        for test_i, test in enumerate(source["tables"][j][test_key]):
                            processed_test, test_refactored, test_refactor_deprecations = restructure_yaml_keys_for_test(
                                test, schema_specs
                            )
                            if test_refactored:
                                refactored = True
                                yml_dict["sources"][i]["tables"][j][test_key][test_i] = processed_test
                                deprecation_refactors.extend(test_refactor_deprecations)

                    if "columns" in processed_source_table:
                        for table_column_i, table_column in enumerate(table["columns"]):
                            processed_table_column, table_column_refactored, table_column_deprecation_refactors = (
                                restructure_yaml_keys_for_node(table_column, "columns", schema_specs)
                            )
                            if table_column_refactored:
                                refactored = True
                                yml_dict["sources"][i]["tables"][j]["columns"][table_column_i] = processed_table_column
                                deprecation_refactors.extend(table_column_deprecation_refactors)

                            some_tests = {"tests", "data_tests"} & set(processed_table_column)
                            if some_tests:
                                test_key = next(iter(some_tests))
                                for test_i, test in enumerate(table_column[test_key]):
                                    processed_test, test_refactored, test_deprecation_refactors = (
                                        restructure_yaml_keys_for_test(test, schema_specs)
                                    )
                                    if test_refactored:
                                        refactored = True
                                        yml_dict["sources"][i]["tables"][j]["columns"][table_column_i][test_key][
                                            test_i
                                        ] = processed_test
                                        deprecation_refactors.extend(test_deprecation_refactors)

    return YMLRuleRefactorResult(
        rule_name="restructure_yaml_keys",
        refactored=refactored,
        refactored_yaml=dict_to_yaml_str(yml_dict) if refactored else yml_str,
        original_yaml=yml_str,
        deprecation_refactors=deprecation_refactors,
    )


def changeset_remove_extra_tabs(yml_str: str) -> YMLRuleRefactorResult:
    """Removes extra tabs in the YAML files"""
    refactored = False
    deprecation_refactors: List[DbtDeprecationRefactor] = []
    current_yaml = yml_str

    while True:
        found_tab_error = False
        for p in yamllint.linter.run(current_yaml, yaml_config):
            if "found character '\\t' that cannot start any token" in p.desc:
                found_tab_error = True
                refactored = True
                deprecation_refactors.append(
                    DbtDeprecationRefactor(log=f"Found extra tabs: line {p.line} - column {p.column}")
                )
                lines = current_yaml.split("\n")
                if p.line <= len(lines):
                    line = lines[p.line - 1]  # Convert to 0-based index
                    if p.column <= len(line):
                        # Replace tab character with NUM_SPACES_TO_REPLACE_TAB spaces
                        new_line = line[: p.column - 1] + " " * NUM_SPACES_TO_REPLACE_TAB + line[p.column :]
                        lines[p.line - 1] = new_line
                        current_yaml = "\n".join(lines)
                        break  # Exit the yamllint loop to restart with updated content

        if not found_tab_error:
            refactored_yaml = current_yaml
            break

    return YMLRuleRefactorResult(
        rule_name="remove_extra_tabs",
        refactored=refactored,
        refactored_yaml=refactored_yaml,
        original_yaml=yml_str,
        deprecation_refactors=deprecation_refactors,
    )


def changeset_remove_duplicate_keys(yml_str: str) -> YMLRuleRefactorResult:
    """Removes duplicate keys in the YAML files, keeping the first occurence only
    The drawback of keeping the first occurence is that we need to use PyYAML and then lose all the comments that were in the file
    """
    refactored = False
    deprecation_refactors: List[DbtDeprecationRefactor] = []

    for p in yamllint.linter.run(yml_str, yaml_config):
        if p.rule == "key-duplicates":
            refactored = True
            deprecation_refactors.append(
                DbtDeprecationRefactor(
                    log=f"Found duplicate keys: line {p.line} - {p.desc}",
                    deprecation="DuplicateYAMLKeysDeprecation"
                )
            )

    if refactored:
        import yaml

        # we use dump from ruamel to keep indentation style but this loses quite a bit of formatting though
        refactored_yaml = DbtYAML().dump_to_string(yaml.safe_load(yml_str))  # type: ignore
    else:
        refactored_yaml = yml_str

    return YMLRuleRefactorResult(
        rule_name="remove_duplicate_keys",
        refactored=refactored,
        refactored_yaml=refactored_yaml,
        original_yaml=yml_str,
        deprecation_refactors=deprecation_refactors,
    )


def changeset_replace_non_alpha_underscores_in_name_values(
    yml_str: str, schema_specs: SchemaSpecs
) -> YMLRuleRefactorResult:
    deprecation_refactors: List[DbtDeprecationRefactor] = []
    yml_dict = DbtYAML().load(yml_str) or {}

    for node_type in schema_specs.yaml_specs_per_node_type:
        if node_type in yml_dict:
            for i, node in enumerate(yml_dict[node_type]):
                processed_node, node_deprecation_refactors = replace_node_name_non_alpha_with_underscores(
                    node, node_type
                )
                if node_deprecation_refactors:
                    yml_dict[node_type][i] = processed_node
                    deprecation_refactors.extend(node_deprecation_refactors)

    refactored = len(deprecation_refactors) > 0
    refactored_yaml = DbtYAML().dump_to_string(yml_dict) if refactored else yml_str

    return YMLRuleRefactorResult(
        rule_name="remove_spaces_in_resource_names",
        refactored=refactored,
        refactored_yaml=refactored_yaml,
        original_yaml=yml_str,
        deprecation_refactors=deprecation_refactors,
    )


def replace_node_name_non_alpha_with_underscores(node: dict[str, str], node_type: str):
    node_deprecation_refactors: List[DbtDeprecationRefactor] = []
    node_copy = node.copy()
    pretty_node_type = node_type[:-1].title()

    deprecation = None
    name = node.get("name", None)
    new_name = None
    if name:
        if node_type == "exposures":
            new_name = name.replace(" ", "_")
            new_name =''.join(c for c in new_name if (c.isalnum() or c == "_"))
            deprecation = "ExposureNameDeprecation"
        else:
            new_name = name.replace(" ", "_")
            deprecation = "ResourceNamesWithSpacesDeprecation"

        if new_name and new_name != name:
            node_copy["name"] = new_name
            node_deprecation_refactors.append(
                DbtDeprecationRefactor(
                    log = f"{pretty_node_type} '{node['name']}' - Updated 'name' from '{name}' to '{new_name}'.",
                    deprecation=deprecation
                )
            )

    return node_copy, node_deprecation_refactors


def changeset_remove_indentation_version(yml_str: str) -> YMLRuleRefactorResult:
    """Standardizes the format of 'version: 2' in YAML files.

    This function looks for any variations of whitespace around 'version: 2' and
    standardizes them to the format 'version: 2'.

    Args:
        yml_str: The YAML string to process

    Returns:
        YMLRuleRefactorResult containing the refactored YAML and any changes made
    """
    refactored = False
    deprecation_refactors: List[DbtDeprecationRefactor] = []

    # Pattern to match any whitespace around 'version: 2'
    pattern = r"^\s*version\s*:\s*2"
    replacement = "version: 2"

    # Process each line
    lines = yml_str.splitlines()
    for i, line in enumerate(lines):
        if re.match(pattern, line):
            if line != replacement:
                refactored = True
                lines[i] = replacement
                deprecation_refactors.append(
                    DbtDeprecationRefactor(
                        log=f"Removed the extra indentation around 'version: 2' on line {i + 1}"
                    )
                )

    refactored_yaml = "\n".join(lines) if refactored else yml_str

    return YMLRuleRefactorResult(
        rule_name="removed_extra_indentation",
        refactored=refactored,
        refactored_yaml=refactored_yaml,
        original_yaml=yml_str,
        deprecation_refactors=deprecation_refactors,
    )


def changeset_dbt_project_remove_deprecated_config(
    yml_str: str, exclude_dbt_project_keys: bool = False
) -> YMLRuleRefactorResult:
    """Remove deprecated keys"""
    refactored = False
    deprecation_refactors: List[DbtDeprecationRefactor] = []

    dict_deprecated_fields_with_defaults = {
        "log-path": "logs",
        "target-path": "target",
    }

    dict_renamed_fields = {
        "data-paths": "seed-paths",
        "source-paths": "model-paths",
    }

    dict_fields_to_deprecation_class = {
        "log-path": "ConfigLogPathDeprecation",
        "target-path": "ConfigTargetPathDeprecation",
        "data-paths": "ConfigDataPathDeprecation",
        "source-paths": "ConfigSourcePathDeprecation",
    }

    yml_dict = DbtYAML().load(yml_str) or {}

    for deprecated_field, _ in dict_deprecated_fields_with_defaults.items():
        if deprecated_field in yml_dict:
            if not exclude_dbt_project_keys:
                # by default we remove it
                refactored = True
                deprecation_refactors.append(
                    DbtDeprecationRefactor(
                        log=f"Removed the deprecated field '{deprecated_field}'",
                        deprecation=dict_fields_to_deprecation_class[deprecated_field]
                    )
                )
                del yml_dict[deprecated_field]
            # with the special field, we only remove it if it's different from the default
            elif yml_dict[deprecated_field] != dict_deprecated_fields_with_defaults[deprecated_field]:
                refactored = True
                deprecation_refactors.append(
                    DbtDeprecationRefactor(
                        log= f"Removed the deprecated field '{deprecated_field}' that wasn't set to the default value",
                        deprecation=dict_fields_to_deprecation_class[deprecated_field]
                    )
                )
                del yml_dict[deprecated_field]

    # TODO: add tests for this
    for deprecated_field, new_field in dict_renamed_fields.items():
        if deprecated_field in yml_dict:
            refactored = True
            if new_field not in yml_dict:
                deprecation_refactors.append(
                    DbtDeprecationRefactor(
                        log=f"Renamed the deprecated field '{deprecated_field}' to '{new_field}'",
                        deprecation=dict_fields_to_deprecation_class[deprecated_field]
                    )
                )
                yml_dict[new_field] = yml_dict[deprecated_field]
            else:
                deprecation_refactors.append(
                    DbtDeprecationRefactor(
                        log=f"Added the config of the deprecated field '{deprecated_field}' to '{new_field}'",
                        deprecation=dict_fields_to_deprecation_class[deprecated_field]
                    )
                )
                yml_dict[new_field] = yml_dict[new_field] + yml_dict[deprecated_field]
            del yml_dict[deprecated_field]

    return YMLRuleRefactorResult(
        rule_name="remove_deprecated_config",
        refactored=refactored,
        refactored_yaml=DbtYAML().dump_to_string(yml_dict) if refactored else yml_str,  # type: ignore
        original_yaml=yml_str,
        deprecation_refactors=deprecation_refactors
    )


def rec_check_yaml_path(
    yml_dict: Dict[str, Any],
    path: Path,
    node_fields: DbtProjectSpecs,
    refactor_logs: Optional[List[str]] = None,
):
    # we can't set refactor_logs as an empty list

    # TODO: what about individual models in the config there?
    # indivdual models would show up here but without the `.sql` (or `.py`)

    if not path.exists() and not _path_exists_as_file(path):
        return yml_dict, [] if refactor_logs is None else refactor_logs

    yml_dict_copy = yml_dict.copy() if yml_dict else {}
    for k, v in yml_dict_copy.items():
        log_msg = None
        if not (path / k).exists() and not _path_exists_as_file(path / k):
            # Built-in config missing "+"
            if k in node_fields.allowed_config_fields_dbt_project:
                new_k = f"+{k}"
                yml_dict[new_k] = v
                log_msg = f"Added '+' in front of the nested config '{k}'"
            # Custom config not in meta
            elif not k.startswith("+"):
                log_msg = f"Moved custom config '{k}' to '+meta'"
                meta = yml_dict.get("+meta", {})
                meta.update({k: v})
                yml_dict["+meta"] = meta
            
            if log_msg:
                if refactor_logs is None:
                    refactor_logs = [log_msg]
                else:
                    refactor_logs.append(log_msg)
            
                del yml_dict[k]
        elif isinstance(yml_dict[k], dict):
            new_dict, refactor_logs = rec_check_yaml_path(yml_dict[k], path / k, node_fields, refactor_logs)
            yml_dict[k] = new_dict
    return yml_dict, [] if refactor_logs is None else refactor_logs

def _path_exists_as_file(path: Path) -> bool:
    return path.with_suffix(".py").exists() or path.with_suffix(".sql").exists() or path.with_suffix(".csv").exists()

def changeset_dbt_project_prefix_plus_for_config(
    yml_str: str, path: Path, schema_specs: SchemaSpecs
) -> YMLRuleRefactorResult:
    """Update keys for the config in dbt_project.yml under to prefix it with a `+`"""
    all_refactor_logs: List[str] = []

    yml_dict = DbtYAML().load(yml_str) or {}

    for node_type, node_fields in schema_specs.dbtproject_specs_per_node_type.items():
        for k, v in (yml_dict.get(node_type) or {}).copy().items():
            # check if this is the project name
            if k == yml_dict["name"]:
                new_dict, refactor_logs = rec_check_yaml_path(v, path / node_type, node_fields)
                yml_dict[node_type][k] = new_dict
                all_refactor_logs.extend(refactor_logs)

            # top level config
            elif k in node_fields.allowed_config_fields_dbt_project:
                all_refactor_logs.append(f"Added '+' in front of top level config '{k}'")
                new_k = f"+{k}"
                yml_dict[node_type][new_k] = v
                del yml_dict[node_type][k]

            # otherwise, treat it as a package
            # TODO: if this is not valid, we could delete it as well
            else:
                packages_path = path / Path(yml_dict.get("packages-paths", "dbt_packages"))
                new_dict, refactor_logs = rec_check_yaml_path(v, packages_path / k / node_type, node_fields)
                yml_dict[node_type][k] = new_dict
                all_refactor_logs.extend(refactor_logs)

    refactored = len(all_refactor_logs) > 0
    deprecation_refactors = [
        DbtDeprecationRefactor(
            log=log,
            deprecation="MissingPlusPrefixDeprecation"
        )
        for log in all_refactor_logs
    ]
    return YMLRuleRefactorResult(
        rule_name="prefix_plus_for_config",
        refactored=refactored,
        refactored_yaml=DbtYAML().dump_to_string(yml_dict) if refactored else yml_str,  # type: ignore
        original_yaml=yml_str,
        deprecation_refactors=deprecation_refactors,
    )


def changeset_dbt_project_flip_behavior_flags(yml_str: str) -> YMLRuleRefactorResult:
    yml_dict = DbtYAML().load(yml_str) or {}
    deprecation_refactors: List[DbtDeprecationRefactor] = []
    refactored = False

    behavior_change_flag_to_explainations = {
        "source_freshness_run_project_hooks": "run project hooks (on-run-start/on-run-end) as part of source freshness commands"
    }

    for key in yml_dict:
        if key == "flags":
            for behavior_change_flag in behavior_change_flag_to_explainations:
                if yml_dict["flags"].get(behavior_change_flag) is False:
                    yml_dict["flags"][behavior_change_flag] = True
                    refactored = True
                    deprecation_refactors.append(
                        DbtDeprecationRefactor(
                            log=f"Set flag '{behavior_change_flag}' to 'True' - This will {behavior_change_flag_to_explainations[behavior_change_flag]}.",
                            deprecation="SourceFreshnessProjectHooksNotRun"
                        )
                    )

    return YMLRuleRefactorResult(
            rule_name="flip_behavior_flags",
            refactored=refactored,
            refactored_yaml=DbtYAML().dump_to_string(yml_dict) if refactored else yml_str,  # type: ignore
            original_yaml=yml_str,
            deprecation_refactors=deprecation_refactors,
        )

def changeset_dbt_project_flip_test_arguments_behavior_flag(yml_str: str) -> YMLRuleRefactorResult:
    yml_dict = DbtYAML().load(yml_str) or {}
    deprecation_refactors: List[DbtDeprecationRefactor] = []
    refactored = False

    existing_flags = yml_dict.get("flags", {})
    if existing_flags.get("require_generic_test_arguments_property") is False or "require_generic_test_arguments_property" not in existing_flags:
        yml_dict["flags"] = existing_flags
        yml_dict["flags"]["require_generic_test_arguments_property"] = True
        refactored = True
        deprecation_refactors.append(
            DbtDeprecationRefactor(
                log="Set flag 'require_generic_test_arguments_property' to 'True' - This will parse the values defined within the `arguments` property of test definition as the test keyword arguments.",
                deprecation="MissingGenericTestArgumentsPropertyDeprecation"
            )
        )

    return YMLRuleRefactorResult(
            rule_name="changeset_dbt_project_flip_test_arguments_behavior_flag",
            refactored=refactored,
            refactored_yaml=DbtYAML().dump_to_string(yml_dict) if refactored else yml_str,  # type: ignore
            original_yaml=yml_str,
            deprecation_refactors=deprecation_refactors,
        )

def get_dbt_files_paths(root_path: Path, include_packages: bool = False) -> Dict[str, str]:
    """Get model and macro paths from dbt_project.yml

    Args:
        path: Project root path
        include_packages: Whether to include packages in the refactoring

    Returns:
        A list of paths to the models, macros, tests, analyses, and snapshots
    """

    if not (root_path / "dbt_project.yml").exists():
        error_console.print(f"Error: dbt_project.yml not found in {root_path}", style="red")
        return {}

    with open(root_path / "dbt_project.yml", "r") as f:
        project_config = safe_load(f)

    if project_config is None:
        return {}

    key_to_paths = {
        "model-paths": project_config.get("model-paths", ["models"]),
        "seed-paths": project_config.get("seed-paths", ["seeds"]),
        "macro-paths": project_config.get("macro-paths", ["macros"]),
        "test-paths": project_config.get("test-paths", ["tests"]),
        "analysis-paths": project_config.get("analysis-paths", ["analyses"]),
        "snapshot-paths": project_config.get("snapshot-paths", ["snapshots"]),
    }

    key_to_node_type = {
        "model-paths": "models",
        "seed-paths": "seeds",
        "macro-paths": "macros",
        "test-paths": "tests",
        "analysis-paths": "analyses",
        "snapshot-paths": "snapshots",
    }

    path_to_node_type = {}

    for key, paths in key_to_paths.items():
        if not isinstance(paths, list):
            error_console.print(f"Warning: Paths '{paths}' for '{key}' cannot be autofixed", style="yellow")
            continue
        for path in paths:
            path_to_node_type[str(path)] = key_to_node_type[key]

    if include_packages:
        packages_path = project_config.get("packages-paths", "dbt_packages")
        packages_dir = root_path / packages_path

        if packages_dir.exists():
            for package_folder in packages_dir.iterdir():
                if package_folder.is_dir():
                    package_dbt_project = package_folder / "dbt_project.yml"
                    if package_dbt_project.exists():
                        with open(package_dbt_project, "r") as f:
                            package_config = safe_load(f)

                        package_model_paths = package_config.get("model-paths", ["models"])
                        package_seed_paths = package_config.get("seed-paths", ["seeds"])
                        package_macro_paths = package_config.get("macro-paths", ["macros"])
                        package_test_paths = package_config.get("test-paths", ["tests"])
                        package_analysis_paths = package_config.get("analysis-paths", ["analyses"])
                        package_snapshot_paths = package_config.get("snapshot-paths", ["snapshots"])

                        # Combine package folder path with each path type
                        for model_path in package_model_paths:
                            path_to_node_type[str(package_folder / model_path)] = "models"
                        for seed_path in package_seed_paths:
                            path_to_node_type[str(package_folder / seed_path)] = "seeds"
                        for macro_path in package_macro_paths:
                            path_to_node_type[str(package_folder / macro_path)] = "macros"
                        for test_path in package_test_paths:
                            path_to_node_type[str(package_folder / test_path)] = "tests"
                        for analysis_path in package_analysis_paths:
                            path_to_node_type[str(package_folder / analysis_path)] = "analyses"
                        for snapshot_path in package_snapshot_paths:
                            path_to_node_type[str(package_folder / snapshot_path)] = "snapshots"

    return path_to_node_type


def get_dbt_roots_paths(root_path: Path, include_packages: bool = False) -> Set[str]:
    """Get all dbt root paths, the main one and the ones under dbt_packages directory if we want to include packages.

    Args:
        root_path: Project root path

    Returns:
        Set of package folder paths as strings
    """
    dbt_roots_paths = {str(root_path)}
    dbt_packages_path = root_path / "dbt_packages"

    if include_packages and dbt_packages_path.exists() and dbt_packages_path.is_dir():
        for package_folder in dbt_packages_path.iterdir():
            if package_folder.is_dir():
                dbt_roots_paths.add(str(package_folder))

    return dbt_roots_paths


def changeset_all_sql_yml_files(  # noqa: PLR0913
    path: Path,
    schema_specs: SchemaSpecs,
    dry_run: bool = False,
    exclude_dbt_project_keys: bool = False,
    select: Optional[List[str]] = None,
    include_packages: bool = False,
    behavior_change: bool = False,
    all: bool = False,
) -> Tuple[List[YMLRefactorResult], List[SQLRefactorResult]]:
    """Process all YAML files and SQL files in the project

    Args:
        path: Project root path
        schema_specs: The schema specifications to use
        dry_run: Whether to perform a dry run
        exclude_dbt_project_keys: Whether to exclude dbt project keys
        select: List of paths to select
        include_packages: Whether to include packages in the refactoring
        behavior_change: Whether to apply fixes that may lead to behavior changes
        all: Whether to run all fixes, including those that may require a behavior change

    Returns:
        Tuple containing:
        - List of YAML refactor results
        - List of SQL refactor results
    """
    dbt_paths_to_node_type = get_dbt_files_paths(path, include_packages)
    dbt_paths = list(dbt_paths_to_node_type.keys())
    dbt_roots_paths = get_dbt_roots_paths(path, include_packages)

    sql_results = process_sql_files(path, dbt_paths_to_node_type, schema_specs, dry_run, select, behavior_change, all)

    # Process dbt_project.yml
    dbt_project_yml_results = []
    for dbt_root_path in dbt_roots_paths:
        dbt_project_yml_results.append(
            process_dbt_project_yml(Path(dbt_root_path), schema_specs, dry_run, exclude_dbt_project_keys, behavior_change, all)
        )

    # Process YAML files
    yaml_results = process_yaml_files_except_dbt_project(
        path, dbt_paths, schema_specs, dry_run, select, behavior_change, all
    )

    return [*yaml_results, *dbt_project_yml_results], sql_results


def apply_changesets(
    yaml_results: List[YMLRefactorResult],
    sql_results: List[SQLRefactorResult],
    json_output: bool = False,
) -> None:
    """Apply both YAML and SQL refactoring changes

    Args:
        yaml_results: List of YAML refactoring results
        sql_results: List of SQL refactoring results
    """
    # Apply YAML changes
    for yaml_result in yaml_results:
        if yaml_result.refactored:
            yaml_result.update_yaml_file()
            yaml_result.print_to_console(json_output)

    # Apply SQL changes
    for sql_result in sql_results:
        if sql_result.refactored:
            sql_result.update_sql_file()
        sql_result.print_to_console(json_output)
