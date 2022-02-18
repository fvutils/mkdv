#****************************************************************************
#* mkdv.mk
#* common makefile
#****************************************************************************
DV_MK_MKFILES_DIR := $(abspath $(dir $(lastword $(MAKEFILE_LIST))))

CWD := $(shell pwd)


ifneq (1,$(RULES))

ifeq (,$(MKDV_RUNDIR))
MKDV_RUNDIR=$(CWD)/rundir
endif

ifneq (1,$(MKDV_VERBOSE))
Q=@
endif

ifeq (,$(MKDV_CACHEDIR))
MKDV_CACHEDIR=$(CWD)/cache/$(MKDV_TOOL)
endif

PACKAGES_DIR ?= PACKAGES_DIR_unset
MKDV_TIMEOUT ?= 1ms

MKDV_MKFILES_PATH += $(DV_MK_MKFILES_DIR)
MKDV_INCLUDE_DIR = $(abspath $(DV_MK_MKFILES_DIR)/../include)

PATH := $(PACKAGES_DIR)/python/bin:$(PATH)
export PATH

MKDV_VL_INCDIRS += $(DV_MK_MKFILES_DIR)/../include

INCFILES = $(foreach dir,$(MKDV_MKFILES_PATH),$(wildcard $(dir)/mkdv_*.mk))
include $(foreach dir,$(MKDV_MKFILES_PATH),$(wildcard $(dir)/mkdv_*.mk))

PYTHONPATH := $(subst $(eval) ,:,$(MKDV_PYTHONPATH)):$(PYTHONPATH)
export PYTHONPATH

#********************************************************************
#* Job parameters are recorded in the job-results database
#********************************************************************
MKDV_JOB_PARAMETERS += MKDV_TOOL=$(MKDV_TOOL)
export MKDV_JOB_PARAMETERS

export MKDV_JOB_TAGS


#info :
#	@echo "MKDV_AVAILABLE_TOOLS: $(MKDV_AVAILABLE_TOOLS)"
#	@echo "MKDV_AVAIABLE_PLUGINS: $(MKDV_AVAILABLE_PLUGINS)"

else # Rules

# All is the default target run from the command line
default : help

.PHONY: _setup
_setup :
ifeq (,$(MKDV_MK))
	@echo "Error: MKDV_MK is not set"; exit 1
endif
ifeq (,$(MKDV_TOOL))
	@echo "Error: MKDV_TOOL is not set"; exit 1
endif
ifeq (,$(findstring $(MKDV_TOOL),$(MKDV_AVAILABLE_TOOLS)))
	@echo "Error: MKDV_TOOL $(MKDV_TOOL) is not available ($(MKDV_AVAILABLE_TOOLS))"; exit 1
endif
	mkdir -p $(MKDV_CACHEDIR)
	$(MAKE) -C $(MKDV_CACHEDIR) -f $(MKDV_MK) \
		MKDV_RUNDIR=$(MKDV_RUNDIR) \
		MKDV_CACHEDIR=$(MKDV_CACHEDIR) \
		build-$(MKDV_TOOL) || (echo "FAIL: exit status $$?" > status.txt; exit 1)

.PHONY: _run pre-run run post-run
_run : 
	#@echo "INCFILES: $(INCFILES) $(MKDV_AVAILABLE_TOOLS) $(MKDV_AVAILABLE_PLUGINS)"
	# Save environment variables for inspection
	@env > job.env
ifeq (,$(MKDV_MK))
	$(Q)echo "Error: MKDV_MK is not set"; exit 1
endif
ifeq (,$(MKDV_TOOL))
	$(Q)echo "Error: MKDV_TOOL is not set"; exit 1
endif
ifeq (,$(findstring $(MKDV_TOOL),$(MKDV_AVAILABLE_TOOLS)))
	$(Q)echo "Error: MKDV_TOOL $(MKDV_TOOL) is not available ($(MKDV_AVAILABLE_TOOLS))"; exit 1
endif
	$(Q)if test $(CWD) != $(MKDV_RUNDIR); then rm -rf $(MKDV_RUNDIR); fi
	$(Q)mkdir -p $(MKDV_RUNDIR)
	$(Q)$(MAKE) -C $(MKDV_RUNDIR) -f $(MKDV_MK) \
		MKDV_RUNDIR=$(MKDV_RUNDIR) \
		MKDV_CACHEDIR=$(MKDV_CACHEDIR) \
		pre-run || (echo "FAIL: pre-run failed with exit status $$?" > $(MKDV_RUNDIR)/status.txt; exit 1)
	$(Q)$(MAKE) -C $(MKDV_RUNDIR) -f $(MKDV_MK) \
		MKDV_RUNDIR=$(MKDV_RUNDIR) \
		MKDV_CACHEDIR=$(MKDV_CACHEDIR) \
		run-$(MKDV_TOOL) || (echo "FAIL: run failed with exit status $$?" > $(MKDV_RUNDIR)/status.txt; exit 1)
	$(Q)$(MAKE) -C $(MKDV_RUNDIR) -f $(MKDV_MK) \
		MKDV_RUNDIR=$(MKDV_RUNDIR) \
		MKDV_CACHEDIR=$(MKDV_CACHEDIR) \
		post-run || (echo "FAIL: post-run failed with exit status $$?" > $(MKDV_RUNDIR)/status.txt; exit 1)
ifeq (,$(MKDV_CHECK_TARGET))
	$(Q)echo "PASS: " > $(MKDV_RUNDIR)/status.txt
endif

_check :
ifeq (,$(MKDV_CHECK_TARGET))
	$(Q)echo "PASS: " > $(MKDV_RUNDIR)/status.txt
else
	$(Q)$(MAKE) -C $(MKDV_RUNDIR) -f $(MKDV_MK) \
		MKDV_RUNDIR=$(MKDV_RUNDIR) \
		MKDV_CACHEDIR=$(MKDV_CACHEDIR) $(MKDV_CHECK_TARGET)
endif

pre-run : $(MKDV_PRE_RUN_TARGETS)
	$(Q)echo "Pre-Run: $(MKDV_PRE_RUN_TARGETS) $(MKDV_POST_RUN_TARGETS)"

post-run : $(MKDV_POST_RUN_TARGETS)
	$(Q)echo "Post-Run: $(MKDV_POST_RUN_TARGETS)"
		
ifneq (,$(MKDV_TESTS))
else
endif	

.PHONY: help
help :
	@echo "mkdv.mk"
	@echo "    Targets:"
	@echo "        list    - list available jobs"
	@echo "        regress - run a set of jobs"
	@echo "        run     - run a single job"
	@echo "        mkrun   - run the Makefile flow without jobspec infrastructure"
	@echo "    Note: pass arguments via MKDV_ARGS variable"

.PHONY: list
list :
	python3 -m mkdv list $(MKDV_ARGS)
	
.PHONY: mkrun
mkrun : _setup _run _check

.PHONY: regress
regress : 
	python3 -m mkdv regress $(MKDV_ARGS)
	
.PHONY: run
run :
	python3 -m mkdv run $(MKDV_ARGS)

clean-all : $(foreach tool,$(DV_TOOLS),clean-$(tool))

clean : 
	rm -rf rundir cache


include $(foreach dir,$(MKDV_MKFILES_PATH),$(wildcard $(dir)/mkdv_*.mk))

endif
