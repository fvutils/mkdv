#****************************************************************************
#* mkdv_vcs.mk
#*
#* Simulator support for VCS
#*
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
MKDV_AVAILABLE_TOOLS += vcs
endif

ifeq (vcs,$(MKDV_TOOL))

ifneq (1,$(RULES))

MKDV_VL_DEFINES += HAVE_BIND HAVE_HDL_CLOCKGEN
VCS ?= vcs

ifeq (1,$(MKDV_DEBUG))
#VCS_COMPILE_ARGS += +debug=acc
SIMV = simv.debug
else
SIMV = simv.ndebug
endif

SIMV = simv

ifeq (1,$(MKDV_VALGRIND))
  SIMV_PREFIX=valgrind --tool=memcheck 
endif

ifeq (1,$(MKDV_GDB))
  VLSIM_PREFIX=gdb --args 
endif

# Enable VPI for Verilator
#VLSIM_OPTIONS += --vpi
#VLSIM_OPTIONS += --top-module $(TOP_MODULE)

VCS_OPTIONS += $(foreach inc,$(MKDV_VL_INCDIRS),+incdir+$(inc))
VCS_OPTIONS += $(foreach dir,$(sort $(dir $(MKDV_VL_SRCS))),+incdir+$(dir))
VCS_OPTIONS += $(foreach def,$(MKDV_VL_DEFINES),+define+$(def))
#SIMV_ARGS += $(foreach vpi,$(VPI_LIBS),+vpi=$(vpi))
#SIMV_ARGS += +vlsim.timeout=$(MKDV_TIMEOUT)
SIMV_ARGS += $(MKDV_RUN_ARGS)

# Always build both images
MKDV_BUILD_DEPS += $(MKDV_CACHEDIR)/simv.debug
#MKDV_BUILD_DEPS += $(MKDV_CACHEDIR)/simv.ndebug

ifneq (,$(DPI_LIBS))
export LD_LIBRARY_PATH:=$(subst $(eval) ,:,$(sort $(dir $(DPI_LIBS)))):$(LD_LIBRARY_PATH)
endif

else # Rules

build-vcs : $(MKDV_BUILD_DEPS)

$(MKDV_CACHEDIR)/simv : $(MKDV_VL_SRCS) $(MKDV_DPI_SRCS)
	cd $(MKDV_CACHEDIR) ; $(VCS) \
		$(VCS_OPTIONS) $(vCS_DEBUG_OPTIONS) $(MKDV_VL_SRCS) \
		$(MKDV_DPI_SRCS) $(foreach l,$(DPI_LIBS),$(l))

run-vcs : $(MKDV_RUN_DEPS)
	echo "LD_LIBRARY_PATH=$(LD_LIBRARY_PATH)"
	$(VCS_PREFIX) $(MKDV_CACHEDIR)/$(SIMV) $(SIMV_ARGS)
	

endif

endif # MKDV_TOOL == vcs
