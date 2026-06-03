# sa_if.py — Virtual interface wrapper around the cocotb DUT handle.
# Centralises all signal-level access so driver and monitor never
# touch dut directly — mirrors the sv virtual interface pattern.

from cocotb.triggers import RisingEdge, Timer

ROWS = 8
COLS = 8

class SaIf:
    def __init__(self, dut):
        self.dut = dut

    async def wait_clk(self):
        await RisingEdge(self.dut.clk)

    async def drive_weights(self, weights):
        """Load an 8x8 weight matrix, one row per cycle."""
        import cocotb
        for row in range(ROWS):
            self.dut.weight_load.value = 1
            self.dut.weight_row.value  = row
            row_val = 0
            for col in range(COLS):
                row_val |= (int(weights[row][col]) & 0xFF) << (col * 8)
            self.dut.weight_data.value = row_val
            cocotb.log.info(f"[IF] loading row={row} row_val=0x{row_val:016x} rst_n={self.dut.rst_n.value}")
            await self.wait_clk()
        self.dut.weight_load.value = 0
        self.dut.weight_data.value = 0

    async def drive_activation(self, act_vec):
        """Drive activation for ROWS cycles — temporal accumulation."""
        val = 0
        for r in range(ROWS):
            val |= (int(act_vec[r]) & 0xFF) << (r * 8)
        self.dut.act_in.value = val
        for _ in range(ROWS):
            await self.wait_clk()
        self.dut.act_in.value = 0

    def sample_psum(self):
        """Read current psum_out as a list of COLS 32-bit values."""
        raw = self.dut.psum_out.value.integer
        return [(raw >> (c * 32)) & 0xFFFFFFFF for c in range(COLS)]
