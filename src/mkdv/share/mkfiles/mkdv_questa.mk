#****************************************************************************
#* mkdv_questa.mk
#*
#* Simulator support for Mentor Questa
#*
#* SRCS           - List of source files
#* INCDIRS        - Include paths
#* DEFINES        - Defines
#* TOP_MODULE     - Top module to load
#* SIM_ARGS       - generic simulation arguments
#* QUESTA_SIM_ARGS - vlsim-specific simulation arguments
#* VPI_LIBS       - List of PLI libraries
#* DPI_LIBS       - List of DPI libraries
#* TIMEOUT        - Simulation timeout, in units of ns,us,ms,s
#****************************************************************************

MKDV_AVAILABLE_TOOLS += questa

ifeq (questa,$(MKDV_TOOL))
ifneq (1,$(RULES))

MKDV_VL_DEFINES += HAVE_HDL_CLOCKGEN
MKDV_VL_DEFINES += HAVE_HDL_VIRTUAL_INTERFACE
MKDV_VL_DEFINES += HAVE_BIND

VLOG_OPTIONS += $(foreach inc,$(MKDV_VL_INCDIRS),+incdir+$(inc))
VLOG_OPTIONS += $(foreach def,$(MKDV_VL_DEFINES),+define+$(def))
VSIM_OPTIONS += $(foreach vpi,$(VPI_LIBS),-pli $(vpi))
VSIM_OPTIONS += $(foreach dpi,$(basename $(DPI_LIBS)),-sv_lib $(dpi))

ifeq (1,$(MKDV_DEBUG))
VSIM_OPTIONS += -qwavedb=+report=class+signal+memory
endif

ifeq (1,$(MKDV_VALGRIND))
  VSIM_OPTIONS += -valgrind --tool=memcheck 
endif

BUILD_QUESTA_DEPS += $(MKDV_BUILD_DEPS)
BUILD_QUESTA_DEPS += questa-vopt

#ifneq (,$(MKDV_VL_SRCS))
#QUESTA_VOPT_DEPS += build-questa-vl.d
#endif

ifneq (,$(MKDV_VH_LIBS))
QUESTA_VOPT_DEPS += build-questa-vh.d
endif

else # Rules

ifneq (,$(TOP_MODULE))
build-questa : $(BUILD_QUESTA_DEPS)
else
build-questa : 
	@echo "Error: TOP_MODULE not specified"
endif

$(MKDV_CACHEDIR)/work : 
	vlib work
	
questa-vopt : $(QUESTA_VOPT_DEPS) $(MKDV_VL_SRCS)
	@echo "MKDV_VL_SRCS: $(MKDV_VL_SRCS)"
#	@if test "x$(MKDV_VL_SRCS)" != "x"; then 
ifneq (,$(MKDV_VL_SRCS))
	vlib work
	vlog $(VLOG_OPTIONS) $(MKDV_VL_SRCS) || (rm -rf work ; exit 1)
endif
	vopt -o $(TOP_MODULE)_opt $(TOP_MODULE) +designfile -debug
	
build-questa-vh.d : $(foreach l,$(MKDV_VH_LIBS),build-questa-vh-$(l).d)

build-questa-vh-%.d : $(MKDV_CACHEDIR)/work $(MKDV_VH_%_SRCS)
	echo "Library sources for $*: $(MKDV_VH_$(*)_SRCS)"
	echo "Deps: $^"
	vmap $* $(MKDV_CACHEDIR)/work
	$(MAKE) -f $(MKDV_MK) MKDV_TOOL=$(MKDV_TOOL) \
		MKDV_VH_LIB_SRCS="$(MKDV_VH_$(*)_SRCS)" \
		MKDV_VH_LIB=$(*) \
		build-questa-vh-lib 
#	touch $@

.PHONY: build-questa-vh-lib	
build-questa-vh-lib : $(MKDV_VH_LIB_SRCS)
	echo "Build with deps of $^"
	$(Q)vcom -work work -2002 $^

build-questa-vl.d : $(MKDV_CACHEDIR)/work $(MKDV_VL_SRCS)
ifeq (,$(TOP_MODULE))
	@echo "Error: TOP_MODULE not specified"; exit 1
endif
	vlog $(VLOG_OPTIONS) $(MKDV_VL_SRCS) || (rm -rf work ; exit 1)
#	vopt -access=rw+/. -o $(TOP_MODULE)_opt $(TOP_MODULE) +designfile -debug
#	vopt -o $(TOP_MODULE)_opt $(TOP_MODULE) +designfile -debug
	touch $@
	
ifeq (1,$(MKDV_GDB))
  WHICH_VSIM:=$(shell which vsim)
  QUESTA_BINDIR:=$(dir $(WHICH_VSIM))

  ifeq ("bin", $(notdir $(QUESTA_BINDIR)))
    QUESTA_ROOT := $(abspath $(QUESTA_BINDIR)/../..)
  else
    QUESTA_ROOT := $(abspath $(QUESTA_BINDIR)/..)
  endif

  VSIMK:=$(QUESTA_ROOT)/linux_x86_64/vsimk
endif

ifeq (1,$(COVERAGE_SAVE))
  BATCH_CMD += coverage save -onexit cov.ucdb;
endif
BATCH_CMD += run $(MKDV_TIMEOUT);
BATCH_CMD += quit -f;


run-questa : $(MKDV_RUN_DEPS)
	vmap work $(MKDV_CACHEDIR)/work
ifeq (1,$(MKDV_GDB))
	gdb --args $(VSIMK) -batch -do "$(BATCH_CMD)" \
		$(VSIM_OPTIONS) $(TOP_MODULE)_opt \
		$(MKDV_RUN_ARGS)
else
	vsim -batch -do "$(BATCH_CMD)" \
		$(VSIM_OPTIONS) $(TOP_MODULE)_opt \
		$(MKDV_RUN_ARGS)
endif

endif
endif
