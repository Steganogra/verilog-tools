VPP+
====

A Verilog preprocessor which allow text substitution, iteration and maths functions to facilitate parametrisable Verilog.

Usage:

Parameters are passed on the command line and used when processing the input file.

python vpp+.py inputfile param1=x param2=y...


Example:

python vpp+.py adder.vpp WIDTH=8


adder.vpp:

    module adder
    (
        input  [`{WIDTH-1}:0]    a,
        input  [`{WIDTH-1}:0]    b,
        output [`{WIDTH-1}:0]    p
    );

    assign p = a + b;

    endmodule

Result:

    module adder
    (
        input  [7:0]    a,
        input  [7:0]    b,
        output [7:0]    p
    );

    assign p = a + b;

    endmodule


Supported Syntax
================

Defines:
    Variable definition for VPP+. Not printed in resulting output but can be used
    by placing `{MYVAR} in the file after the definition.
    Can be used in for/if/ifdef etc.

    `define MYVAR 3

Escaped Defines:
    Ignored by VPP+ and printed to the output with leading tick removed i.e. a way
    of passing defines through VPP to resulting output.

    ``define MYVAR 3

For:
    Executed by VPP+ to allow text to be repeated in a loop. The Start, end and interator must be valid Python.

    `for (i=0;i<PORTS;i=i+1)
        // Index = `{i}
    `endfor

Ifdef:
    Check if a definition exists.

    `ifdef MYVAR
        // Only if MYVAR exists
    `endif

Undef:
    Undefine a definition.

    `undef MYVAR

If condition:
    The condition is evaluated by VPP+ (and thus should be valid Python).

    `if MYVAR > 3
        // Only if MYVAR more than 3
    `endif

log2w:
    Find the width required to express a variable i.e. (ceiling) Log2(N)

    `define MYVAR   4
    reg [`{log2w(MYVAR)}-1:0] myreg;

