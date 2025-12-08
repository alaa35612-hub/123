from __future__ import annotations
import re
from pathlib import Path

SOURCE_FILE = Path('111111.txt')
TARGET_FILE = Path('indicator.py')


def convert_ternary(expr: str) -> str:
    pattern = re.compile(r"([^?]+?)\?([^:]+?):([^?:]+)")
    previous = None
    while previous != expr:
        previous = expr
        expr = pattern.sub(lambda m: f"({m.group(2).strip()} if {m.group(1).strip()} else {m.group(3).strip()})", expr)
    return expr


def replace_get_and_size(line: str) -> str:
    line = re.sub(r"([A-Za-z0-9_]+)\.size\(\)", r"len(\1)", line)
    line = re.sub(r"([A-Za-z0-9_]+)\.get\((.*)\)", r"\1[\2]", line)
    line = re.sub(r"\[([^\]]+?)\)\]", r"[\1]", line)
    line = re.sub(r"\[([^\]]+?)\)\)", r"[\1]", line)
    line = line.replace(')]', ']')
    line = line.replace(']]', ']')
    open_brackets = line.count('[')
    close_brackets = line.count(']')
    while close_brackets > open_brackets:
        idx = line.rfind(']')
        line = line[:idx] + line[idx + 1:]
        close_brackets -= 1
    return line


def convert_line(line: str) -> str:
    original = line.rstrip('\n')
    stripped = original.lstrip()
    indent = ' ' * (len(original) - len(stripped))

    if stripped.startswith('//'):
        return indent + '#' + stripped[2:]

    stripped = stripped.rstrip(';')
    stripped = stripped.replace(':=', '=')

    if stripped.startswith('else if'):
        stripped = 'elif ' + stripped[len('else if '):]
    elif stripped.startswith('if '):
        stripped = 'if ' + stripped[len('if '):]

    loop_match = re.match(r"for\s+(\w+)\s*=\s*([^ ]+)\s+to\s+(.+)", stripped)
    if loop_match:
        var, start, end = loop_match.groups()
        stripped = f"for {var} in range({start}, ({end}) + 1)"

    stripped = re.sub(r"\bvar\s+", "", stripped)

    if '?' in stripped and ':' in stripped:
        stripped = convert_ternary(stripped)

    stripped = replace_get_and_size(stripped)

    stripped = stripped.replace('array.push', 'array_push')
    stripped = stripped.replace('array.insert', 'array_insert')
    stripped = stripped.replace('array.remove', 'array_remove')

    stripped = re.sub(r"\binput\.([a-zA-Z_]+)", r"inputs.\1", stripped)
    stripped = stripped.replace('color.rgb', 'Color.rgb')

    if re.match(r"^(if |elif |else$|for )", stripped) and not stripped.rstrip().endswith(':'):
        stripped = stripped + ':'

    return indent + stripped


def main():
    src_lines = SOURCE_FILE.read_text(encoding='utf-8').splitlines()
    converted = [
        "# Auto-generated Python translation of Pine Script indicator",
        "from __future__ import annotations",
        "from dataclasses import dataclass",
        "from typing import List, Any",
        "\n",
        "class Inputs:",
        "    def int(self, default: int, *_args, **_kwargs) -> int: return default",
        "    def bool(self, default: bool, *_args, **_kwargs) -> bool: return default",
        "    def color(self, default: Any, *_args, **_kwargs) -> Any: return default",
        "    def string(self, default: str, *_args, **_kwargs) -> str: return default",
        "    def float(self, default: float, *_args, **_kwargs) -> float: return default",
        "\n",
        "class Color:",
        "    @staticmethod",
        "    def rgb(r, g, b, a=255): return (r, g, b, a)",
        "\n",
        "def array_push(arr: List[Any], value: Any) -> None: arr.append(value)",
        "def array_insert(arr: List[Any], idx: int, value: Any) -> None: arr.insert(idx, value)",
        "def array_remove(arr: List[Any], idx: int) -> Any: return arr.pop(idx)",
        "\n",
        "class TA:",
        "    @staticmethod",
        "    def highest(length: int): return 0",
        "    @staticmethod",
        "    def lowest(length: int): return 0",
        "\n",
        "inputs = Inputs()",
        "ta = TA()",
        "\n",
    ]

    converted.extend(convert_line(line) for line in src_lines)
    TARGET_FILE.write_text('\n'.join(converted), encoding='utf-8')


if __name__ == '__main__':
    main()
