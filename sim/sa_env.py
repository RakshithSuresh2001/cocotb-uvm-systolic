from uvm import *
from sa_driver import SaDriver
from sa_monitor import SaMonitor
from sa_scoreboard import SaScoreboard

class SaEnv(UVMEnv):
    def __init__(self, name, parent):
        super().__init__(name, parent)
        self.seqr    = None
        self.driver  = None
        self.monitor = None
        self.sb      = None

    def build_phase(self, phase):
        super().build_phase(phase)
        self.seqr    = UVMSequencer("seqr", self)
        self.driver  = SaDriver("driver", self)
        self.monitor = SaMonitor("monitor", self)
        self.sb      = SaScoreboard("sb", self)
        uvm_info("ENV", "build_phase done", UVM_LOW)

    def connect_phase(self, phase):
        self.driver.seq_item_port.connect(self.seqr.seq_item_export)
        self.monitor.ap.connect(self.sb.imp)
        uvm_info("ENV", "connect_phase done", UVM_LOW)

uvm_component_utils(SaEnv)
