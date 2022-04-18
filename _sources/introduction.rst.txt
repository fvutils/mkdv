############
Introduction
############

What is MKDV?
==============

MKDV is a framework for organizing, running, and reporting jobs
in Design and Verification (DV) workflows. While MKDV can be 
used to run other types of jobs, such as tests in a regression
suite for a software tool, its primary focus is on DV flows.

As its name suggests, MKDV leverages Makefiles for specifying
lowest-level flow commands. MKDV's upper-level infrastructure
is written in Python.


Key Features
============

Tools and Methodologies
-----------------------
MKDV provides out-of-box support for running the following tools:


HDL Simulators
^^^^^^^^^^^^^^
- Siemens Questa
- Icarus Verilog
- Verilator

Synthesis Tools
^^^^^^^^^^^^^^^
- Project Icestorm (targets iCE40 devices)
- Intel Quartus

ASIC Flows
^^^^^^^^^^
- OpenRoad Openlane


Methodologies
^^^^^^^^^^^^^
- cocotb 
- pybfms

New tools and tool add-ons (plug-ins) are added using Makefile fragments. 
These can either be addded to the MKDV distribution or kept local to a
site or project.


Parallel execution
------------------
Currently, MKDV supports running parallel jobs on the local machine.
In the future, support for external job managers (eg LSF, SLURM, etc) 
will be added.

Results viewing
---------------

MKDV is integrated with the `Allure <https://docs.qameta.io/allure/>`_
reporting framework, enabling regression results to be easily viewed.

.. figure:: images/Allure.PNG
  :align: center
  
  Regression result displayed with Allure.

        




Contributors
============

.. spelling::
   Ballance

