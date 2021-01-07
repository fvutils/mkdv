
MKDV_AVAILABLE_TOOLS += quartus

ifeq (quartus,$(MKDV_TOOL))

ifneq (1,$(RULES))

else # Rules

build-quartus :

$(TOP_MODULE).qsf : 
	echo "" > $@
	echo 'set_global_assignment -name FAMILY "Cyclone V"' >> $@
	echo "set_global_assignment -name DEVICE 5CGXFC7C7F23C8" >> $@
	echo "set_global_assignment -name TOP_LEVEL_ENTITY $(TOP_MODULE)" >> $@
	for def in $(MKDV_VL_DEFINES); do \
		echo "set_global_assignment -name VERILOG_MACRO \"$$def\"" >> $@; \
	done
	for inc in $(MKDV_VL_INCDIRS); do \
		echo "set_global_assignment -name SEARCH_PATH $$inc" >> $@; \
	done
	for src in $(MKDV_VL_SRCS); do \
		echo "set_global_assignment -name SYSTEMVERILOG_FILE $$src" >> $@; \
	done
ifneq (,$(SDC_FILE))
	echo "set_global_assignment -name SDC_FILE $(SDC_FILE)" >> $@
endif

$(TOP_MODULE).qpf : 
	echo 'PROJECT_REVISION = "$(TOP_MODULE)"' > $@

run-quartus : $(TOP_MODULE).qpf $(TOP_MODULE).qsf
	quartus_map $(TOP_MODULE) #  --source=filtref.bdf --family="Cyclone V"
	quartus_fit $(TOP_MODULE) # --part=EP3C10F256C8 --pack_register=minimize_area
	quartus_asm $(TOP_MODULE)					
	quartus_sta $(TOP_MODULE)
	

endif

endif

