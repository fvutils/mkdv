#****************************************************************************
#* mkdv_vlsim.mk
#*
#* Simulator support for Verilator via the vlsim script
#*
#* SRCS           - List of source files
#* MKDV_VL_INCDIRS        - Include paths
#* MKDV_VL_DEFINES        - MKDV_VL_DEFINES
#* PYBFMS_MODULES - Modules to query for BFMs
#* SIM_ARGS       - generic simulation arguments
#* VLSIM_SIM_ARGS - vlsim-specific simulation arguments
#* VLSIM_CLKSPEC  - clock-generation options for VLSIM
#* VPI_LIBS       - List of PLI libraries
#* DPI_LIBS       - List of DPI libraries
#* MKDV_TIMEOUT        - Simulation timeout, in units of ns,us,ms,s
#****************************************************************************

ifneq (1,$(RULES))
MKDV_AVAILABLE_TOOLS += vlsim
endif

ifeq (vlsim,$(MKDV_TOOL))

ifneq (1,$(RULES))
VLSIM := $(PACKAGES_DIR)/python/bin/vlsim

MKDV_VL_DEFINES += HAVE_BIND

ifneq (,$(DEBUG))
VLSIM_OPTIONS += --trace-fst
SIMV_ARGS += +vlsim.trace
#SIMV = $(MKDV_CACHEDIR)/simv.debug
SIMV = simv.debug
else
#SIMV = $(MKDV_CACHEDIR)/simv.ndebug
SIMV = simv.ndebug
endif

# Enable VPI for Verilator
VLSIM_OPTIONS += --vpi
VLSIM_OPTIONS += --top-module $(TOP_MODULE)

VLSIM_OPTIONS += $(foreach inc,$(MKDV_VL_INCDIRS),+incdir+$(inc))
VLSIM_OPTIONS += $(foreach def,$(MKDV_VL_DEFINES),+define+$(def))
VLSIM_OPTIONS += $(foreach spec,$(VLSIM_CLKSPEC), -clkspec $(spec))
SIMV_ARGS += $(foreach vpi,$(VPI_LIBS),+vpi=$(vpi))
SIMV_ARGS += +vlsim.timeout=$(MKDV_TIMEOUT)
SIMV_ARGS += $(MKDV_RUN_ARGS)

MKDV_BUILD_DEPS += $(MKDV_CACHEDIR)/$(SIMV)

else # Rules

build-vlsim : $(MKDV_BUILD_DEPS)

$(MKDV_CACHEDIR)/$(SIMV) : $(MKDV_VL_SRCS) $(MKDV_DPI_SRCS)
ifeq (,$(VLSIM_CLKSPEC))
	@echo "Error: no VLSIM_CLKSPEC specified (eg clk=10ns)"; exit 1
endif
	cd $(MKDV_CACHEDIR) ; flock $(MKDV_CACHEDIR) $(VLSIM) -o $(notdir $@) \
		$(VLSIM_OPTIONS) $(MKDV_VL_SRCS) $(MKDV_DPI_SRCS) \
		$(foreach l,$(DPI_LIBS),$(l))

run-vlsim : $(MKDV_RUN_DEPS)
	$(MKDV_CACHEDIR)/$(SIMV) $(SIMV_ARGS) $(MKDV_RUN_ARGS)
	

endif

endif # MKDV_TOOL == vlsim
