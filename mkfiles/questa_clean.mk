#****************************************************************************
#* questa_target.mk
#*
#* Clean target for Mentor Questa
#*
#****************************************************************************

clean ::
	rm -rf work transcript modelsim.ini
	rm -rf design.bin qwave.db visualizer.log
