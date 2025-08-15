"""
Bytecode manipulation and protection utilities
"""

import marshal
import dis
import types
import sys
import logging
import random
from .utils import generate_random_name


class BytecodeManager:
    """Manage Python bytecode operations and transformations"""
    
    def __init__(self):
        self.logger = logging.getLogger(self.__class__.__name__)
    
    def compile_to_bytecode(self, source_code, filename='<obfuscated>'):
        """
        Compile source code to bytecode
        
        Args:
            source_code (str): Python source code
            filename (str): Filename for compilation
            
        Returns:
            types.CodeType: Compiled code object
        """
        try:
            return compile(source_code, filename, 'exec')
        except Exception as e:
            self.logger.error(f"Bytecode compilation failed: {str(e)}")
            raise
    
    def serialize_bytecode(self, code_obj):
        """
        Serialize code object to bytes
        
        Args:
            code_obj (types.CodeType): Code object
            
        Returns:
            bytes: Serialized bytecode
        """
        try:
            return marshal.dumps(code_obj)
        except Exception as e:
            self.logger.error(f"Bytecode serialization failed: {str(e)}")
            raise
    
    def deserialize_bytecode(self, bytecode_data):
        """
        Deserialize bytecode data to code object
        
        Args:
            bytecode_data (bytes): Serialized bytecode
            
        Returns:
            types.CodeType: Code object
        """
        try:
            return marshal.loads(bytecode_data)
        except Exception as e:
            self.logger.error(f"Bytecode deserialization failed: {str(e)}")
            raise
    
    def obfuscate_bytecode(self, code_obj):
        """
        Apply bytecode-level obfuscation
        
        Args:
            code_obj (types.CodeType): Original code object
            
        Returns:
            types.CodeType: Obfuscated code object
        """
        try:
            # Extract code attributes
            co_argcount = code_obj.co_argcount
            co_posonlyargcount = getattr(code_obj, 'co_posonlyargcount', 0)
            co_kwonlyargcount = code_obj.co_kwonlyargcount
            co_nlocals = code_obj.co_nlocals
            co_stacksize = code_obj.co_stacksize
            co_flags = code_obj.co_flags
            co_code = code_obj.co_code
            co_consts = code_obj.co_consts
            co_names = code_obj.co_names
            co_varnames = code_obj.co_varnames
            co_filename = code_obj.co_filename
            co_name = code_obj.co_name
            co_firstlineno = code_obj.co_firstlineno
            co_lnotab = code_obj.co_lnotab
            co_freevars = code_obj.co_freevars
            co_cellvars = code_obj.co_cellvars
            
            # Obfuscate constants
            obfuscated_consts = self._obfuscate_constants(co_consts)
            
            # Obfuscate names
            obfuscated_names = self._obfuscate_names(co_names)
            obfuscated_varnames = self._obfuscate_names(co_varnames)
            
            # Create new code object with obfuscated elements
            if sys.version_info >= (3, 8):
                new_code_obj = types.CodeType(
                    co_argcount,
                    co_posonlyargcount,
                    co_kwonlyargcount,
                    co_nlocals,
                    co_stacksize,
                    co_flags,
                    co_code,
                    obfuscated_consts,
                    obfuscated_names,
                    obfuscated_varnames,
                    co_filename,
                    co_name,
                    co_firstlineno,
                    co_lnotab,
                    co_freevars,
                    co_cellvars
                )
            else:
                new_code_obj = types.CodeType(
                    co_argcount,
                    co_kwonlyargcount,
                    co_nlocals,
                    co_stacksize,
                    co_flags,
                    co_code,
                    obfuscated_consts,
                    obfuscated_names,
                    obfuscated_varnames,
                    co_filename,
                    co_name,
                    co_firstlineno,
                    co_lnotab,
                    co_freevars,
                    co_cellvars
                )
            
            return new_code_obj
            
        except Exception as e:
            self.logger.error(f"Bytecode obfuscation failed: {str(e)}")
            return code_obj  # Return original on failure
    
    def _obfuscate_constants(self, consts):
        """
        Obfuscate constants in bytecode
        
        Args:
            consts (tuple): Original constants
            
        Returns:
            tuple: Obfuscated constants
        """
        obfuscated = []
        
        for const in consts:
            if isinstance(const, str) and len(const) > 1:
                # Don't obfuscate very short strings or special strings
                if const in ['', ' ', '\n', '\t', '__main__']:
                    obfuscated.append(const)
                else:
                    # Replace with a lambda that returns the string
                    obfuscated.append(const)  # Keep original for now
            elif isinstance(const, (int, float)) and abs(const) > 1:
                # Obfuscate numbers with mathematical expressions
                if isinstance(const, int):
                    # Create equivalent expression
                    offset = random.randint(1, 100)
                    obfuscated.append(const)  # Keep original for now
                else:
                    obfuscated.append(const)
            elif isinstance(const, types.CodeType):
                # Recursively obfuscate nested code objects
                obfuscated.append(self.obfuscate_bytecode(const))
            else:
                obfuscated.append(const)
        
        return tuple(obfuscated)
    
    def _obfuscate_names(self, names):
        """
        Obfuscate names in bytecode
        
        Args:
            names (tuple): Original names
            
        Returns:
            tuple: Obfuscated names
        """
        # For now, keep original names to maintain functionality
        # In a more advanced implementation, this would maintain a mapping
        # and update all references accordingly
        return names
    
    def create_bytecode_wrapper(self, bytecode_data):
        """
        Create a wrapper that loads and executes bytecode
        
        Args:
            bytecode_data (bytes): Serialized bytecode
            
        Returns:
            str: Python code that executes the bytecode
        """
        import base64
        
        encoded_bytecode = base64.b64encode(bytecode_data).decode('ascii')
        
        wrapper_template = f'''
import base64
import marshal
import sys

def _load_and_execute():
    """Load and execute protected bytecode"""
    try:
        # Decode bytecode
        bytecode_data = base64.b64decode('{encoded_bytecode}')
        
        # Load code object
        code_obj = marshal.loads(bytecode_data)
        
        # Execute code
        exec(code_obj, globals())
        
    except Exception:
        sys.exit(1)

if __name__ == "__main__":
    _load_and_execute()
else:
    _load_and_execute()
'''
        
        return wrapper_template
    
    def analyze_bytecode(self, code_obj):
        """
        Analyze bytecode for optimization opportunities
        
        Args:
            code_obj (types.CodeType): Code object to analyze
            
        Returns:
            dict: Analysis results
        """
        analysis = {
            'instructions': [],
            'constants': len(code_obj.co_consts),
            'names': len(code_obj.co_names),
            'variables': len(code_obj.co_varnames),
            'stack_size': code_obj.co_stacksize,
            'flags': code_obj.co_flags
        }
        
        try:
            # Disassemble bytecode
            instructions = list(dis.get_instructions(code_obj))
            analysis['instructions'] = len(instructions)
            
            # Analyze instruction patterns
            opcode_counts = {}
            for instr in instructions:
                opname = instr.opname
                opcode_counts[opname] = opcode_counts.get(opname, 0) + 1
            
            analysis['opcodes'] = opcode_counts
            analysis['complexity'] = len(opcode_counts)
            
        except Exception as e:
            self.logger.debug(f"Bytecode analysis failed: {str(e)}")
        
        return analysis
    
    def create_polymorphic_loader(self, bytecode_data):
        """
        Create a polymorphic loader that changes appearance
        
        Args:
            bytecode_data (bytes): Serialized bytecode
            
        Returns:
            str: Polymorphic loader code
        """
        import base64
        
        # Generate random variable names
        loader_vars = {
            'data_var': generate_random_name(),
            'decode_func': generate_random_name(),
            'execute_func': generate_random_name(),
            'temp_var': generate_random_name()
        }
        
        encoded_bytecode = base64.b64encode(bytecode_data).decode('ascii')
        
        # Split encoded data into chunks for obfuscation
        chunk_size = random.randint(100, 200)
        chunks = [encoded_bytecode[i:i+chunk_size] 
                 for i in range(0, len(encoded_bytecode), chunk_size)]
        
        # Create chunk variables
        chunk_vars = [generate_random_name() for _ in chunks]
        chunk_assignments = []
        
        for var, chunk in zip(chunk_vars, chunks):
            chunk_assignments.append(f"{var} = '{chunk}'")
        
        loader_template = f'''
import base64
import marshal
import sys
import random

# Obfuscated data chunks
{chr(10).join(chunk_assignments)}

def {loader_vars['decode_func']}():
    """Decode the protected payload"""
    {loader_vars['data_var']} = {''.join([f" + {var}" for var in chunk_vars])[3:]}  # Remove first " + "
    return base64.b64decode({loader_vars['data_var']})

def {loader_vars['execute_func']}():
    """Execute the protected code"""
    try:
        # Add some fake operations
        {loader_vars['temp_var']} = random.randint(1, 1000)
        {loader_vars['temp_var']} = {loader_vars['temp_var']} * 2 - {loader_vars['temp_var']} * 2 + {loader_vars['temp_var']}
        
        # Decode and execute
        bytecode = {loader_vars['decode_func']}()
        code_obj = marshal.loads(bytecode)
        
        # More fake operations
        dummy_list = [i for i in range({loader_vars['temp_var']} % 10)]
        _ = sum(dummy_list)
        
        exec(code_obj, globals())
        
    except Exception:
        sys.exit(1)

if __name__ == "__main__":
    {loader_vars['execute_func']}()
else:
    {loader_vars['execute_func']}()
'''
        
        return loader_template
    
    def inject_fake_bytecode(self, code_obj):
        """
        Inject fake bytecode instructions to confuse analysis
        
        Args:
            code_obj (types.CodeType): Original code object
            
        Returns:
            types.CodeType: Code object with fake instructions
        """
        # This is a complex operation that would require
        # low-level bytecode manipulation. For now, return original
        # In a full implementation, this would inject NOPs,
        # fake jumps, and other misleading instructions
        
        return code_obj
    
    def create_self_modifying_loader(self, bytecode_data):
        """
        Create loader that modifies itself during execution
        
        Args:
            bytecode_data (bytes): Serialized bytecode
            
        Returns:
            str: Self-modifying loader code
        """
        import base64
        
        encoded_bytecode = base64.b64encode(bytecode_data).decode('ascii')
        
        # Create self-modifying loader
        loader_template = f'''
import base64
import marshal
import sys
import types

class SelfModifyingLoader:
    def __init__(self):
        self.data = '{encoded_bytecode}'
        self.decoded = False
        
    def __call__(self):
        if not self.decoded:
            # Decode data
            bytecode = base64.b64decode(self.data)
            code_obj = marshal.loads(bytecode)
            
            # Modify self to remove trace
            self.data = None
            self.decoded = True
            
            # Execute
            exec(code_obj, globals())
        else:
            # Already executed, do nothing
            pass

# Create and execute loader
_loader = SelfModifyingLoader()
_loader()

# Clean up
del _loader
'''
        
        return loader_template
