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
SBY_MODE ?= cover
SBY_DEPTH ?= 16
SBY_ENGINES ?= smtbmc:boolector

else # Rules

run-sby : $(TOP_MODULE).sby
	sby -f $(TOP_MODULE).sby

.PHONY: $(TOP_MODULE).sby

$(TOP_MODULE).sby : $(MKDV_VL_SRCS)
ifeq (,$(TOP_MODULE))
	@echo "Error: TOP_MODULE not specified" && exit 1
endif
	echo "" > $@
	echo "[options]" >> $@
	echo "mode $(SBY_MODE)" >> $@
ifeq (1,$(SBY_MULTICLOCK))
	echo "multiclock on" >> $@
endif
	echo "depth $(SBY_DEPTH)" >> $@

	echo "[engines]" >> $@
	for eng in $(SBY_ENGINES); do \
		echo $$eng | sed -e 's/:/ /' >> $@ ; \
	done

	echo "[script]" >> $@
	echo "read_verilog -sv -formal \\" >> $@
	echo "$(foreach inc,$(MKDV_VL_INCDIRS),-I$(inc)) \\" >> $@
	echo "$(foreach def,$(MKDV_VL_DEFINES),-D$(def)) \\" >> $@
	echo "$(notdir $(MKDV_VL_SRCS))" >> $@
	echo "prep -top $(TOP_MODULE)" >> $@
	echo "" >> $@; \
	echo "[files]" >> $@
	for src in $(MKDV_VL_SRCS); do \
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

