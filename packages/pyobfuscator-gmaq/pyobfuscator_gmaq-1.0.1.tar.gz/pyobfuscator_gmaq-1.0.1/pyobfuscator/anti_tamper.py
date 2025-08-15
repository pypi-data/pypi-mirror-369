"""
Anti-tampering and anti-analysis protection mechanisms
"""

import os
import sys
import hashlib
import time
import random
import psutil
import threading
import logging
from .utils import generate_random_name


class AntiTamperProtection:
    """Comprehensive anti-tampering protection system"""
    
    def __init__(self, enable_debug_detection=True, enable_modification_detection=True, max_security=False):
        """
        Initialize anti-tamper protection
        
        Args:
            enable_debug_detection (bool): Enable debugger detection
            enable_modification_detection (bool): Enable file modification detection
            max_security (bool): Enable maximum security features
        """
        self.logger = logging.getLogger(self.__class__.__name__)
        self.enable_debug_detection = enable_debug_detection
        self.enable_modification_detection = enable_modification_detection
        self.max_security = max_security
        
        # Protection mechanisms
        self.protection_methods = [
            self._generate_debugger_detection,
            self._generate_timing_checks,
            self._generate_integrity_checks,
            self._generate_environment_checks
        ]
        
        if max_security:
            self.protection_methods.extend([
                self._generate_memory_protection,
                self._generate_process_monitoring,
                self._generate_vm_detection
            ])
    
    def wrap_code(self, source_code):
        """
        Wrap source code with anti-tamper protection
        
        Args:
            source_code (str): Original source code
            
        Returns:
            str: Protected source code
        """
        self.logger.debug("Adding anti-tamper protection to code...")
        
        # Generate all protection mechanisms
        protection_code = self._generate_protection_wrapper()
        
        # Embed original code
        protected_code = f"""
{protection_code}

# Protected code execution
def _execute_protected():
    \"\"\"Execute the protected code with all checks\"\"\"
    _comprehensive_protection_check()
    
    # Original code starts here
{self._indent_code(source_code, 4)}
    # Original code ends here

if __name__ == "__main__":
    _execute_protected()
else:
    # Import mode
    _comprehensive_protection_check()
{self._indent_code(source_code, 4)}
"""
        
        return protected_code
    
    def _generate_protection_wrapper(self):
        """Generate comprehensive protection wrapper"""
        
        protection_imports = """
import sys
import os
import time
import hashlib
import psutil
import threading
import random
import gc
from pathlib import Path
"""
        
        # Generate all protection functions
        protection_functions = []
        
        for method in self.protection_methods:
            protection_functions.append(method())
        
        # Main protection check function
        main_check = self._generate_main_protection_check()
        
        return protection_imports + "\n\n" + "\n\n".join(protection_functions) + "\n\n" + main_check
    
    def _generate_debugger_detection(self):
        """Generate debugger detection code"""
        return f"""
def {generate_random_name()}():
    \"\"\"Detect common debuggers and analysis tools\"\"\"
    try:
        # Check for debugger processes
        debugger_names = [
            'gdb', 'lldb', 'pdb', 'windbg', 'x64dbg', 'ida', 'ida64',
            'ollydbg', 'immunity', 'x32dbg', 'radare2', 'r2', 'ghidra',
            'strace', 'ltrace', 'dtruss', 'python-dbg'
        ]
        
        for proc in psutil.process_iter(['name', 'cmdline']):
            if proc.info['name']:
                proc_name = proc.info['name'].lower()
                if any(debugger in proc_name for debugger in debugger_names):
                    os._exit(1)
            
            if proc.info['cmdline']:
                cmdline = ' '.join(proc.info['cmdline']).lower()
                if any(debugger in cmdline for debugger in debugger_names):
                    os._exit(1)
        
        # Check for Python debugging flags
        if hasattr(sys, 'gettrace') and sys.gettrace():
            os._exit(1)
        
        # Check for interactive mode
        if hasattr(sys, 'ps1'):
            os._exit(1)
        
        # Check for IDEs
        if 'idlelib' in sys.modules or 'pdb' in sys.modules:
            os._exit(1)
            
        # Check environment variables
        debug_vars = ['PYTHONBREAKPOINT', 'PYTHONDEBUG', 'PDBDEBUG']
        for var in debug_vars:
            if os.getenv(var):
                os._exit(1)
                
    except Exception:
        os._exit(1)
"""
    
    def _generate_timing_checks(self):
        """Generate timing-based anti-analysis checks"""
        return f"""
def {generate_random_name()}():
    \"\"\"Timing-based detection of analysis attempts\"\"\"
    try:
        # Multiple timing checks with different delays
        timings = []
        
        for delay in [0.001, 0.005, 0.01, 0.02]:
            start_time = time.perf_counter()
            time.sleep(delay)
            end_time = time.perf_counter()
            
            actual_delay = end_time - start_time
            expected_delay = delay
            
            # If timing is significantly off, likely being analyzed
            if actual_delay > expected_delay * 10:
                os._exit(1)
            
            timings.append(actual_delay)
        
        # Check for consistent timing patterns (emulation detection)
        if len(set(f"{{t:.6f}}" for t in timings)) < len(timings) // 2:
            os._exit(1)
            
        # Random computation timing check
        start = time.perf_counter()
        _ = sum(i * i for i in range(1000))
        end = time.perf_counter()
        
        if end - start > 0.1:  # Should be much faster
            os._exit(1)
            
    except Exception:
        os._exit(1)
"""
    
    def _generate_integrity_checks(self):
        """Generate file integrity checks"""
        return f"""
def {generate_random_name()}():
    \"\"\"Check file integrity and detect modifications\"\"\"
    try:
        current_file = __file__
        if not os.path.exists(current_file):
            os._exit(1)
        
        with open(current_file, 'rb') as f:
            content = f.read()
        
        # Check file size (approximate)
        if len(content) < 1000:  # Suspiciously small
            os._exit(1)
        
        # Check for expected patterns
        required_patterns = [
            b'def ', b'import ', b'os._exit(1)',
            b'psutil', b'time.', b'hashlib'
        ]
        
        for pattern in required_patterns:
            if pattern not in content:
                os._exit(1)
        
        # Check for suspicious modifications
        suspicious_patterns = [
            b'print(', b'input(', b'raw_input(',
            b'debug', b'trace', b'break',
            b'pdb.', b'ipdb.', b'pudb.'
        ]
        
        content_lower = content.lower()
        for pattern in suspicious_patterns:
            if pattern in content_lower and b'#' not in content_lower[content_lower.find(pattern):content_lower.find(pattern)+50]:
                os._exit(1)
                
    except Exception:
        os._exit(1)
"""
    
    def _generate_environment_checks(self):
        """Generate environment-based checks"""
        return f"""
def {generate_random_name()}():
    \"\"\"Check execution environment for analysis indicators\"\"\"
    try:
        # Check if running in virtual machine
        vm_indicators = [
            '/proc/scsi/scsi',  # Check SCSI info for VM signatures
            '/proc/ide/hd0/model'  # Check hard drive model
        ]
        
        for indicator in vm_indicators:
            if os.path.exists(indicator):
                try:
                    with open(indicator, 'r') as f:
                        content = f.read().lower()
                        vm_names = ['virtualbox', 'vmware', 'qemu', 'xen', 'bochs']
                        if any(vm in content for vm in vm_names):
                            # Running in VM - could be analysis environment
                            time.sleep(random.uniform(0.5, 2.0))  # Delay instead of exit
                except:
                    pass
        
        # Check system load
        try:
            load_avg = os.getloadavg()[0] if hasattr(os, 'getloadavg') else 0.5
            if load_avg < 0.01:  # Suspiciously low load
                time.sleep(0.1)
        except:
            pass
        
        # Check available memory
        try:
            mem = psutil.virtual_memory()
            if mem.available < 100 * 1024 * 1024:  # Less than 100MB available
                os._exit(1)
        except:
            pass
            
        # Check process parent
        try:
            parent = psutil.Process().parent()
            if parent and parent.name().lower() in ['gdb', 'lldb', 'strace']:
                os._exit(1)
        except:
            pass
            
    except Exception:
        pass  # Don't exit on environment checks failure
"""
    
    def _generate_memory_protection(self):
        """Generate memory protection mechanisms"""
        return f"""
def {generate_random_name()}():
    \"\"\"Memory-based protection and obfuscation\"\"\"
    try:
        # Force garbage collection
        gc.collect()
        
        # Check memory usage patterns
        process = psutil.Process()
        mem_info = process.memory_info()
        
        # Detect memory debugging tools
        if mem_info.rss > 500 * 1024 * 1024:  # More than 500MB
            # Might be under memory analysis
            pass
        
        # Create decoy objects to confuse memory analysis
        decoy_data = []
        for i in range(100):
            decoy_data.append({
                f'fake_key_{i}': f'fake_value_{i}' * random.randint(10, 50),
                'random_data': os.urandom(random.randint(100, 1000)),
                'computed': sum(j * j for j in range(random.randint(50, 200)))
            })
        
        # Clear decoy data randomly
        if random.random() < 0.5:
            del decoy_data
        
        # Memory access pattern obfuscation
        dummy_list = list(range(1000))
        random.shuffle(dummy_list)
        _ = sum(dummy_list[::2])  # Access every other element
        
    except Exception:
        pass
"""
    
    def _generate_process_monitoring(self):
        """Generate process monitoring code"""
        return f"""
def {generate_random_name()}():
    \"\"\"Monitor process environment continuously\"\"\"
    def monitor_processes():
        while True:
            try:
                # Check for new suspicious processes
                for proc in psutil.process_iter(['name', 'create_time']):
                    if proc.info['name'] and proc.info['create_time']:
                        proc_name = proc.info['name'].lower()
                        
                        # Check if process started recently (within last 10 seconds)
                        if time.time() - proc.info['create_time'] < 10:
                            suspicious_names = [
                                'strace', 'ltrace', 'gdb', 'lldb',
                                'dtrace', 'dtruss', 'procmon'
                            ]
                            
                            if any(name in proc_name for name in suspicious_names):
                                os._exit(1)
                
                time.sleep(1)  # Check every second
                
            except Exception:
                time.sleep(2)
    
    # Start monitoring in background thread
    monitor_thread = threading.Thread(target=monitor_processes, daemon=True)
    monitor_thread.start()
"""
    
    def _generate_vm_detection(self):
        """Generate virtual machine detection"""
        return f"""
def {generate_random_name()}():
    \"\"\"Detect virtual machine environments\"\"\"
    try:
        vm_indicators = []
        
        # Check MAC address for VM signatures
        try:
            import uuid
            mac = uuid.getnode()
            mac_str = f'{{mac:012x}}'
            
            # Common VM MAC prefixes
            vm_mac_prefixes = [
                '000569',  # VMware
                '001c14',  # VMware
                '005056',  # VMware
                '080027',  # VirtualBox
                '525400',  # QEMU/KVM
            ]
            
            if any(mac_str.startswith(prefix) for prefix in vm_mac_prefixes):
                vm_indicators.append('mac')
        except:
            pass
        
        # Check CPU information
        try:
            with open('/proc/cpuinfo', 'r') as f:
                cpu_info = f.read().lower()
                
            vm_cpu_indicators = [
                'hypervisor', 'vmware', 'virtualbox',
                'qemu', 'kvm', 'xen', 'microsoft corporation'
            ]
            
            if any(indicator in cpu_info for indicator in vm_cpu_indicators):
                vm_indicators.append('cpu')
        except:
            pass
        
        # Check DMI information
        dmi_files = [
            '/sys/class/dmi/id/sys_vendor',
            '/sys/class/dmi/id/product_name',
            '/sys/class/dmi/id/board_vendor'
        ]
        
        for dmi_file in dmi_files:
            try:
                if os.path.exists(dmi_file):
                    with open(dmi_file, 'r') as f:
                        dmi_info = f.read().lower().strip()
                    
                    vm_vendors = [
                        'vmware', 'virtualbox', 'qemu',
                        'microsoft corporation', 'xen',
                        'red hat', 'parallels'
                    ]
                    
                    if any(vendor in dmi_info for vendor in vm_vendors):
                        vm_indicators.append('dmi')
                        break
            except:
                continue
        
        # If multiple VM indicators detected, likely in analysis environment
        if len(vm_indicators) >= 2:
            # Add delays and false operations instead of immediate exit
            time.sleep(random.uniform(1.0, 3.0))
            
            # Perform some fake operations
            fake_data = [random.random() for _ in range(1000)]
            _ = sum(fake_data)
            
    except Exception:
        pass
"""
    
    def _generate_main_protection_check(self):
        """Generate main protection check function that calls all others"""
        # Get all function names from the generated protection methods
        func_names = [generate_random_name() for _ in self.protection_methods]
        
        calls = "\n    ".join([f"{name}()" for name in func_names])
        
        return f"""
def _comprehensive_protection_check():
    \"\"\"Execute all protection mechanisms\"\"\"
    try:
        {calls}
    except SystemExit:
        raise
    except Exception:
        # If any protection check fails, exit
        os._exit(1)
"""
    
    def _indent_code(self, code, spaces):
        """Indent code by specified number of spaces"""
        lines = code.split('\n')
        indented_lines = []
        
        for line in lines:
            if line.strip():  # Don't indent empty lines
                indented_lines.append(' ' * spaces + line)
            else:
                indented_lines.append(line)
        
        return '\n'.join(indented_lines)


class RuntimeProtection:
    """Runtime protection mechanisms that activate during execution"""
    
    def __init__(self):
        self.logger = logging.getLogger(self.__class__.__name__)
        self.protection_active = False
    
    def activate_protection(self):
        """Activate runtime protection mechanisms"""
        if self.protection_active:
            return
        
        self.protection_active = True
        
        # Start protection threads
        self._start_integrity_monitor()
        self._start_debugger_monitor()
        self._start_performance_monitor()
    
    def _start_integrity_monitor(self):
        """Monitor file integrity during runtime"""
        def integrity_monitor():
            original_file = __file__ if '__file__' in globals() else None
            if not original_file:
                return
            
            try:
                # Get initial file hash
                with open(original_file, 'rb') as f:
                    initial_content = f.read()
                initial_hash = hashlib.sha256(initial_content).hexdigest()
                
                while True:
                    time.sleep(5)  # Check every 5 seconds
                    
                    if os.path.exists(original_file):
                        with open(original_file, 'rb') as f:
                            current_content = f.read()
                        current_hash = hashlib.sha256(current_content).hexdigest()
                        
                        if current_hash != initial_hash:
                            os._exit(1)  # File was modified
                    else:
                        os._exit(1)  # File was deleted
                        
            except Exception:
                os._exit(1)
        
        thread = threading.Thread(target=integrity_monitor, daemon=True)
        thread.start()
    
    def _start_debugger_monitor(self):
        """Continuously monitor for debuggers"""
        def debugger_monitor():
            while True:
                try:
                    # Check trace function
                    if hasattr(sys, 'gettrace') and sys.gettrace():
                        os._exit(1)
                    
                    # Check for new debugger processes
                    for proc in psutil.process_iter(['name']):
                        if proc.info['name']:
                            name = proc.info['name'].lower()
                            if any(debugger in name for debugger in ['gdb', 'pdb', 'lldb']):
                                os._exit(1)
                    
                    time.sleep(2)
                    
                except Exception:
                    time.sleep(1)
        
        thread = threading.Thread(target=debugger_monitor, daemon=True)
        thread.start()
    
    def _start_performance_monitor(self):
        """Monitor performance for analysis detection"""
        def performance_monitor():
            while True:
                try:
                    start_time = time.perf_counter()
                    
                    # Perform standard operations
                    dummy_data = [i * i for i in range(1000)]
                    _ = sum(dummy_data)
                    
                    end_time = time.perf_counter()
                    
                    # If operations take too long, might be under analysis
                    if end_time - start_time > 0.1:
                        # Add delay instead of immediate exit
                        time.sleep(random.uniform(0.5, 2.0))
                    
                    time.sleep(3)
                    
                except Exception:
                    time.sleep(1)
        
        thread = threading.Thread(target=performance_monitor, daemon=True)
        thread.start()
