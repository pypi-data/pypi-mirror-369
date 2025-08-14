import ast
from typing import Dict, List, Optional, Set, Any
from pathlib import Path


class DependencyTracer:
    """
    Traces variable dependencies in Python code using AST analysis.
    Handles variable reassignments by tracking each assignment separately.
    """
    
    def __init__(self, file_path: str):
        """Initialize the tracer with a Python file."""
        self.file_path = file_path
        self.ast_tree = None
        self.source_lines = []
        self._all_assignments = []  # List of all assignments ordered by line number
        self._function_definitions = {}
        
        self._load_and_parse()
    
    def _load_and_parse(self):
        """Load the file and parse it into an AST."""
        try:
            with open(self.file_path, 'r', encoding='utf-8') as f:
                source_code = f.read()
                self.source_lines = source_code.splitlines()
            
            self.ast_tree = ast.parse(source_code, filename=self.file_path)
            self._analyze_ast()
            
        except (FileNotFoundError, SyntaxError) as e:
            raise ValueError(f"Could not parse file {self.file_path}: {e}")
    
    def _analyze_ast(self):
        """Analyze the AST to extract variable assignments and function definitions."""
        # Use ast.walk to get all nodes, but we need to process them in order
        all_nodes = []
        for node in ast.walk(self.ast_tree):
            if isinstance(node, (ast.Assign, ast.FunctionDef)):
                all_nodes.append(node)
        
        # Sort by line number to process assignments in order
        all_nodes.sort(key=lambda n: n.lineno)
        
        for node in all_nodes:
            if isinstance(node, ast.Assign):
                self._process_assignment(node)
            elif isinstance(node, ast.FunctionDef):
                self._process_function_def(node)
    
    def _process_assignment(self, node: ast.Assign):
        """Process an assignment node to extract variable information."""
        for target in node.targets:
            if isinstance(target, ast.Name):
                var_name = target.id
                
                # Handle multi-line statements by checking end_lineno
                end_line = getattr(node, 'end_lineno', node.lineno)
                source_code = self._get_source_code(node.lineno, end_line)
                
                assignment_info = {
                    'variable': var_name,
                    'node': node,
                    'line_number': node.lineno,
                    'end_line_number': end_line,
                    'source_code': source_code,
                    'dependencies': self._extract_dependencies_from_node(node.value)
                }
                self._all_assignments.append(assignment_info)
    
    def _process_function_def(self, node: ast.FunctionDef):
        """Process a function definition node."""
        self._function_definitions[node.name] = {
            'node': node,
            'line_number': node.lineno,
            'args': [arg.arg for arg in node.args.args],
            'source_code': self._get_source_code(node.lineno)
        }
    
    def _extract_dependencies_from_node(self, node: ast.AST) -> List[str]:
        """Extract variable dependencies from an AST node, excluding lambda parameters."""
        dependencies = []
        
        def extract_from_node_recursive(current_node: ast.AST, excluded_names: Set[str] = None):
            """Recursively extract dependencies while respecting scope boundaries."""
            if excluded_names is None:
                excluded_names = set()
            
            # Handle lambda functions - their parameters should be excluded from dependencies
            if isinstance(current_node, ast.Lambda):
                # Get lambda parameter names
                lambda_params = set()
                for arg in current_node.args.args:
                    lambda_params.add(arg.arg)
                
                # Process the lambda body with excluded parameter names
                new_excluded = excluded_names | lambda_params
                extract_from_node_recursive(current_node.body, new_excluded)
                return
            
            # Handle comprehensions (list, dict, set, generator) - they have their own scope
            elif isinstance(current_node, (ast.ListComp, ast.DictComp, ast.SetComp, ast.GeneratorExp)):
                comp_excluded = excluded_names.copy()
                
                # Add comprehension variables to excluded names
                for generator in current_node.generators:
                    if isinstance(generator.target, ast.Name):
                        comp_excluded.add(generator.target.id)
                    # Handle tuple unpacking in comprehensions like: for x, y in items
                    elif isinstance(generator.target, (ast.Tuple, ast.List)):
                        for elt in generator.target.elts:
                            if isinstance(elt, ast.Name):
                                comp_excluded.add(elt.id)
                
                # Process the comprehension with excluded names
                if hasattr(current_node, 'elt'):  # ListComp, SetComp, GeneratorExp
                    extract_from_node_recursive(current_node.elt, comp_excluded)
                elif hasattr(current_node, 'key'):  # DictComp
                    extract_from_node_recursive(current_node.key, comp_excluded)
                    extract_from_node_recursive(current_node.value, comp_excluded)
                
                # Process generators (iter and ifs)
                for generator in current_node.generators:
                    extract_from_node_recursive(generator.iter, excluded_names)  # Use original scope for iter
                    for if_ in generator.ifs:
                        extract_from_node_recursive(if_, comp_excluded)  # Use comprehension scope for ifs
                return
            
            # Handle variable names
            elif isinstance(current_node, ast.Name) and isinstance(current_node.ctx, ast.Load):
                if current_node.id not in excluded_names:
                    dependencies.append(current_node.id)
                return
            
            # Handle function calls
            elif isinstance(current_node, ast.Call):
                if isinstance(current_node.func, ast.Name):
                    if current_node.func.id not in excluded_names:
                        dependencies.append(current_node.func.id)
                elif isinstance(current_node.func, ast.Attribute):
                    # Handle method calls like obj.method()
                    if isinstance(current_node.func.value, ast.Name):
                        if current_node.func.value.id not in excluded_names:
                            dependencies.append(current_node.func.value.id)
                
                # Process call arguments
                for arg in current_node.args:
                    extract_from_node_recursive(arg, excluded_names)
                for keyword in current_node.keywords:
                    extract_from_node_recursive(keyword.value, excluded_names)
                return
            
            # For all other nodes, recursively process children
            for child in ast.iter_child_nodes(current_node):
                extract_from_node_recursive(child, excluded_names)
        
        extract_from_node_recursive(node)
        return list(set(dependencies))  # Remove duplicates
    
    def _get_source_code(self, line_number: int, end_line: Optional[int] = None) -> str:
        """Get the source code for a specific line or range of lines."""
        if not (1 <= line_number <= len(self.source_lines)):
            return ""
        
        if end_line is None:
            return self.source_lines[line_number - 1].strip()
        
        # Handle multi-line statements
        if end_line > len(self.source_lines):
            end_line = len(self.source_lines)
        
        lines = []
        for i in range(line_number - 1, end_line):
            lines.append(self.source_lines[i].rstrip())
        
        return '\n'.join(lines)
    
    def find_variable_assignment(self, variable_name: str, before_line: Optional[int] = None, 
                                function_name: Optional[str] = None) -> Optional[Dict[str, Any]]:
        """
        Find the most recent assignment for a specific variable before a given line.
        
        Args:
            variable_name: The variable to find
            before_line: Only consider assignments before this line number
            function_name: Only consider assignments within this function
        
        Returns:
            Assignment info dict or None if not found
        """
        candidates = []
        for assignment in self._all_assignments:
            if assignment['variable'] == variable_name:
                # Check temporal constraint
                if before_line is not None and assignment['line_number'] >= before_line:
                    continue
                
                # Check function scope constraint
                if function_name is not None:
                    assignment_function = self._get_function_containing_line(assignment['line_number'])
                    if assignment_function != function_name:
                        continue
                
                candidates.append(assignment)
        
        if not candidates:
            return None
        
        # Return the most recent assignment (highest line number)
        return max(candidates, key=lambda a: a['line_number'])
    
    def _get_function_containing_line(self, line_number: int) -> Optional[str]:
        """
        Find which function contains the given line number.
        
        Args:
            line_number: The line number to check
            
        Returns:
            Function name if the line is inside a function, None if module-level
        """
        for func_name, func_info in self._function_definitions.items():
            func_node = func_info['node']
            func_start = func_node.lineno
            func_end = getattr(func_node, 'end_lineno', None)
            
            # If end_lineno is not available, estimate by finding the next function or end of file
            if func_end is None:
                func_end = self._estimate_function_end(func_node)
            
            if func_start <= line_number <= func_end:
                return func_name
        
        return None  # Module-level
    
    def _estimate_function_end(self, func_node: ast.FunctionDef) -> int:
        """
        Estimate the end line of a function when end_lineno is not available.
        """
        # Find the maximum line number in the function's body
        max_line = func_node.lineno
        for node in ast.walk(func_node):
            if hasattr(node, 'lineno') and node.lineno > max_line:
                max_line = node.lineno
        return max_line
    
    def trace_dependencies(self, variable_name: str, target_line: Optional[int] = None, 
                          max_depth: int = 10, function_name: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Trace all dependencies for a given variable.
        
        Args:
            variable_name: The variable to trace
            target_line: The line number where the variable is used (to find correct assignment)
            max_depth: Maximum recursion depth
            function_name: Only trace variables within this function (None for module-level)
            
        Returns:
            List of dependency information dictionaries
        """
        visited_assignments = set()  # Track (var_name, line_number) tuples
        dependencies = []
        
        def _trace_recursive(var_name: str, current_line: Optional[int], depth: int = 0):
            if depth >= max_depth:
                return
            
            # Find the appropriate assignment for this variable
            var_info = self.find_variable_assignment(var_name, current_line, function_name)
            if not var_info:
                # If we're in a function and didn't find the variable, check if it's a parameter
                if function_name and var_name in self._function_definitions.get(function_name, {}).get('args', []):
                    func_info = self._function_definitions[function_name]
                    dependencies.append({
                        'variable': var_name,
                        'type': 'function_parameter',
                        'line_number': func_info['line_number'],
                        'source_code': f'def {function_name}(..., {var_name}, ...)',
                        'file_path': self.file_path,
                        'depth': depth
                    })
                return
            
            # Create a unique identifier for this specific assignment
            assignment_id = (var_name, var_info['line_number'])
            if assignment_id in visited_assignments:
                return
            
            visited_assignments.add(assignment_id)
            
            dep_info = {
                'variable': var_name,
                'type': 'variable',
                'line_number': var_info['line_number'],
                'source_code': var_info['source_code'],
                'file_path': self.file_path,
                'depth': depth
            }
            dependencies.append(dep_info)
            
            # Recursively trace dependencies from this specific assignment
            for dep_var in var_info['dependencies']:
                # Check if it's a function first
                if dep_var in self._function_definitions:
                    func_info = self._function_definitions[dep_var]
                    func_dep_info = {
                        'variable': dep_var,
                        'type': 'function',
                        'line_number': func_info['line_number'],
                        'source_code': func_info['source_code'],
                        'file_path': self.file_path,
                        'depth': depth + 1
                    }
                    dependencies.append(func_dep_info)
                else:
                    # For variables, look for assignments before the current assignment
                    _trace_recursive(dep_var, var_info['line_number'], depth + 1)
        
        # Start tracing from the target variable
        _trace_recursive(variable_name, target_line)
        return dependencies
    
    def get_dependency_chain(self, variable_name: str, target_line: Optional[int] = None) -> List[Dict[str, Any]]:
        """
        Get a formatted dependency chain showing the path from target to dependencies.
        
        Args:
            variable_name: The variable to analyze
            target_line: The line number where the variable is used
            
        Returns:
            List of dependencies ordered by depth (target variable first)
        """
        dependencies = self.trace_dependencies(variable_name, target_line)
        
        # Sort by depth (target variable first, then deeper dependencies)
        dependencies.sort(key=lambda x: x['depth'])
        
        return dependencies
    
    def get_all_variables(self, function_name: Optional[str] = None) -> Dict[str, List[Dict[str, Any]]]:
        """
        Get all variables and their assignments, grouped by name.
        
        Args:
            function_name: Only return variables within this function (None for module-level or all)
        
        Returns:
            Dictionary mapping variable names to lists of assignment info dicts
        """
        variables = {}
        for assignment in self._all_assignments:
            # Check function scope constraint
            if function_name is not None:
                assignment_function = self._get_function_containing_line(assignment['line_number'])
                if assignment_function != function_name:
                    continue
            
            var_name = assignment['variable']
            if var_name not in variables:
                variables[var_name] = []
            variables[var_name].append(assignment)
        return variables
    
    def get_all_functions(self) -> Dict[str, Dict[str, Any]]:
        """
        Get all function definitions.
        
        Returns:
            Dictionary mapping function names to function info
        """
        return self._function_definitions.copy()
    
    def format_dependency_report(self, variable_name: str, target_line: Optional[int] = None) -> str:
        """
        Generate a formatted report of variable dependencies.
        
        Args:
            variable_name: The variable to analyze
            target_line: The line number where the variable is used
            
        Returns:
            Formatted string report
        """
        # Find if the variable exists at all
        target_assignment = self.find_variable_assignment(variable_name, target_line)
        if not target_assignment:
            return f"Variable '{variable_name}' not found in {self.file_path}"
        
        dependencies = self.get_dependency_chain(variable_name, target_line)
        
        if not dependencies:
            return f"No dependencies found for variable '{variable_name}'"
        
        report_lines = [
            f"Dependency Analysis for '{variable_name}' in {Path(self.file_path).name}",
            "=" * 60,
            ""
        ]
        
        # Group dependencies by depth to show parallel dependencies better
        depth_groups = {}
        for dep in dependencies:
            depth = dep['depth']
            if depth not in depth_groups:
                depth_groups[depth] = []
            depth_groups[depth].append(dep)
        
        # Sort and display by depth
        for depth in sorted(depth_groups.keys()):
            deps_at_depth = sorted(depth_groups[depth], key=lambda x: x['line_number'])
            
            for dep in deps_at_depth:
                indent = "  " * dep['depth']
                dep_type = dep['type'].upper()
                report_lines.append(
                    f"{indent}{dep['variable']} ({dep_type}) - Line {dep['line_number']}"
                )
                
                # Handle multi-line source code properly
                source_lines = dep['source_code'].split('\n')
                for i, line in enumerate(source_lines):
                    if i == 0:
                        report_lines.append(f"{indent}  {line}")
                    else:
                        report_lines.append(f"{indent}  {line}")
                
                report_lines.append("")
        
        return "\n".join(report_lines)