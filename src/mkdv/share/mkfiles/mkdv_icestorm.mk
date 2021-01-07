
MKDV_AVAILABLE_TOOLS += icestorm

ifeq (icestorm,$(MKDV_TOOL))

ifneq (1,$(RULES))

YOSYS_SYNTH_OPTIONS += -top $(TOP_MODULE)
DEVICE ?= up5k
#DEVICE ?= hx1k

else # Rules

build-icestorm :

icestorm-cmds.do : 
	echo "" > $@
	echo "read_verilog -sv \\" >> $@
	echo "$(foreach inc,$(MKDV_VL_INCDIRS),-I$(inc)) \\" >> $@
	echo "$(foreach def,$(MKDV_VL_DEFINES),-D$(def)) \\" >> $@
	echo "$(foreach src,$(MKDV_VL_SRCS),$(src)) \\" >> $@
	echo "" >> $@
	echo "synth_ice40 -top $(TOP_MODULE) -json $(TOP_MODULE).json -blif $(TOP_MODULE).blif" >> $@
	echo "write_verilog -attr2comment $(TOP_MODULE)_syn.v" >> $@

icestorm-write-syn.do :
	echo "" > $@
	echo "read_blif -wideports $(TOP_MODULE).blif" >> $@
	echo "write_verilog $(TOP_MODULE)_syn.v" >> $@

run-icestorm : icestorm-cmds.do
	yosys -s icestorm-cmds.do
#	yosys -s icestorm-write-syn.do
#	arachne-pnr -d $(subst up,,$(subst hx,,$(subst lp,,$(DEVICE)))) \
#		-o $(TOP_MODULE).asc -p $(TOP_MODULE).blif 
#	yosys -p 'read_blif -wideports $(TOP_MODULE).blif; write_verilog $(TOP_MODULE)_syn.v'
#	arachne-pnr -d $(subst up,,$(subst hx,,$(subst lp,,$(DEVICE)))) \
#		-o $(TOP_MODULE).asc $(TOP_MODULE).blif 
#	nextpnr-ice40 --$(DEVICE) \
#		--asc $(TOP_MODULE).asc --json $(TOP_MODULE).json 
#	icetime -d $(DEVICE) -mtr $(TOP_MODULE).rpt $(TOP_MODULE).asc 
	

endif

endif

