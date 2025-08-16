# transpiler_fixed_full_v2.py
# Full Clyp -> Python transpiler (v2)
# Fixes: method-header conversion without 'function', let -> assignment, robust parsing, etc.

import os
import sys
import pathlib
import re
import inspect
from typing import List, Optional, Match, Tuple

# local imports (keep path hack if needed)
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import typeguard
import clyp.stdlib as stdlib
from clyp.ErrorHandling import ClypSyntaxError


def _replace_keywords_outside_strings(line: str) -> str:
    """
    Replaces specific Clyp keywords with Python equivalents outside of string literals.
    Replaces 'unless' -> 'if not', 'is not' -> '!=', 'is' -> '=='.
    """
    # Split on simple single/double quoted strings (won't capture triple-quote groups inside)
    parts = re.split(r'(".*?"|\'.*?\')', line)
    for i in range(0, len(parts), 2):
        part = parts[i]
        part = re.sub(r"\bunless\b", "if not", part)
        part = re.sub(r"\bis not\b", "!=", part)
        part = re.sub(r"\bis\b", "==", part)
        parts[i] = part
    return "".join(parts)


def _resolve_clyp_module_path(
    module_name: str, base_dir: pathlib.Path, script_path: Optional[str] = None
) -> Optional[pathlib.Path]:
    """
    Resolves a dotted Clyp module name to a `.clyp` file or package `__init__.clyp` within base_dir
    and optional clypPackages locations.
    """
    search_dirs = [base_dir]
    if script_path:
        script_dir = pathlib.Path(script_path).parent
        clyp_packages_dir = script_dir / "clypPackages"
        if clyp_packages_dir.exists() and clyp_packages_dir.is_dir():
            search_dirs.insert(0, clyp_packages_dir)
    try:
        import clyp

        wheel_dir = pathlib.Path(clyp.__file__).parent.parent
        wheel_clyp_packages = wheel_dir / "clypPackages"
        if wheel_clyp_packages.exists() and wheel_clyp_packages.is_dir():
            search_dirs.append(wheel_clyp_packages)
    except Exception:
        pass

    for search_dir in search_dirs:
        candidate = search_dir / (module_name.replace(".", os.sep) + ".clyp")
        if candidate.exists() and candidate.is_file():
            return candidate
        pkg_dir = search_dir / module_name.replace(".", os.sep)
        init_file = pkg_dir / "__init__.clyp"
        if init_file.exists():
            # verify package chain
            parts = module_name.split(".")
            check_dir = search_dir
            for part in parts:
                check_dir = check_dir / part
                if not (check_dir / "__init__.clyp").exists():
                    raise ClypSyntaxError(f"[E100] Parent directory missing __init__.clyp for package '{module_name}'", -1, -1)
            return init_file
    return None


@typeguard.typechecked
def transpile_to_clyp(python_code: str) -> str:
    """
    Transpile Python -> Clyp (reverse transpilation). Uses AST to generate simple Clyp.
    """
    import ast

    class ClypTranspiler(ast.NodeVisitor):
        def __init__(self):
            self.lines: List[str] = []
            self.indent = 0
            self.in_class = False

        def emit(self, line: str = ""):
            self.lines.append("    " * self.indent + line)

        def visit_Module(self, node):
            for stmt in node.body:
                self.visit(stmt)

        def visit_FunctionDef(self, node):
            args: List[str] = []
            for arg in node.args.args:
                if arg.arg == "self":
                    continue
                arg_type = None
                if arg.annotation:
                    arg_type = ast.unparse(arg.annotation)
                if arg_type:
                    args.append(f"{arg_type} {arg.arg}")
                else:
                    args.append(arg.arg)
            returns = ast.unparse(node.returns) if node.returns else "any"
            self.emit(f"function {node.name}({', '.join(args)}) returns {returns} {{")
            self.indent += 1
            for stmt in node.body:
                self.visit(stmt)
            self.indent -= 1
            self.emit("}")

        def visit_Assign(self, node):
            if len(node.targets) == 1:
                target = node.targets[0]
                if isinstance(target, ast.Name):
                    self.emit(f"{target.id} = {ast.unparse(node.value)};")
                else:
                    self.emit(f"{ast.unparse(target)} = {ast.unparse(node.value)};")
            else:
                self.emit(f"{', '.join([ast.unparse(t) for t in node.targets])} = {ast.unparse(node.value)};")

        def visit_AnnAssign(self, node):
            target = node.target
            if isinstance(target, ast.Name):
                var_type = ast.unparse(node.annotation)
                if node.value is not None:
                    value = ast.unparse(node.value)
                    self.emit(f"{var_type} {target.id} = {value};")
                else:
                    self.emit(f"{var_type} {target.id};")
            else:
                if node.value is not None:
                    self.emit(f"{ast.unparse(target)}: {ast.unparse(node.annotation)} = {ast.unparse(node.value)};")
                else:
                    self.emit(f"{ast.unparse(target)}: {ast.unparse(node.annotation)};")

        def visit_If(self, node):
            test = ast.unparse(node.test)
            self.emit(f"if {test} {{")
            self.indent += 1
            for stmt in node.body:
                self.visit(stmt)
            self.indent -= 1
            if node.orelse:
                self.emit("else {")
                self.indent += 1
                for stmt in node.orelse:
                    self.visit(stmt)
                self.indent -= 1
                self.emit("}")
            else:
                self.emit("}")

        def visit_For(self, node):
            target = ast.unparse(node.target)
            iter_ = ast.unparse(node.iter)
            self.emit(f"for {target} in {iter_} {{")
            self.indent += 1
            for stmt in node.body:
                self.visit(stmt)
            self.indent -= 1
            self.emit("}")

        def visit_While(self, node):
            test = ast.unparse(node.test)
            self.emit(f"while {test} {{")
            self.indent += 1
            for stmt in node.body:
                self.visit(stmt)
            self.indent -= 1
            self.emit("}")

        def visit_Return(self, node):
            value = ast.unparse(node.value) if node.value else ""
            self.emit(f"return {value};")

        def visit_Expr(self, node):
            self.emit(f"{ast.unparse(node.value)};")

        def visit_ClassDef(self, node):
            self.emit(f"class {node.name} {{")
            self.indent += 1
            self.in_class = True
            for stmt in node.body:
                self.visit(stmt)
            self.in_class = False
            self.indent -= 1
            self.emit("}")

        def visit_Pass(self, node):
            self.emit("pass;")

        def visit_Break(self, node):
            self.emit("break;")

        def visit_Continue(self, node):
            self.emit("continue;")

        def visit_Import(self, node):
            self.emit(f"// import {', '.join([ast.unparse(alias) for alias in node.names])}")

        def visit_ImportFrom(self, node):
            self.emit(f"// from {node.module} import {', '.join([ast.unparse(alias) for alias in node.names])}")

        def generic_visit(self, node):
            for child in ast.iter_child_nodes(node):
                self.visit(child)

    tree = ast.parse(python_code)
    transpiler = ClypTranspiler()
    transpiler.visit(tree)
    return "\n".join(transpiler.lines)


# ----------------------------
# Clyp -> Python parser
# ----------------------------
@typeguard.typechecked
def parse_clyp(
    clyp_code: str,
    file_path: Optional[str] = None,
    return_line_map: bool = False,
    target_lang: str = "python",
):
    """
    Transpiles Clyp source code into Python code.
    """
    if target_lang == "clyp":
        return transpile_to_clyp(clyp_code)

    python_keywords = {
        "False", "None", "True", "and", "as", "assert", "async", "await", "break",
        "class", "continue", "def", "del", "elif", "else", "except", "finally", "for",
        "from", "global", "if", "import", "in", "is", "lambda", "nonlocal", "not",
        "or", "pass", "raise", "return", "try", "while", "with", "yield",
        # Built-in types
        "int", "float", "str", "list", "dict", "set", "tuple", "bool", "object",
        "bytes", "complex", "type",
        # Other built-ins
        "print", "input", "len", "open", "range", "map", "filter", "zip", "min", "max",
        "sum", "any", "all", "abs",
    }

    indentation_level: int = 0
    indentation_sign: str = "    "

    stdlib_names = [
        name
        for name, member in inspect.getmembers(stdlib)
        if not name.startswith("_")
        and (inspect.isfunction(member) or inspect.isclass(member))
        and member.__module__ == stdlib.__name__
    ]
    stdlib_imports = ", ".join(stdlib_names) if stdlib_names else ""

    # Load clyp std module mapping (list of [full_name, alias]) if available.
    try:
        import clyp.std as _clyp_std

        CLYP_STD_LIST = getattr(_clyp_std, "std_list", []) or []
    except Exception:
        CLYP_STD_LIST = []

    python_code: str = (
        "from typeguard import install_import_hook; install_import_hook()\n"
        "import gc\n"
        "gc.enable()\n"
        "del gc\n"
        "import clyp\n"
        "from clyp.importer import clyp_import, clyp_include\n"
    )
    if stdlib_imports:
        python_code += f"from clyp.stdlib import {stdlib_imports}\n"
    else:
        python_code += "import clyp.stdlib as _clyp_stdlib\n"
    python_code += "del clyp\n"
    python_code += "true = True; false = False; null = None\n"

    # Char-level pass: normalize semicolons and braces while preserving strings and comments
    processed_chars: List[str] = []
    in_string = False
    string_char = ""
    escape_next = False
    i = 0
    src = clyp_code
    n = len(src)

    while i < n:
        ch = src[i]

        if escape_next:
            processed_chars.append(ch)
            escape_next = False
            i += 1
            continue

        if ch == "\\":
            processed_chars.append(ch)
            escape_next = True
            i += 1
            continue

        # detect triple quotes (''' or """)
        if not in_string and i + 2 < n and src[i : i + 3] in ("'''", '"""'):
            in_string = True
            string_char = src[i : i + 3]
            processed_chars.extend(list(string_char))
            i += 3
            continue

        # detect single or double quote start
        if not in_string and ch in ("'", '"'):
            in_string = True
            string_char = ch
            processed_chars.append(ch)
            i += 1
            continue

        # inside string handling
        if in_string:
            if string_char in ("'''", '"""'):
                if src[i : i + 3] == string_char:
                    processed_chars.extend(list(string_char))
                    i += 3
                    in_string = False
                    string_char = ""
                else:
                    processed_chars.append(ch)
                    i += 1
            else:
                if ch == string_char:
                    processed_chars.append(ch)
                    i += 1
                    in_string = False
                    string_char = ""
                else:
                    processed_chars.append(ch)
                    i += 1
            continue

        # comments
        if ch == "#":
            processed_chars.append(ch)
            i += 1
            while i < n and src[i] != "\n":
                processed_chars.append(src[i])
                i += 1
            continue

        # semicolon -> newline
        if ch == ";":
            processed_chars.append("\n")
            i += 1
            continue

        # braces -> keep as their own token with newline
        if ch == "{":
            processed_chars.append("{")
            processed_chars.append("\n")
            i += 1
            continue
        if ch == "}":
            processed_chars.append("}")
            processed_chars.append("\n")
            i += 1
            continue

        processed_chars.append(ch)
        i += 1

    infile_str_raw = "".join(processed_chars)

    # Handle clyp imports (line-oriented)
    processed_import_lines: List[str] = []
    for raw_line in infile_str_raw.split("\n"):
        line = raw_line.rstrip("\r")
        stripped_line = line.strip()
        if not stripped_line:
            processed_import_lines.append(line)
            continue

        # pyimport -> leave as a normal Python import
        if stripped_line.startswith("pyimport "):
            # e.g. "pyimport os" -> "import os"
            py_stmt = stripped_line.replace("pyimport ", "import ", 1)
            processed_import_lines.append(py_stmt)
            continue

        # import -> treat as a Clyp module import via clyp_import(...)
        if stripped_line.startswith("import "):
            parts = stripped_line.split()
            if len(parts) != 2:
                raise ClypSyntaxError(f"Invalid import statement: {stripped_line}")
            module_name = parts[1]

            # Special-case: map short std aliases to clyp.std.<module> if listed in clyp.std.std_list
            mapped: Optional[Tuple[str, str]] = None
            for entry in CLYP_STD_LIST:
                if not entry:
                    continue
                full_name = entry[0] if len(entry) > 0 else None
                alias = entry[1] if len(entry) > 1 else None
                # match by alias or full module name or trailing name
                if alias and module_name == alias:
                    mapped = (full_name, alias)
                    break
                if full_name and module_name == full_name:
                    mapped = (full_name, alias or full_name.split(".")[-1])
                    break

            if mapped:
                full_name, alias = mapped
                # Emit a normal Python import for standard clyp std modules
                processed_import_lines.append(f"import {full_name} as {alias}")
                continue

            # Not a core std import — treat as Clyp module import via clyp_import(...)
            module_path = None
            if file_path:
                base_dir = pathlib.Path(file_path).parent
                module_path = _resolve_clyp_module_path(module_name, base_dir, file_path)
            if module_path is not None:
                processed_import_lines.append(f"{module_name} = clyp_import('{module_name}', {repr(file_path)})")
            else:
                raise ClypSyntaxError(
                    f"Cannot import Clyp module '{module_name}': not a Clyp package or single-file script."
                )
            continue

        # from <module> import ... -> treat as Clyp module member import
        if stripped_line.startswith("from "):
            match = re.match(r"from\s+([\w\.]+)\s+import\s+(.*)", stripped_line)
            if match:
                module_name, imports_str = match.groups()
                imported_names = [name.strip() for name in imports_str.split(",") if name.strip()]

                # If this is a std module, map to the clyp.std.<module> Python import
                mapped_full: Optional[str] = None
                for entry in CLYP_STD_LIST:
                    if not entry:
                        continue
                    full_name = entry[0] if len(entry) > 0 else None
                    alias = entry[1] if len(entry) > 1 else None
                    if alias and module_name == alias:
                        mapped_full = full_name
                        break
                    if full_name and module_name == full_name:
                        mapped_full = full_name
                        break
                    if full_name and module_name == full_name.split(".")[-1]:
                        mapped_full = full_name
                        break

                if mapped_full:
                    # Preserve the RHS of the import as written
                    processed_import_lines.append(f"from {mapped_full} import {imports_str}")
                    continue

                # Not a std module — fall back to clyp_import(...) behavior
                module_path = None
                if file_path:
                    base_dir = pathlib.Path(file_path).parent
                    module_path = _resolve_clyp_module_path(module_name, base_dir, file_path)
                if module_path is not None:
                    processed_import_lines.append(f"_temp_module = clyp_import('{module_name}', {repr(file_path)})")
                    for name in imported_names:
                        processed_import_lines.append(f"{name} = _temp_module.{name}")
                    processed_import_lines.append("del _temp_module")
                else:
                    raise ClypSyntaxError(
                        f"Cannot import from Clyp module '{module_name}': not a Clyp package or single-file script."
                    )
            else:
                raise ClypSyntaxError(f"Invalid from-import statement: {stripped_line}")
            continue

        # include stays the same
        if stripped_line.startswith("include "):
            match = re.match(r'include\s+"([^"]+\.clb)"', stripped_line)
            if match:
                clb_path = match.group(1)
                processed_import_lines.append(f'clyp_include(r"{clb_path}", r"{file_path}")')
            else:
                raise ClypSyntaxError(f"Invalid include statement: {stripped_line}")
            continue

        processed_import_lines.append(line)
    infile_str_raw = "\n".join(processed_import_lines)

    # Insert pass for empty blocks: { ... } => { pass }
    infile_str_raw = re.sub(r"{(\s|#[^\n]*)*}", "{\n    pass\n}", infile_str_raw)

    infile_str_indented: str = ""
    line_map = {}
    clyp_lines = clyp_code.splitlines()
    py_line_num = python_code.count("\n") + 1
    in_class_block = False
    class_indentation_level: Optional[int] = None

    def strip_trailing_semicolon_from_call(s: str) -> str:
        """
        Remove trailing semicolon from balanced call lines ending with ');'
        """
        t = s.rstrip()
        if not t.endswith(");"):
            return s
        balance = 0
        in_str_local = False
        str_char_local = ""
        esc_local = False
        for ch in t:
            if esc_local:
                esc_local = False
                continue
            if ch == "\\":
                esc_local = True
                continue
            if in_str_local:
                if ch == str_char_local:
                    in_str_local = False
                    str_char_local = ""
                continue
            if ch in ('"', "'"):
                in_str_local = True
                str_char_local = ch
                continue
            if ch == "(":
                balance += 1
            elif ch == ")":
                balance -= 1
        if balance == 0:
            return t[:-1]
        return s

    def find_unquoted_hash(s: str) -> int:
        in_str_local = False
        str_char_local = ""
        esc_local = False
        for i, ch in enumerate(s):
            if esc_local:
                esc_local = False
                continue
            if ch == "\\":
                esc_local = True
                continue
            if in_str_local:
                if ch == str_char_local:
                    in_str_local = False
                    str_char_local = ""
                continue
            if ch in ("'", '"'):
                # naive triple-quote detection handled in earlier pass, keep simple here
                in_str_local = True
                str_char_local = ch
                continue
            if ch == "#":
                return i
        return -1

    for idx, raw_line in enumerate(infile_str_raw.split("\n")):
        clyp_line_num = idx + 1
        line = raw_line.rstrip("\r")

        # skip defines
        if re.match(r"^\s*define\s+\w+(\s+\S+)?\s*;?\s*$", line):
            continue

        # split comment (avoid hashes in strings)
        hash_idx = find_unquoted_hash(line)
        if hash_idx != -1:
            code_part = line[:hash_idx]
            add_comment = line[hash_idx:]
        else:
            code_part = line
            add_comment = ""

        if not code_part.strip():
            infile_str_indented += indentation_level * indentation_sign + add_comment.lstrip() + "\n"
            continue

        # handle 'let ' declarations: let x = ... -> x = ...
        if code_part.lstrip().startswith("let "):
            code_part = code_part.lstrip()[4:].lstrip()

        stripped_line = code_part.strip()

        # handle closing braces at start of line or lone '}'
        if stripped_line == "}" or stripped_line.startswith("}"):
            indentation_level = max(0, indentation_level - 1)
            if in_class_block and (class_indentation_level is not None and indentation_level < class_indentation_level):
                in_class_block = False
                class_indentation_level = None
            code_part = code_part.lstrip("}").lstrip()
            stripped_line = code_part.strip()
            if not stripped_line:
                infile_str_indented += indentation_level * indentation_sign + add_comment.lstrip() + "\n"
                line_map[py_line_num] = clyp_line_num
                py_line_num += 1
                continue

        # class declaration
        if stripped_line.startswith("class "):
            class_match = re.match(r"class\s+([a-zA-Z_][\w]*)\s*\{?", stripped_line)
            if class_match:
                class_name = class_match.group(1)
                infile_str_indented += indentation_sign * indentation_level + f"class {class_name}:" + add_comment + "\n"
                in_class_block = True
                class_indentation_level = indentation_level + 1
                indentation_level += 1
                line_map[py_line_num] = clyp_line_num
                py_line_num += 1
                continue

        # class member declaration -> annotation (e.g., "int count = 0" -> "count: int = 0")
        class_field_match = re.match(r"^([a-zA-Z_][\w]*)\s+([a-zA-Z_][\w]*)(\s*=\s*.+)?;?$", stripped_line)
        if in_class_block and class_field_match:
            typ, name, default = class_field_match.groups()
            default = default.strip() if default else ""
            if default:
                default = default.lstrip("= ").strip()
                outfile_line = f"{name}: {typ} = {default}"
            else:
                outfile_line = f"{name}: {typ}"
            infile_str_indented += indentation_sign * indentation_level + outfile_line + add_comment + "\n"
            line_map[py_line_num] = clyp_line_num
            py_line_num += 1
            continue

        # METHOD HEADER WITHOUT 'function' KEYWORD
        # e.g. increment(self) returns null:
        method_def_match = re.match(
            r"^([a-zA-Z_][\w]*)\s*\(([^)]*)\)\s*returns\s+([a-zA-Z_][\w\.\[\]]*)\s*[:{]?",
            stripped_line,
        )
        if method_def_match:
            name, args_str, return_type = method_def_match.groups()
            args = [a.strip() for a in args_str.split(",") if a.strip()]
            new_args: List[str] = []
            # If inside class block, auto-add self if not provided
            if in_class_block:
                if not any(a.split()[0] == "self" for a in args):
                    new_args.append("self")
            for arg in args:
                if arg == "self" or arg.startswith("*"):
                    new_args.append(arg)
                    continue
                parts = arg.split()
                if len(parts) >= 2:
                    arg_type = parts[0]
                    arg_name = parts[1]
                    default_value = " ".join(parts[2:]) if len(parts) > 2 else ""
                    new_arg_str = f"{arg_name}: {arg_type}"
                    if default_value:
                        new_arg_str += f" = {default_value.lstrip('= ').strip()}"
                    new_args.append(new_arg_str)
                else:
                    # If user wrote "x" (no type), accept it as-is
                    if len(parts) == 1:
                        new_args.append(parts[0])
                    else:
                        raise ClypSyntaxError(
                            f"Argument '{arg}' in method definition is malformed. Found in line: {stripped_line}"
                        )
            new_args_str = ", ".join(new_args)
            # map Clyp 'null' -> Python 'None' in return type if present
            py_return_type = "None" if return_type == "null" else return_type
            infile_str_indented += indentation_sign * indentation_level + f"def {name}({new_args_str}) -> {py_return_type}:" + add_comment + "\n"
            indentation_level += 1
            line_map[py_line_num] = clyp_line_num
            py_line_num += 1
            continue

        # function definitions (explicit 'function' keyword)
        func_def_match = re.match(
            r"^function\s+([a-zA-Z_][\w]*)\s*\(([^)]*)\)\s*returns\s+([a-zA-Z_][\w\.\[\]]*)\s*\{?",
            stripped_line,
        )
        if func_def_match:
            func_name, args_str, return_type = func_def_match.groups()
            args = [arg.strip() for arg in args_str.split(",") if arg.strip()]
            new_args: List[str] = []
            # If inside a class, auto-add self if not present
            if in_class_block:
                if not any(a.split()[0] == "self" for a in args):
                    new_args.append("self")
            for arg in args:
                if arg == "self" or arg.startswith("*"):
                    new_args.append(arg)
                    continue
                parts = arg.split()
                if len(parts) >= 2:
                    arg_type = parts[0]
                    arg_name = parts[1]
                    default_value = " ".join(parts[2:]) if len(parts) > 2 else ""
                    new_arg_str = f"{arg_name}: {arg_type}"
                    if default_value:
                        new_arg_str += f" = {default_value.lstrip('= ').strip()}"
                    new_args.append(new_arg_str)
                else:
                    # allow untyped arg names
                    if len(parts) == 1:
                        new_args.append(parts[0])
                    else:
                        raise ClypSyntaxError(
                            f"Argument '{arg}' in function definition must be in 'type name' format. Found in line: {stripped_line}"
                        )
            new_args_str = ", ".join(new_args)
            py_return_type = "None" if return_type == "null" else return_type
            infile_str_indented += indentation_sign * indentation_level + f"def {func_name}({new_args_str}) -> {py_return_type}:" + add_comment + "\n"
            indentation_level += 1
            line_map[py_line_num] = clyp_line_num
            py_line_num += 1
            continue

        # repeat blocks heuristics
        if stripped_line.startswith("repeat "):
            match_repeat = re.match(r"repeat\s+(\d+)\s*\{?", stripped_line)
            if match_repeat:
                times = match_repeat.group(1)
                infile_str_indented += indentation_sign * indentation_level + f"for _ in range({times}):" + add_comment + "\n"
                indentation_level += 1
                line_map[py_line_num] = clyp_line_num
                py_line_num += 1
                continue
            else:
                transformed = re.sub(r"repeat\s+\[(.*)\]\s+times", r"for _ in range(\1):", stripped_line)
                infile_str_indented += indentation_sign * indentation_level + transformed + add_comment + "\n"
                line_map[py_line_num] = clyp_line_num
                py_line_num += 1
                continue

        # range x to y -> range(x, y + 1)
        code_part = re.sub(r"\brange\s+(\S+)\s+to\s+(\S+)", r"range(\1, \2 + 1)", code_part)

        # replace keywords outside strings
        code_part = _replace_keywords_outside_strings(code_part)

        # remove trailing semicolon from function calls where parentheses are balanced
        code_part = strip_trailing_semicolon_from_call(code_part)

        # left-trim and indent
        code_part = code_part.lstrip()
        indented_line = indentation_level * indentation_sign + code_part

        # handle block opener leftover '{'
        if indented_line.rstrip().endswith("{"):
            indented_line = indented_line.rsplit("{", 1)[0].rstrip() + ":"
            infile_str_indented += indented_line + add_comment + "\n"
            indentation_level += 1
            line_map[py_line_num] = clyp_line_num
            py_line_num += 1
            continue

        # else if -> elif
        indented_line = re.sub(r"^\s*else\s+if\b", lambda m: m.group(0).replace("else if", "elif"), indented_line, flags=re.IGNORECASE)

        # strip stray semicolons at end of line
        if indented_line.rstrip().endswith(";"):
            indented_line = indented_line.rstrip().rstrip(";")

        infile_str_indented += indented_line + add_comment + "\n"
        line_map[py_line_num] = clyp_line_num
        py_line_num += 1

    # final cleanups: remove leftover single-line closing braces
    infile_str_indented = re.sub(r'^[ \t]*\}\s*$\n?', '', infile_str_indented, flags=re.M)
    infile_str_indented = re.sub(r";\n", "\n", infile_str_indented)

    python_code += infile_str_indented

    if return_line_map:
        return python_code, line_map, clyp_lines
    return python_code
