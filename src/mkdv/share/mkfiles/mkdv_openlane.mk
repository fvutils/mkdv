#****************************************************************************
#* mkdv_openlane.mk
#*
#* MKDV Makefile for running Openlane 
#****************************************************************************
MKDV_AVAILABLE_TOOLS += openlane

ifeq (openlane,$(MKDV_TOOL))
ifneq (1,$(RULES))

# Podman (Centos8) doesn't like the -u switches
# Only add if we're not using podman in emulation
ifeq (,$(shell which podman))
   DOCKER_UID_OPTIONS = -u $(shell id -u $(USER)):$(shell id -g $(USER))
endif

VERILOG_FILES := $(MKDV_VL_SRCS)
export VERILOG_FILES

VERILOG_FILES_BLACKBOX := $(MKDV_VL_SRCS_BB)
export VERILOG_FILES_BLACKBOX

VERILOG_INCLUDE_DIRS := $(MKDV_VL_INCDIRS)
export VERILOG_INCLUDE_DIRS

SYNTH_DEFINES := $(MKDV_VL_DEFINES)
export SYNTH_DEFINES

DESIGN_NAME := $(TOP_MODULE)
export DESIGN_NAME

OPENLANE_SRCDIRS += $(dir $(MKDV_MK))
OPENLANE_SRCDIRS += $(dir $(MKDV_VL_SRCS))
OPENLANE_SRCDIRS += $(dir $(MKDV_VL_SRCS_BB))
OPENLANE_SRCDIRS += $(MKDV_VL_INCDIRS)

SRCDIRS = $(sort $(OPENLANE_SRCDIRS))

OPENLANE_CMD ?= "cd /mkdv_rundir && pwd && ls && flow.tcl -design ./$(TOP_MODULE) -save_path . -save -tag $(TOP_MODULE) -overwrite"

else # Rules

build-openlane :


$(MKDV_RUNDIR)/$(TOP_MODULE)/config.tcl : $(dir $(MKDV_MK))/config.tcl
	mkdir -p `dirname $@`
	cp $^ $@

run-openlane : $(MKDV_RUNDIR)/$(TOP_MODULE)/config.tcl
ifeq (,$(TOP_MODULE))
	@echo "Error: TOP_MODULE not set"; exit 1
endif
	docker run -it -v $(OPENLANE_ROOT):/openLANE_flow \
		-v $(PDK_ROOT):$(PDK_ROOT) \
		-v $(MKDV_RUNDIR):/mkdv_rundir \
		$(foreach dir,$(SRCDIRS),-v $(dir):$(dir)) \
		-e PDK_ROOT=$(PDK_ROOT) \
		-e DESIGN_NAME=$(TOP_MODULE) \
		-e SYNTH_DIR=$(dir $(MKDV_MK)) \
		-e VERILOG_FILES="$(MKDV_VL_SRCS)" \
		-e VERILOG_FILES_BLACKBOX="$(MKDV_VL_SRCS_BB)" \
		-e VERILOG_INCLUDE_DIRS="$(MKDV_VL_INCDIRS)" \
		-e EXTRA_LEFS=$(MKDV_LEF_FILES) \
		-e EXTRA_GDS_FILES=$(MKDV_GDS_FILES) \
		-e SYNTH_DEFINES="$(MKDV_VL_DEFINES)" \
		$(DOCKER_UID_OPTIONS) \
		$(OPENLANE_IMAGE_NAME) sh -c $(OPENLANE_CMD)

endif
endif

