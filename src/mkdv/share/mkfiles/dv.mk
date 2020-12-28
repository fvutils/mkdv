#****************************************************************************
#* mkdv.mk
#* common makefile
#****************************************************************************
DV_MK_MKFILES_DIR := $(abspath $(dir $(lastword $(MAKEFILE_LIST))))

CWD := $(shell pwd)

ifneq (1,$(RULES))
PACKAGES_DIR ?= PACKAGES_DIR_unset
TOOL ?= unknown
#SIMTYPE ?= functional
TIMEOUT ?= 1ms

MKDV_MKFILES_PATH += $(DV_MK_MKFILES_DIR)
MKDV_INCLUDE_DIR = $(abspath $(DV_MK_MKFILES_DIR)/../include)


# PYBFMS_MODULES += wishbone_bfms
# VLSIM_CLKSPEC += -clkspec clk=10ns

#TOP_MODULE ?= unset

PATH := $(PACKAGES_DIR)/python/bin:$(PATH)
export PATH

INCDIRS += $(DV_MK_MKFILES_DIR)/../include

#include $(wildcard $(DV_MK_MKFILES_DIR)/tool_*.mk)
INCFILES = $(foreach dir,$(MKDV_MKFILES_PATH),$(wildcard $(dir)/mkdv_*.mk))
include $(foreach dir,$(MKDV_MKFILES_PATH),$(wildcard $(dir)/mkdv_*.mk))

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
	mkdir -p cache
	$(MAKE) -C rundir -f $(MKDV_MK) \
		MKDV_RUNDIR=$(CWD)/rundir \
		MKDV_CACHEDIR=$(CWD)/cache \
		run-$(MKDV_TOOL)

clean-all : $(foreach tool,$(DV_TOOLS),clean-$(tool))

clean : 
	rm -rf rundir cache

help : help-$(TOOL)

help-all : 
	@echo "dv-mk help."
	@echo "Available tools: $(DV_TOOLS)"

include $(foreach dir,$(MKDV_MKFILES_PATH),$(wildcard $(dir)/mkdv_*.mk))
#include $(wildcard $(DV_MK_MKFILES_DIR)/tool_*.mk)

endif
