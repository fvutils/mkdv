/****************************************************************************
 * iverilog_control.svh
 *
 * Supports selectively enabling debug and controling timeout 
 * in Icarus Verilog
 ****************************************************************************/
// Icarus requires help with timeout 
// and wave capture
reg[31:0]               _iverilog_timeout;
initial begin
	if ($test$plusargs("dumpvars")) begin
            $dumpfile("simx.vcd");
            $dumpvars;
        end
        if (!$value$plusargs("timeout=%d", _iverilog_timeout)) begin
            _iverilog_timeout=1000;
        end
        # _iverilog_timeout;
	$display("%0t: Timeout", $time);
        $finish();
end

