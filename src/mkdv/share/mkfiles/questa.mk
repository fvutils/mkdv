#****************************************************************************
#* questa.mk
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

ifneq (1,$(RULES))
PYBFMS_DPI_LIB := $(shell $(PACKAGES_DIR)/python/bin/pybfms lib)
COCOTB_PREFIX := $(shell $(PACKAGES_DIR)/python/bin/cocotb-config --prefix)

IFC?=vpi

ifeq (dpi,$(IFC))
DPI_LIBS += $(subst .so,,$(PYBFMS_DPI_LIB))
else
VPI_LIBS += $(PYBFMS_DPI_LIB)
endif

VPI_LIBS += $(COCOTB_PREFIX)/cocotb/libs/libcocotbvpi_modelsim.so

DEFINES += HAVE_HDL_CLOCKGEN

VLOG_OPTIONS += $(foreach inc,$(INCDIRS),+incdir+$(inc))
VLOG_OPTIONS += $(foreach def,$(DEFINES),+define+$(def))
VSIM_OPTIONS += $(foreach vpi,$(VPI_LIBS),-pli $(vpi))
VSIM_OPTIONS += $(foreach dpi,$(DPI_LIBS),-sv_lib $(dpi))


ifeq (dpi,$(IFC))
SRCS += pybfms_gen.sv pybfms_gen.c
VSIM_OPTIONS += -dpioutoftheblue 1
else
SRCS += pybfms_gen.v
endif
#SRCS += pybfms_gen.v

else # Rules

build : $(SRCS)
	vlib work
	vlog $(VLOG_OPTIONS) $(SRCS)
#	vopt -access=rw+/. -o $(TOP_MODULE)_opt $(TOP_MODULE) +designfile -debug
	vopt -o $(TOP_MODULE)_opt $(TOP_MODULE) +designfile -debug


run : build
	vsim -batch -do "run $(TIMEOUT); quit -f" \
		$(VSIM_OPTIONS) $(TOP_MODULE)_opt \
		-qwavedb=+report=class+signal

pybfms_gen.sv pybfms_gen.c :
	$(PACKAGES_DIR)/python/bin/pybfms generate \
		-l sv $(foreach m,$(PYBFMS_MODULES),-m $(m)) -o $@

pybfms_gen.v :
	$(PACKAGES_DIR)/python/bin/pybfms generate \
		-l vlog $(foreach m,$(PYBFMS_MODULES),-m $(m)) -o $@

endif
