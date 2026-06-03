from uvm import *
from sa_seq_item import SaSeqItem

COLS = 8

class SaScoreboard(UVMScoreboard):
    def __init__(self, name, parent):
        super().__init__(name, parent)
        self.imp      = None
        self.exp_psum = None   # set by add_expected
        self.passed   = 0
        self.failed   = 0

    def build_phase(self, phase):
        super().build_phase(phase)
        self.imp = UVMAnalysisImp("imp", self)
        uvm_info("SB", "build_phase done", UVM_LOW)

    def add_expected(self, exp_psum):
        self.exp_psum = list(exp_psum)
        uvm_info("SB", f"expected loaded: {self.exp_psum}", UVM_LOW)

    def write(self, tr):
        if self.exp_psum is None:
            uvm_error("SB", "write() called before add_expected()")
            return
        col = tr._col
        got = tr._got
        exp = tr._exp
        if got == exp:
            uvm_info("SB", f"PASS col={col} exp=0x{exp:08x} got=0x{got:08x}", UVM_LOW)
            self.passed += 1
        else:
            uvm_error("SB", f"MISMATCH col={col} exp=0x{exp:08x} got=0x{got:08x}")
            self.failed += 1

    def check_phase(self, phase):
        total = self.passed + self.failed
        if self.failed == 0 and total == COLS:
            uvm_info("SB", f"RESULT: PASS {self.passed}/{total}", UVM_LOW)
        else:
            uvm_error("SB", f"RESULT: FAIL passed={self.passed} failed={self.failed} total={total}")

uvm_component_utils(SaScoreboard)
