import cocotb
from cocotb.clock import Clock
from cocotb.triggers import RisingEdge
from uvm import *
from sa_test import SaDirectedTest

async def apply_reset(dut):
    dut.rst_n.value = 0
    for _ in range(5):
        await RisingEdge(dut.clk)
    dut.rst_n.value = 1

@cocotb.test()
async def test_dut(dut):
    cocotb.start_soon(Clock(dut.clk, 10, units="ns").start())
    cocotb.start_soon(apply_reset(dut))
    UVMConfigDb.set(None, "*", "dut", dut)
    await run_test("SaDirectedTest")
