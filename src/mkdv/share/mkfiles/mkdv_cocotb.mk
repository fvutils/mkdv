#****************************************************************************
#* mkdv_cocotb.mk
#*
#* mkdv support for cocotb
#****************************************************************************

ifneq (1,$(RULES))
MKDV_AVAILABLE_PLUGINS += cocotb
endif

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

MODULE=$(MKDV_COCOTB_MODULE)
export MODULE


else # Rules

endif

endif # cocotb in $(MKDV_PLUGINS)
