// Example:
//   python vpp+.py mux.v PORTS=4 WIDTH=8

module mux
(
    input wire [7:0]   port0, 
    input wire [7:0]   port1, 
    input wire [7:0]   port2, 
    input wire [7:0]   port3, 

    input wire [2-1:0] sel,
    output reg [7:0]   p
);

always @ *
begin
   case (sel)

   2'd1 : p = port1;
   2'd2 : p = port2;
   2'd3 : p = port3;

   default : p   = port0;
   endcase
end

endmodule
