# sa_seq_item.py — One transaction = one full weight load + one activation.
import random
from uvm.seq import UVMSequenceItem
from uvm.macros import uvm_object_utils

ROWS = 8
COLS = 8
DATA_W = 8

@uvm_object_utils
class SaSeqItem(UVMSequenceItem):
    def __init__(self, name="SaSeqItem"):
        super().__init__(name)
        self.weights = [[0]*COLS for _ in range(ROWS)]
        self.act     = [0]*ROWS
        self.exp_psum = [0]*COLS  # filled by ref model

    def randomize(self):
        """Constrained random: signed 8-bit weights and activations."""
        for r in range(ROWS):
            for c in range(COLS):
                self.weights[r][c] = random.randint(-128, 127)
        for r in range(ROWS):
            self.act[r] = random.randint(-128, 127)
        return self

    def compute_expected(self):
        """Reference model: C[col] = sum over rows of weight[row][col]*act[row]."""
        for col in range(COLS):
            acc = 0
            for row in range(ROWS):
                acc += self.weights[row][col] * self.act[row]
            # Truncate to 32-bit signed to match RTL
            acc = acc & 0xFFFFFFFF
            self.exp_psum[col] = acc
        return self.exp_psum

    def __str__(self):
        return f"SaSeqItem weights[0]={self.weights[0]} act={self.act} exp={self.exp_psum}"
