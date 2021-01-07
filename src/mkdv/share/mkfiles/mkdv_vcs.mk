#****************************************************************************
#* vcs.mk
#*
#* Simulator support for Synopsys VCS
#*
#* SRCS           - List of source files
#* INCDIRS        - Include paths
#* DEFINES        - Defines
#* TOP_MODULE     - Top module to load
#* SIM_ARGS       - generic simulation arguments
#* VCS_SIM_ARGS   - VCS-specific simulation arguments
#* VPI_LIBS       - List of PLI libraries
#* DPI_LIBS       - List of DPI libraries
#* TIMEOUT        - Simulation timeout, in units of ns,us,ms,s
#****************************************************************************
MKDV_AVAIABLE_TOOLS += vcs

ifeq (vcs,$(MKDV_TOOL))

ifneq (1,$(RULES))
COMMON_DIR := $(abspath $(dir $(lastword $(MAKEFILE_LIST))))
PACKAGES_DIR := $(abspath $(COMMON_DIR)/../../packages)
PYBFMS_DPI_LIB := $(shell $(PACKAGES_DIR)/python/bin/pybfms lib)
COCOTB_PREFIX := $(shell $(PACKAGES_DIR)/python/bin/cocotb-config --prefix)
VCS?=vcs

IFC?=vpi

ifeq (dpi,$(IFC))
#DPI_LIBS += $(subst .so,,$(PYBFMS_DPI_LIB))
DPI_LIBS += $(PYBFMS_DPI_LIB)
else
VPI_LIBS += $(PYBFMS_DPI_LIB)
endif

VPI_LIBS += $(COCOTB_PREFIX)/cocotb/libs/libcocotbvpi_vcs.so

DEFINES += HAVE_HDL_CLOCKGEN

VCS_OPTIONS += -full64 +vpi -debug +acc+1 -P pli.tab
VCS_OPTIONS += $(foreach inc,$(INCDIRS),+incdir+$(inc))
VCS_OPTIONS += $(foreach def,$(DEFINES),+define+$(def))
VCS_OPTIONS += $(foreach vpi,$(VPI_LIBS),-load $(vpi))
#SIMV_OPTIONS += $(foreach vpi,$(VPI_LIBS),-load $(vpi))
#VCS_OPTIONS += $(foreach dpi,$(DPI_LIBS),-L$(dir $(dpi)) -l $(notdir $(dpi)))
VCS_OPTIONS += $(foreach dpi,$(DPI_LIBS),$(dpi))


ifeq (dpi,$(IFC))
SRCS += pybfms_gen.sv pybfms_gen.c
SIMV_OPTIONS += -dpioutoftheblue 1
else
SRCS += pybfms_gen.v
endif
#SRCS += pybfms_gen.v

else # Rules

build-vcs : $(SRCS)
	echo "acc+=rw,wn:*" > pli.tab
	$(VCS) -sverilog $(VCS_OPTIONS) $(SRCS)


run : build
	./simv $(SIMV_OPTIONS)

endif

endif
