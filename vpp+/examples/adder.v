// Example:
//   python vpp+.py adder.v WIDTH=8

module adder
(
    input  [8-1:0]    a,
    input  [8-1:0]    b,
    output [8-1:0]    p
);

assign p = a + b;

endmodule
