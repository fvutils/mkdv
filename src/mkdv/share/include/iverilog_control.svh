/****************************************************************************
 * iverilog_control.svh
 *
 * Supports selectively enabling debug and controling timeout 
 * in Icarus Verilog
 ****************************************************************************/
// Icarus requires help with timeout 
// and wave capture
reg[31:0]               _iverilog_timeout;
reg[8*256-1:0]          _iverilog_dumpfile;
initial begin
    
	if ($test$plusargs("dumpvars")) begin
		if (!$value$plusargs("dumpfile=%s", _iverilog_dumpfile)) begin
			$display("Error: no +dumpfile argument specified");
			$finish();
		end
		$dumpfile(_iverilog_dumpfile);
        $dumpvars;
    end
        if (!$value$plusargs("timeout=%d", _iverilog_timeout)) begin
            _iverilog_timeout=1000;
        end
        # _iverilog_timeout;
	$display("%0t: Timeout", $time);
        $finish();
end

