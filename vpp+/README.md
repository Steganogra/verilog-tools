VPP+
====

A Verilog preprocessor which allow text substitution, iteration and maths functions to facilitate parametrisable Verilog.

Example Usage:

python vpp+.py myverilogfile.v WIDTH=8


myverilogfile.v:

    module adder
    (
        input  [`{WIDTH}-1:0]    a,
        input  [`{WIDTH}-1:0]    b,
        output [`{WIDTH}-1:0]    p
    );

    assign p = a + b;

    endmodule

Result:

    module adder
    (
        input  [8-1:0]    a,
        input  [8-1:0]    b,
        output [8-1:0]    p
    );

    assign p = a + b;

    endmodule


Syntax
======
