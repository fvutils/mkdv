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

VERILOG_INCLUDE_DIRS := $(MKDV_VL_INCDIRS)
export VERILOG_INCLUDE_DIRS

SYNTH_DEFINES := $(MKDV_VL_DEFINES)
export SYNTH_DEFINES

DESIGN_NAME := $(TOP_MODULE)
export DESIGN_NAME

SRCDIRS = $(sort $(dir $(MKDV_VL_SRCS)) $(dir $(MKDV_VL_INCDIRS)))

OPENLANE_CMD ?= "cd /mkdv_rundir && pwd && ls && flow.tcl -design ./$(TOP_MODULE) -save_path . -save -tag $(TOP_MODULE) -overwrite"

else # Rules

build-openlane :


$(MKDV_RUNDIR)/$(TOP_MODULE)/config.tcl : $(dir $(MKDV_MK))/config.tcl
	mkdir -p `dirname $@`
	cp $^ $@

run-openlane : $(MKDV_RUNDIR)/$(TOP_MODULE)/config.tcl
	docker run -it -v $(OPENLANE_ROOT):/openLANE_flow \
		-v $(PDK_ROOT):$(PDK_ROOT) \
		-v $(MKDV_RUNDIR):/mkdv_rundir \
		$(foreach dir,$(SRCDIRS),-v $(dir):$(dir)) \
		-e PDK_ROOT=$(PDK_ROOT) \
		-e VERILOG_FILES="$(MKDV_VL_SRCS)" \
		-e VERILOG_INCLUDE_DIRS="$(MKDV_VL_INCDIRS)" \
		-e SYNTH_DEFINES="$(MKDV_VL_DEFINES)" \
		$(DOCKER_UID_OPTIONS) \
		$(OPENLANE_IMAGE_NAME) sh -c $(OPENLANE_CMD)

endif
endif

