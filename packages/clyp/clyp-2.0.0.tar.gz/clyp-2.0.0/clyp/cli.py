import sys
import os
import json
import traceback
import shutil
import re
from typing import Optional, Tuple, Dict, List, Any
from clyp import __version__
from clyp.transpiler import parse_clyp, transpile_to_clyp
from clyp.formatter import format_clyp_code
from .importer import find_clyp_imports

# Error code mapping (see errors.md)
ERROR_CODE_MAP = {
    # Syntax errors
    "SyntaxError": "A100",
    "IndentationError": "A100",
    "TabError": "A100",
    # Lexical errors (no direct Python mapping)
    # Type errors
    "TypeError": "C100",
    "OverflowError": "C100",
    # Runtime errors
    "RuntimeError": "D100",
    "RecursionError": "D100",
    "ZeroDivisionError": "D101",
    "ArithmeticError": "D100",
    "FloatingPointError": "D100",
    "SystemExit": "D100",
    "KeyboardInterrupt": "D100",
    "StopIteration": "D100",
    "StopAsyncIteration": "D100",
    # Import/module errors
    "ImportError": "E100",
    "ModuleNotFoundError": "E100",
    # File system errors
    "FileNotFoundError": "F100",
    "OSError": "F101",
    "IsADirectoryError": "F101",
    "NotADirectoryError": "F101",
    "PermissionError": "P100",
    # IO errors
    "IOError": "G100",
    "BlockingIOError": "G100",
    "ChildProcessError": "G100",
    "ConnectionError": "G100",
    "ConnectionAbortedError": "G100",
    "ConnectionRefusedError": "G100",
    "ConnectionResetError": "G100",
    "BrokenPipeError": "G100",
    "TimeoutError": "Q100",
    # Semantic errors
    "AssertionError": "H100",
    # Deprecation warnings
    "DeprecationWarning": "I100",
    "PendingDeprecationWarning": "I100",
    "FutureWarning": "I100",
    # Compiler internal errors
    "NotImplementedError": "J100",
    # Argument errors
    # Scope errors
    "AttributeError": "M100",
    "KeyError": "M101",
    "UnboundLocalError": "M100",
    # Name errors
    "NameError": "N100",
    # Optimization warnings (no direct Python mapping)
    # Permission errors (see above)
    # Concurrency errors
    "BrokenProcessPool": "Q100",
    # Memory errors
    "MemoryError": "R100",
    # Security errors
    # Transform errors
    # Versioning errors
    # Validation errors
    "ValueError": "V100",
    "UnicodeError": "V100",
    "UnicodeDecodeError": "V100",
    "UnicodeEncodeError": "V100",
    "UnicodeTranslateError": "V100",
    # Warning-level notices
    "Warning": "W501",
    "UserWarning": "W501",
    "ResourceWarning": "W501",
    "SyntaxWarning": "W501",
    "ImportWarning": "W501",
    "BytesWarning": "W501",
    "EncodingWarning": "W501",
    # Experimental feature fails
    # Language feature errors
    # Unknown/unclassified
    # Custom Clyp errors
    "ClypSyntaxError": "A100",
    "ClypTypeError": "C100",
    "ClypImportError": "E100",
    "ClypRuntimeError": "D100",
    "ClypValidationError": "V100",
    "ClypVersionError": "U500",
    "ClypDeprecationWarning": "W501",
}

def get_error_code(exc: Exception) -> str:
    """
    Map an exception to an error code string based on ERROR_CODE_MAP.
    Returns 'Z999' for unknown exceptions.
    """
    name = exc.__class__.__name__
    return ERROR_CODE_MAP.get(name, 'Z999')

class Log:
    """A simple logger with color support."""
    HEADER = "\033[95m"
    BLUE = "\033[94m"
    CYAN = "\033[96m"
    GREEN = "\033[92m"
    WARNING = "\033[93m"
    FAIL = "\033[91m"
    ENDC = "\033[0m"
    BOLD = "\033[1m"
    UNDERLINE = "\033[4m"
    _supports_color = hasattr(sys.stdout, "isatty") and sys.stdout.isatty()
    @classmethod
    def _print(cls, color, *args, **kwargs):
        msg = "".join(map(str, args))
        if cls._supports_color:
            print(f"{color}{msg}{cls.ENDC}", **kwargs)
        else:
            print(msg, **kwargs)
    @classmethod
    def info(cls, *args, **kwargs):
        cls._print(cls.CYAN, *args, **kwargs)
    @classmethod
    def success(cls, *args, **kwargs):
        cls._print(cls.GREEN, *args, **kwargs)
    @classmethod
    def warn(cls, *args, **kwargs):
        cls._print(cls.WARNING, *args, **kwargs)
    @classmethod
    def error(cls, *args, **kwargs):
        cls._print(cls.FAIL, *args, **kwargs)
    @classmethod
    def bold(cls, *args, **kwargs):
        msg = "".join(map(str, args))
        if cls._supports_color:
            print(f"{cls.BOLD}{msg}{cls.ENDC}", **kwargs)
        else:
            print(msg, **kwargs)
    @classmethod
    def traceback_header(cls, *args, **kwargs):
        cls._print(cls.BOLD, *args, **kwargs)
    @classmethod
    def traceback_location(cls, *args, **kwargs):
        cls._print(cls.BLUE, *args, **kwargs)
    @classmethod
    def traceback_code(cls, *args, **kwargs):
        cls._print(cls.CYAN, *args, **kwargs)

# Helper functions (move to top-level)
def get_clyp_line_for_py(
    py_line: int,
    line_map: Optional[Dict[int, int]],
    clyp_lines: Optional[List[str]],
) -> Tuple[Any, str]:
    # If we don't have mapping or source lines, return unknown
    if not line_map or not clyp_lines:
        return "?", ""
    # Try direct mapping first (exact python line -> clyp line)
    if py_line in line_map:
        clyp_line = line_map[py_line]
    else:
        # fall back to the nearest preceding mapping key (largest key <= py_line)
        keys = sorted(line_map.keys())
        prev_key = None
        for k in keys:
            if k <= py_line:
                prev_key = k
            else:
                break
        if prev_key is not None:
            clyp_line = line_map[prev_key]
        else:
            # no preceding mapping; use first mapped location as best-effort
            try:
                clyp_line = line_map[keys[0]]
            except Exception:
                return "?", ""
    # Normalize and bound-check the resulting clyp line
    try:
        if isinstance(clyp_line, int) and 1 <= clyp_line <= len(clyp_lines):
            return clyp_line, clyp_lines[clyp_line - 1]
    except Exception:
        pass
    # fallback: show last available line if any
    if clyp_lines:
        return len(clyp_lines), clyp_lines[-1]
    return "?", ""

def extract_optimization_level(clyp_code: str) -> int:
    """
    Extracts the optimization level from a line like:
    define optimization_level <level>;
    Returns 0 if not found or invalid.
    """
    match = re.search(r"define\s+optimization_level\s+(\d+)\s*;", clyp_code)
    if match:
        try:
            level = int(match.group(1))
            if level in (0, 1, 2):
                return level
        except Exception:
            pass
    return 0

# Add global verbose flag
VERBOSE = False

def python_to_clyp_transpile(py_code):
    # Log when transpiler is invoked if verbose
    if VERBOSE:
        Log.info("Transpiler: starting transpile_to_clyp()")
    result = transpile_to_clyp(py_code)
    if VERBOSE:
        Log.info("Transpiler: finished transpile_to_clyp()")
    return result

def remove_dirs(root, dirs):
    for d in dirs:
        path = os.path.join(root, d)
        if os.path.exists(path):
            shutil.rmtree(path, ignore_errors=True)
            Log.success(f"Removed {path}")

def print_deps(file_path, seen=None, level=0):
    if seen is None:
        seen = set()
    abs_path = os.path.abspath(file_path)
    if abs_path in seen:
        print("  " * level + f"- {os.path.basename(file_path)} (already shown)")
        return
    seen.add(abs_path)
    print("  " * level + f"- {os.path.basename(file_path)}")
    try:
        imports = find_clyp_imports(abs_path)
        if VERBOSE:
            Log.info(f"print_deps: found imports for {file_path}: {imports}")
        for imp in imports:
            # Verbose: detect std / stdlib style imports
            if VERBOSE and (imp.startswith("std") or imp.startswith("stdlib")):
                Log.info(f"Detected standard library import: {imp}")
            resolved = resolve_import_path(imp, abs_path)
            if VERBOSE:
                Log.info(f"Resolved import '{imp}' -> {resolved}")
            if resolved:
                print_deps(resolved, seen, level + 1)
    except Exception as e:
        print("  " * (level + 1) + f"[error: {e}]")



def resolve_import_path(import_name, current_file_path):
    """Resolves the absolute path of a Clyp import."""
    module_path = import_name.replace(".", os.path.sep) + ".clyp"
    search_paths = [os.path.dirname(current_file_path)] + sys.path
    if VERBOSE:
        Log.info(f"resolve_import_path: resolving {import_name} from {current_file_path}")
        Log.info(f"resolve_import_path: search_paths={search_paths}")
    for path in search_paths:
        potential_path = os.path.join(path, module_path)
        if os.path.exists(potential_path):
            if VERBOSE:
                Log.info(f"resolve_import_path: found {potential_path}")
            return os.path.abspath(potential_path)
    if VERBOSE:
        Log.info(f"resolve_import_path: could not resolve {import_name}")
    return None

# Main entry point
def main():
    import argparse
    # print(sys.argv)  # (optional: remove debug print)
    parser = argparse.ArgumentParser(description="Clyp CLI tool (interpreted mode only).")
    # Add global verbose flag
    parser.add_argument("-v", "--verbose", action="store_true", help="Enable verbose output.")
    parser.add_argument("--version", action="store_true", help="Display the version of Clyp.")
    subparsers = parser.add_subparsers(dest="command", help=argparse.SUPPRESS)
    # Only keep run, format, py2clyp, check, deps, init commands
    run_parser = subparsers.add_parser("run", help="Run a Clyp file (interpreted mode).")
    run_parser.add_argument("file", type=str, help="Path to the Clyp file to execute.")
    run_parser.add_argument("args", nargs=argparse.REMAINDER, help="Arguments to pass to the Clyp script.")
    format_parser = subparsers.add_parser("format", help="Format a Clyp file (overwrites by default).")
    format_parser.add_argument("file", type=str, help="Path to the Clyp file to format.")
    format_parser.add_argument("--print", action="store_true", help="Print formatted code instead of overwriting.")
    format_parser.add_argument("--no-write", action="store_true", help="Do not overwrite the file (alias for --print).")
    py2clyp_parser = subparsers.add_parser("py2clyp", help="Transpile Python code to Clyp with advanced options.")
    py2clyp_parser.add_argument("file", type=str, help="Path to the Python file to transpile.")
    py2clyp_parser.add_argument("-o", "--output", type=str, default=None, help="Output file for Clyp code.")
    py2clyp_parser.add_argument("--print", action="store_true", help="Print transpiled Clyp code to stdout.")
    py2clyp_parser.add_argument("--format", action="store_true", help="Format the output Clyp code.")
    py2clyp_parser.add_argument("--diff", action="store_true", help="Show a diff between the Python and Clyp code.")
    py2clyp_parser.add_argument("--overwrite", action="store_true", help="Overwrite the input Python file with Clyp code.")
    py2clyp_parser.add_argument("--check", action="store_true", help="Check if the file can be transpiled (dry run, no output).")
    py2clyp_parser.add_argument("--quiet", action="store_true", help="Suppress non-error output.")
    py2clyp_parser.add_argument("--no-format", action="store_true", help="Do not format the output.")
    py2clyp_parser.add_argument("--stats", action="store_true", help="Show statistics about the transpilation (lines, tokens, etc.).")
    py2clyp_parser.add_argument("-r", "--recursive", action="store_true", help="Recursively transpile a directory of Python files.")
    check_parser = subparsers.add_parser("check", help="Check a Clyp file or project for syntax errors.")
    check_parser.add_argument("file", type=str, nargs="?", default=None, help="Clyp file or project to check. If omitted, checks the project in the current directory.")
    deps_parser = subparsers.add_parser("deps", help="Show the dependency tree for a Clyp file or project.")
    deps_parser.add_argument("file", type=str, nargs="?", default=None, help="Clyp file or project to analyze.")
    init_parser = subparsers.add_parser("init", help="Initialize a new Clyp project.")
    init_parser.add_argument("name", type=str, help="The name of the project.")
    args = parser.parse_args()
    # ... existing code ...

    # Activate global verbose flag for use in helper functions
    global VERBOSE
    VERBOSE = bool(getattr(args, "verbose", False))
    if VERBOSE:
        Log.info(f"Verbose mode enabled. Command: {args.command} args={sys.argv[1:]}")

    if args.version:
        print(f"{__version__}")
        sys.exit(0)

    if args.command == "run":
        file_path = os.path.abspath(args.file)
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                clyp_code = f.read()
        except FileNotFoundError as e:
            code = get_error_code(e)
            Log.error(f"[{code}] File {args.file} not found.", file=sys.stderr)
            sys.exit(1)
        except (IOError, UnicodeDecodeError) as e:
            code = get_error_code(e)
            Log.error(f"[{code}] Error reading file {args.file}: {e}", file=sys.stderr)
            sys.exit(1)
        except Exception as e:
            code = get_error_code(e)
            Log.error(f"[{code}] Unexpected error reading file {args.file}: {e}", file=sys.stderr)
            sys.exit(1)
        # --- Run precheck before executing ---
        from clyp.precheck import precheck_clyp_code
        if VERBOSE:
            Log.info("Precheck: starting precheck_clyp_code()")
        precheck_errors = precheck_clyp_code(clyp_code)
        if VERBOSE:
            Log.info(f"Precheck: finished precheck_clyp_code(); errors={precheck_errors}")
        if precheck_errors:
            for err in precheck_errors:
                print(err, file=sys.stderr)
            sys.exit(1)
        try:
            if VERBOSE:
                Log.info("Calling parse_clyp(..., return_line_map=True)")
            result = parse_clyp(clyp_code, file_path, return_line_map=True)
            if VERBOSE:
                Log.info("parse_clyp returned successfully")
        except Exception as e:
            code = get_error_code(e)
            Log.error(f"[{code}] {type(e).__name__}: {e}", file=sys.stderr)
            sys.exit(1)
        if isinstance(result, tuple):
            python_code, line_map, clyp_lines = result
        else:
            python_code = result
            line_map = None
            clyp_lines = None
        # Verbose: show input and output code
        if VERBOSE:
            Log.info("=== INPUT CLYP CODE ===")
            print(clyp_code)
            Log.info("=== GENERATED PYTHON CODE ===")
            print(python_code)
        sys.argv = [file_path] + (args.args if hasattr(args, "args") else [])
        try:
            exec(python_code, {"__name__": "__main__", "__file__": file_path})
        except SyntaxError as e:
            code = get_error_code(e)
            py_line = e.lineno or 1
            Log.traceback_header("\nTraceback (most recent call last):", file=sys.stderr)
            clyp_line, code_line = get_clyp_line_for_py(py_line, line_map, clyp_lines)
            Log.traceback_location(f"  File '{args.file}', line {clyp_line}", file=sys.stderr)
            # If we can show Clyp context, show surrounding lines with pointer
            if clyp_lines and clyp_line != "?":
                start = max(0, clyp_line - 3)
                end = min(len(clyp_lines), clyp_line + 2)
                for i in range(start, end):
                    pointer = "->" if (i + 1) == clyp_line else "  "
                    Log.traceback_code(f"{pointer} {i + 1}: {clyp_lines[i]}", file=sys.stderr)
            else:
                Log.traceback_code(f"    {code_line}", file=sys.stderr)
            Log.warn(f"(Python error at transpiled line {py_line})", file=sys.stderr)
            Log.error(f"[{code}] {type(e).__name__}: {e}", file=sys.stderr)
            sys.exit(1)
        except Exception as e:
            err_code = get_error_code(e)
            tb = traceback.extract_tb(sys.exc_info()[2])
            Log.traceback_header("\nTraceback (most recent call last):", file=sys.stderr)
            clyp_frame_indices = [idx for idx, frame in enumerate(tb) if frame.filename == "<string>"]
            last_clyp_frame_idx = clyp_frame_indices[-1] if clyp_frame_indices else None
            for idx, frame in enumerate(tb):
                if frame.filename == "<string>":
                    py_line = frame.lineno
                    clyp_line, code_line = get_clyp_line_for_py(py_line, line_map, clyp_lines)
                    marker = ">>>" if idx == last_clyp_frame_idx else "   "
                    Log.traceback_location(f"{marker} File '{args.file}', line {clyp_line}", file=sys.stderr)
                    if clyp_lines and clyp_line != "?":
                        start = max(0, clyp_line - 3)
                        end = min(len(clyp_lines), clyp_line + 2)
                        for i in range(start, end):
                            pointer = "->" if (i + 1) == clyp_line else "  "
                            Log.traceback_code(f"{pointer} {i + 1}: {clyp_lines[i]}", file=sys.stderr)
                    else:
                        Log.traceback_code(f"    {code_line}", file=sys.stderr)
                else:
                    Log.traceback_location(f"    File '{frame.filename}', line {frame.lineno}", file=sys.stderr)
                    Log.traceback_code(f"      {frame.line}", file=sys.stderr)
            Log.error(f"[{err_code}] {type(e).__name__}: {e}", file=sys.stderr)
            sys.exit(1)
    elif args.command == "init":
        project_name = args.name
        project_root = os.path.join(os.getcwd(), project_name)
        if os.path.exists(project_root):
            Log.error(f"Directory '{project_name}' already exists.")
            sys.exit(1)
        os.makedirs(project_root)
        config = {
            "name": project_name,
            "version": "0.1.0",
            "entry": "src/main.clyp"
        }
        config_path = os.path.join(project_root, "clyp.json")
        with open(config_path, "w") as f:
            json.dump(config, f, indent=4)
        src_dir = os.path.join(project_root, "src")
        os.makedirs(src_dir)
        main_clyp_path = os.path.join(src_dir, "main.clyp")
        with open(main_clyp_path, "w") as f:
            f.write('print("Hello from Clyp!")\n')
        gitignore_path = os.path.join(project_root, ".gitignore")
        with open(gitignore_path, "w") as f:
            f.write("dist/\n")
            f.write(".clyp-cache/\n")
        Log.success(f"Initialized Clyp project '{project_name}'")
        Log.info(f"Created project structure in: {project_root}")
        Log.info("You can now `cd` into the directory and run `clyp <file.clyp>`. Interpreted mode is default.")
    elif args.command == "format":
        file_path = os.path.abspath(args.file)
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                clyp_code = f.read()
        except Exception as e:
            code = get_error_code(e)
            Log.error(f"[{code}] Error reading file {args.file}: {e}", file=sys.stderr)
            sys.exit(1)
        try:
            if VERBOSE:
                Log.info("Calling format_clyp_code()")
                Log.info("=== ORIGINAL CLYP ===")
                print(clyp_code)
            formatted = format_clyp_code(clyp_code)
            if VERBOSE:
                Log.info("=== FORMATTED CLYP ===")
                print(formatted)
        except Exception as e:
            code = get_error_code(e)
            Log.error(f"[{code}] Formatting failed: {e}", file=sys.stderr)
            sys.exit(1)
        if args.print or args.no_write:
            print(formatted)
        else:
            try:
                with open(file_path, "w", encoding="utf-8") as f:
                    f.write(formatted)
                Log.success(f"Formatted {args.file} in place.")
            except Exception as e:
                code = get_error_code(e)
                Log.error(f"[{code}] Error writing file {args.file}: {e}", file=sys.stderr)
                sys.exit(1)
    elif args.command == "py2clyp":
        from clyp.transpiler import transpile_to_clyp
        import difflib

        file_path = os.path.abspath(args.file)

        # If the target is a directory, handle it explicitly.
        if os.path.isdir(file_path):
            if not getattr(args, "recursive", False):
                # Provide a clear error rather than attempting to open the directory.
                Log.error(
                    f"[P100] {args.file} is a directory. "
                    "Use --recursive (-r) to transpile a directory of Python files "
                    "or provide a single Python file."
                )
                sys.exit(1)
            # Directory + recursive mode: walk and transpile .py files.
            if args.output:
                Log.error("[Z999] --output is not supported when transpiling a directory.")
                sys.exit(1)
            for dirpath, _, filenames in os.walk(file_path):
                for fname in filenames:
                    if not fname.endswith(".py"):
                        continue
                    src = os.path.join(dirpath, fname)
                    try:
                        with open(src, "r", encoding="utf-8") as f:
                            py_code = f.read()
                    except Exception as e:
                        code = get_error_code(e)
                        Log.error(f"[{code}] Error reading file {src}: {e}")
                        continue
                    try:
                        if VERBOSE:
                            Log.info(f"py2clyp (dir): transpiling {src}")
                        clyp_code = transpile_to_clyp(py_code)
                    except Exception as e:
                        code = get_error_code(e)
                        Log.error(f"[{code}] Transpilation failed for {src}: {e}")
                        continue
                    if args.format and not args.no_format:
                        try:
                            clyp_code = format_clyp_code(clyp_code)
                        except Exception as e:
                            code = get_error_code(e)
                            Log.warn(f"[{code}] Formatting failed for {src}: {e}")
                    out_path = os.path.splitext(src)[0] + ".clyp"
                    if args.print:
                        print(f"# Transpiled from {src}\n{clyp_code}")
                    else:
                        try:
                            with open(out_path, "w", encoding="utf-8") as f:
                                f.write(clyp_code)
                            if not args.quiet:
                                Log.success(f"Wrote transpiled Clyp code to {out_path}")
                        except Exception as e:
                            code = get_error_code(e)
                            Log.error(f"[{code}] Error writing to {out_path}: {e}")
            # Finished directory processing
            sys.exit(0)

        def python_to_clyp_transpile(py_code):
            if VERBOSE:
                Log.info("py2clyp: invoking transpile_to_clyp()")
            res = transpile_to_clyp(py_code)
            if VERBOSE:
                Log.info("py2clyp: transpile_to_clyp() finished")
            return res

        try:
            with open(file_path, "r", encoding="utf-8") as f:
                py_code = f.read()
        except Exception as e:
            code = get_error_code(e)
            Log.error(f"[{code}] Error reading file {args.file}: {e}", file=sys.stderr)
            sys.exit(1)
        if args.check:
            # Just check if transpilation is possible
            try:
                clyp_code = python_to_clyp_transpile(py_code)
                if not clyp_code or not isinstance(clyp_code, str):
                    Log.error(
                        "[Z999] Transpilation failed: No output generated.", file=sys.stderr
                    )
                    sys.exit(1)
                if not args.quiet:
                    Log.success(f"{args.file} can be transpiled to Clyp.")
                sys.exit(0)
            except Exception as e:
                code = get_error_code(e)
                Log.error(f"[{code}] Transpilation failed: {e}", file=sys.stderr)
                sys.exit(1)  # Ensure SystemExit is always raised on failure
            # Fallback: if we ever reach here, exit with error
            sys.exit(1)
        try:
            if VERBOSE:
                Log.info("py2clyp: starting transpilation")
                Log.info("=== INPUT PYTHON ===")
                print(py_code)
            clyp_code = python_to_clyp_transpile(py_code)
            if VERBOSE:
                Log.info("py2clyp: transpilation finished")
                Log.info("=== OUTPUT CLYP ===")
                print(clyp_code)
        except Exception as e:
            code = get_error_code(e)
            Log.error(f"[{code}] Transpilation failed: {e}", file=sys.stderr)
            sys.exit(1)
        if args.format and not args.no_format:
            try:
                if VERBOSE:
                    Log.info("py2clyp: formatting transpiled code")
                clyp_code = format_clyp_code(clyp_code)
                if VERBOSE:
                    Log.info("py2clyp: formatting complete")
            except Exception as e:
                code = get_error_code(e)
                Log.warn(f"[{code}] Formatting failed: {e}", file=sys.stderr)
        if args.stats:
            py_lines = len(py_code.splitlines())
            clyp_lines = len(clyp_code.splitlines())
            Log.info(f"Python lines: {py_lines}, Clyp lines: {clyp_lines}")
        if args.diff:
            diff = difflib.unified_diff(
                py_code.splitlines(),
                clyp_code.splitlines(),
                fromfile=args.file,
                tofile=args.output or "clyp_output.clyp",
                lineterm="",  # No extra newlines
            )
            print("\n".join(diff))
        if args.print:
            print(clyp_code)
        if args.output:
            try:
                with open(args.output, "w", encoding="utf-8") as f:
                    f.write(clyp_code)
                if not args.quiet:
                    Log.success(f"Wrote transpiled Clyp code to {args.output}")
            except Exception as e:
                code = get_error_code(e)
                Log.error(f"[{code}] Error writing to {args.output}: {e}", file=sys.stderr)
                sys.exit(1)
        if args.overwrite:
            try:
                with open(file_path, "w", encoding="utf-8") as f:
                    f.write(clyp_code)
                if not args.quiet:
                    Log.success(f"Overwrote {args.file} with transpiled Clyp code.")
            except Exception as e:
                code = get_error_code(e)
                Log.error(f"[{code}] Error overwriting {args.file}: {e}", file=sys.stderr)
                sys.exit(1)
        if not (args.print or args.output or args.overwrite or args.diff):
            # Default: print to stdout
            print(clyp_code)
    elif args.command == "clean":

        def remove_dirs(root, dirs):
            for d in dirs:
                path = os.path.join(root, d)
                if os.path.exists(path):
                    shutil.rmtree(path, ignore_errors=True)
                    Log.success(f"Removed {path}")

        if args.all:
            for dirpath, dirnames, _ in os.walk(os.getcwd()):
                remove_dirs(dirpath, ["build", "dist", ".clyp-cache"])
        else:
            remove_dirs(os.getcwd(), ["build", "dist", ".clyp-cache"])
    elif args.command == "check":

        def check_file(file_path):
            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    clyp_code = f.read()
                parse_clyp(clyp_code, file_path)
                Log.success(f"{file_path} OK")
            except Exception as e:
                code = get_error_code(e)
                Log.error(f"[{code}] {file_path}: {e}")
                return False
            return True

        if args.file:
            check_file(os.path.abspath(args.file))
        else:
            # Check all .clyp files in project
            ok = True
            for dirpath, _, filenames in os.walk(os.getcwd()):
                for f in filenames:
                    if f.endswith(".clyp"):
                        if not check_file(os.path.join(dirpath, f)):
                            ok = False
            if ok:
                Log.success("All files OK.")
            else:
                sys.exit(1)
    elif args.command == "deps":
        from .importer import find_clyp_imports

        def print_deps(file_path, seen=None, level=0):
            # keep behavior similar to top-level print_deps but with verbose logging
            if seen is None:
                seen = set()
            abs_path = os.path.abspath(file_path)
            if abs_path in seen:
                print("  " * level + f"- {os.path.basename(file_path)} (already shown)")
                return
            seen.add(abs_path)
            print("  " * level + f"- {os.path.basename(file_path)}")
            try:
                imports = find_clyp_imports(abs_path)
                if VERBOSE:
                    Log.info(f"deps.print_deps: imports for {file_path}: {imports}")
                for imp in imports:
                    if VERBOSE and (imp.startswith("std") or imp.startswith("stdlib")):
                        Log.info(f"Detected standard library import: {imp}")
                    resolved = resolve_import_path(imp, abs_path)
                    if VERBOSE:
                        Log.info(f"deps.print_deps: resolved {imp} -> {resolved}")
                    if resolved:
                        print_deps(resolved, seen, level + 1)
            except Exception as e:
                print("  " * (level + 1) + f"[error: {e}]")

        if args.file:
            print_deps(args.file)
        else:
            # Try to find entry from clyp.json
            config_path = os.path.join(os.getcwd(), "clyp.json")
            if os.path.exists(config_path):
                with open(config_path, "r") as f:
                    config = json.load(f)
                entry = config.get("entry")
                if entry:
                    print_deps(entry)
                else:
                    Log.error("No entry found in clyp.json.")
            else:
                Log.error("No file specified and no clyp.json found.")
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
