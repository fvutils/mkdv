#****************************************************************************
#* mkdv_none.mk
#*
#* Simple tool target that delegates everything to the test mkdv.mk
#****************************************************************************

ifneq (1,$(RULES))
MKDV_AVAILABLE_TOOLS += none
endif

ifeq ($(MKDV_TOOL),none)

ifneq (1,$(RULES))

else # Rules

build-none : $(MKDV_BUILD_DEPS)

run-none : $(MKDV_RUN_DEPS)

endif

endif # ifeq $(MKDV_TOOL) == none
