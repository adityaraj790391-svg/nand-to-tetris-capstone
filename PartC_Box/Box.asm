// Aditya Raj - Nand to Tetris Capstone
// Roll number: 2501730238 | K = 38
// Box: starts at row 38, 20 rows high, 48 pixels wide (3 words)
// First screen word: SCREEN + 32*38 = 16384 + 1216 = 17600
(LOOP)
    @KBD
    D=M
    @CLEAR
    D;JEQ          // No key: clear the box
    @COLOR
    M=-1           // Key pressed: black pixels (all 1s)
    @DRAW
    0;JMP
(CLEAR)
    @COLOR
    M=0            // Key released: white pixels (all 0s)
(DRAW)
    @17600
    D=A
    @ADDR
    M=D            // Start at screen row 38
    @20
    D=A
    @ROWS
    M=D            // Repeat for 20 rows
(ROW)
    @COLOR
    D=M
    @ADDR
    A=M
    M=D            // Word 1
    @ADDR
    M=M+1
    @COLOR
    D=M
    @ADDR
    A=M
    M=D            // Word 2
    @ADDR
    M=M+1
    @COLOR
    D=M
    @ADDR
    A=M
    M=D            // Word 3 (48 pixels total)
    @ADDR
    M=M+1
    @29
    D=A
    @ADDR
    M=D+M          // 3 words written + 29 = 32-word row stride
    @ROWS
    M=M-1
    D=M
    @ROW
    D;JGT          // Continue until 20 rows are written
    @LOOP
    0;JMP           // Re-check keyboard continuously
