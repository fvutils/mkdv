#****************************************************************************
#* mkdv_cocotb.mk
#*
#* mkdv support for cocotb
#****************************************************************************

MKDV_AVAILABLE_PLUGINS += cocotb

ifneq (,$(findstring cocotb,$(MKDV_PLUGINS)))
ifneq (1,$(RULES))
COCOTB_PREFIX := $(shell $(PACKAGES_DIR)/python/bin/cocotb-config --prefix)

ifeq (icarus,$(MKDV_TOOL))
	VPI_LIBS += $(COCOTB_PREFIX)/cocotb/libs/libcocotbvpi_icarus.vpl
else
	ifeq (vlsim,$(MKDV_TOOL))
		VPI_LIBS += $(COCOTB_PREFIX)/cocotb/libs/libcocotbvpi_verilator.so
	else
		VPI_LIBS += $(COCOTB_PREFIX)/cocotb/libs/libcocotbvpi_modelsim.so
	endif
endif


else # Rules

endif

endif # cocotb in $(MKDV_PLUGINS)
