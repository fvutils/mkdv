#****************************************************************************
#* mkdv_sby.mk
#****************************************************************************

ifneq (1,$(RULES))
MKDV_AVAILABLE_TOOLS += sby
endif

ifeq (sby,$(MKDV_TOOL))

ifneq (1,$(RULES))

DV_TOOLS += sby
DV_TOOL_DESC += "sby:(Runs the SymbiYosys model-checking tool)"

else # Rules

run-sby : $(TOP_MODULE).sby
	sby -f $(TOP_MODULE).sby

.PHONY: $(TOP_MODULE).sby

$(TOP_MODULE).sby : $(SRCS)
ifeq (,$(TOP_MODULE))
	@echo "Error: TOP_MODULE not specified" && exit 1
endif
	echo "" > $@
	echo "[options]" >> $@
	echo "mode cover" >> $@
	echo "multiclock on" >> $@
	echo "depth 100" >> $@

	echo "[engines]" >> $@
	echo "smtbmc boolector" >> $@

	echo "[script]" >> $@
	echo "read_verilog -sv -formal \\" >> $@
	echo "$(foreach inc,$(INCDIRS),-I$(inc)) \\" >> $@
	echo "$(foreach def,$(DEFINES),-D$(def)) \\" >> $@
	echo "$(notdir $(SRCS))" >> $@
	echo "prep -top $(TOP_MODULE)" >> $@
	echo "" >> $@; \
	echo "[files]" >> $@
	for src in $(SRCS); do \
	    echo "$$src" >> $@; \
	done
	echo "" >> $@; \

clean-sby :
	rm -rf $(TOP_MODULE).sby $(TOP_MODULE)

desc-sby :
	@echo "sby - Runs the SymbiYosys model-checking tool"

help-sby :
	@echo "sby help"

endif

endif

