import json
import yaml
import typer
import questionary
from pathlib import Path
from typing import Optional, Dict, Any, List
from .dependency_tracer import DependencyTracer
from .multi_file_tracer import MultiFileDependencyTracer

# Export main classes for library usage
__all__ = [
    'DependencyTracer',
    'MultiFileDependencyTracer', 
    'make_json_serializable',
    'dependencies_to_tree',
    'format_dependencies_as_yaml',
    'format_tree_as_yaml'
]


def make_json_serializable(data: Any) -> Any:
    """
    Clean data to make it JSON serializable by removing AST nodes and other non-serializable objects.
    """
    if isinstance(data, dict):
        result = {}
        for key, value in data.items():
            # Skip AST nodes and other non-serializable keys
            if key in ["node"]:
                continue
            result[key] = make_json_serializable(value)
        return result
    elif isinstance(data, list):
        return [make_json_serializable(item) for item in data]
    elif hasattr(data, "__dict__") and not isinstance(data, (str, int, float, bool)):
        # Skip complex objects that aren't basic Python types
        return str(data)
    else:
        return data


def dependencies_to_tree(
    dependencies: List[Dict[str, Any]],
    root_variable: str,
    tracer=None,
    file_path: str = None,
) -> Dict[str, Any]:
    """
    Convert flat dependency list to nested tree structure.

    The approach: Re-trace the dependencies starting from the root, but this time
    build a tree structure directly instead of a flat list.

    Args:
        dependencies: Flat list of dependency dictionaries (for reference)
        root_variable: The root variable name to start the tree from
        tracer: The tracer object (MultiFileDependencyTracer or DependencyTracer)
        file_path: The file path for single-file analysis

    Returns:
        Nested dictionary representing the dependency tree
    """
    if not dependencies:
        return {"variable": root_variable, "error": "No dependencies found"}

    if not tracer:
        return {
            "variable": root_variable,
            "error": "Tracer required for tree generation",
        }

    # We need to re-trace to build the proper tree structure
    visited_assignments = set()  # Track (file_path, var_name, line_number) tuples

    def build_tree_node(
        var_name: str,
        current_file: str,
        current_line: Optional[int] = None,
        depth: int = 0,
    ) -> Dict[str, Any]:
        """Build a tree node recursively."""
        if depth >= 10:  # Max depth limit
            return {
                "variable": var_name,
                "error": "Max depth reached",
                "file_path": current_file,
                "line_number": current_line,
            }

        # Check if this is a multi-file or single-file tracer
        if hasattr(tracer, "file_tracers"):  # MultiFileDependencyTracer
            # First, try to find the variable in the current/specified file
            file_tracer = tracer.file_tracers.get(current_file)
            if file_tracer:
                var_info = file_tracer.find_variable_assignment(var_name, current_line)
                if var_info:
                    assignment_id = (current_file, var_name, var_info["line_number"])

                    # Always build the node data to show the reference
                    node_data = {
                        "variable": var_name,
                        "type": "variable",
                        "line_number": var_info["line_number"],
                        "source_code": var_info["source_code"],
                        "file_path": current_file,
                    }

                    # Only recurse if we haven't visited this assignment before (to prevent infinite recursion)
                    if assignment_id not in visited_assignments:
                        visited_assignments.add(assignment_id)

                        # Add dependencies recursively
                        child_deps = []
                        for dep_var in var_info["dependencies"]:
                            child_node = build_tree_node(
                                dep_var,
                                current_file,
                                var_info["line_number"],
                                depth + 1,
                            )
                            child_deps.append(child_node)

                        if child_deps:
                            node_data["dependencies"] = child_deps

                    return node_data

            # If not found in current file, look for cross-file dependencies
            if var_name in tracer.global_variables:
                def_file, def_line = tracer.global_variables[var_name]

                if def_file != current_file:
                    # Truly cross-file dependency
                    assignment_id = (def_file, var_name, def_line)
                    cross_file_tracer = tracer.file_tracers.get(def_file)
                    if cross_file_tracer:
                        # For cross-file references, use the assignment tracked in global_variables
                        # Find the specific assignment at the tracked line
                        all_assignments = cross_file_tracer.get_all_variables().get(
                            var_name, []
                        )
                        var_info = None
                        for assignment in all_assignments:
                            if assignment["line_number"] == def_line:
                                var_info = assignment
                                break

                        if var_info:
                            # Always build the node data to show the reference
                            node_data = {
                                "variable": var_name,
                                "type": "cross_file_variable",
                                "line_number": var_info["line_number"],
                                "source_code": var_info["source_code"],
                                "file_path": def_file,
                            }

                            # Only recurse if we haven't visited this assignment before
                            if assignment_id not in visited_assignments:
                                visited_assignments.add(assignment_id)

                                # Add dependencies recursively
                                child_deps = []
                                for dep_var in var_info["dependencies"]:
                                    child_node = build_tree_node(
                                        dep_var,
                                        def_file,
                                        var_info["line_number"],
                                        depth + 1,
                                    )
                                    child_deps.append(child_node)

                                if child_deps:
                                    node_data["dependencies"] = child_deps

                            return node_data
                else:
                    # Same file - check if the assignment in global_variables comes before current_line
                    if current_line is None or def_line < current_line:
                        # This assignment comes before our reference point, so it's valid
                        assignment_id = (def_file, var_name, def_line)
                        same_file_tracer = tracer.file_tracers.get(def_file)
                        if same_file_tracer:
                            # Find the specific assignment at the line tracked in global_variables
                            all_assignments = same_file_tracer.get_all_variables().get(
                                var_name, []
                            )
                            var_info = None
                            for assignment in all_assignments:
                                if assignment["line_number"] == def_line:
                                    var_info = assignment
                                    break

                            if var_info:
                                # Always build the node data to show the reference
                                node_data = {
                                    "variable": var_name,
                                    "type": "variable",
                                    "line_number": var_info["line_number"],
                                    "source_code": var_info["source_code"],
                                    "file_path": def_file,
                                }

                                # Only recurse if we haven't visited this assignment before
                                if assignment_id not in visited_assignments:
                                    visited_assignments.add(assignment_id)

                                    # Add dependencies recursively
                                    child_deps = []
                                    for dep_var in var_info["dependencies"]:
                                        child_node = build_tree_node(
                                            dep_var,
                                            def_file,
                                            var_info["line_number"],
                                            depth + 1,
                                        )
                                        child_deps.append(child_node)

                                    if child_deps:
                                        node_data["dependencies"] = child_deps

                                return node_data
                    # If def_line >= current_line, then this assignment comes after our reference point
                    # and should not be followed (temporal ordering violation)

            # Check for functions/classes
            elif var_name in tracer.global_definitions:
                def_file, def_line = tracer.global_definitions[var_name]
                assignment_id = (def_file, var_name, def_line)
                if assignment_id not in visited_assignments:
                    visited_assignments.add(assignment_id)

                    return {
                        "variable": var_name,
                        "type": "cross_file_function",
                        "line_number": def_line,
                        "source_code": tracer._get_definition_source(
                            def_file, def_line
                        ),
                        "file_path": def_file,
                    }

            # Out of scope dependency
            return {
                "variable": var_name,
                "type": "out_of_scope",
                "line_number": None,
                "source_code": f"# {var_name} - dependency chain leaves scope (external import or builtin)",
                "file_path": None,
            }

        else:  # Single-file DependencyTracer
            var_info = tracer.find_variable_assignment(var_name, current_line)
            if var_info:
                assignment_id = (current_file, var_name, var_info["line_number"])
                if assignment_id not in visited_assignments:
                    visited_assignments.add(assignment_id)

                    node_data = {
                        "variable": var_name,
                        "type": "variable",
                        "line_number": var_info["line_number"],
                        "source_code": var_info["source_code"],
                        "file_path": current_file,
                    }

                    # Add dependencies recursively
                    child_deps = []
                    for dep_var in var_info["dependencies"]:
                        child_node = build_tree_node(
                            dep_var, current_file, var_info["line_number"], depth + 1
                        )
                        child_deps.append(child_node)

                    if child_deps:
                        node_data["dependencies"] = child_deps

                    return node_data
                else:
                    # This assignment was already visited, but we still want to show it in the tree
                    # for completeness in tree structure (unlike flat structure)
                    return {
                        "variable": var_name,
                        "type": "circular_reference",
                        "line_number": var_info["line_number"],
                        "source_code": var_info["source_code"],
                        "file_path": current_file,
                        "note": "circular reference - already processed above",
                        # No dependencies to avoid infinite recursion
                    }

            # Unresolved in single file
            return {
                "variable": var_name,
                "type": "unresolved",
                "line_number": None,
                "source_code": f"# {var_name} - not found in file (external import or builtin)",
                "file_path": current_file,
            }

    # Start building the tree from the root
    return build_tree_node(root_variable, file_path)


def format_dependencies_as_yaml(
    dependencies: List[Dict[str, Any]],
    variable: str,
    source_file: str,
    scope: Optional[str] = None,
    analysis_type: str = "single_file",
) -> str:
    """Format dependencies as YAML for readable output."""

    # Create the main structure with minimal visual noise
    yaml_data = {"dependencies": []}

    # Convert dependencies to a cleaner format for YAML
    for dep in dependencies:
        source_code = dep.get("source_code", "").strip()

        clean_dep = {
            "variable": dep["variable"],
            "source": source_code,
        }

        # Add file:line for editor navigation
        if dep.get("file_path") and dep.get("line_number") is not None:
            clean_dep["file"] = f"{dep['file_path']}:{dep['line_number']}"

        # Add type if it's not a standard variable
        if dep.get("type") and dep.get("type") != "variable":
            clean_dep["type"] = dep.get("type")

        yaml_data["dependencies"].append(clean_dep)

    # Add analysis metadata at the end
    yaml_data["analysis"] = {
        "variable": variable,
        "source_file": source_file,
        "scope": scope or source_file,
        "type": analysis_type,
    }

    # Custom YAML dump with literal block scalars for multiline strings
    return _dump_yaml_with_literal_blocks(yaml_data)


def format_tree_as_yaml(
    tree_data: Dict[str, Any],
    variable: str,
    source_file: str,
    scope: Optional[str] = None,
    analysis_type: str = "single_file",
) -> str:
    """Format tree structure as YAML for readable output."""

    def clean_tree_node(node: Dict[str, Any], depth: int = 0) -> Dict[str, Any]:
        """Recursively clean tree node for YAML output."""
        source_code = node.get("source_code", "").strip()

        clean_node = {"variable": node["variable"], "source": source_code}

        # Add file:line for editor navigation
        if node.get("file_path") and node.get("line_number") is not None:
            clean_node["file"] = f"{node['file_path']}:{node['line_number']}"

        # Add type if it's not a standard variable
        if node.get("type") and node.get("type") != "variable":
            clean_node["type"] = node.get("type")

        # Add error if present
        if node.get("error"):
            clean_node["error"] = node.get("error")

        # Add note if present (for circular references)
        if node.get("note"):
            clean_node["note"] = node.get("note")

        # Handle dependencies recursively
        if "dependencies" in node and node["dependencies"]:
            clean_node["dependencies"] = [
                clean_tree_node(child, depth + 1) for child in node["dependencies"]
            ]

        return clean_node

    yaml_data = {
        "dependency_tree": clean_tree_node(tree_data),
        "analysis": {
            "variable": variable,
            "source_file": source_file,
            "scope": scope or source_file,
            "type": analysis_type,
            "format": "tree",
        },
    }

    return _dump_yaml_with_literal_blocks(yaml_data)


def _dump_yaml_with_literal_blocks(data: Any) -> str:
    """Custom YAML dumper that uses literal block scalars for multiline strings."""

    class LiteralStr(str):
        """String subclass to trigger literal block scalar output."""

        pass

    def represent_literal_str(dumper, data):
        """Custom representer for literal strings."""
        return dumper.represent_scalar("tag:yaml.org,2002:str", data, style="|")

    # Custom representer function to handle multiline strings
    def convert_multiline_strings(obj):
        """Recursively convert multiline strings to LiteralStr objects."""
        if isinstance(obj, dict):
            return {k: convert_multiline_strings(v) for k, v in obj.items()}
        elif isinstance(obj, list):
            return [convert_multiline_strings(item) for item in obj]
        elif isinstance(obj, str) and ("\n" in obj or len(obj) > 80):
            return LiteralStr(obj)
        else:
            return obj

    # Convert multiline strings
    converted_data = convert_multiline_strings(data)

    # Create custom dumper
    yaml.add_representer(LiteralStr, represent_literal_str)

    try:
        return yaml.dump(
            converted_data,
            default_flow_style=False,
            sort_keys=False,
            width=100,
            allow_unicode=True,
            indent=2,
        )
    finally:
        # Clean up the representer to avoid affecting other YAML operations
        if LiteralStr in yaml.representer.Representer.yaml_representers:
            del yaml.representer.Representer.yaml_representers[LiteralStr]


app = typer.Typer(help="CodeSlice - Trace variable dependencies in Python code")


@app.command()
def trace(
    file_path: str = typer.Argument(
        ..., help="Path to the Python file containing the variable"
    ),
    variable: Optional[str] = typer.Option(
        None, "--var", "-v", help="Variable name to trace"
    ),
    scope: Optional[str] = typer.Option(
        None,
        "--scope",
        "-s",
        help="Directory scope for multi-file analysis (defaults to file-only)",
    ),
    function: Optional[str] = typer.Option(
        None,
        "--function",
        "-f",
        help="Function name to search within (for function-scoped variables)",
    ),
    interactive: bool = typer.Option(
        False, "--interactive", "-i", help="Interactive mode"
    ),
    max_depth: int = typer.Option(
        10, "--max-depth", "-d", help="Maximum recursion depth"
    ),
    exclude: Optional[str] = typer.Option(
        None,
        "--exclude",
        "-e",
        help="Comma-separated patterns to exclude (e.g., 'test_,__pycache__')",
    ),
    json_output: bool = typer.Option(
        False, "--json", help="Output results in JSON format"
    ),
    tree_format: bool = typer.Option(
        False, "--tree", help="Output as nested tree structure"
    ),
):
    """Trace variable dependencies in a Python file, optionally with multi-file scope."""

    # Tree format can be used with both JSON and YAML output
    # No validation needed - tree format works with both

    file_obj = Path(file_path)

    # Validate file path
    if not file_obj.exists():
        typer.echo(f"Error: File '{file_path}' does not exist", err=True)
        raise typer.Exit(1)

    if not file_obj.is_file():
        typer.echo(f"Error: '{file_path}' is not a file", err=True)
        raise typer.Exit(1)

    if not file_path.endswith(".py"):
        typer.echo(f"Error: '{file_path}' is not a Python file", err=True)
        raise typer.Exit(1)

    # Validate scope if provided
    if scope:
        scope_obj = Path(scope)
        if not scope_obj.exists():
            typer.echo(f"Error: Scope directory '{scope}' does not exist", err=True)
            raise typer.Exit(1)
        if not scope_obj.is_dir():
            typer.echo(f"Error: Scope '{scope}' is not a directory", err=True)
            raise typer.Exit(1)

    # Determine analysis mode
    use_multi_file = scope is not None

    try:
        if use_multi_file:
            # Multi-file analysis with explicit scope
            exclude_patterns = exclude.split(",") if exclude else None
            multi_tracer = MultiFileDependencyTracer(scope, exclude_patterns)

            # Ensure the target file is within scope or can be analyzed
            file_tracer = multi_tracer.get_file_tracer(file_path)
            if not file_tracer:
                # File might not be in scope, try to create a tracer for it directly
                single_tracer = DependencyTracer(file_path)
                # This is a more complex case - file outside scope but we want multi-file deps
                # For now, let's require the file to be within scope
                typer.echo(
                    f"Error: File '{file_path}' is not within the specified scope '{scope}'",
                    err=True,
                )
                raise typer.Exit(1)
        else:
            # Single-file analysis
            single_tracer = DependencyTracer(file_path)

    except ValueError as e:
        typer.echo(f"Error: {e}", err=True)
        raise typer.Exit(1)

    # Handle variable selection
    if interactive or variable is None:
        if use_multi_file:
            tracer_to_use = multi_tracer.get_file_tracer(file_path)
        else:
            tracer_to_use = single_tracer

        # Get variables, optionally filtered by function
        if function:
            # Check if the function exists
            all_functions = tracer_to_use.get_all_functions()
            if function not in all_functions:
                typer.echo(f"Function '{function}' not found in {Path(file_path).name}")
                available_functions = list(all_functions.keys())
                if available_functions:
                    typer.echo(f"Available functions: {', '.join(available_functions)}")
                raise typer.Exit(1)

            all_variables = tracer_to_use.get_all_variables(function_name=function)
            scope_desc = f"function '{function}' in {Path(file_path).name}"
        else:
            all_variables = tracer_to_use.get_all_variables()
            scope_desc = Path(file_path).name

        if not all_variables:
            typer.echo(f"No variables found in {scope_desc}")
            raise typer.Exit(1)

        if interactive:
            # Create choices showing variable name and line numbers
            choices = []
            for var_name, assignments in all_variables.items():
                if len(assignments) == 1:
                    location = f"line {assignments[0]['line_number']}"
                    if function:
                        location += f" in {function}()"
                    choices.append(f"{var_name} ({location})")
                else:
                    for assignment in assignments:
                        location = f"line {assignment['line_number']}"
                        if function:
                            location += f" in {function}()"
                        choices.append(f"{var_name} ({location})")

            selected = questionary.select(
                f"Select a variable to trace from {Path(file_path).name}:",
                choices=choices,
            ).ask()

            if not selected:
                typer.echo("No variable selected")
                raise typer.Exit(1)

            variable = selected.split(" (line ")[0]
        else:
            # List available variables
            typer.echo(f"Available variables in {scope_desc}:")
            for var_name, assignments in all_variables.items():
                if len(assignments) == 1:
                    location = f"line {assignments[0]['line_number']}"
                    if function:
                        location += f" in {function}()"
                    typer.echo(f"  - {var_name} ({location})")
                else:
                    locations = []
                    for assignment in assignments:
                        location = f"line {assignment['line_number']}"
                        if function:
                            location += f" in {function}()"
                        locations.append(location)
                    typer.echo(f"  - {var_name} ({', '.join(locations)})")

            typer.echo("\nUse --var <variable_name> to trace a specific variable")
            if not function:
                # Show available functions if not already scoped to a function
                all_functions = tracer_to_use.get_all_functions()
                if all_functions:
                    func_names = list(all_functions.keys())
                    typer.echo(
                        f"Use --function <function_name> to scope to a function. Available: {', '.join(func_names)}"
                    )
            raise typer.Exit(0)

    # Generate dependency analysis
    if use_multi_file:
        dependencies = multi_tracer.trace_dependencies_multi_file(
            variable, file_path, max_depth=max_depth
        )
        if json_output:
            if tree_format:
                # Generate tree structure
                tree_data = dependencies_to_tree(
                    dependencies, variable, multi_tracer, file_path
                )
                result = {
                    "variable": variable,
                    "source_file": file_path,
                    "scope": scope,
                    "analysis_type": "multi_file",
                    "format": "tree",
                    "dependency_tree": make_json_serializable(tree_data),
                }
            else:
                # Generate flat list
                result = {
                    "variable": variable,
                    "source_file": file_path,
                    "scope": scope,
                    "analysis_type": "multi_file",
                    "format": "flat",
                    "dependencies": make_json_serializable(dependencies),
                }
            typer.echo(json.dumps(result, indent=2))
        else:
            if tree_format:
                # Generate tree structure for YAML output
                tree_data = dependencies_to_tree(
                    dependencies, variable, multi_tracer, file_path
                )
                yaml_output = format_tree_as_yaml(
                    tree_data, variable, file_path, scope, "multi_file"
                )
                typer.echo(yaml_output)
            else:
                # Generate flat YAML output
                yaml_output = format_dependencies_as_yaml(
                    dependencies, variable, file_path, scope, "multi_file"
                )
                typer.echo(yaml_output)
    else:
        dependencies = single_tracer.trace_dependencies(
            variable, max_depth=max_depth, function_name=function
        )
        if json_output:
            if tree_format:
                # Generate tree structure
                tree_data = dependencies_to_tree(
                    dependencies, variable, single_tracer, file_path
                )
                result = {
                    "variable": variable,
                    "source_file": file_path,
                    "scope": file_path,
                    "analysis_type": "single_file",
                    "format": "tree",
                    "dependency_tree": make_json_serializable(tree_data),
                }
            else:
                # Generate flat list
                result = {
                    "variable": variable,
                    "source_file": file_path,
                    "scope": file_path,
                    "analysis_type": "single_file",
                    "format": "flat",
                    "dependencies": make_json_serializable(dependencies),
                }
            typer.echo(json.dumps(result, indent=2))
        else:
            if tree_format:
                # Generate tree structure for YAML output
                tree_data = dependencies_to_tree(
                    dependencies, variable, single_tracer, file_path
                )
                yaml_output = format_tree_as_yaml(
                    tree_data, variable, file_path, file_path, "single_file"
                )
                typer.echo(yaml_output)
            else:
                # Generate flat YAML output
                yaml_output = format_dependencies_as_yaml(
                    dependencies, variable, file_path, file_path, "single_file"
                )
                typer.echo(yaml_output)


@app.command()
def list_vars(
    path: str = typer.Argument(
        ..., help="Path to the Python file or directory to analyze"
    ),
    scope: Optional[str] = typer.Option(
        None,
        "--scope",
        "-s",
        help="Directory scope for multi-file listing (when path is a file)",
    ),
    exclude: Optional[str] = typer.Option(
        None, "--exclude", "-e", help="Comma-separated patterns to exclude"
    ),
    json_output: bool = typer.Option(
        False, "--json", help="Output results in JSON format"
    ),
):
    """List all variables in a Python file, or all files in a directory."""

    path_obj = Path(path)

    if not path_obj.exists():
        typer.echo(f"Error: Path '{path}' does not exist", err=True)
        raise typer.Exit(1)

    # Determine if we're listing a single file or directory
    if path_obj.is_file():
        if scope:
            # File with directory scope - list all files in scope
            scope_obj = Path(scope)
            if not scope_obj.exists() or not scope_obj.is_dir():
                typer.echo(
                    f"Error: Scope '{scope}' must be an existing directory", err=True
                )
                raise typer.Exit(1)

            # Multi-file listing with specific scope
            exclude_patterns = exclude.split(",") if exclude else None
            try:
                multi_tracer = MultiFileDependencyTracer(scope, exclude_patterns)
                all_files = multi_tracer.get_all_files()

                if not all_files:
                    typer.echo(f"No Python files found in scope directory '{scope}'")
                    return

                # Collect all variables from all files
                all_file_vars = {}
                for file_path in all_files:
                    file_tracer = multi_tracer.get_file_tracer(file_path)
                    if file_tracer:
                        variables = file_tracer.get_all_variables()
                        if variables:
                            relative_path = str(Path(file_path).relative_to(scope))
                            all_file_vars[relative_path] = {
                                "file_path": file_path,
                                "variables": variables,
                            }

                if json_output:
                    result = {
                        "listing_type": "multi_file_with_scope",
                        "scope": scope,
                        "target_file": path,
                        "files": make_json_serializable(all_file_vars),
                    }
                    typer.echo(json.dumps(result, indent=2))
                else:
                    typer.echo(f"Variables in scope: {Path(scope).name}")
                    typer.echo("=" * 50)

                    for relative_path, file_info in sorted(all_file_vars.items()):
                        typer.echo(f"\n📁 {relative_path}:")
                        typer.echo("-" * 30)

                        for var_name, assignments in file_info["variables"].items():
                            if len(assignments) == 1:
                                assignment = assignments[0]
                                typer.echo(
                                    f"  {var_name} (line {assignment['line_number']})"
                                )
                                source = (
                                    assignment["source_code"][:80] + "..."
                                    if len(assignment["source_code"]) > 80
                                    else assignment["source_code"]
                                )
                                typer.echo(f"    {source}")
                            else:
                                lines = ", ".join(
                                    str(a["line_number"]) for a in assignments
                                )
                                typer.echo(
                                    f"  {var_name} (multiple assignments: lines {lines})"
                                )

            except Exception as e:
                typer.echo(f"Error: {e}", err=True)
                raise typer.Exit(1)
        else:
            # Single file listing
            if not path.endswith(".py"):
                typer.echo(f"Error: '{path}' is not a Python file", err=True)
                raise typer.Exit(1)

            try:
                tracer = DependencyTracer(path)
                all_variables = tracer.get_all_variables()

                if not all_variables:
                    if json_output:
                        result = {
                            "listing_type": "single_file",
                            "file_path": path,
                            "variables": {},
                        }
                        typer.echo(json.dumps(result, indent=2))
                    else:
                        typer.echo("No variables found in the file")
                    return

                if json_output:
                    result = {
                        "listing_type": "single_file",
                        "file_path": path,
                        "variables": make_json_serializable(all_variables),
                    }
                    typer.echo(json.dumps(result, indent=2))
                else:
                    typer.echo(f"Variables in {Path(path).name}:")
                    typer.echo("=" * 40)

                    for var_name, assignments in all_variables.items():
                        if len(assignments) == 1:
                            assignment = assignments[0]
                            typer.echo(
                                f"  {var_name} (line {assignment['line_number']})"
                            )
                            typer.echo(f"    {assignment['source_code']}")
                            typer.echo()
                        else:
                            typer.echo(f"  {var_name} (multiple assignments):")
                            for assignment in assignments:
                                typer.echo(
                                    f"    Line {assignment['line_number']}: {assignment['source_code']}"
                                )
                            typer.echo()

            except ValueError as e:
                typer.echo(f"Error: {e}", err=True)
                raise typer.Exit(1)

    elif path_obj.is_dir():
        # Directory listing
        exclude_patterns = exclude.split(",") if exclude else None
        try:
            multi_tracer = MultiFileDependencyTracer(path, exclude_patterns)
            all_files = multi_tracer.get_all_files()

            if not all_files:
                if json_output:
                    result = {
                        "listing_type": "directory",
                        "directory_path": path,
                        "files": {},
                    }
                    typer.echo(json.dumps(result, indent=2))
                else:
                    typer.echo(f"No Python files found in directory '{path}'")
                return

            # Collect all variables from all files
            all_file_vars = {}
            for file_path in all_files:
                file_tracer = multi_tracer.get_file_tracer(file_path)
                if file_tracer:
                    variables = file_tracer.get_all_variables()
                    if variables:
                        relative_path = str(Path(file_path).relative_to(path))
                        all_file_vars[relative_path] = {
                            "file_path": file_path,
                            "variables": variables,
                        }

            if json_output:
                result = {
                    "listing_type": "directory",
                    "directory_path": path,
                    "files": make_json_serializable(all_file_vars),
                }
                typer.echo(json.dumps(result, indent=2))
            else:
                typer.echo(f"Variables in directory: {Path(path).name}")
                typer.echo("=" * 50)

                for relative_path, file_info in sorted(all_file_vars.items()):
                    typer.echo(f"\n📁 {relative_path}:")
                    typer.echo("-" * 30)

                    for var_name, assignments in file_info["variables"].items():
                        if len(assignments) == 1:
                            assignment = assignments[0]
                            typer.echo(
                                f"  {var_name} (line {assignment['line_number']})"
                            )
                            source = (
                                assignment["source_code"][:80] + "..."
                                if len(assignment["source_code"]) > 80
                                else assignment["source_code"]
                            )
                            typer.echo(f"    {source}")
                        else:
                            lines = ", ".join(
                                str(a["line_number"]) for a in assignments
                            )
                            typer.echo(
                                f"  {var_name} (multiple assignments: lines {lines})"
                            )

        except Exception as e:
            typer.echo(f"Error: {e}", err=True)
            raise typer.Exit(1)

    else:
        typer.echo(f"Error: '{path}' is neither a file nor a directory", err=True)
        raise typer.Exit(1)


def main() -> None:
    app()
