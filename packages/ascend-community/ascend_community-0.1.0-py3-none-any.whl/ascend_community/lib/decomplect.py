"""Decomplect Ascend projects from internal template to public variants.

# Overview

This module provides the functionality to "decomplect" the internal Otto's Expeditions Ascend Project.

Publicly, the Ascend Community repository contains 3 Project templates:

1. Otto's Expeditions (`ottos-expeditions`): the full demo
2. Default (`default`): the default template with some useful examples
3. Minimal (`minimal`): a minimal template with only the essentials

For each template, there are 4 variants:

1. BigQuery (`bigquery`)
2. Databricks (`databricks`)
3. DuckDB with DuckLake (`duckdb`)
4. Snowflake (`snowflake`)

Internally, we work on a fifth `internal` variant, which for Otto's Expeditions is a superset of all other variants.

## Process

For each Project template:
  For each Project variant:
    If template == OE and variant == internal:
      SKIP
    PROCESS_PROJECT(template, variant)

For the Data Plane variants, we must:

- Remove all `flows/<flow_name>-<data_plane>/` directories that do not match the data plane
- Rename all `flows/<flow_name>-<data_plane>/` directories to `flows/<flow_name>/`
- Update all cross-Flow refs in each `flows/<flow_name>/components/<component_name>.<ext>` to match the above
- Remove all `connections/` for the other Data Planes (without deleting the other examples connections)

## Requirements

The Default template will have one `sales` Flow that takes all the sales data sources from `extract-load`
and all the sales transformations from `transform` and combines them into one Flow.

The Minimal template will have one `hello` flow, with minimal components for demonstration.

All directories with their README.md files should be preserved.

## Conventions

We use the "## Internal" heading in Markdown files to indicate any file from that line and below
should be trimmed from the output for the derived Projects (except the `internal` variants).
Our code should not assume this is a H2, but is a Markdown heading.
"""

import re
import shutil
from enum import StrEnum
from pathlib import Path
from typing import Any, Dict

import yaml
from rich.console import Console

console = Console()

# File and directory constants
README_FILE = "README.md"
ASCEND_PROJECT_FILE = "ascend_project.yaml"
IGNORE_DIRS = {"ascend-out"}

# Processing constants
INTERNAL_MARKER = "internal"
PROCESSABLE_EXTENSIONS = {".py", ".sql", ".yaml"}
VAULT_REPLACEMENTS = {"vaults.google_secret_manager": "vaults.environment"}

# Project template constants
MINIMAL_CLEANUP_DIRS = ["data", "macros", "src", "templates"]
KEPT_PROFILE_FILES = {"deployment_template.yaml", "workspace_template.yaml"}

# Sales flow component constants
SALES_READ_COMPONENTS = [
    "read_sales_stores.yaml",
    "read_sales_vendors.yaml",
    "read_sales_website.yaml",
]
SALES_TRANSFORM_COMPONENTS = [
    "sales_stores.py",
    "sales_vendors.py",
    "sales_website.py",
    "sales.py",
]
SALES_REF_NAMES = ["read_sales_stores", "read_sales_vendors", "read_sales_website"]
DATA_PLANE_REPLACEMENTS: Dict[str, Dict[str, str | Dict]] = {
    "snowflake": {
        "account": "YOUR_ACCOUNT",
        "user": "YOUR_USER",
        "role": "YOUR_ROLE",
        "warehouse": "YOUR_WAREHOUSE",
        "database": "YOUR_DATABASE",
    },
    "databricks": {
        "workspace_url": "YOUR_WORKSPACE_URL",
        "client_id": "YOUR_CLIENT_ID",
        "cluster_id": "YOUR_CLUSTER_ID",
        "cluster_http_path": "YOUR_CLUSTER_HTTP_PATH",
        "warehouse_http_path": "YOUR_WAREHOUSE_HTTP_PATH",
        "catalog": "YOUR_CATALOG",
    },
    "duckdb": {},
    "gcp": {
        "project_id": "YOUR_PROJECT_ID",
        "bigquery": {
            "dataset": "YOUR_DATASET",
        },
    },
}


class ProjectName(StrEnum):
    DEFAULT = "default"
    MINIMAL = "minimal"
    OTTOS_EXPEDITIONS = "ottos-expeditions"


class ProjectVariant(StrEnum):
    BIGQUERY = "bigquery"
    DATABRICKS = "databricks"
    DUCKDB = "duckdb"
    INTERNAL = "internal"
    SNOWFLAKE = "snowflake"


def get_projects_root() -> Path:
    return Path(__file__).parent.parent.parent.parent / "projects"


def _is_internal_variant(project_variant: ProjectVariant) -> bool:
    """Check if the project variant is internal."""
    return project_variant == ProjectVariant.INTERNAL


def _create_component_name(
    base_name: str, variant: ProjectVariant, is_internal_project: bool
) -> str:
    """Create component name based on variant and project type."""
    return f"{base_name}-{variant}" if is_internal_project else base_name


def _safe_unlink(file_path: Path) -> None:
    """Safely unlink a file if it exists."""
    if file_path.exists():
        file_path.unlink()


def _remove_cross_flow_references(content: str) -> str:
    """Remove cross-flow references from component content."""
    for variant in ProjectVariant:
        if variant != ProjectVariant.INTERNAL:
            for ref_name in SALES_REF_NAMES:
                # Remove flow parameter with trailing comma - format properly for ruff
                content = re.sub(
                    rf'ref\(\s*"{ref_name}",\s*flow="extract-load-{variant}",',
                    f'ref(\n            "{ref_name}",',
                    content,
                )
                # Remove flow parameter without trailing comma
                content = re.sub(
                    rf'ref\(\s*"{ref_name}",\s*flow="extract-load-{variant}"\s*\)',
                    f'ref("{ref_name}")',
                    content,
                )
    return content


def _clean_directory_preserving_readme(directory_path: Path) -> None:
    """Remove all items in directory except README.md."""
    if not directory_path.exists():
        return

    for item in directory_path.iterdir():
        if item.is_file() and item.name != README_FILE:
            item.unlink()
        elif item.is_dir():
            shutil.rmtree(item)


def clean_minimal_flows(project_path: Path) -> None:
    """Remove all existing flows from minimal project, keeping only README.md."""
    flows_path = project_path / "flows"
    _clean_directory_preserving_readme(flows_path)


def _replace_sensitive_values(obj: Any, data_plane_name: str) -> Any:
    """Replace sensitive values using the configured replacements for each data plane."""
    if isinstance(obj, dict):
        result = {}
        replacements = DATA_PLANE_REPLACEMENTS.get(data_plane_name, {})

        for key, value in obj.items():
            # If this key has a replacement defined, use the placeholder
            if key in replacements:
                result[key] = replacements[key]
            else:
                # Recursively process the value
                result[key] = _replace_sensitive_values(value, data_plane_name)
        return result
    elif isinstance(obj, list):
        return [_replace_sensitive_values(item, data_plane_name) for item in obj]
    else:
        # For non-dict, non-list values, return as-is
        return obj


def clean_ascend_project_yaml(
    ascend_project_path: Path, project_variant: ProjectVariant
) -> None:
    """Clean and customize ascend_project.yaml for non-internal variants."""
    with open(ascend_project_path) as f:
        config = yaml.safe_load(f)

    # Clean data plane parameters - keep only the current variant and gcp (for BigQuery)
    project_params = config.get("project", {}).get("parameters", {})
    if project_params:
        cleaned_params = {}

        # For BigQuery variant, keep GCP (which contains BigQuery settings)
        if project_variant == ProjectVariant.BIGQUERY and "gcp" in project_params:
            gcp_config = _replace_sensitive_values(project_params["gcp"].copy(), "gcp")
            cleaned_params["gcp"] = gcp_config
        # For other variants, keep only the matching data plane parameters
        elif project_variant.value in project_params:
            variant_config = _replace_sensitive_values(
                project_params[project_variant.value].copy(), project_variant.value
            )
            cleaned_params[project_variant.value] = variant_config

        config["project"]["parameters"] = cleaned_params

    # Simplify defaults - only one entry for the current variant
    if "project" in config:
        config["project"]["defaults"] = [
            {
                "kind": "Flow",
                "name": {"regex": ".*"},
                "spec": {
                    "data_plane": {"connection_name": f"data_plane_{project_variant}"}
                },
            }
        ]

    # Write back the cleaned config
    with open(ascend_project_path, "w") as f:
        yaml.dump(
            config, f, default_flow_style=False, sort_keys=False, allow_unicode=True
        )


def create_minimal_flows(project_path: Path, project_variant: ProjectVariant) -> None:
    """Create minimal hello world flows for minimal projects."""
    if _is_internal_variant(project_variant):
        # For internal variants, create hello flows for all variants
        variants_to_create = [v for v in ProjectVariant if not _is_internal_variant(v)]
        for variant in variants_to_create:
            _create_single_hello_flow(project_path, variant, is_internal_project=True)
    else:
        # For non-internal variants, create only the matching hello flow
        _create_single_hello_flow(
            project_path, project_variant, is_internal_project=False
        )


def _create_single_hello_flow(
    project_path: Path, variant: ProjectVariant, is_internal_project: bool
) -> None:
    """Create a single hello flow for the specified variant."""
    flows_path = project_path / "flows"
    hello_flow_name = _create_component_name("hello", variant, is_internal_project)
    hello_flow_path = flows_path / hello_flow_name
    components_path = hello_flow_path / "components"

    # Create directory structure
    components_path.mkdir(parents=True, exist_ok=True)

    # Create hello.yaml or hello-{variant}.yaml flow file
    flow_yaml_content = """flow:
  version: 0.1.0
"""
    (hello_flow_path / f"{hello_flow_name}.yaml").write_text(flow_yaml_content)

    # Create world.py component
    world_py_content = '''from ascend.resources import task
from ascend.common.events import log
from ascend.application.context import ComponentExecutionContext


@task()
def world(context: ComponentExecutionContext) -> None:
    """A simple hello world task component."""
    log("Hello, world!")
'''
    (components_path / "world.py").write_text(world_py_content)


def create_sales_automations(
    project_path: Path, project_variant: ProjectVariant
) -> None:
    """Create sales automations for default projects."""
    automations_path = project_path / "automations"

    if _is_internal_variant(project_variant):
        # For internal variants, create sales automations for all variants
        variants_to_create = [v for v in ProjectVariant if not _is_internal_variant(v)]
        for variant in variants_to_create:
            _create_single_sales_automation(
                automations_path, variant, is_internal_project=True
            )
    else:
        # For non-internal variants, create only the matching sales automation
        _create_single_sales_automation(
            automations_path, project_variant, is_internal_project=False
        )


def _create_single_sales_automation(
    automations_path: Path, variant: ProjectVariant, is_internal_project: bool
) -> None:
    """Create a single sales automation for the specified variant."""
    # Determine automation name and flow name based on whether this is internal project
    automation_name = _create_component_name("sales", variant, is_internal_project)
    flow_name = automation_name
    file_name = f"{automation_name}.yaml"

    automation_content = f"""automation:
  enabled: true
  name: {automation_name}
  triggers:
    sensors:
      - type: timer
        name: cron-timer
        config:
          schedule:
            cron: '0 * * * *'
  actions:
    - type: run_flow
      name: run-{automation_name}
      config:
        flow: {flow_name}
"""

    (automations_path / file_name).write_text(automation_content)


def create_sales_flow(project_path: Path, project_variant: ProjectVariant) -> None:
    """Create a sales flow combining sales components from extract-load and transform flows."""
    oe_internal_path = get_project_path(
        ProjectName.OTTOS_EXPEDITIONS, ProjectVariant.INTERNAL
    )

    if _is_internal_variant(project_variant):
        # For internal variants, create sales flows for all variants
        variants_to_create = [v for v in ProjectVariant if not _is_internal_variant(v)]
        for variant in variants_to_create:
            _create_single_sales_flow(
                project_path, variant, oe_internal_path, is_internal_project=True
            )
    else:
        # For non-internal variants, create only the matching sales flow
        _create_single_sales_flow(
            project_path, project_variant, oe_internal_path, is_internal_project=False
        )


def _create_single_sales_flow(
    project_path: Path,
    variant: ProjectVariant,
    oe_internal_path: Path,
    is_internal_project: bool = None,
) -> None:
    """Create a single sales flow for the specified variant."""
    flows_path = project_path / "flows"

    # Determine flow name based on whether this is internal project or not
    if is_internal_project is None:
        is_internal_project = any(
            (project_path / "flows").glob("*-*")
        )  # Internal project (has variant-specific flows)

    if is_internal_project:
        sales_flow_name = f"sales-{variant}"
    else:
        sales_flow_name = "sales"

    sales_flow_path = flows_path / sales_flow_name
    components_path = sales_flow_path / "components"

    # Create directory structure
    components_path.mkdir(parents=True, exist_ok=True)

    # Create sales.yaml flow file
    flow_yaml_content = """flow:
  version: 0.1.0
"""
    (sales_flow_path / f"{sales_flow_name}.yaml").write_text(flow_yaml_content)

    # Copy sales read components from extract-load flow
    extract_load_source = (
        oe_internal_path / "flows" / f"extract-load-{variant}" / "components"
    )
    for file_name in SALES_READ_COMPONENTS:
        source_file = extract_load_source / file_name
        if source_file.exists():
            shutil.copy2(source_file, components_path / file_name)

    # Copy and modify sales transform components from transform flow
    transform_source = (
        oe_internal_path / "flows" / f"transform-{variant}" / "components"
    )
    for file_name in SALES_TRANSFORM_COMPONENTS:
        source_file = transform_source / file_name
        if source_file.exists():
            content = source_file.read_text()
            content = _remove_cross_flow_references(content)
            (components_path / file_name).write_text(content)


def get_project_path(
    project_name: ProjectName,
    project_variant: ProjectVariant,
) -> Path:
    return get_projects_root() / project_name / project_variant


def remove_project(project_name: ProjectName, project_variant: ProjectVariant) -> None:
    project_path = get_project_path(project_name, project_variant)
    if project_path.exists():
        shutil.rmtree(project_path)


def _should_ignore_path(path: Path, ignore_dirs: set[str]) -> bool:
    """Check if a path should be ignored based on ignore directories."""
    return any(ignore_dir in path.parts for ignore_dir in ignore_dirs)


def copy_oe_internal(
    project_name: ProjectName,
    project_variant: ProjectVariant,
) -> None:
    """Copy Otto's Expeditions internal project as base for new project variant."""
    remove_project(project_name, project_variant)
    source = get_project_path(ProjectName.OTTOS_EXPEDITIONS, ProjectVariant.INTERNAL)
    destination = get_project_path(project_name, project_variant)

    def ignore_func(dir_path: str, names: list[str]) -> list[str]:
        """Return list of names to ignore during copy."""
        return [name for name in names if name in IGNORE_DIRS]

    shutil.copytree(source, destination, ignore=ignore_func)


def _process_flows(project_path: Path, project_variant: ProjectVariant) -> None:
    """Process flow directories: rename variant-specific flows and remove others."""
    flows_path = project_path / "flows"
    if not flows_path.exists():
        return

    # For internal variants, preserve ALL flows
    if _is_internal_variant(project_variant):
        return

    variant_suffix = f"-{project_variant}"
    flow_paths = list(flows_path.iterdir())

    for flow_path in flow_paths:
        if not flow_path.is_dir():
            continue

        if variant_suffix not in flow_path.name:
            # Remove non-matching flows for non-internal variants
            shutil.rmtree(flow_path)
            continue

        # Rename variant-specific flow to generic name
        new_name = flow_path.name.replace(variant_suffix, "")
        new_flow_path = flows_path / new_name
        flow_path.rename(new_flow_path)

        # Rename the yaml file inside the flow directory
        yaml_file = new_flow_path / f"{flow_path.name}.yaml"
        if yaml_file.exists():
            yaml_file.rename(new_flow_path / f"{new_name}.yaml")


def process_project(project_name: ProjectName, project_variant: ProjectVariant) -> None:
    """Process a project variant by cleaning and customizing it."""
    project_path = get_project_path(project_name, project_variant)

    _process_flows(project_path, project_variant)
    _process_automations(project_path, project_name, project_variant)
    _process_connections(project_path, project_name, project_variant)
    _process_directory_cleanups(project_path, project_name, project_variant)
    _process_ascend_project_yaml(project_path, project_variant)
    _process_profiles(project_path, project_variant)
    _process_all_files(project_path, project_name, project_variant)


def _process_automations(
    project_path: Path, project_name: ProjectName, project_variant: ProjectVariant
) -> None:
    """Process automation files: handle Default projects specially, others keep otto- files and rename variant files."""
    automations_path = project_path / "automations"
    if not automations_path.exists():
        return

    if project_name == ProjectName.DEFAULT:
        _process_default_automations(automations_path, project_path, project_variant)
    elif project_name == ProjectName.MINIMAL:
        _process_minimal_automations(automations_path)
    elif _is_internal_variant(project_variant):
        # For internal variants of other projects, preserve existing automations
        return
    else:
        _process_oe_automations(automations_path, project_variant)


def _process_connections(
    project_path: Path, project_name: ProjectName, project_variant: ProjectVariant
) -> None:
    """Process connection files: keep only relevant data plane connections."""
    connections_path = project_path / "connections"
    if not connections_path.exists():
        return

    expected_data_plane_file = f"data_plane_{project_variant}.yaml"

    for connection_file in connections_path.iterdir():
        if not connection_file.is_file():
            continue

        if project_name == ProjectName.MINIMAL:
            # For minimal project: keep only data_plane_<variant>.yaml and README.md
            if project_variant == ProjectVariant.INTERNAL:
                # For minimal internal: keep all data_plane_*.yaml files and README.md
                if connection_file.name == README_FILE or (
                    connection_file.name.startswith("data_plane_")
                    and connection_file.name.endswith(".yaml")
                ):
                    continue
            else:
                # For minimal non-internal: keep only matching data_plane_<variant>.yaml and README.md
                if connection_file.name in (README_FILE, expected_data_plane_file):
                    continue
            # Remove all other files (including read_* connections and non-matching data_plane files)
            connection_file.unlink()
        else:
            # For non-minimal projects: handle internal vs non-internal differently
            if project_variant == ProjectVariant.INTERNAL:
                # For non-minimal internal variants, preserve all connections
                continue

            # For non-minimal non-internal: keep read_* connections and only remove non-matching data_plane files
            is_data_plane_file = connection_file.name.startswith(
                "data_plane_"
            ) and connection_file.name.endswith(".yaml")

            if is_data_plane_file and connection_file.name != expected_data_plane_file:
                connection_file.unlink()
            # Keep read_* connections and README.md for default projects


def _process_directory_cleanups(
    project_path: Path, project_name: ProjectName, project_variant: ProjectVariant
) -> None:
    """Clean up directories based on project type and variant."""
    _cleanup_vaults_for_non_internal(project_path, project_variant)

    if project_name == ProjectName.MINIMAL:
        _setup_minimal_project(project_path, project_variant)
    elif project_name == ProjectName.DEFAULT:
        _setup_default_project(project_path, project_variant)


def _cleanup_vaults_for_non_internal(
    project_path: Path, project_variant: ProjectVariant
) -> None:
    """Remove vaults/ files (except README.md) for all non-internal projects."""
    if not _is_internal_variant(project_variant):
        vaults_path = project_path / "vaults"
        _clean_directory_preserving_readme(vaults_path)


def _setup_minimal_project(project_path: Path, project_variant: ProjectVariant) -> None:
    """Setup minimal project by cleaning directories and creating minimal flows."""
    # Clean out additional directories
    for dir_name in MINIMAL_CLEANUP_DIRS:
        dir_path = project_path / dir_name
        _clean_directory_preserving_readme(dir_path)

    # Clean out flows directory and create minimal hello world flow
    clean_minimal_flows(project_path)
    create_minimal_flows(project_path, project_variant)


def _setup_default_project(project_path: Path, project_variant: ProjectVariant) -> None:
    """Setup default project by cleaning directories and creating sales flows."""
    _clean_default_flows(project_path)
    _clean_default_templates(project_path)
    _clean_default_src(project_path)
    create_sales_flow(project_path, project_variant)


def _clean_default_flows(project_path: Path) -> None:
    """Remove all existing flows except README.md for default projects."""
    flows_path = project_path / "flows"
    if flows_path.exists():
        for item in flows_path.iterdir():
            if item.is_dir():
                shutil.rmtree(item)
            elif item.is_file() and item.name != README_FILE:
                item.unlink()


def _clean_default_templates(project_path: Path) -> None:
    """Clean out templates directory for default projects."""
    templates_path = project_path / "templates"
    _clean_directory_preserving_readme(templates_path)


def _clean_default_src(project_path: Path) -> None:
    """Remove specific files from src/ that aren't needed in default projects."""
    src_path = project_path / "src"
    nps_analysis_file = src_path / "nps_analysis.py"
    _safe_unlink(nps_analysis_file)


def _clean_profile_parameters(
    profile_path: Path, available_params: set[str], project_config: dict
) -> None:
    """Clean profile parameters to only include those available in ascend_project.yaml."""
    if not profile_path.suffix.lower() == ".yaml":
        return

    with open(profile_path) as f:
        profile_config = yaml.safe_load(f)

    if not profile_config or "profile" not in profile_config:
        return

    profile_params = profile_config.get("profile", {}).get("parameters", {})
    if not profile_params:
        return

    cleaned_params = {}

    for param_name, param_value in profile_params.items():
        # Keep parameter if it exists directly in available_params
        if param_name in available_params:
            cleaned_params[param_name] = param_value
        # Special case: keep parameters that reference available nested parameters
        elif (
            isinstance(param_value, dict)
            and "$<" in param_value
            and _is_valid_parameter_reference(
                param_value["$<"], available_params, project_config
            )
        ):
            cleaned_params[param_name] = param_value

    # Update the profile config
    profile_config["profile"]["parameters"] = cleaned_params

    # Write back the cleaned config
    with open(profile_path, "w") as f:
        yaml.dump(
            profile_config,
            f,
            default_flow_style=False,
            sort_keys=False,
            allow_unicode=True,
        )


def _is_valid_parameter_reference(
    ref: str, available_params: set[str], project_config: dict
) -> bool:
    """Check if a parameter reference is valid given the available parameters."""
    # Handle references like "$parameters.gcp.bigquery"
    if not ref.startswith("$parameters."):
        return False

    # Extract the path after "$parameters."
    param_path = ref[len("$parameters.") :]
    path_parts = param_path.split(".")

    if not path_parts:
        return False

    # Check if the root parameter exists
    root_param = path_parts[0]
    if root_param not in available_params:
        return False

    # Check if the nested path exists in the project config
    try:
        current = (
            project_config.get("project", {}).get("parameters", {}).get(root_param)
        )
        for part in path_parts[1:]:
            if not isinstance(current, dict) or part not in current:
                return False
            current = current[part]
        return True
    except (TypeError, KeyError):
        return False


def _process_profiles(project_path: Path, project_variant: ProjectVariant) -> None:
    """Process profile files: keep only default profiles for non-internal variants and clean parameters."""
    profiles_path = project_path / "profiles"
    if not profiles_path.exists() or _is_internal_variant(project_variant):
        return

    # Get available parameters from ascend_project.yaml
    ascend_project_path = project_path / ASCEND_PROJECT_FILE
    available_params = set()
    project_config = {}
    if ascend_project_path.exists():
        with open(ascend_project_path) as f:
            project_config = yaml.safe_load(f)
            project_params = project_config.get("project", {}).get("parameters", {})
            available_params = set(project_params.keys())

    for profile_path in profiles_path.iterdir():
        if profile_path.name not in KEPT_PROFILE_FILES:
            profile_path.unlink()
        else:
            # Clean parameters in kept profile files
            _clean_profile_parameters(profile_path, available_params, project_config)


def _process_ascend_project_yaml(
    project_path: Path, project_variant: ProjectVariant
) -> None:
    """Process ascend_project.yaml for non-internal variants."""
    if _is_internal_variant(project_variant):
        return

    ascend_project_path = project_path / ASCEND_PROJECT_FILE
    if ascend_project_path.exists():
        clean_ascend_project_yaml(ascend_project_path, project_variant)


def _process_all_files(
    project_path: Path, project_name: ProjectName, project_variant: ProjectVariant
) -> None:
    """Process all files in the project directory."""
    for file_path in project_path.glob("**/*"):
        if file_path.is_file():
            process_file(project_name, project_variant, file_path)


def process_file(
    project_name: ProjectName,
    project_variant: ProjectVariant,
    file_path: Path,
) -> None:
    """Process individual files based on their type and variant."""
    # Skip ascend_project.yaml as it's handled separately by clean_ascend_project_yaml
    if file_path.name == ASCEND_PROJECT_FILE:
        return

    # Skip profile files as they're handled separately by _process_profiles
    if file_path.parent.name == "profiles" and file_path.name in KEPT_PROFILE_FILES:
        return

    if file_path.suffix.lower() == ".md":
        strip_internal_section(file_path)
    elif file_path.suffix.lower() in PROCESSABLE_EXTENSIONS:
        _process_code_file(file_path, project_variant)


def _process_code_file(file_path: Path, project_variant: ProjectVariant) -> None:
    """Process code files: remove variant suffixes and update vault references."""
    if _is_internal_variant(project_variant):
        return

    content = file_path.read_text()
    original_content = content

    # Replace variant suffixes
    for variant in ProjectVariant:
        if not _is_internal_variant(variant):
            content = content.replace(f"-{variant}", "")

    # Replace vault references with default environment vault
    for old_vault, new_vault in VAULT_REPLACEMENTS.items():
        content = content.replace(old_vault, new_vault)

    if content != original_content:
        file_path.write_text(content)


def _process_default_automations(
    automations_path: Path, project_path: Path, project_variant: ProjectVariant
) -> None:
    """Process automations for default projects."""
    _remove_non_otto_automations(automations_path)
    create_sales_automations(project_path, project_variant)


def _process_minimal_automations(automations_path: Path) -> None:
    """Process automations for minimal projects."""
    _remove_non_otto_automations(automations_path)


def _process_oe_automations(
    automations_path: Path, project_variant: ProjectVariant
) -> None:
    """Process automations for Otto's Expeditions projects."""
    variant_suffix = f"-{project_variant}"

    for automation_file in automations_path.iterdir():
        if not automation_file.is_file():
            continue

        # Keep otto- files and README
        if _should_keep_automation_file(automation_file.name):
            continue

        # Rename our variant's files
        if variant_suffix in automation_file.name:
            new_name = automation_file.name.replace(variant_suffix, "")
            automation_file.rename(automations_path / new_name)
            continue

        # Delete other variant's files
        if _is_other_variant_file(automation_file.name, project_variant):
            automation_file.unlink()


def _remove_non_otto_automations(automations_path: Path) -> None:
    """Remove all automation files except otto- files and README."""
    for automation_file in automations_path.iterdir():
        if not automation_file.is_file():
            continue
        if not _should_keep_automation_file(automation_file.name):
            automation_file.unlink()


def _should_keep_automation_file(filename: str) -> bool:
    """Check if an automation file should be kept."""
    return filename.startswith("otto-") or filename == README_FILE


def _is_other_variant_file(filename: str, current_variant: ProjectVariant) -> bool:
    """Check if a file belongs to a different variant."""
    return any(
        f"-{v}" in filename
        for v in ProjectVariant
        if v not in (current_variant, ProjectVariant.INTERNAL)
    )


def strip_internal_section(file_path: Path) -> None:
    """Remove internal sections from markdown files marked with '## Internal' headers."""
    lines = file_path.read_text().splitlines()
    result = []

    for line in lines:
        stripped_line = line.strip().lower()
        if stripped_line.startswith("#") and INTERNAL_MARKER in stripped_line:
            break
        result.append(line)

    if len(result) < len(lines):  # Only write if we actually removed content
        file_path.write_text("\n".join(result) + "\n")


def run(clean: bool = False) -> None:
    """Run the atomization process for all project templates and variants.

    Args:
        clean: If True, only remove existing projects without recreating them.
    """
    for project_name in ProjectName:
        console.print(f"Processing project: {project_name}", style="bold blue")

        for project_variant in ProjectVariant:
            console.print(f"  Variant: {project_variant}", style="bold green")

            # Skip internal variant for Otto's Expeditions (it's the source)
            if (
                project_name == ProjectName.OTTOS_EXPEDITIONS
                and project_variant == ProjectVariant.INTERNAL
            ):
                console.print("    Skipping source of truth!", style="yellow")
                continue

            # If clean mode is enabled, remove the project without processing further
            if clean:
                remove_project(project_name, project_variant)
                continue

            copy_oe_internal(project_name, project_variant)
            process_project(project_name, project_variant)
