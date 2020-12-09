#****************************************************************************
#* icarus.mk
#*
#* Simulator support for Icarus Verilog
#*
#* SRCS           - List of source files
#* INCDIRS        - Include paths
#* DEFINES        - Defines
#* PYBFMS_MODULES - Modules to query for BFMs
#* SIM_ARGS       - generic simulation arguments
#* VPI_LIBS       - List of PLI libraries
#* DPI_LIBS       - List of DPI libraries
#* TIMEOUT        - Simulation timeout, in units of ns,us,ms,s
#****************************************************************************

ifneq (1,$(RULES))
PYBFMS_VPI_LIB := $(shell $(PACKAGES_DIR)/python/bin/pybfms lib)
COCOTB_PREFIX := $(shell $(PACKAGES_DIR)/python/bin/cocotb-config --prefix)
TIMEOUT?=1ms

DEFINES += IVERILOG HAVE_HDL_CLOCKGEN NEED_TIMESCALE

ifeq (ms,$(findstring ms,$(TIMEOUT)))
  timeout=$(shell expr $(subst ms,,$(TIMEOUT)) '*' 1000000)
else
  ifeq (us,$(findstring us,$(TIMEOUT)))
    timeout=$(shell expr $(subst us,,$(TIMEOUT)) '*' 1000)
  else
    ifeq (ns,$(findstring ns,$(TIMEOUT)))
      timeout=$(shell expr $(subst ns,,$(TIMEOUT)) '*' 1)
    else
      ifeq (s,$(findstring s,$(TIMEOUT)))
        timeout=$(shell expr $(subst s,,$(TIMEOUT)) '*' 1000000000)
      else
        timeout=error: unknown $(TIMEOUT)
      endif
    endif
  endif
endif

SIMV_ARGS += +timeout=$(timeout)

SIMV=simv.vvp
ifneq (,$(DEBUG))
SIMV_ARGS += +dumpvars
endif

IVERILOG_OPTIONS += $(foreach inc,$(INCDIRS),-I $(inc))
IVERILOG_OPTIONS += $(foreach def,$(DEFINES),-D $(def))
VVP_OPTIONS += $(foreach vpi,$(VPI_LIBS),-m $(vpi))

VPI_LIBS += $(PYBFMS_VPI_LIB)
VPI_LIBS += $(COCOTB_PREFIX)/cocotb/libs/libcocotbvpi_icarus.vpl

else # Rules

build : $(SIMV)

$(SIMV) : $(SRCS) pybfms_gen.v
	iverilog -o $@ $(IVERILOG_OPTIONS) $(SRCS) pybfms_gen.v 

run : $(SIMV)
	@echo "PYTHONPATH=$(PYTHONPATH)"
	vvp $(VVP_OPTIONS) $(SIMV) $(SIMV_ARGS)
	
pybfms_gen.v :
	@echo "PYTHONPATH=$(PYTHONPATH)"
	$(PACKAGES_DIR)/python/bin/pybfms generate \
		-l vlog $(foreach m,$(PYBFMS_MODULES),-m $(m)) -o $@

endif
