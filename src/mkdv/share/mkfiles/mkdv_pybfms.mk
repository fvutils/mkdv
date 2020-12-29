#****************************************************************************
#* mkdv_pybfms.mk
#****************************************************************************

ifneq (1,$(RULES))
MKDV_AVAILABLE_PLUGINS += pybfms
endif

ifneq (,$(findstring pybfms,$(MKDV_PLUGINS)))

ifneq (1,$(RULES))
PYBFMS_LIB := $(shell $(PACKAGES_DIR)/python/bin/pybfms lib)

ifeq (vlsim,$(MKDV_TOOL))
	MKDV_VL_SRCS += $(MKDV_CACHEDIR)/pybfms_gen.sv 
	MKDV_DPI_SRCS += $(MKDV_CACHEDIR)/pybfms_gen.c
	DPI_LIBS += $(PYBFMS_LIB)
else
	MKDV_VL_SRCS += $(MKDV_CACHEDIR)/pybfms_gen.v
	VPI_LIBS += $(PYBFMS_LIB)
endif


else # Rules

$(MKDV_CACHEDIR)/pybfms_gen.sv $(MKDV_CACHEDIR)/pybfms_gen.c :
	$(PACKAGES_DIR)/python/bin/pybfms generate \
		-l sv $(foreach m,$(PYBFMS_MODULES),-m $(m)) -o $@
		
$(MKDV_CACHEDIR)/pybfms_gen.v :
	$(PACKAGES_DIR)/python/bin/pybfms generate \
		-l vlog $(foreach m,$(PYBFMS_MODULES),-m $(m)) -o $@

endif

endif
