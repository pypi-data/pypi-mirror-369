# FILE 1: dome/__init__.py (Universal Library - Works in Terminal, IDEs, Notebooks)
"""
DOME - Natural Language Programming with Claude AI
=================================================

Universal Usage (works everywhere):
    import dome
    
    # Method 1: Direct execution (works in all environments)
    dome.run("make a list of the first 10 square numbers")
    dome.run("calculate factorial of 15")
    
    # Method 2: Get result back (perfect for notebooks)
    result = dome.execute("create fibonacci sequence up to 100")
    
    # Method 3: Multi-line programs
    dome.run('''
    load data from sales.csv
    clean the data by removing nulls
    create a bar chart
    save as analysis.png
    ''')
    
    # Method 4: Interactive mode (terminal only, graceful fallback in IDEs)
    dome.start()
"""

import sys
import ast
import code
import types
import traceback
import threading
import builtins
import os
import logging
import re
import io
import contextlib
from typing import Any, Dict, Optional, Union, List
import requests
import json
from datetime import datetime

__version__ = "2.0.0"
__author__ = "e-dome.dev"
__description__ = "DOME - Universal Natural Language Programming"

# REPLACE WITH YOUR ACTUAL CLAUDE API KEY
CLAUDE_API_KEY = "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"

# Security Configuration
DOME_SECURITY_ENABLED = True
DOME_EXECUTION_TIMEOUT = 30
DOME_RESTRICTED_IMPORTS = {
    'os.system', 'subprocess.run', 'subprocess.call', 'subprocess.Popen',
    'eval', 'exec', '__import__', 'shutil.rmtree', 'os.remove'
}

# Environment Detection


def _detect_environment():
    """Detect the current execution environment"""
    try:
        # Check for Jupyter/Colab
        if 'ipykernel' in sys.modules or 'google.colab' in sys.modules:
            return 'jupyter'
        # Check for IPython
        if 'IPython' in sys.modules:
            return 'ipython'
        # Check for VSCode
        if 'VSCODE_PID' in os.environ:
            return 'vscode'
        # Check if TTY is available (terminal)
        if hasattr(sys.stdin, 'isatty') and sys.stdin.isatty():
            return 'terminal'
        # Default to script/IDE
        return 'ide'
    except:
        return 'unknown'


ENVIRONMENT = _detect_environment()

# Setup logging
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - DOME - %(message)s')
logger = logging.getLogger('DOME')

# Global execution context
_global_context = {
    'math': __import__('math'),
    'random': __import__('random'),
    'datetime': __import__('datetime'),
    'json': __import__('json'),
    're': __import__('re'),
}

# Try to import data science libraries
try:
    _global_context['np'] = __import__('numpy')
    _global_context['numpy'] = _global_context['np']
except ImportError:
    pass

try:
    _global_context['pd'] = __import__('pandas')
    _global_context['pandas'] = _global_context['pd']
except ImportError:
    pass

try:
    _global_context['plt'] = __import__(
        'matplotlib.pyplot', fromlist=['pyplot'])
    _global_context['matplotlib'] = __import__('matplotlib')
except ImportError:
    pass


class DOMESecurityError(Exception):
    """Security violation error"""
    pass


class DOMEResult:
    """Result object for DOME execution"""

    def __init__(self, command: str, success: bool = True, output: str = "",
                 data: Any = None, error: str = None, code: str = ""):
        self.command = command
        self.success = success
        self.output = output
        self.data = data
        self.error = error
        self.code = code
        self.timestamp = datetime.now()

    def __str__(self):
        if self.success:
            return self.output
        else:
            return f"Error: {self.error}"

    def __repr__(self):
        status = "✅" if self.success else "❌"
        return f"DOMEResult({status} '{self.command[:30]}...')"


class ClaudeTranslator:
    """Translates natural language to Python using Claude AI"""

    def __init__(self):
        self.api_key = CLAUDE_API_KEY
        self.api_url = "https://api.anthropic.com/v1/messages"
        self.headers = {
            "Content-Type": "application/json",
            "x-api-key": self.api_key,
            "anthropic-version": "2023-06-01"
        }

    def translate_to_python(self, natural_language: str, context: Dict = None) -> str:
        """Translate natural language to Python with advanced error handling"""
        try:
            return self._primary_translation(natural_language, context)
        except Exception as e:
            logger.warning(f"Primary translation failed: {e}")
            try:
                return self._stronger_claude_api(natural_language, context)
            except Exception as e2:
                logger.warning(f"Stronger API failed: {e2}")
                return self._enhanced_pattern_matching(natural_language)

    def _primary_translation(self, natural_language: str, context: Dict = None) -> str:
        """Primary Claude API translation"""
        if not self.api_key or self.api_key == "your-claude-api-key-here":
            raise Exception("Claude API key not configured")

        context_info = ""
        if context:
            vars_info = {k: str(type(v).__name__) for k, v in context.items()
                         if not k.startswith('_') and not callable(v)}
            if vars_info:
                context_info = f"Available variables: {vars_info}\n"

        is_multiline = '\n' in natural_language or len(
            natural_language.split('.')) > 3

        # Enhanced prompt for universal environments
        if is_multiline:
            prompt = f"""Convert this multi-line natural language program into Python code. Return ONLY executable Python code.

{context_info}

CRITICAL REQUIREMENTS:
- Return ONLY Python code, no explanations, no markdown
- Import ALL required libraries at the top
- Code must work in any Python environment (Jupyter, IDE, terminal)
- Store final results in variables when appropriate
- Use print() for meaningful output
- Handle errors gracefully with try/except

Multi-line Program:
{natural_language}

Python code:"""
        else:
            prompt = f"""Convert this natural language command to Python code. Return ONLY executable Python code.

{context_info}

CRITICAL REQUIREMENTS:
- Return ONLY Python code, no explanations, no markdown
- Import required libraries if needed
- Code must work in Jupyter notebooks, IDEs, and terminal
- Use print() for output
- Store result in a variable if appropriate

Command: {natural_language}

Python code:"""

        payload = {
            "model": "claude-3-5-sonnet-20241022",
            "max_tokens": 2000 if is_multiline else 1000,
            "messages": [{"role": "user", "content": prompt}]
        }

        try:
            response = requests.post(
                self.api_url, headers=self.headers, json=payload, timeout=30)

            if response.status_code == 400:
                raise Exception(
                    f"Bad Request: Invalid model name. Try updating model name.")
            elif response.status_code == 401:
                raise Exception("Unauthorized: Invalid API key")
            elif response.status_code == 404:
                raise Exception(f"Model not found: {payload['model']}")
            elif response.status_code == 429:
                raise Exception("Rate limit exceeded")

            response.raise_for_status()

        except requests.exceptions.ConnectionError:
            raise Exception("Connection Error: Check internet connection")
        except requests.exceptions.Timeout:
            raise Exception("Timeout: API request too slow")

        result = response.json()
        python_code = result['content'][0]['text'].strip()

        # Clean up code blocks more thoroughly
        if '```python' in python_code:
            python_code = python_code.split('```python')[1].split('```')[0]
        elif '```' in python_code:
            python_code = python_code.split('```')[1].split('```')[0]

        # Remove any remaining markdown or explanations
        lines = python_code.split('\n')
        code_lines = []
        for line in lines:
            line = line.strip()
            if line and not line.startswith('#') or (line.startswith('#') and 'import' in line):
                code_lines.append(line)

        return '\n'.join(code_lines).strip()

    def _stronger_claude_api(self, natural_language: str, context: Dict = None) -> str:
        """Stronger Claude API fallback"""
        stronger_prompt = f"""You are an expert Python programmer. Convert this to executable Python code.

ABSOLUTE REQUIREMENTS:
1. Return ONLY Python code - zero explanations
2. Code must execute in any environment (Jupyter/IDE/terminal)
3. Import ALL required libraries
4. Use print() for meaningful output
5. Handle all errors gracefully

Command: {natural_language}

Python code:"""

        payload = {
            "model": "claude-3-5-sonnet-20241022",
            "max_tokens": 2000,
            "temperature": 0.1,
            "messages": [{"role": "user", "content": stronger_prompt}]
        }

        try:
            response = requests.post(
                self.api_url, headers=self.headers, json=payload, timeout=45)
            response.raise_for_status()

            result = response.json()
            python_code = result['content'][0]['text'].strip()

            # Clean aggressively
            if '```' in python_code:
                python_code = python_code.split(
                    '```')[1] if python_code.count('```') >= 2 else python_code
                python_code = python_code.split('```')[0]

            return python_code.strip()

        except Exception:
            raise Exception("Stronger API also failed")

    def _enhanced_pattern_matching(self, command: str) -> str:
        """Enhanced pattern matching fallback"""
        command = command.lower().strip()

        patterns = {
            r'calculate factorial of (\d+)': lambda m: f"""
import math
result = math.factorial({m.group(1)})
print(f"Factorial of {m.group(1)}: {{result:,}}")
""",
            r'make a list of (?:the )?first (\d+) square numbers': lambda m: f"""
squares = [i**2 for i in range(1, {int(m.group(1))+1})]
print(f"First {m.group(1)} square numbers: {{squares}}")
result = squares
""",
            r'create (?:a )?fibonacci sequence up to (\d+)': lambda m: f"""
fib = [0, 1]
while True:
    next_fib = fib[-1] + fib[-2]
    if next_fib > {m.group(1)}:
        break
    fib.append(next_fib)
print(f"Fibonacci sequence up to {m.group(1)}: {{fib}}")
result = fib
""",
            r'hello world': lambda m: 'print("Hello, World!")',
            r'current (?:date and )?time': lambda m: '''
from datetime import datetime
now = datetime.now()
print(f"Current time: {now}")
result = now
''',
        }

        for pattern, code_func in patterns.items():
            match = re.search(pattern, command)
            if match:
                try:
                    return code_func(match).strip()
                except:
                    continue

        return f'print("⚠️ Command not understood: {command}")'


class SecuritySandbox:
    """Security sandbox for safe code execution"""

    def __init__(self):
        self.timeout = DOME_EXECUTION_TIMEOUT
        self.restricted_patterns = [
            r'import\s+os\b', r'subprocess\.', r'eval\s*\(', r'exec\s*\(',
            r'__import__\s*\(', r'open\s*\([^)]*["\']w', r'shutil\.rmtree'
        ]

    def check_code_safety(self, code: str) -> tuple[bool, str]:
        """Check if code is safe to execute"""
        if not DOME_SECURITY_ENABLED:
            return True, "Security disabled"

        for pattern in self.restricted_patterns:
            if re.search(pattern, code, re.IGNORECASE):
                return False, f"Restricted pattern: {pattern}"
        return True, "Safe"

    def execute_with_timeout(self, code: str, globals_dict: dict, locals_dict: dict):
        """Execute code with timeout and security checks"""
        is_safe, message = self.check_code_safety(code)
        if not is_safe:
            raise DOMESecurityError(f"Security violation: {message}")

        if ENVIRONMENT in ['jupyter', 'ipython', 'vscode']:
            # Direct execution in notebook/IDE environments
            return exec(code, globals_dict, locals_dict)

        # Threaded execution with timeout for terminal
        result = None
        exception = None

        def target():
            nonlocal result, exception
            try:
                result = exec(code, globals_dict, locals_dict)
            except Exception as e:
                exception = e

        thread = threading.Thread(target=target, daemon=True)
        thread.start()
        thread.join(timeout=self.timeout)

        if thread.is_alive():
            raise TimeoutError(
                f"Execution timed out after {self.timeout} seconds")

        if exception:
            raise exception

        return result


class DOMEExecutor:
    """Universal DOME executor that works in all environments"""

    def __init__(self):
        self.translator = ClaudeTranslator()
        self.sandbox = SecuritySandbox()
        self.execution_history: List[DOMEResult] = []
        self.context = _global_context.copy()

    def execute(self, natural_language: str, return_result: bool = True, show_code: bool = False) -> Union[DOMEResult, Any]:
        """
        Execute natural language command universally

        Args:
            natural_language: The natural language command
            return_result: Whether to return a DOMEResult object (True) or just the output (False)
            show_code: Whether to display the generated Python code

        Returns:
            DOMEResult object if return_result=True, otherwise the execution output
        """
        command = natural_language.strip()

        if not command:
            result = DOMEResult(command, success=False, error="Empty command")
            return result if return_result else None

        try:
            # Translate to Python
            python_code = self.translator.translate_to_python(
                command, self.context)

            if show_code:
                print(f"🐍 Generated Python code:")
                print("-" * 40)
                print(python_code)
                print("-" * 40)

            # Capture output
            output_buffer = io.StringIO()
            result_data = None

            with contextlib.redirect_stdout(output_buffer):
                try:
                    # Execute the code
                    self.sandbox.execute_with_timeout(
                        python_code, self.context, self.context)

                    # Try to capture result if there's a 'result' variable
                    if 'result' in self.context:
                        result_data = self.context['result']

                except Exception as e:
                    # Handle execution errors with helpful messages
                    error_message = self._format_execution_error(e, command)
                    if not return_result:
                        print(f"🔴 {error_message}")
                        return None

                    result = DOMEResult(
                        command=command,
                        success=False,
                        error=error_message,
                        code=python_code
                    )
                    self.execution_history.append(result)
                    return result if return_result else None

            # Get captured output
            output = output_buffer.getvalue().strip()

            # Create successful result
            result = DOMEResult(
                command=command,
                success=True,
                output=output,
                data=result_data,
                code=python_code
            )

            self.execution_history.append(result)

            # Display output if not returning result object
            if not return_result:
                if output:
                    print(output)
                return result_data

            return result

        except Exception as e:
            # Handle translation errors
            error_message = f"Translation failed: {str(e)}"
            if not return_result:
                print(f"🔴 {error_message}")
                return None

            result = DOMEResult(
                command=command,
                success=False,
                error=error_message
            )
            self.execution_history.append(result)
            return result

    def _format_execution_error(self, error: Exception, command: str) -> str:
        """Format execution errors with helpful messages"""
        error_type = type(error).__name__
        error_msg = str(error)

        helpful_messages = {
            'ImportError': "📦 Missing library. Try: pip install [library-name]",
            'FileNotFoundError': "📁 File not found. Check the file path and name",
            'PermissionError': "🚫 Permission denied. Check file permissions",
            'ValueError': "❌ Invalid value. Check your input data",
            'TypeError': "🔤 Type error. Check data types in your command",
            'ZeroDivisionError': "➗ Cannot divide by zero",
            'KeyError': "🔑 Key not found. Check if the key/column exists",
            'IndexError': "📍 Index out of range. Check array/list bounds",
            'MemoryError': "💾 Not enough memory. Try smaller datasets",
            'TimeoutError': "⏱️ Execution timeout. Command took too long",
            'DOMESecurityError': "🔒 Security restriction. Command blocked for safety",
        }

        helpful_msg = helpful_messages.get(error_type, "🔴 Unexpected error")
        return f"{helpful_msg}: {error_msg}"

    def run_multiline(self, program: str, show_code: bool = False) -> DOMEResult:
        """Execute a multi-line natural language program"""
        return self.execute(program, return_result=True, show_code=show_code)

    def history(self, limit: int = 10) -> List[DOMEResult]:
        """Get execution history"""
        return self.execution_history[-limit:] if limit else self.execution_history

    def clear_history(self):
        """Clear execution history"""
        self.execution_history.clear()

    def clear_context(self):
        """Reset execution context"""
        self.context = _global_context.copy()


# Global executor instance
_dome_executor = DOMEExecutor()


# ==================== PUBLIC API ====================

def run(natural_language: str, show_code: bool = False) -> None:
    """
    Execute natural language command and display output
    Perfect for interactive use in any environment

    Args:
        natural_language: Natural language command or multi-line program
        show_code: Whether to show the generated Python code
    """
    _dome_executor.execute(
        natural_language, return_result=False, show_code=show_code)


def execute(natural_language: str, show_code: bool = False) -> DOMEResult:
    """
    Execute natural language command and return result object
    Perfect for programmatic use and notebooks

    Args:
        natural_language: Natural language command or multi-line program
        show_code: Whether to show the generated Python code

    Returns:
        DOMEResult object with execution details
    """
    return _dome_executor.execute(natural_language, return_result=True, show_code=show_code)


def history(limit: int = 10) -> List[DOMEResult]:
    """Get execution history"""
    return _dome_executor.history(limit)


def clear_history():
    """Clear execution history"""
    _dome_executor.clear_history()


def clear_context():
    """Reset execution context"""
    _dome_executor.clear_context()


def start():
    """
    Start interactive REPL mode
    Works in terminal, graceful fallback in IDEs
    """
    if ENVIRONMENT == 'terminal':
        _start_interactive_repl()
    elif ENVIRONMENT in ['jupyter', 'ipython']:
        print("🏛️ DOME Interactive Mode")
        print("💡 In Jupyter/IPython, use:")
        print("   dome.run('your natural language command')")
        print("   result = dome.execute('your command')")
        print("📖 Examples:")
        print("   dome.run('make a list of the first 10 square numbers')")
        print("   dome.run('calculate factorial of 15')")
    else:
        print("🏛️ DOME - Natural Language Programming")
        print("💡 In this environment, use:")
        print("   dome.run('your natural language command')")
        print("   result = dome.execute('your command')")
        print("📖 Examples:")
        print("   dome.run('hello world')")
        print("   dome.run('create fibonacci sequence up to 100')")


def _start_interactive_repl():
    """Start terminal REPL (internal function)"""
    print("🏛️ DOME - Interactive Natural Language Programming")
    print("=" * 60)
    print("🚀 Type natural language commands directly!")
    print("🔒 Security sandbox enabled")
    print("💡 Examples:")
    print("   calculate factorial of 15")
    print("   make a list of square numbers")
    print("   hello world")
    print("💡 Commands: 'help', 'history', 'clear', 'exit'")
    print("=" * 60)

    while True:
        try:
            command = input(">>> ").strip()

            if not command:
                continue
            elif command.lower() in ['exit', 'quit']:
                print("👋 Goodbye!")
                break
            elif command.lower() == 'help':
                _show_help()
            elif command.lower() == 'history':
                _show_history()
            elif command.lower() == 'clear':
                _dome_executor.clear_context()
                print("🧹 Context cleared")
            else:
                print(f"🤖 Processing: {command}")
                run(command)

        except (KeyboardInterrupt, EOFError):
            print("\n👋 Goodbye!")
            break
        except Exception as e:
            print(f"🔴 Error: {e}")


def _show_help():
    """Show help information"""
    print("""
🏛️ DOME - Natural Language Programming

✨ EXAMPLES:
   calculate factorial of 15
   make a list of the first 10 square numbers
   create fibonacci sequence up to 100
   hello world
   current time

🛠️ COMMANDS:
   help     - Show this help
   history  - Show execution history
   clear    - Clear context/variables
   exit     - Exit DOME

🌐 UNIVERSAL USAGE:
   dome.run("command")       - Execute and show output
   dome.execute("command")   - Execute and return result
   dome.start()             - Interactive mode
""")


def _show_history():
    """Show execution history"""
    history_list = _dome_executor.history()
    if not history_list:
        print("📋 No execution history")
        return

    print("\n📋 Recent Execution History:")
    for i, result in enumerate(history_list, 1):
        status = "✅" if result.success else "❌"
        print(f"{i}. {status} {result.command[:50]}...")
        if not result.success:
            print(f"   🔴 {result.error}")


# ==================== MODULE SETUP ====================

# Environment-specific setup
if ENVIRONMENT == 'jupyter':
    print("🏛️ DOME - Natural Language Programming (Jupyter Mode)")
    print("🚀 Usage: dome.run('your command') or result = dome.execute('your command')")
elif ENVIRONMENT == 'vscode':
    print("🏛️ DOME - Natural Language Programming (VSCode Mode)")
    print("🚀 Usage: dome.run('your command') or dome.start() for interactive")
elif ENVIRONMENT == 'terminal':
    print("🏛️ DOME - Natural Language Programming (Terminal Mode)")
    print("🚀 Usage: dome.start() for interactive or dome.run('your command')")
else:
    print("🏛️ DOME - Natural Language Programming")
    print("🚀 Usage: dome.run('your command') or result = dome.execute('your command')")

# API status
if CLAUDE_API_KEY == "your-claude-api-key-here":
    print("⚠️ Claude API key not configured - using fallback patterns")
    print("🔑 Set API key for full functionality")
else:
    print("✅ Claude AI ready")

# Export public functions
__all__ = [
    'run', 'execute', 'start', 'history', 'clear_history', 'clear_context',
    'DOMEResult', '__version__', '__author__', '__description__'
]
