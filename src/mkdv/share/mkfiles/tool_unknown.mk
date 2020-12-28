#****************************************************************************
#* tool_unknown.mk
#*
#* Backstop include file to present mk options
#****************************************************************************

ifneq (1,$(RULES))


else # Rules

build :
	echo "Error: TOOL unspecified"
	exit 1

run-unknown : 
	echo "Error: TOOL unspecified"
	exit 1

clean-unknown:
	# nop

help-unknown: help-all

endif

