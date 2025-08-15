#!/usr/bin/env python3
"""
Simplified obfuscator for testing without anti-tampering
"""

import ast
import random
import string
import base64
import logging
from .utils import generate_random_name, encode_string

class SimpleObfuscator:
    """Simple obfuscator without anti-tampering features"""
    
    def __init__(self):
        self.logger = logging.getLogger(self.__class__.__name__)
        self.name_mappings = {}
        self.used_names = set()
        
        # Built-in names that shouldn't be renamed
        self.builtin_names = {
            'print', 'len', 'str', 'int', 'float', 'list', 'dict', 'tuple',
            'range', 'enumerate', 'zip', 'map', 'filter', 'sum', 'max', 'min',
            'open', 'file', 'input', 'raw_input', '__name__', '__main__',
            'True', 'False', 'None', '__file__', '__doc__', '__dict__',
            'Exception', 'ValueError', 'TypeError', 'ImportError'
        }
    
    def obfuscate_code(self, source_code):
        """
        Obfuscate Python source code (simple version)
        
        Args:
            source_code (str): Original Python source code
            
        Returns:
            str: Obfuscated Python source code
        """
        try:
            self.logger.info("Starting simple obfuscation...")
            
            # Parse AST
            tree = ast.parse(source_code)
            
            # Apply transformations
            tree = self._rename_variables(tree)
            tree = self._obfuscate_strings(tree)
            tree = self._add_fake_code(tree)
            
            # Fix missing line numbers
            ast.fix_missing_locations(tree)
            
            # Convert back to source
            obfuscated_code = ast.unparse(tree)
            
            self.logger.info("Simple obfuscation completed")
            return obfuscated_code
            
        except Exception as e:
            self.logger.error(f"Obfuscation failed: {str(e)}")
            raise
    
    def _rename_variables(self, tree):
        """Rename variables and functions"""
        class VariableRenamer(ast.NodeTransformer):
            def __init__(self, parent):
                self.parent = parent
            
            def visit_FunctionDef(self, node):
                if not node.name.startswith('__') or not node.name.endswith('__'):
                    node.name = self.parent._get_obfuscated_name(node.name)
                
                # Rename parameters
                for arg in node.args.args:
                    arg.arg = self.parent._get_obfuscated_name(arg.arg)
                
                return self.generic_visit(node)
            
            def visit_Name(self, node):
                if isinstance(node.ctx, (ast.Store, ast.Load)):
                    if not node.id.startswith('__') or not node.id.endswith('__'):
                        node.id = self.parent._get_obfuscated_name(node.id)
                
                return self.generic_visit(node)
        
        renamer = VariableRenamer(self)
        return renamer.visit(tree)
    
    def _obfuscate_strings(self, tree):
        """Obfuscate string literals"""
        class StringObfuscator(ast.NodeTransformer):
            def visit_Constant(self, node):
                if isinstance(node.value, str) and len(node.value) > 1:
                    if node.value not in ['', ' ', '\n', '\t'] and len(node.value) > 2:
                        encoded = encode_string(node.value)
                        
                        # Replace with decode expression
                        decode_expr = ast.parse(f"__import__('base64').b64decode('{encoded}').decode('utf-8')").body[0].value
                        return decode_expr
                
                return node
        
        obfuscator = StringObfuscator()
        return obfuscator.visit(tree)
    
    def _add_fake_code(self, tree):
        """Add fake variables and operations"""
        if isinstance(tree, ast.Module):
            fake_vars = []
            
            # Add fake imports
            fake_imports = [
                ast.Import(names=[ast.alias(name='os', asname=f'_os_{random.randint(1000, 9999)}')]),
                ast.Import(names=[ast.alias(name='sys', asname=f'_sys_{random.randint(1000, 9999)}')]),
                ast.Import(names=[ast.alias(name='random', asname=f'_rand_{random.randint(1000, 9999)}')])
            ]
            
            # Add fake variables
            for _ in range(5):
                var_name = generate_random_name()
                value = random.randint(1000, 9999)
                fake_var = ast.Assign(
                    targets=[ast.Name(id=var_name, ctx=ast.Store())],
                    value=ast.Constant(value=value)
                )
                fake_vars.append(fake_var)
            
            # Insert fake code at the beginning
            tree.body = fake_imports + fake_vars + tree.body
        
        return tree
    
    def _get_obfuscated_name(self, original_name):
        """Get or generate obfuscated name"""
        if original_name in self.builtin_names:
            return original_name
        
        if original_name not in self.name_mappings:
            new_name = generate_random_name()
            while new_name in self.used_names or new_name in self.builtin_names:
                new_name = generate_random_name()
            
            self.name_mappings[original_name] = new_name
            self.used_names.add(new_name)
        
        return self.name_mappings[original_name]