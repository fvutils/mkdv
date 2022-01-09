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
VLSIM := python3 -m vlsim

MKDV_PYTHONPATH += $(PACKAGES_DIR)/vlsim/src

MKDV_VL_DEFINES += HAVE_BIND

ifeq (1,$(MKDV_DEBUG))
#VLSIM_OPTIONS += --trace-fst
SIMV_ARGS += +vlsim.trace
SIMV = simv.debug
else
SIMV = simv.ndebug
endif

SIMV = simv.debug

ifeq (1,$(MKDV_VALGRIND))
  VLSIM_PREFIX=valgrind --tool=memcheck 
endif

ifeq (1,$(MKDV_GDB))
  VLSIM_PREFIX=gdb --args 
endif

# Enable VPI for Verilator
VLSIM_OPTIONS += --vpi
VLSIM_OPTIONS += --top-module $(TOP_MODULE)

VLSIM_OPTIONS += $(foreach inc,$(MKDV_VL_INCDIRS),+incdir+$(inc))
VLSIM_OPTIONS += $(foreach dir,$(sort $(dir $(MKDV_VL_SRCS))),+incdir+$(dir))
VLSIM_OPTIONS += $(foreach def,$(MKDV_VL_DEFINES),+define+$(def))
VLSIM_OPTIONS += $(foreach spec,$(VLSIM_CLKSPEC), -clkspec $(spec))
SIMV_ARGS += $(foreach vpi,$(VPI_LIBS),+vpi=$(vpi))
SIMV_ARGS += +vlsim.timeout=$(MKDV_TIMEOUT)
SIMV_ARGS += $(MKDV_RUN_ARGS)

VLSIM_DEBUG_OPTIONS += --trace-fst 

# Always build both images
MKDV_BUILD_DEPS += $(MKDV_CACHEDIR)/simv.debug
#MKDV_BUILD_DEPS += $(MKDV_CACHEDIR)/simv.ndebug

ifneq (,$(DPI_LIBS))
export LD_LIBRARY_PATH:=$(subst $(eval) ,:,$(sort $(dir $(DPI_LIBS)))):$(LD_LIBRARY_PATH)
endif

else # Rules

build-vlsim : $(MKDV_BUILD_DEPS)

$(MKDV_CACHEDIR)/simv.debug : $(MKDV_VL_SRCS) $(MKDV_DPI_SRCS)
ifeq (,$(VLSIM_CLKSPEC))
	@echo "Error: no VLSIM_CLKSPEC specified (eg clk=10ns)"; exit 1
endif
	cd $(MKDV_CACHEDIR) ; $(VLSIM) -o $(notdir $@) \
		$(VLSIM_OPTIONS) $(VLSIM_DEBUG_OPTIONS) $(MKDV_VL_SRCS) \
		$(MKDV_DPI_SRCS) $(foreach l,$(DPI_LIBS),$(l))

$(MKDV_CACHEDIR)/simv.ndebug : $(MKDV_VL_SRCS) $(MKDV_DPI_SRCS)
ifeq (,$(VLSIM_CLKSPEC))
	@echo "Error: no VLSIM_CLKSPEC specified (eg clk=10ns)"; exit 1
endif
	cd $(MKDV_CACHEDIR) ; $(VLSIM) -o $(notdir $@) \
		$(VLSIM_OPTIONS) $(MKDV_VL_SRCS) $(MKDV_DPI_SRCS) \
		$(foreach l,$(DPI_LIBS),$(l))

run-vlsim : $(MKDV_RUN_DEPS)
	echo "LD_LIBRARY_PATH=$(LD_LIBRARY_PATH)"
	$(VLSIM_PREFIX) $(MKDV_CACHEDIR)/$(SIMV) $(SIMV_ARGS)
	

endif

endif # MKDV_TOOL == vlsim
