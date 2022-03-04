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
OPENLANE_SRCDIRS += $(dir $(MKDV_LEF_FILES))
OPENLANE_SRCDIRS += $(dir $(MKDV_GDS_FILES))
OPENLANE_SRCDIRS += $(MKDV_VL_INCDIRS)
OPENLANE_SRCDIRS += $(abspath $(dir $(MKDV_MK)))

SRCDIRS = $(sort $(OPENLANE_SRCDIRS))

OPENLANE_CMD ?= "cd /mkdv_rundir && pwd && ls && flow.tcl -design ./$(TOP_MODULE) -save_path . -save -tag $(TOP_MODULE) -overwrite"

OPENLANE_ENV += -e PDK_ROOT=$(PDK_ROOT)
OPENLANE_ENV +=	-e DESIGN_NAME=$(TOP_MODULE)
OPENLANE_ENV +=	-e SYNTH_DIR=$(abspath $(dir $(MKDV_MK)))
OPENLANE_ENV +=	-e VERILOG_FILES="$(MKDV_VL_SRCS)"
OPENLANE_ENV +=	-e VERILOG_FILES_BLACKBOX="$(MKDV_VL_SRCS_BB)" 
OPENLANE_ENV +=	-e VERILOG_INCLUDE_DIRS="$(MKDV_VL_INCDIRS)"
OPENLANE_ENV +=	-e SYNTH_DEFINES="$(MKDV_VL_DEFINES)"

# Openlane is picky about these environment variables. 
# If they're set (even to empty values), macro placement
# will be attempted. This will error out if the value
# is an empty string
ifneq (,$(MKDV_LEF_FILES))
OPENLANE_ENV +=	-e EXTRA_LEFS="$(MKDV_LEF_FILES)"
endif
ifneq (,$(MKDV_GDS_FILES))
OPENLANE_ENV +=	-e EXTRA_GDS_FILES="$(MKDV_GDS_FILES)"
endif

MKDV_POST_RUN_TARGETS += openlane-copy-results

else # Rules


build-openlane : $(MKDV_BUILD_DEPS)


$(MKDV_RUNDIR)/$(TOP_MODULE)/config.tcl : $(dir $(MKDV_MK))/config.tcl
	mkdir -p `dirname $@`
	cp $^ $@

run-openlane : $(MKDV_RUNDIR)/$(TOP_MODULE)/config.tcl $(MKDV_RUN_DEPS)
ifeq (,$(TOP_MODULE))
	@echo "Error: TOP_MODULE not set"; exit 1
endif
	cd $(OPENLANE_ROOT) && \
	docker run -it -v $(OPENLANE_ROOT):/openLANE_flow \
		-v $(PDK_ROOT):$(PDK_ROOT) \
		-v $(MKDV_RUNDIR):/mkdv_rundir \
		$(foreach dir,$(sort $(abspath $(SRCDIRS))),-v $(dir):$(dir)) \
		$(OPENLANE_ENV) \
		$(DOCKER_UID_OPTIONS) \
		$(OPENLANE_IMAGE_NAME) sh -c $(OPENLANE_CMD)
		
openlane-copy-results :
ifeq (,$(MKDV_OPENLANE_DESTDIR))
	$(Q)echo "Note: Not copying artifacts, since MKDV_OPENLANE_DESTDIR not set"
else
	$(Q)mkdir -p $(MKDV_OPENLANE_DESTDIR)/gds
	$(Q)mkdir -p $(MKDV_OPENLANE_DESTDIR)/lef
	$(Q)mkdir -p $(MKDV_OPENLANE_DESTDIR)/mag
	$(Q)mkdir -p $(MKDV_OPENLANE_DESTDIR)/verilog/gl
	$(Q)cp $(MKDV_RUNDIR)/gds/$(TOP_MODULE).gds $(MKDV_OPENLANE_DESTDIR)/gds
	$(Q)cp $(MKDV_RUNDIR)/lef/$(TOP_MODULE).lef $(MKDV_OPENLANE_DESTDIR)/lef
	$(Q)cp $(MKDV_RUNDIR)/mag/$(TOP_MODULE).mag $(MKDV_OPENLANE_DESTDIR)/mag
	$(Q)cp $(MKDV_RUNDIR)/verilog/gl/$(TOP_MODULE).v $(MKDV_OPENLANE_DESTDIR)/verilog/gl
endif

endif
endif

