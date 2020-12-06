#****************************************************************************
#* icarus_clean.mk
#*
#* Clean target for Icarus Verilog
#****************************************************************************

clean ::
	rm -f simv.* simx.fst simx.vcd pybfms_gen.v
	rm -rf obj_dir
