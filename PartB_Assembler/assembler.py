#!/usr/bin/env python3
"""Two-pass assembler for the 16-bit Hack computer.

Student-specific feature for K=38 (38 % 3 == 2): warn when a label
is defined more than once. The first definition is retained.
"""
from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

PREDEFINED = {
    **{f"R{i}": i for i in range(16)},
    "SP": 0,
    "LCL": 1,
    "ARG": 2,
    "THIS": 3,
    "THAT": 4,
    "SCREEN": 16384,
    "KBD": 24576,
}

DEST = {
    "": "000", "M": "001", "D": "010", "MD": "011",
    "A": "100", "AM": "101", "AD": "110", "AMD": "111",
}

COMP = {
    "0": "0101010", "1": "0111111", "-1": "0111010",
    "D": "0001100", "A": "0110000", "M": "1110000",
    "!D": "0001101", "!A": "0110001", "!M": "1110001",
    "-D": "0001111", "-A": "0110011", "-M": "1110011",
    "D+1": "0011111", "A+1": "0110111", "M+1": "1110111",
    "D-1": "0001110", "A-1": "0110010", "M-1": "1110010",
    "D+A": "0000010", "D+M": "1000010",
    "D-A": "0010011", "D-M": "1010011",
    "A-D": "0000111", "M-D": "1000111",
    "D&A": "0000000", "D&M": "1000000",
    "D|A": "0010101", "D|M": "1010101",
}

JUMP = {
    "": "000", "JGT": "001", "JEQ": "010", "JGE": "011",
    "JLT": "100", "JNE": "101", "JLE": "110", "JMP": "111",
}

SYMBOL_RE = re.compile(r"^[A-Za-z_.$:][A-Za-z0-9_.$:]*$")


class AssemblyError(Exception):
    """Raised when a source line cannot be assembled."""


def clean_source(path: Path) -> list[tuple[int, str]]:
    """Return (original_line_number, cleaned_instruction) pairs."""
    records: list[tuple[int, str]] = []
    try:
        lines = path.read_text(encoding="utf-8").splitlines()
    except OSError as exc:
        raise AssemblyError(f"cannot read {path}: {exc}") from exc

    for line_no, raw in enumerate(lines, start=1):
        instruction = raw.split("//", 1)[0].strip()
        instruction = re.sub(r"\s+", "", instruction)
        if instruction:
            records.append((line_no, instruction))
    return records


def first_pass(records: list[tuple[int, str]]) -> dict[str, int]:
    """Resolve labels to ROM addresses and warn about duplicate labels."""
    symbols = dict(PREDEFINED)
    rom_address = 0

    for line_no, instruction in records:
        if instruction.startswith("(") and instruction.endswith(")"):
            label = instruction[1:-1]
            if not SYMBOL_RE.fullmatch(label):
                raise AssemblyError(f"Line {line_no}: invalid label '{instruction}'")
            if label in symbols:
                print(
                    f"Warning: Line {line_no}: label '{label}' is already defined; "
                    f"keeping its first definition at address {symbols[label]}.",
                    file=sys.stderr,
                )
            else:
                symbols[label] = rom_address
        else:
            if instruction.startswith("(") or instruction.endswith(")"):
                raise AssemblyError(f"Line {line_no}: malformed label '{instruction}'")
            rom_address += 1

    if rom_address > 32768:
        raise AssemblyError("program exceeds the 32K instruction ROM")
    return symbols


def encode_a(instruction: str, symbols: dict[str, int], next_variable: list[int], line_no: int) -> str:
    token = instruction[1:]
    if not token:
        raise AssemblyError(f"Line {line_no}: missing value after '@'")

    if token.isdecimal():
        value = int(token)
    else:
        if not SYMBOL_RE.fullmatch(token):
            raise AssemblyError(f"Line {line_no}: invalid A-instruction symbol '{token}'")
        if token not in symbols:
            symbols[token] = next_variable[0]
            next_variable[0] += 1
        value = symbols[token]

    if not 0 <= value <= 32767:
        raise AssemblyError(f"Line {line_no}: A-instruction value must be between 0 and 32767")
    return f"{value:016b}"


def encode_c(instruction: str, line_no: int) -> str:
    if instruction.count(";") > 1 or instruction.count("=") > 1:
        raise AssemblyError(f"Line {line_no}: invalid C-instruction '{instruction}'")

    if ";" in instruction:
        left, jump = instruction.split(";", 1)
    else:
        left, jump = instruction, ""

    if "=" in left:
        dest, comp = left.split("=", 1)
    else:
        dest, comp = "", left

    if dest not in DEST:
        raise AssemblyError(f"Line {line_no}: invalid destination '{dest}'")
    if comp not in COMP:
        raise AssemblyError(f"Line {line_no}: invalid computation '{comp}'")
    if jump not in JUMP:
        raise AssemblyError(f"Line {line_no}: invalid jump '{jump}'")

    return "111" + COMP[comp] + DEST[dest] + JUMP[jump]


def assemble(source: Path, output: Path) -> int:
    records = clean_source(source)
    symbols = first_pass(records)
    next_variable = [16]
    machine_code: list[str] = []

    for line_no, instruction in records:
        if instruction.startswith("(") and instruction.endswith(")"):
            continue
        if instruction.startswith("@"):
            machine_code.append(encode_a(instruction, symbols, next_variable, line_no))
        else:
            machine_code.append(encode_c(instruction, line_no))

    output.write_text("\n".join(machine_code) + "\n", encoding="utf-8")
    return len(machine_code)


def main() -> int:
    parser = argparse.ArgumentParser(description="Assemble Hack .asm source into a .hack file")
    parser.add_argument("source", type=Path, help="input .asm file")
    parser.add_argument("output", nargs="?", type=Path, help="output .hack file (default: same name)")
    args = parser.parse_args()
    output = args.output or args.source.with_suffix(".hack")

    try:
        count = assemble(args.source, output)
    except AssemblyError as exc:
        print(exc, file=sys.stderr)
        return 1
    except OSError as exc:
        print(f"File error: {exc}", file=sys.stderr)
        return 1

    print(f"Assembled {args.source.name} -> {output.name} ({count} instructions)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
