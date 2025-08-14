import ast
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple
from .dependency_tracer import DependencyTracer


class MultiFileDependencyTracer:
    """
    Traces variable dependencies across multiple Python files in a directory.
    Handles imports and cross-file references.
    """
    
    def __init__(self, directory_path: str, exclude_patterns: Optional[List[str]] = None):
        """
        Initialize the multi-file tracer.
        
        Args:
            directory_path: Path to the directory containing Python files
            exclude_patterns: List of patterns to exclude (e.g., ['test_', '__pycache__'])
        """
        self.directory_path = Path(directory_path)
        self.exclude_patterns = exclude_patterns or ['__pycache__', '.pyc', 'test_', '_test']
        
        # Dictionary of file_path -> DependencyTracer
        self.file_tracers: Dict[str, DependencyTracer] = {}
        
        # Dictionary of import mappings: module_name -> file_path
        self.import_map: Dict[str, str] = {}
        
        # Dictionary of function/class definitions: name -> (file_path, line_number)
        self.global_definitions: Dict[str, Tuple[str, int]] = {}
        
        # Dictionary of variable definitions: name -> (file_path, line_number)  
        self.global_variables: Dict[str, Tuple[str, int]] = {}
        
        self._scan_directory()
    
    def _scan_directory(self):
        """Scan the directory and load all Python files."""
        python_files = []
        
        # Find all Python files recursively
        for py_file in self.directory_path.rglob('*.py'):
            if self._should_include_file(py_file):
                python_files.append(str(py_file))
        
        # Load each file with DependencyTracer
        for file_path in python_files:
            try:
                tracer = DependencyTracer(file_path)
                self.file_tracers[file_path] = tracer
                self._extract_module_info(file_path, tracer)
            except Exception as e:
                print(f"Warning: Could not parse {file_path}: {e}")
    
    def _should_include_file(self, file_path: Path) -> bool:
        """Check if a file should be included based on exclude patterns."""
        file_name = file_path.name
        path_parts = file_path.parts
        
        # Check patterns more precisely
        for pattern in self.exclude_patterns:
            # For specific extensions or cache directories
            if pattern in ['.pyc', '__pycache__']:
                if pattern in str(file_path):
                    return False
            # For filename prefixes like 'test_'
            elif pattern.endswith('_'):
                if file_name.startswith(pattern):
                    return False
                # Also check directory names
                for part in path_parts:
                    if part.startswith(pattern):
                        return False
            # For other patterns, exact match
            else:
                if pattern == file_name or pattern in path_parts:
                    return False
        return True
    
    def _extract_module_info(self, file_path: str, tracer: DependencyTracer):
        """Extract module-level information like imports and function definitions."""
        relative_path = Path(file_path).relative_to(self.directory_path)
        module_name = str(relative_path).replace('/', '.').replace('\\', '.').replace('.py', '')
        
        # Map module name to file path
        self.import_map[module_name] = file_path
        
        # Also map the file name without path
        file_name = Path(file_path).stem
        if file_name not in self.import_map:
            self.import_map[file_name] = file_path
        
        # Extract function, class, and variable definitions
        if tracer.ast_tree:
            for node in ast.walk(tracer.ast_tree):
                if isinstance(node, (ast.FunctionDef, ast.ClassDef)):
                    self.global_definitions[node.name] = (file_path, node.lineno)
        
        # Extract variable assignments
        all_variables = tracer.get_all_variables()
        for var_name, assignments in all_variables.items():
            # Use the most recent assignment (highest line number)
            latest_assignment = max(assignments, key=lambda a: a['line_number'])
            self.global_variables[var_name] = (file_path, latest_assignment['line_number'])
    
    def find_cross_file_dependencies(self, variable_name: str, source_file: str) -> List[Dict[str, Any]]:
        """
        Find dependencies that might exist in other files.
        
        Args:
            variable_name: The variable/function name to search for
            source_file: The file where the variable is being used
            
        Returns:
            List of cross-file dependency information
        """
        cross_file_deps = []
        
        # Check if it's a variable defined in another file
        if variable_name in self.global_variables:
            def_file, def_line = self.global_variables[variable_name]
            if def_file != source_file:
                cross_file_deps.append({
                    'variable': variable_name,
                    'type': 'cross_file_variable',
                    'file_path': def_file,
                    'line_number': def_line,
                    'source_code': self._get_definition_source(def_file, def_line)
                })
        
        # Check if it's a function/class defined in another file  
        elif variable_name in self.global_definitions:
            def_file, def_line = self.global_definitions[variable_name]
            if def_file != source_file:
                cross_file_deps.append({
                    'variable': variable_name,
                    'type': 'cross_file_definition',
                    'file_path': def_file,
                    'line_number': def_line,
                    'source_code': self._get_definition_source(def_file, def_line)
                })
        
        # Check imports in the source file to resolve module references
        source_tracer = self.file_tracers.get(source_file)
        if source_tracer and source_tracer.ast_tree:
            imports = self._extract_imports(source_tracer.ast_tree)
            
            # Look for the variable in imported modules
            for import_info in imports:
                if self._variable_could_be_from_import(variable_name, import_info):
                    imported_file = self.import_map.get(import_info['module'])
                    if imported_file and imported_file in self.file_tracers:
                        imported_tracer = self.file_tracers[imported_file]
                        # Check if the variable exists in the imported file
                        if imported_tracer.find_variable_assignment(variable_name):
                            var_info = imported_tracer.find_variable_assignment(variable_name)
                            cross_file_deps.append({
                                'variable': variable_name,
                                'type': 'imported_variable',
                                'file_path': imported_file,
                                'line_number': var_info['line_number'],
                                'source_code': var_info['source_code'],
                                'import_info': import_info
                            })
        
        return cross_file_deps
    
    def _extract_imports(self, ast_tree: ast.AST) -> List[Dict[str, Any]]:
        """Extract import statements from an AST."""
        imports = []
        
        for node in ast.walk(ast_tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    imports.append({
                        'type': 'import',
                        'module': alias.name,
                        'alias': alias.asname,
                        'line': node.lineno
                    })
            elif isinstance(node, ast.ImportFrom):
                if node.module:
                    for alias in node.names:
                        imports.append({
                            'type': 'from_import',
                            'module': node.module,
                            'name': alias.name,
                            'alias': alias.asname,
                            'line': node.lineno
                        })
        
        return imports
    
    def _variable_could_be_from_import(self, variable_name: str, import_info: Dict[str, Any]) -> bool:
        """Check if a variable could come from a specific import."""
        if import_info['type'] == 'import':
            # For 'import module', check if variable is 'module.something'
            module_name = import_info['alias'] or import_info['module']
            return variable_name.startswith(module_name + '.')
        
        elif import_info['type'] == 'from_import':
            # For 'from module import name', check if variable matches name
            imported_name = import_info['alias'] or import_info['name']
            return variable_name == imported_name or variable_name == import_info['name']
        
        return False
    
    def _get_definition_source(self, file_path: str, line_number: int) -> str:
        """Get source code for a definition in another file."""
        tracer = self.file_tracers.get(file_path)
        if tracer:
            return tracer._get_source_code(line_number)
        return ""
    
    def trace_dependencies_multi_file(self, variable_name: str, source_file: str, 
                                     target_line: Optional[int] = None, 
                                     max_depth: int = 10) -> List[Dict[str, Any]]:
        """
        Trace dependencies across multiple files.
        
        Args:
            variable_name: The variable to trace
            source_file: The file containing the variable
            target_line: The line number where the variable is used
            max_depth: Maximum recursion depth
            
        Returns:
            List of dependency information including cross-file dependencies
        """
        visited_assignments = set()  # Track (file_path, var_name, line_number) tuples
        dependencies = []
        
        def _trace_recursive(var_name: str, current_file: str, current_line: Optional[int], depth: int = 0):
            if depth >= max_depth:
                return
            
            # First, try to find the variable in the current file
            file_tracer = self.file_tracers.get(current_file)
            if file_tracer:
                var_info = file_tracer.find_variable_assignment(var_name, current_line)
                if var_info:
                    assignment_id = (current_file, var_name, var_info['line_number'])
                    
                    # Always add the dependency to show the reference
                    dep_info = {
                        'variable': var_name,
                        'type': 'variable',
                        'line_number': var_info['line_number'],
                        'source_code': var_info['source_code'],
                        'file_path': current_file,
                        'depth': depth
                    }
                    dependencies.append(dep_info)
                    
                    # Only recurse if we haven't visited this assignment before (to prevent infinite recursion)
                    if assignment_id not in visited_assignments:
                        visited_assignments.add(assignment_id)
                        
                        # Recursively trace its dependencies in the same file
                        for dep_var in var_info['dependencies']:
                            _trace_recursive(dep_var, current_file, var_info['line_number'], depth + 1)
                    return
            
            # If not found in current file, look for cross-file dependencies
            if var_name in self.global_variables:
                def_file, def_line = self.global_variables[var_name]
                
                if def_file != current_file:
                    # Truly cross-file dependency
                    cross_file_tracer = self.file_tracers.get(def_file)
                    if cross_file_tracer:
                        # For different files, use the most recent assignment (which global_variables tracks)
                        # This is safe because cross-file references don't have temporal constraints
                        var_info = cross_file_tracer.find_variable_assignment(var_name)
                        # Ensure we get the specific assignment tracked in global_variables
                        if var_info and var_info['line_number'] != def_line:
                            # Try to find the specific assignment at the expected line
                            all_assignments = cross_file_tracer.get_all_variables().get(var_name, [])
                            for assignment in all_assignments:
                                if assignment['line_number'] == def_line:
                                    var_info = assignment
                                    break
                        
                        if var_info:
                            assignment_id = (def_file, var_name, var_info['line_number'])
                            
                            # Always add the dependency to show the reference
                            dep_info = {
                                'variable': var_name,
                                'type': 'cross_file_variable',
                                'line_number': var_info['line_number'],
                                'source_code': var_info['source_code'],
                                'file_path': def_file,
                                'depth': depth
                            }
                            dependencies.append(dep_info)
                            
                            # Only recurse if we haven't visited this assignment before
                            if assignment_id not in visited_assignments:
                                visited_assignments.add(assignment_id)
                                
                                # Recursively trace dependencies in the cross-file
                                for dep_var in var_info['dependencies']:
                                    _trace_recursive(dep_var, def_file, var_info['line_number'], depth + 1)
                else:
                    # Same file - check if the assignment in global_variables comes before current_line
                    if current_line is None or def_line < current_line:
                        # This assignment comes before our reference point, so it's valid
                        assignment_id = (def_file, var_name, def_line)
                        file_tracer = self.file_tracers.get(def_file)
                        if file_tracer:
                            # Find the specific assignment at the line tracked in global_variables
                            all_assignments = file_tracer.get_all_variables().get(var_name, [])
                            var_info = None
                            for assignment in all_assignments:
                                if assignment['line_number'] == def_line:
                                    var_info = assignment
                                    break
                            
                            if var_info:
                                # Always add the dependency to show the reference
                                dep_info = {
                                    'variable': var_name,
                                    'type': 'variable',
                                    'line_number': var_info['line_number'],
                                    'source_code': var_info['source_code'],
                                    'file_path': def_file,
                                    'depth': depth
                                }
                                dependencies.append(dep_info)
                                
                                # Only recurse if we haven't visited this assignment before
                                if assignment_id not in visited_assignments:
                                    visited_assignments.add(assignment_id)
                                    
                                    # Recursively trace dependencies
                                    for dep_var in var_info['dependencies']:
                                        _trace_recursive(dep_var, def_file, var_info['line_number'], depth + 1)
                    # If def_line >= current_line, then this assignment comes after our reference point
                    # and should not be followed (temporal ordering violation)
            
            elif var_name in self.global_definitions:
                def_file, def_line = self.global_definitions[var_name]
                assignment_id = (def_file, var_name, def_line)
                if assignment_id not in visited_assignments:
                    visited_assignments.add(assignment_id)
                    
                    # Add cross-file function/class
                    dep_info = {
                        'variable': var_name,
                        'type': 'cross_file_function',
                        'line_number': def_line,
                        'source_code': self._get_definition_source(def_file, def_line),
                        'file_path': def_file,
                        'depth': depth
                    }
                    dependencies.append(dep_info)
            
            else:
                # Variable not found in any file - outside scope boundary
                dep_info = {
                    'variable': var_name,
                    'type': 'out_of_scope',
                    'line_number': None,
                    'source_code': f'# {var_name} - dependency chain leaves scope (external import or builtin)',
                    'file_path': None,
                    'depth': depth
                }
                dependencies.append(dep_info)
        
        # Start the recursive tracing
        _trace_recursive(variable_name, source_file, target_line)
        
        return dependencies
    
    def get_all_files(self) -> List[str]:
        """Get list of all analyzed files."""
        return list(self.file_tracers.keys())
    
    def get_file_tracer(self, file_path: str) -> Optional[DependencyTracer]:
        """Get the DependencyTracer for a specific file."""
        return self.file_tracers.get(file_path)
    
    def format_multi_file_report(self, variable_name: str, source_file: str, 
                                target_line: Optional[int] = None) -> str:
        """Generate a formatted report including cross-file dependencies."""
        dependencies = self.trace_dependencies_multi_file(variable_name, source_file, target_line)
        
        if not dependencies:
            return f"No dependencies found for variable '{variable_name}'"
        
        # Group by file for better organization
        file_groups = {}
        for dep in dependencies:
            file_path = dep.get('file_path', source_file)
            if file_path not in file_groups:
                file_groups[file_path] = []
            file_groups[file_path].append(dep)
        
        report_lines = [
            f"Multi-File Dependency Analysis for '{variable_name}'",
            "=" * 60,
            f"Source: {Path(source_file).name}",
            ""
        ]
        
        # Sort files with source file first, handling None values
        def sort_key(f):
            if f is None:
                return (2, "")  # None files last
            return (f != source_file, f)  # Source file first, then alphabetical
        
        sorted_files = sorted(file_groups.keys(), key=sort_key)
        
        for file_path in sorted_files:
            deps_in_file = sorted(file_groups[file_path], key=lambda x: x.get('depth', 0))
            
            if file_path != source_file:
                if file_path is None:
                    report_lines.append("🌐 External/Unresolved:")
                else:
                    report_lines.append(f"📁 {Path(file_path).name}:")
                report_lines.append("")
            
            for dep in deps_in_file:
                indent = "  " * dep.get('depth', 0)
                dep_type = dep.get('type', 'variable').upper()
                
                cross_file_marker = " 🔗" if dep.get('cross_file') else ""
                
                report_lines.append(
                    f"{indent}{dep['variable']} ({dep_type}) - Line {dep['line_number']}{cross_file_marker}"
                )
                
                # Handle multi-line source code
                source_lines = dep.get('source_code', '').split('\n')
                for line in source_lines:
                    if line.strip():
                        report_lines.append(f"{indent}  {line}")
                
                report_lines.append("")
        
        return "\n".join(report_lines)