from uvm import *
from cocotb.triggers import RisingEdge, Timer

class SaDriver(UVMDriver):
    def __init__(self, name, parent):
        super().__init__(name, parent)
        self.dut = None

    def build_phase(self, phase):
        super().build_phase(phase)
        arr = []
        UVMConfigDb.get(self, "", "dut", arr)
        self.dut = arr[0]
        uvm_info("DRV", "build_phase done", UVM_LOW)

    async def run_phase(self, phase):
        uvm_info("DRV", "run_phase started", UVM_LOW)
        # Wait for reset to deassert before driving anything
        from cocotb.triggers import RisingEdge
        while self.dut.rst_n.value == 0:
            await RisingEdge(self.dut.clk)
        uvm_info("DRV", "reset deasserted, ready to drive", UVM_LOW)
        while True:
            item = []
            await self.seq_item_port.get_next_item(item)
            tr = item[0]
            uvm_info("DRV", f"got item weights[0][0]={tr.weights[0][0]}", UVM_LOW)
            # Drive weights
            from sa_if import SaIf
            vif = SaIf(self.dut)
            await vif.drive_weights(tr.weights)
            await Timer(50, "NS")
            await vif.drive_activation(tr.act)
            await Timer(300, "NS")
            self.seq_item_port.item_done()

uvm_component_utils(SaDriver)
