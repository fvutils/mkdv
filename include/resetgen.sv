
/****************************************************************************
 * resetgen.sv
 ****************************************************************************/

  
/**
 * Module: resetgen
 * 
 * TODO: Add module documentation
 */
module resetgen #(
		parameter INITIAL_DELAY = 2,
		parameter ASSERT_COUNT = 20
		) (
		input		clock,
		output		reset);
	reg[1:0]		state = 0;
	reg[31:0]		count = 0;
	reg				reset_r = 0;
	
	assign reset = reset_r;
	
	always @(posedge clock) begin
		case (state) 
			0: begin
				if (count == INITIAL_DELAY) begin
					reset_r <= 1;
					count <= 0;
					state <= 1;
				end else begin
					count <= count + 1;
				end
			end
			1: begin
				if (count == ASSERT_COUNT) begin
					reset_r <= 0;
				end else begin
					count <= count + 1;
				end
			end
		endcase
	end

endmodule


