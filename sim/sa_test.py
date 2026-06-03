import cocotb
from uvm import *
from sa_seq_item import SaSeqItem
from sa_env import SaEnv

PE_LAT       = 4
COLS         = 8
ACT_CYCLE    = 19
SAMPLE_CYCLE = ACT_CYCLE + PE_LAT + COLS - 1   # 30


class SaDirectedSeq(UVMSequence):
    def __init__(self, name="SaDirectedSeq"):
        super().__init__(name)

    async def body(self):
        arr = []
        if not UVMConfigDb.get(None, "", "mon", arr):
            uvm_fatal("SEQ", "Could not get monitor from ConfigDb")
        mon = arr[0]

        arr2 = []
        if not UVMConfigDb.get(None, "", "sb", arr2):
            uvm_fatal("SEQ", "Could not get scoreboard from ConfigDb")
        sb = arr2[0]

        item = SaSeqItem("item")
        await self.start_item(item)

        for r in range(8):
            for c in range(8):
                item.weights[r][c] = 1
        item.act = [1] * 8
        item.compute_expected()

        cocotb.log.info(f"[SEQ] exp[0]={item.exp_psum[0]}  sample_cycle={SAMPLE_CYCLE}")
        cocotb.log.info(f"[SEQ] mon ref = {mon}")

        sb.add_expected(item.exp_psum[:])
        mon.schedule_sample(ACT_CYCLE, item.exp_psum[:])
        cocotb.log.info("[SEQ] schedule_sample called")

        await self.finish_item(item)


uvm_component_utils(SaDirectedSeq)


class SaDirectedTest(UVMTest):
    def __init__(self, name="SaDirectedTest", parent=None):
        super().__init__(name, parent)
        self.env = None

    def build_phase(self, phase):
        super().build_phase(phase)
        self.env = SaEnv("env", self)

    def connect_phase(self, phase):
        UVMConfigDb.set(None, "", "mon", self.env.monitor)
        UVMConfigDb.set(None, "", "sb",  self.env.sb)

    async def run_phase(self, phase):
        phase.raise_objection(self)
        seq = SaDirectedSeq("directed_seq")
        await seq.start(self.env.seqr)
        await Timer(200, "ns")
        phase.drop_objection(self)

    def report_phase(self, phase):
        from uvm.base.uvm_report_server import UVMReportServer
        server = UVMReportServer.get_server()
        count = server.get_severity_count(UVM_ERROR)
        if count > 0:
            import cocotb
            raise cocotb.result.TestFailure(f"UVM reported {count} UVM_ERROR(s)")


uvm_component_utils(SaDirectedTest)
