#****************************************************************************
#* sim_mk.mk
#* common makefile
#****************************************************************************
SIM_MK_MKFILES_DIR    := $(abspath $(dir $(lastword $(MAKEFILE_LIST))))

ifneq (1,$(RULES))
PACKAGES_DIR ?= PACKAGES_DIR_unset
SIM ?= icarus
SIMTYPE ?= functional
TIMEOUT ?= 1ms


# PYBFMS_MODULES += wishbone_bfms
# VLSIM_CLKSPEC += -clkspec clk=10ns

TOP_MODULE ?= unset

PATH := $(PACKAGES_DIR)/python/bin:$(PATH)
export PATH

INCDIRS += $(SIM_MK_MKFILES_DIR)/../include

include $(SIM_MK_MKFILES_DIR)/$(SIM).mk

else # Rules

clean ::
	rm -f results.xml

include $(SIM_MK_MKFILES_DIR)/$(SIM).mk
include $(wildcard $(SIM_MK_MKFILES_DIR)/*_clean.mk)

endif
