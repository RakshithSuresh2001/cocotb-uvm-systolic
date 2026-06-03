from uvm import *
from cocotb.triggers import RisingEdge, Timer
from sa_seq_item import SaSeqItem

COLS = 8
ROWS = 8
PE_LAT   = 4
# col[k] peaks at base_cycle + k due to horizontal skew
COL_SKEW = 1

class SaMonitor(UVMMonitor):
    def __init__(self, name, parent):
        super().__init__(name, parent)
        self.ap      = None
        self.dut     = None
        self.pending = []  # list of (base_act_cycle, exp_psum)

    def build_phase(self, phase):
        super().build_phase(phase)
        self.ap = UVMAnalysisPort("ap", self)
        arr = []
        UVMConfigDb.get(self, "", "dut", arr)
        self.dut = arr[0]
        uvm_info("MON", "build_phase done", UVM_LOW)

    def schedule_sample(self, act_cycle, exp_psum):
        """act_cycle = cycle when first activation was driven."""
        self.pending.append((act_cycle, list(exp_psum)))
        uvm_info("MON", f"scheduled sample base_act_cycle={act_cycle}", UVM_LOW)

    async def run_phase(self, phase):
        uvm_info("MON", "run_phase started", UVM_LOW)
        cycle = 0
        # col[k] peak = act_cycle + ROWS(acc) + 2(input regs) + k(skew) + 2(output regs) - 1
        # From raw calibration: act starts cycle 19, col[0] peaks cycle 30 → offset=11
        # col[k] peaks at act_cycle + 11 + k
        BASE_OFFSET = 11   # calibrated from raw test
        while True:
            await RisingEdge(self.dut.clk)
            await Timer(1, "NS")
            cycle += 1
            for entry_idx, (act_cycle, exp_psum) in enumerate(self.pending):
                raw = self.dut.psum_out.value.integer
                for col in range(COLS):
                    peak_cycle = act_cycle + BASE_OFFSET + col
                    if cycle == peak_cycle:
                        got = (raw >> (col * 32)) & 0xFFFFFFFF
                        uvm_info("MON", f"sampled col={col} cycle={cycle} got={got} exp={exp_psum[col]}", UVM_LOW)
                        tr = SaSeqItem(f"mon_tr_col{col}")
                        tr.exp_psum = [0] * COLS
                        tr.exp_psum[col] = got
                        # Pack col index into item so scoreboard knows which col
                        tr._col   = col
                        tr._got   = got
                        tr._exp   = exp_psum[col]
                        self.ap.write(tr)
                # Remove entry after all cols sampled
                if cycle == act_cycle + BASE_OFFSET + COLS - 1:
                    self.pending.pop(entry_idx)
                    break

uvm_component_utils(SaMonitor)
