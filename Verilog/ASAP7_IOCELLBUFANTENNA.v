module IOCELLBUFANTENNAOUT
(
	input wire in,
	output wire out
);

wire w1, w2, w3, w4;


INVx1_ASAP7_75t_R buff1(.A(in), .Y(w1));
INVx3_ASAP7_75t_R buff2(.A(w1), .Y(w2));
INVx8_ASAP7_75t_R buff3(.A(w2), .Y(w3));
//BUFFD16BWP buff4(.I(w3), .Z(w4));
INVx13_ASAP7_75t_R  buff4(.A(w3), .Y(out));
ANTENNA_ASAP7_75t_R antenna1(.A(out));
ANTENNA_ASAP7_75t_R antenna2(.A(out));
//ANTENNABWP antenna3(.I(out));
//ANTENNABWP antenna4(.I(out));
//ANTENNABWP antenna5(.I(out));

endmodule

module IOCELLBUFANTENNAIN
(
        input wire in,
        output wire out
);

wire w1, w2, w3, w4;

ANTENNA_ASAP7_75t_R antenna1(.A(in));
ANTENNA_ASAP7_75t_R antenna2(.A(in));
//ANTENNABWP antenna3(.I(in));
//ANTENNABWP antenna4(.I(in));
//ANTENNABWP antenna5(.I(in));
//INVD1BWP buff1(.I(in), .Z(w1));
INVx2_ASAP7_75t_R buff1(.A(in), .Y(w2));
INVx6_ASAP7_75t_R buff2(.A(w2), .Y(out));

endmodule
