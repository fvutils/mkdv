#****************************************************************************
#* vlsim_clean.mk
#*
#* Clean target for Verilotor Vlsim
#*
#****************************************************************************

clean ::
	rm -f simv.* simx.fst simx.vcd pybfms_gen.sv pybfms_gen.c
	rm -rf obj_dir
