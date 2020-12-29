

# Defines

- NEED_TIMESCALE
- HAVE_HDL_CLOCKGEN

# Makefile Variables

These variables are used inside the Makefile system.

- MKDV_TOOL     -- Primary tool to be run
- MKDV_PLUGINS  -- Plug-ins to be used in addition to the primary tool
- MKDV_VL_SRCS  -- Verilog sources
- MKDV_VH_SRCS  -- (Future) VHDL sources
- MKDV_SC_SRCS  -- (Future) SystemC sources
- MKDV_VPI_SRCS -- VPI .c and .cpp files to be compiled by the simulator

- MKDV_VL_INCDIRS
- MKDV_VL_DEFINES

- MKDV_PYTHONPATH       -- List of Python library directories

- MKDV_TIMEOUT          -- Simulation run timeout in ns,us,ms,s

- MKDV_CACHEDIR         -- Tool-specific directory for caching intermediate results
- MKDV_RUNDIR           -- Directory where execution occurs


- Separate build and run?


## Plug-in Variables
- MKDV_AVAIABLE_TOOLS   -- List of available tools 
- MKDV_AVAIABLE_PLUGINS -- List of available plug-ins

# Plug-ins

## cocotb
