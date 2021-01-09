#****************************************************************************
#* ncsim.mk
#*
#* Simulator support for Cadence NCSim
#*
#* SRCS           - List of source files
#* INCDIRS        - Include paths
#* DEFINES        - Defines
#* TOP_MODULE     - Top module to load
#* SIM_ARGS       - generic simulation arguments
#* NCSIM_SIM_ARGS - ncsim-specific simulation arguments
#* VPI_LIBS       - List of PLI libraries
#* DPI_LIBS       - List of DPI libraries
#* TIMEOUT        - Simulation timeout, in units of ns,us,ms,s
#****************************************************************************

ifeq (ncsim,$(MKDV_TOOL))
ifneq (1,$(RULES))
COMMON_DIR := $(abspath $(dir $(lastword $(MAKEFILE_LIST))))
PACKAGES_DIR := $(abspath $(COMMON_DIR)/../../packages)
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

VLOG_OPTIONS += $(foreach inc,$(INCDIRS),-INCDIR $(inc))
VLOG_OPTIONS += $(foreach def,$(DEFINES),-DEFINE $(def))
NCELAB_OPTIONS += $(foreach vpi,$(VPI_LIBS),-loadvpi $(vpi):vlog_startup_routines_bootstrap)
NCSIM_OPTIONS += $(foreach vpi,$(VPI_LIBS),-loadvpi $(vpi):vlog_startup_routines_bootstrap)
NCSIM_OPTIONS += $(foreach dpi,$(DPI_LIBS),-sv_lib $(dpi))


ifeq (dpi,$(IFC))
SRCS += pybfms_gen.sv pybfms_gen.c
NCSIM_OPTIONS += -dpioutoftheblue 1
else
SRCS += pybfms_gen.v
endif
#SRCS += pybfms_gen.v

else # Rules

build : $(SRCS)
	mkdir -p worklib
	echo "DEFINE worklib ./worklib" > cds.lib
	echo "" > hdl.var
	ncvlog -64BIT -work worklib -sv $(VLOG_OPTIONS) $(SRCS)
	ncelab -64BIT $(NCELAB_OPTIONS) $(TOP_MODULE) -snapshot worklib.$(TOP_MODULE):snap


run : build
	ncsim -64BIT $(NCSIM_OPTIONS) worklib.$(TOP_MODULE):snap

pybfms_gen.sv pybfms_gen.c :
	$(PACKAGES_DIR)/python/bin/pybfms generate \
		-l sv $(foreach m,$(PYBFMS_MODULES),-m $(m)) -o $@

pybfms_gen.v :
	$(PACKAGES_DIR)/python/bin/pybfms generate \
		-l vlog $(foreach m,$(PYBFMS_MODULES),-m $(m)) -o $@

endif
endif
