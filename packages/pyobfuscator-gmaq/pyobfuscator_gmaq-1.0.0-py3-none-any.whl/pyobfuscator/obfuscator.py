"""
Advanced code obfuscation engine using AST manipulation
"""

import ast
import random
import string
import base64
import marshal
import logging
from .ast_transformer import *
from .utils import generate_random_name, encode_string

class CodeObfuscator:
    """Advanced Python code obfuscator with multiple transformation techniques"""
    
    def __init__(self, remove_docstrings=True, max_obfuscation=False):
        """
        Initialize the obfuscator
        
        Args:
            remove_docstrings (bool): Remove docstrings and comments
            max_obfuscation (bool): Apply maximum obfuscation techniques
        """
        self.logger = logging.getLogger(self.__class__.__name__)
        self.remove_docstrings = remove_docstrings
        self.max_obfuscation = max_obfuscation
        
        # Name mappings for consistency across passes
        self.name_mappings = {}
        self.string_mappings = {}
        self.used_names = set()
        
        # Initialize transformers
        self.transformers = [
            VariableRenamer(self.name_mappings, self.used_names),
            StringObfuscator(self.string_mappings),
            ControlFlowObfuscator(),
            DeadCodeInjector(),
            FunctionInliner(),
        ]
        
        if max_obfuscation:
            self.transformers.extend([
                BytecodeObfuscator(),
                AntiDecompilerProtection(),
                FakeCodeGenerator()
            ])
    
    def obfuscate(self, source_code):
        """
        Obfuscate Python source code
        
        Args:
            source_code (str): Original Python source code
            
        Returns:
            str: Obfuscated Python source code
        """
        try:
            self.logger.debug("Parsing source code to AST...")
            tree = ast.parse(source_code)
            
            # Remove docstrings if requested
            if self.remove_docstrings:
                tree = DocstringRemover().visit(tree)
            
            # Apply all transformations
            for transformer in self.transformers:
                self.logger.debug(f"Applying transformer: {transformer.__class__.__name__}")
                tree = transformer.visit(tree)
                ast.fix_missing_locations(tree)
            
            # Convert back to source code
            obfuscated_code = ast.unparse(tree)
            
            # Additional string-level obfuscations
            obfuscated_code = self._apply_string_obfuscations(obfuscated_code)
            
            return obfuscated_code
            
        except Exception as e:
            self.logger.error(f"Obfuscation failed: {str(e)}")
            raise
    
    def _apply_string_obfuscations(self, code):
        """Apply additional string-level obfuscation techniques"""
        
        # Add fake imports and unused code
        fake_imports = [
            "import sys as _sys_module",
            "import os as _os_module", 
            "import random as _random_module",
            "from collections import defaultdict as _dd",
            "import hashlib as _hash_lib"
        ]
        
        # Generate random variable assignments
        fake_vars = []
        for _ in range(random.randint(5, 15)):
            var_name = generate_random_name()
            if random.choice([True, False]):
                value = random.randint(1000, 9999)
                fake_vars.append(f"{var_name} = {value}")
            else:
                value = ''.join(random.choices(string.ascii_letters, k=random.randint(10, 20)))
                fake_vars.append(f"{var_name} = {repr(value)}")
        
        # Insert fake code at the beginning
        fake_code = "\n".join(fake_imports + fake_vars) + "\n\n"
        
        # Add random comments throughout the code
        lines = code.split('\n')
        obfuscated_lines = []
        
        for line in lines:
            obfuscated_lines.append(line)
            
            # Randomly insert fake comments
            if random.random() < 0.1:  # 10% chance
                fake_comment = f"# {generate_random_name()}"
                obfuscated_lines.append(fake_comment)
        
        return fake_code + '\n'.join(obfuscated_lines)


class DocstringRemover(ast.NodeTransformer):
    """Remove docstrings and comments from AST"""
    
    def visit_FunctionDef(self, node):
        """Remove docstrings from functions"""
        if (node.body and 
            isinstance(node.body[0], ast.Expr) and 
            isinstance(node.body[0].value, ast.Constant) and 
            isinstance(node.body[0].value.value, str)):
            node.body = node.body[1:]
        return self.generic_visit(node)
    
    def visit_ClassDef(self, node):
        """Remove docstrings from classes"""
        if (node.body and 
            isinstance(node.body[0], ast.Expr) and 
            isinstance(node.body[0].value, ast.Constant) and 
            isinstance(node.body[0].value.value, str)):
            node.body = node.body[1:]
        return self.generic_visit(node)
    
    def visit_Module(self, node):
        """Remove module-level docstrings"""
        if (node.body and 
            isinstance(node.body[0], ast.Expr) and 
            isinstance(node.body[0].value, ast.Constant) and 
            isinstance(node.body[0].value.value, str)):
            node.body = node.body[1:]
        return self.generic_visit(node)


class VariableRenamer(ast.NodeTransformer):
    """Rename all variables, functions, and classes to obfuscated names"""
    
    def __init__(self, name_mappings, used_names):
        self.name_mappings = name_mappings
        self.used_names = used_names
        self.local_scopes = [set()]  # Stack of local scopes
        
        # Built-in names that shouldn't be renamed
        self.builtin_names = {
            'print', 'len', 'str', 'int', 'float', 'list', 'dict', 'tuple',
            'range', 'enumerate', 'zip', 'map', 'filter', 'sum', 'max', 'min',
            'open', 'file', 'input', 'raw_input', '__name__', '__main__',
            'True', 'False', 'None', '__file__', '__doc__', '__dict__',
            'Exception', 'ValueError', 'TypeError', 'ImportError',
            'sys', 'os', 're', 'json', 'time', 'datetime', 'math', 'random'
        }
    
    def _get_obfuscated_name(self, original_name):
        """Get or generate obfuscated name for original name"""
        if original_name in self.builtin_names:
            return original_name
        
        if original_name not in self.name_mappings:
            new_name = generate_random_name()
            while new_name in self.used_names or new_name in self.builtin_names:
                new_name = generate_random_name()
            
            self.name_mappings[original_name] = new_name
            self.used_names.add(new_name)
        
        return self.name_mappings[original_name]
    
    def visit_FunctionDef(self, node):
        """Rename function definitions"""
        # Enter new scope
        self.local_scopes.append(set())
        
        # Rename function name
        if not node.name.startswith('__') or not node.name.endswith('__'):
            node.name = self._get_obfuscated_name(node.name)
        
        # Rename parameters
        for arg in node.args.args:
            arg.arg = self._get_obfuscated_name(arg.arg)
            self.local_scopes[-1].add(arg.arg)
        
        # Visit function body
        node = self.generic_visit(node)
        
        # Exit scope
        self.local_scopes.pop()
        
        return node
    
    def visit_ClassDef(self, node):
        """Rename class definitions"""
        node.name = self._get_obfuscated_name(node.name)
        return self.generic_visit(node)
    
    def visit_Name(self, node):
        """Rename variable names"""
        if isinstance(node.ctx, (ast.Store, ast.Load)):
            if not node.id.startswith('__') or not node.id.endswith('__'):
                node.id = self._get_obfuscated_name(node.id)
        
        return self.generic_visit(node)


class StringObfuscator(ast.NodeTransformer):
    """Obfuscate string literals"""
    
    def __init__(self, string_mappings):
        self.string_mappings = string_mappings
    
    def visit_Constant(self, node):
        """Obfuscate string constants"""
        if isinstance(node.value, str) and len(node.value) > 1:
            # Don't obfuscate very short strings or special strings
            if node.value in ['', ' ', '\n', '\t'] or len(node.value) <= 2:
                return node
            
            # Create obfuscated string access
            encoded = encode_string(node.value)
            
            # Replace with base64 decode call
            decode_call = ast.Call(
                func=ast.Attribute(
                    value=ast.Name(id='base64', ctx=ast.Load()),
                    attr='b64decode',
                    ctx=ast.Load()
                ),
                args=[ast.Constant(value=encoded)],
                keywords=[]
            )
            
            # Wrap in decode call
            final_call = ast.Call(
                func=ast.Attribute(
                    value=decode_call,
                    attr='decode',
                    ctx=ast.Load()
                ),
                args=[ast.Constant(value='utf-8')],
                keywords=[]
            )
            
            return final_call
        
        return node


class ControlFlowObfuscator(ast.NodeTransformer):
    """Obfuscate control flow structures"""
    
    def visit_If(self, node):
        """Add fake conditions and nested structures"""
        if random.random() < 0.3:  # 30% chance to obfuscate
            # Create a fake condition that's always true
            fake_var = generate_random_name()
            fake_condition = ast.Compare(
                left=ast.BinOp(
                    left=ast.Constant(value=random.randint(1, 10)),
                    op=ast.Mult(),
                    right=ast.Constant(value=random.randint(1, 10))
                ),
                ops=[ast.Gt()],
                comparators=[ast.Constant(value=0)]
            )
            
            # Wrap original condition with fake logic
            complex_condition = ast.BoolOp(
                op=ast.And(),
                values=[fake_condition, node.test]
            )
            
            node.test = complex_condition
        
        return self.generic_visit(node)
    
    def visit_For(self, node):
        """Add complexity to for loops"""
        if random.random() < 0.2:  # 20% chance
            # Add a fake nested loop structure
            fake_var = generate_random_name()
            fake_loop = ast.For(
                target=ast.Name(id=fake_var, ctx=ast.Store()),
                iter=ast.Call(
                    func=ast.Name(id='range', ctx=ast.Load()),
                    args=[ast.Constant(value=1)],
                    keywords=[]
                ),
                body=[ast.Pass()],
                orelse=[]
            )
            
            # Insert fake loop before real one
            return [fake_loop, self.generic_visit(node)]
        
        return self.generic_visit(node)


class DeadCodeInjector(ast.NodeTransformer):
    """Inject dead code that never executes"""
    
    def visit_Module(self, node):
        """Inject dead code throughout the module"""
        new_body = []
        
        for stmt in node.body:
            new_body.append(stmt)
            
            # Randomly inject dead code
            if random.random() < 0.1:  # 10% chance
                dead_code = self._generate_dead_code()
                new_body.extend(dead_code)
        
        node.body = new_body
        return self.generic_visit(node)
    
    def _generate_dead_code(self):
        """Generate dead code that looks real but never executes"""
        dead_code = []
        
        # Fake variable assignments
        for _ in range(random.randint(2, 5)):
            var_name = generate_random_name()
            value = random.choice([
                ast.Constant(value=random.randint(1, 1000)),
                ast.Constant(value=generate_random_name()),
                ast.List(elts=[ast.Constant(value=i) for i in range(3)], ctx=ast.Load())
            ])
            
            assign = ast.Assign(
                targets=[ast.Name(id=var_name, ctx=ast.Store())],
                value=value
            )
            dead_code.append(assign)
        
        # Fake if statement that never executes
        fake_if = ast.If(
            test=ast.Compare(
                left=ast.Constant(value=1),
                ops=[ast.Gt()],
                comparators=[ast.Constant(value=2)]
            ),
            body=dead_code,
            orelse=[]
        )
        
        return [fake_if]


class FunctionInliner(ast.NodeTransformer):
    """Inline simple functions to obfuscate call patterns"""
    
    def __init__(self):
        self.functions_to_inline = {}
    
    def visit_FunctionDef(self, node):
        """Identify functions suitable for inlining"""
        # Only inline very simple functions
        if (len(node.body) == 1 and 
            isinstance(node.body[0], ast.Return) and
            len(node.args.args) <= 2):
            
            self.functions_to_inline[node.name] = node
        
        return self.generic_visit(node)


class BytecodeObfuscator(ast.NodeTransformer):
    """Advanced bytecode-level obfuscation"""
    
    def visit_Module(self, node):
        """Apply bytecode obfuscation techniques"""
        # This is a placeholder for more advanced bytecode manipulation
        # In a real implementation, this would involve marshal/unmarshal
        # operations and bytecode modification
        
        return self.generic_visit(node)


class AntiDecompilerProtection(ast.NodeTransformer):
    """Add protection against common decompiler tools"""
    
    def visit_Module(self, node):
        """Add anti-decompiler checks"""
        # Add checks at module level
        protection_code = ast.parse("""
import sys
import os
if hasattr(sys, 'ps1'): sys.exit()
if 'idlelib' in sys.modules: sys.exit()
""").body
        
        node.body = protection_code + node.body
        return self.generic_visit(node)


class FakeCodeGenerator(ast.NodeTransformer):
    """Generate realistic but fake code to confuse analysts"""
    
    def visit_Module(self, node):
        """Add fake but realistic-looking code"""
        fake_functions = []
        
        # Generate fake utility functions
        for i in range(random.randint(3, 7)):
            func_name = generate_random_name()
            fake_func = ast.FunctionDef(
                name=func_name,
                args=ast.arguments(
                    posonlyargs=[],
                    args=[ast.arg(arg=generate_random_name(), annotation=None)],
                    vararg=None,
                    kwonlyargs=[],
                    kw_defaults=[],
                    kwarg=None,
                    defaults=[]
                ),
                body=[
                    ast.Return(
                        value=ast.BinOp(
                            left=ast.Name(id='len', ctx=ast.Load()),
                            op=ast.Mult(),
                            right=ast.Constant(value=random.randint(1, 100))
                        )
                    )
                ],
                decorator_list=[],
                returns=None
            )
            fake_functions.append(fake_func)
        
        # Insert fake functions at the beginning
        node.body = fake_functions + node.body
        return self.generic_visit(node)
