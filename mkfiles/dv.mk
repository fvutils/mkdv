#****************************************************************************
#* dv.mk
#* common makefile
#****************************************************************************
DV_MK_MKFILES_DIR    := $(abspath $(dir $(lastword $(MAKEFILE_LIST))))

ifneq (1,$(RULES))
PACKAGES_DIR ?= PACKAGES_DIR_unset
TOOL ?= unknown
#SIMTYPE ?= functional
TIMEOUT ?= 1ms


# PYBFMS_MODULES += wishbone_bfms
# VLSIM_CLKSPEC += -clkspec clk=10ns

#TOP_MODULE ?= unset

PATH := $(PACKAGES_DIR)/python/bin:$(PATH)
export PATH

INCDIRS += $(DV_MK_MKFILES_DIR)/../include

include $(wildcard $(DV_MK_MKFILES_DIR)/tool_*.mk)

else # Rules

all : run-$(TOOL)

clean-all : $(foreach tool,$(DV_TOOLS),clean-$(tool))

clean : clean-$(TOOL)
	rm -f results.xml

help : help-$(TOOL)

help-all : 
	@echo "dv-mk help."
	@echo "Available tools: $(DV_TOOLS)"

include $(wildcard $(DV_MK_MKFILES_DIR)/tool_*.mk)

endif
