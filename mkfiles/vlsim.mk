#****************************************************************************
#* vlsim.mk
#*
#* Simulator support for Verilator via the vlsim script
#*
#* SRCS           - List of source files
#* INCDIRS        - Include paths
#* DEFINES        - Defines
#* PYBFMS_MODULES - Modules to query for BFMs
#* SIM_ARGS       - generic simulation arguments
#* VLSIM_SIM_ARGS - vlsim-specific simulation arguments
#* VLSIM_CLKSPEC  - clock-generation options for VLSIM
#* VPI_LIBS       - List of PLI libraries
#* DPI_LIBS       - List of DPI libraries
#* TIMEOUT        - Simulation timeout, in units of ns,us,ms,s
#****************************************************************************

ifneq (1,$(RULES))
VLSIM := $(PACKAGES_DIR)/python/bin/vlsim
PYBFMS_DPI_LIB := $(shell $(PACKAGES_DIR)/python/bin/pybfms lib)
COCOTB_PREFIX := $(shell $(PACKAGES_DIR)/python/bin/cocotb-config --prefix)

ifneq (,$(DEBUG))
VLSIM_OPTIONS += --trace-fst
SIMV_ARGS += +vlsim.trace
SIMV := simv.debug
else
SIMV := simv.ndebug
endif

# Enable VPI for Verilator
VLSIM_OPTIONS += --vpi
VLSIM_OPTIONS += --top-module $(TOP_MODULE)

VLSIM_OPTIONS += $(foreach inc,$(INCDIRS),+incdir+$(inc))
VLSIM_OPTIONS += $(foreach def,$(DEFINES),+define+$(def))
SIMV_ARGS += $(foreach vpi,$(VPI_LIBS),+vpi=$(vpi))

DPI_LIBS += $(PYBFMS_DPI_LIB)
VPI_LIBS += $(COCOTB_PREFIX)/cocotb/libs/libcocotbvpi_verilator.so

else # Rules

build : $(SIMV)

$(SIMV) : $(SRCS) pybfms_gen.sv pybfms_gen.c
	$(VLSIM) -o $@ $(VLSIM_CLKSPEC) $(VLSIM_OPTIONS) $(SRCS) pybfms_gen.sv pybfms_gen.c \
		$(foreach l,$(DPI_LIBS),$(l))

run : $(SIMV)
	./$(SIMV) $(SIMV_ARGS)
	
pybfms_gen.sv :
	$(PACKAGES_DIR)/python/bin/pybfms generate \
		-l sv $(foreach m,$(PYBFMS_MODULES),-m $(m)) -o $@

endif
