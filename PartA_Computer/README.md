# Part A — Hack Computer HDL

This folder contains a fresh, modular implementation of the Hack computer
components required by the capstone:

- `CPU.hdl` — instruction decode, ALU control, register destinations, jumps.
- `Memory.hdl` — Hack memory map for RAM, Screen, and Keyboard.
- `Computer.hdl` — connects instruction ROM, CPU, and data memory.
- `ALU.hdl` — 16-bit Hack ALU and zero/negative flags.
- `ARegister.hdl`, `DRegister.hdl` — 16-bit CPU registers.
- `PC.hdl` — 16-bit program counter with reset/load/increment priority.

## Simulator-provided chips used by these files

The implementation uses standard Nand2Tetris built-in chips for primitive
logic and platform devices: `Not`, `And`, `Or`, `Mux16`, `Not16`, `And16`,
`Or8Way`, `Add16`, `Inc16`, `Register`, `DMux`, `RAM16K`, `Screen`,
`Keyboard`, and `ROM32K`.

The `.hdl` files above should be kept together in this directory when opened
with the Hardware Simulator. The simulator resolves the listed built-in chips
from its standard chip library.

## Suggested verification

Run the official course test scripts against `CPU.hdl`, `Memory.hdl`, and
`Computer.hdl` using the Hardware Simulator. In particular, use the official
`CPU.tst`, `Memory.tst`, `ComputerAdd.tst`, `ComputerMax.tst`, and
`ComputerRect.tst` files provided with your Nand2Tetris course materials.

Do not mark a test as passed until the Hardware Simulator displays:

`End of script - Comparison ended successfully`

These HDL files are a newly prepared implementation. They are not claimed to
be the exact source files from any earlier local simulator session. Keep your
own lab-specific gate/ALU/register implementations instead, if your instructor
requires those exact chips to be student-authored rather than simulator built-ins.
