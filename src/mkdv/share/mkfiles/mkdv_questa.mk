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
MKDV_VL_DEFINES += HAVE_BIND

VLOG_OPTIONS += $(foreach inc,$(MKDV_VL_INCDIRS),+incdir+$(inc))
VLOG_OPTIONS += $(foreach def,$(MKDV_VL_DEFINES),+define+$(def))
VSIM_OPTIONS += $(foreach vpi,$(VPI_LIBS),-pli $(vpi))
VSIM_OPTIONS += $(foreach dpi,$(basename $(DPI_LIBS)),-sv_lib $(dpi))

ifeq (1,$(MKDV_DEBUG))
VSIM_OPTIONS += -qwavedb=+report=class+signal+memory
endif

MKDV_BUILD_DEPS += $(MKDV_CACHEDIR)/work

else # Rules

build-questa : $(MKDV_BUILD_DEPS)

$(MKDV_CACHEDIR)/work : $(MKDV_VL_SRCS)
	vlib work
	vlog $(VLOG_OPTIONS) $(MKDV_VL_SRCS) || (rm -rf work ; exit 1)
#	vopt -access=rw+/. -o $(TOP_MODULE)_opt $(TOP_MODULE) +designfile -debug
	vopt -o $(TOP_MODULE)_opt $(TOP_MODULE) +designfile -debug


run-questa : $(MKDV_RUN_DEPS)
	vmap work $(MKDV_CACHEDIR)/work
	vsim -batch -do "run $(MKDV_TIMEOUT); quit -f" \
		$(VSIM_OPTIONS) $(TOP_MODULE)_opt \
		$(MKDV_RUN_ARGS)

endif
endif
