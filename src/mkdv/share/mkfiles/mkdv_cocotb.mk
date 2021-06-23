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

MKDV_JOB_PARAMETERS += COCOTB_MODULE=$(MKDV_COCOTB_MODULE)

COCOTB_REDUCED_LOG_FMT=1
export COCOTB_REDUCED_LOG_FMT

MKDV_CHECK_TARGET ?= check-cocotb


else # Rules

check-cocotb:
	$(Q)if test ! -f results.xml; then \
		echo "FAIL: no results.xml file" > status.txt; \
	else \
		failure_wc=`grep 'failure' results.xml | wc -l`; \
		if test $$failure_wc -eq 0; then \
			echo "PASS: " > status.txt; \
		else \
			echo "FAIL: " > status.txt; \
		fi \
	fi
	

endif

endif # cocotb in $(MKDV_PLUGINS)
