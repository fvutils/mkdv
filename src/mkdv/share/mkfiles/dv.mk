#****************************************************************************
#* mkdv.mk
#* common makefile
#****************************************************************************
DV_MK_MKFILES_DIR := $(abspath $(dir $(lastword $(MAKEFILE_LIST))))

CWD := $(shell pwd)

ifneq (1,$(RULES))
PACKAGES_DIR ?= PACKAGES_DIR_unset
MKDV_TIMEOUT ?= 1ms

MKDV_MKFILES_PATH += $(DV_MK_MKFILES_DIR)
MKDV_INCLUDE_DIR = $(abspath $(DV_MK_MKFILES_DIR)/../include)


# PYBFMS_MODULES += wishbone_bfms
# VLSIM_CLKSPEC += -clkspec clk=10ns

#TOP_MODULE ?= unset

PATH := $(PACKAGES_DIR)/python/bin:$(PATH)
export PATH

MKDV_VL_INCDIRS += $(DV_MK_MKFILES_DIR)/../include

INCFILES = $(foreach dir,$(MKDV_MKFILES_PATH),$(wildcard $(dir)/mkdv_*.mk))
include $(foreach dir,$(MKDV_MKFILES_PATH),$(wildcard $(dir)/mkdv_*.mk))

PYTHONPATH := $(subst $(eval) ,:,$(MKDV_PYTHONPATH))
export PYTHONPATH

else # Rules

run : 
	@echo "INCFILES: $(INCFILES) $(MKDV_AVAILABLE_TOOLS) $(MKDV_AVAILABLE_PLUGINS)"
ifeq (,$(MKDV_MK))
	@echo "Error: MKDV_MK is not set"; exit 1
endif
ifeq (,$(MKDV_TOOL))
	@echo "Error: MKDV_TOOL is not set"; exit 1
endif
ifeq (,$(findstring $(MKDV_TOOL),$(MKDV_AVAILABLE_TOOLS)))
	@echo "Error: MKDV_TOOL $(MKDV_TOOL) is not available ($(MKDV_AVAILABLE_TOOLS))"; exit 1
endif
	rm -rf rundir
	mkdir rundir
	mkdir -p cache/$(MKDV_TOOL)
	$(MAKE) -C rundir -f $(MKDV_MK) \
		MKDV_RUNDIR=$(CWD)/rundir \
		MKDV_CACHEDIR=$(CWD)/cache/$(MKDV_TOOL) \
		run-$(MKDV_TOOL)

clean-all : $(foreach tool,$(DV_TOOLS),clean-$(tool))

clean : 
	rm -rf rundir cache

help : help-$(TOOL)

help-all : 
	@echo "dv-mk help."
	@echo "Available tools: $(DV_TOOLS)"

include $(foreach dir,$(MKDV_MKFILES_PATH),$(wildcard $(dir)/mkdv_*.mk))

endif
