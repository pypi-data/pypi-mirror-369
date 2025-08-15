"""
Advanced AST transformation utilities for code obfuscation
"""

import ast
import random
import string
from .utils import generate_random_name


class BaseTransformer(ast.NodeTransformer):
    """Base class for AST transformers with common utilities"""
    
    def __init__(self):
        self.transformation_count = 0
    
    def transform_node(self, node):
        """Apply transformation to a node and increment counter"""
        self.transformation_count += 1
        return self.generic_visit(node)


class ComplexExpressionGenerator(BaseTransformer):
    """Generate complex mathematical expressions that evaluate to simple values"""
    
    def create_complex_number(self, target_value):
        """Create a complex expression that evaluates to target_value"""
        operations = [
            lambda x, y: ast.BinOp(left=x, op=ast.Add(), right=y),
            lambda x, y: ast.BinOp(left=x, op=ast.Sub(), right=y),
            lambda x, y: ast.BinOp(left=x, op=ast.Mult(), right=y),
        ]
        
        # Start with target value
        expr = ast.Constant(value=target_value)
        
        # Add complexity
        for _ in range(random.randint(2, 5)):
            operation = random.choice(operations)
            rand_val = random.randint(1, 100)
            
            if operation == operations[0]:  # Add
                expr = operation(expr, ast.Constant(value=rand_val))
                expr = ast.BinOp(left=expr, op=ast.Sub(), right=ast.Constant(value=rand_val))
            elif operation == operations[1]:  # Sub
                expr = operation(expr, ast.Constant(value=rand_val))
                expr = ast.BinOp(left=expr, op=ast.Add(), right=ast.Constant(value=rand_val))
            elif operation == operations[2] and rand_val != 0:  # Mult
                expr = operation(expr, ast.Constant(value=rand_val))
                expr = ast.BinOp(left=expr, op=ast.FloorDiv(), right=ast.Constant(value=rand_val))
        
        return expr
    
    def visit_Constant(self, node):
        """Replace simple constants with complex expressions"""
        if isinstance(node.value, int) and abs(node.value) < 1000:
            if random.random() < 0.3:  # 30% chance
                return self.create_complex_number(node.value)
        
        return self.generic_visit(node)


class LoopUnroller(BaseTransformer):
    """Unroll small loops to obfuscate iteration patterns"""
    
    def visit_For(self, node):
        """Unroll simple for loops"""
        # Only unroll simple range() loops
        if (isinstance(node.iter, ast.Call) and
            isinstance(node.iter.func, ast.Name) and
            node.iter.func.id == 'range' and
            len(node.iter.args) == 1 and
            isinstance(node.iter.args[0], ast.Constant) and
            isinstance(node.iter.args[0].value, int) and
            node.iter.args[0].value <= 5):
            
            # Unroll the loop
            unrolled_body = []
            for i in range(node.iter.args[0].value):
                # Replace loop variable with constant
                target_id = node.target.id if hasattr(node.target, 'id') else str(node.target)
                replacer = VariableReplacer(target_id, ast.Constant(value=i))
                for stmt in node.body:
                    new_stmt = replacer.visit(stmt)
                    unrolled_body.append(new_stmt)
            
            return unrolled_body
        
        return self.generic_visit(node)


class VariableReplacer(BaseTransformer):
    """Replace all occurrences of a variable with a given expression"""
    
    def __init__(self, var_name, replacement):
        super().__init__()
        self.var_name = var_name
        self.replacement = replacement
    
    def visit_Name(self, node):
        """Replace variable references"""
        if node.id == self.var_name and isinstance(node.ctx, ast.Load):
            return self.replacement
        return node


class FunctionCallObfuscator(BaseTransformer):
    """Obfuscate function calls with indirect calls"""
    
    def __init__(self):
        super().__init__()
        self.function_refs = {}
    
    def visit_Module(self, node):
        """Add function reference dictionary at module level"""
        # First pass - collect function calls
        self.generic_visit(node)
        
        # Add function reference dictionary
        if self.function_refs:
            func_dict_name = generate_random_name()
            func_dict = ast.Assign(
                targets=[ast.Name(id=func_dict_name, ctx=ast.Store())],
                value=ast.Dict(
                    keys=[ast.Constant(value=k) for k in self.function_refs.keys()],
                    values=[ast.Name(id=v, ctx=ast.Load()) for v in self.function_refs.values()]
                )
            )
            
            node.body.insert(0, func_dict)
        
        return node
    
    def visit_Call(self, node):
        """Replace direct function calls with dictionary lookups"""
        if (isinstance(node.func, ast.Name) and
            node.func.id not in ['print', 'len', 'str', 'int', 'float', 'range']):
            
            func_name = node.func.id
            if func_name not in self.function_refs:
                self.function_refs[func_name] = func_name
            
            # Create indirect call
            dict_name = generate_random_name()
            indirect_call = ast.Call(
                func=ast.Subscript(
                    value=ast.Name(id=dict_name, ctx=ast.Load()),
                    slice=ast.Constant(value=func_name),
                    ctx=ast.Load()
                ),
                args=node.args,
                keywords=node.keywords
            )
            
            return indirect_call
        
        return self.generic_visit(node)


class ExceptionObfuscator(BaseTransformer):
    """Add fake exception handling to confuse analysis"""
    
    def visit_FunctionDef(self, node):
        """Wrap function bodies in fake try-except blocks"""
        if random.random() < 0.4:  # 40% chance
            fake_exception = generate_random_name()
            
            # Create fake exception class
            fake_exc_class = ast.ClassDef(
                name=fake_exception,
                bases=[ast.Name(id='Exception', ctx=ast.Load())],
                keywords=[],
                body=[ast.Pass()],
                decorator_list=[]
            )
            
            # Wrap function body in try-except
            try_block = ast.Try(
                body=node.body,
                handlers=[
                    ast.ExceptHandler(
                        type=ast.Name(id=fake_exception, ctx=ast.Load()),
                        name=None,
                        body=[ast.Pass()]
                    )
                ],
                orelse=[],
                finalbody=[]
            )
            
            node.body = [try_block]
            
            # Add fake exception class before function
            return [fake_exc_class, node]
        
        return self.generic_visit(node)


class ImportObfuscator(BaseTransformer):
    """Obfuscate import statements"""
    
    def __init__(self):
        super().__init__()
        self.import_aliases = {}
    
    def visit_Import(self, node):
        """Create aliases for imports"""
        new_aliases = []
        
        for alias in node.names:
            if alias.asname is None:
                # Create random alias
                new_alias = generate_random_name()
                self.import_aliases[alias.name] = new_alias
                new_aliases.append(ast.alias(name=alias.name, asname=new_alias))
            else:
                new_aliases.append(alias)
        
        node.names = new_aliases
        return node
    
    def visit_ImportFrom(self, node):
        """Create aliases for from imports"""
        if node.names and node.names[0].name != '*':
            new_aliases = []
            
            for alias in node.names:
                if alias.asname is None:
                    new_alias = generate_random_name()
                    import_key = f"{node.module}.{alias.name}"
                    self.import_aliases[import_key] = new_alias
                    new_aliases.append(ast.alias(name=alias.name, asname=new_alias))
                else:
                    new_aliases.append(alias)
            
            node.names = new_aliases
        
        return node


class ListComprehensionObfuscator(BaseTransformer):
    """Convert simple loops to list comprehensions and vice versa"""
    
    def visit_For(self, node):
        """Convert simple for loops to list comprehensions where possible"""
        # Look for simple append patterns
        if (len(node.body) == 1 and
            isinstance(node.body[0], ast.Expr) and
            isinstance(node.body[0].value, ast.Call) and
            isinstance(node.body[0].value.func, ast.Attribute) and
            node.body[0].value.func.attr == 'append'):
            
            # Convert to list comprehension
            target = node.body[0].value.func.value
            element = node.body[0].value.args[0] if node.body[0].value.args else ast.Constant(value=None)
            
            list_comp = ast.ListComp(
                elt=element,
                generators=[
                    ast.comprehension(
                        target=node.target,
                        iter=node.iter,
                        ifs=[],
                        is_async=0
                    )
                ]
            )
            
            # Create assignment
            assign = ast.Assign(
                targets=[target],
                value=list_comp
            )
            
            return assign
        
        return self.generic_visit(node)


class DictionaryObfuscator(BaseTransformer):
    """Obfuscate dictionary access patterns"""
    
    def visit_Subscript(self, node):
        """Replace dictionary access with get() method calls"""
        if isinstance(node.slice, ast.Constant) and random.random() < 0.3:
            # Replace dict[key] with dict.get(key, None)
            get_call = ast.Call(
                func=ast.Attribute(
                    value=node.value,
                    attr='get',
                    ctx=ast.Load()
                ),
                args=[
                    node.slice,
                    ast.Constant(value=None)
                ],
                keywords=[]
            )
            
            return get_call
        
        return self.generic_visit(node)


class StringConcatenationObfuscator(BaseTransformer):
    """Obfuscate string concatenation patterns"""
    
    def visit_BinOp(self, node):
        """Replace string concatenation with join() calls"""
        if (isinstance(node.op, ast.Add) and
            self._is_string_node(node.left) and
            self._is_string_node(node.right)):
            
            if random.random() < 0.4:  # 40% chance
                # Replace with join
                join_call = ast.Call(
                    func=ast.Attribute(
                        value=ast.Constant(value=''),
                        attr='join',
                        ctx=ast.Load()
                    ),
                    args=[
                        ast.List(
                            elts=[node.left, node.right],
                            ctx=ast.Load()
                        )
                    ],
                    keywords=[]
                )
                
                return join_call
        
        return self.generic_visit(node)
    
    def _is_string_node(self, node):
        """Check if node represents a string"""
        return (isinstance(node, ast.Constant) and isinstance(node.value, str)) or \
               (isinstance(node, ast.Call) and 
                isinstance(node.func, ast.Name) and 
                node.func.id == 'str')
