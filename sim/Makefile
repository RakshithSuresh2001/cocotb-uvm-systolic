# Cocotb + Verilator Makefile for Systolic Array UVM TB
TOPLEVEL_LANG = verilog
VERILOG_SOURCES = $(shell pwd)/../rtl/pe.sv \
                  $(shell pwd)/../rtl/systolic_array.sv
TOPLEVEL = systolic_array
MODULE   = tb_systolic

SIM = verilator
EXTRA_ARGS += --trace --trace-structs

include $(shell cocotb-config --makefiles)/Makefile.sim
