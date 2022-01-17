#****************************************************************************
#* mkdv_icarus.mk
#*
#* Simulator support for Icarus Verilog
#*
#* SRCS           - List of source files
#* MKDV_VL_INCDIRS        - Include paths
#* MKDV_VL_DEFINES        - MKDV_VL_DEFINES
#* PYBFMS_MODULES - Modules to query for BFMs
#* SIM_ARGS       - generic simulation arguments
#* VPI_LIBS       - List of PLI libraries
#* DPI_LIBS       - List of DPI libraries
#* MKDV_TIMEOUT        - Simulation MKDV_TIMEOUT, in units of ns,us,ms,s
#****************************************************************************

ifneq (1,$(RULES))
MKDV_AVAILABLE_TOOLS += icarus
endif

ifeq ($(MKDV_TOOL),icarus)

ifneq (1,$(RULES))

MKDV_TIMEOUT?=1ms

MKDV_VL_DEFINES += IVERILOG HAVE_HDL_CLOCKGEN NEED_TIMESCALE

ifeq (ms,$(findstring ms,$(MKDV_TIMEOUT)))
  ICARUS_TIMEOUT=$(shell expr $(subst ms,,$(MKDV_TIMEOUT)) '*' 1000000)
else
  ifeq (us,$(findstring us,$(MKDV_TIMEOUT)))
    ICARUS_TIMEOUT=$(shell expr $(subst us,,$(MKDV_TIMEOUT)) '*' 1000)
  else
    ifeq (ns,$(findstring ns,$(MKDV_TIMEOUT)))
      ICARUS_TIMEOUT=$(shell expr $(subst ns,,$(MKDV_TIMEOUT)) '*' 1)
    else
      ifeq (s,$(findstring s,$(MKDV_TIMEOUT)))
        ICARUS_TIMEOUT=$(shell expr $(subst s,,$(MKDV_TIMEOUT)) '*' 1000000000)
      else
        ICARUS_TIMEOUT=error: unknown $(MKDV_TIMEOUT)
      endif
    endif
  endif
endif

SIMV_ARGS += +timeout=$(ICARUS_TIMEOUT)
SIMV_ARGS += $(MKDV_RUN_ARGS)

SIMV=simv.vvp
ifeq (1,$(MKDV_DEBUG))
SIMV_ARGS += +dumpvars
endif

ifeq (1,$(MKDV_VALGRIND))
  VVP_PREFIX=valgrind --tool=memcheck 
endif

ifeq (1,$(MKDV_GDB))
  VVP_PREFIX=gdb --args 
endif

IVERILOG_OPTIONS += $(foreach inc,$(MKDV_VL_INCDIRS),-I $(inc))
IVERILOG_OPTIONS += $(foreach def,$(MKDV_VL_DEFINES),-D $(def))
IVERILOG_OPTIONS += -s $(TOP_MODULE)
IVERILOG_OPTIONS += -g2005
VVP_OPTIONS += $(foreach vpi,$(VPI_LIBS),-m $(vpi))
SIMV_ARGS += -fst +dumpfile=simx.fst

MKDV_BUILD_DEPS += $(MKDV_CACHEDIR)/$(SIMV)

else # Rules

build-icarus : $(MKDV_BUILD_DEPS)

$(MKDV_CACHEDIR)/$(SIMV) : $(MKDV_VL_SRCS)
	$(Q)iverilog -o $@ -M depfile.mk $(IVERILOG_OPTIONS) $(MKDV_VL_SRCS)

run-icarus : $(MKDV_RUN_DEPS)
	$(Q)$(VVP_PREFIX) vvp $(VVP_OPTIONS) $(MKDV_CACHEDIR)/$(SIMV) $(SIMV_ARGS)

endif

endif # ifeq $(MKDV_TOOL) == icarus
