# cocotb-uvm-systolic

A Python UVM testbench for an 8x8 weight-stationary systolic array, built with uvm-python 0.4.0 and cocotb 1.9.1 running under Verilator 5.020. This is a separate project from the SystemVerilog UVM-style testbench in [uvm_systolic](https://github.com/RakshithSuresh2001/uvm_systolic) — the goal here is a proper UVM architecture in Python, with a sequencer, driver, monitor, scoreboard, and analysis port all wired up correctly.

## Stack

| Tool | Version |
|---|---|
| uvm-python | 0.4.0 |
| cocotb | 1.9.1 |
| Verilator | 5.020 |
| Python | 3.12 |
| OS | Ubuntu 22.04 (WSL2) |

> uvm-python 0.4.0 is incompatible with cocotb 2.x. Pin cocotb to 1.9.1.

## DUT

An 8x8 weight-stationary systolic array with 64 registered MAC processing elements. Activations travel horizontally left to right, partial sums accumulate vertically top to bottom. There are two input pipeline registers before the array and two output pipeline registers after it.

The array accumulates both spatially and temporally. Each column's output is the dot product of its weight column with the activation vector, but because every PE stage is registered, you need to drive activation for ROWS consecutive cycles to fill the pipeline and get the full accumulation. Each column also peaks one cycle later than the previous due to the registered horizontal activation chain.

```
act_in[0..7] ──► [PE00][PE01]...[PE07] ──► (discarded)
                 [PE10][PE11]...[PE17]
                  ...
                 [PE70][PE71]...[PE77]
                    ↓    ↓         ↓
              psum[0] psum[1] ... psum[7]
```

Weight loading is serial: one row per cycle via `weight_load`, `weight_row`, and `weight_data`. Reset is active-low (`rst_n`).

## UVM Architecture

```
sim/
├── tb_systolic.py    — cocotb entry point, clock gen, reset, run_test()
├── sa_env.py         — SaEnv: instantiates and connects all UVM components
├── sa_test.py        — SaDirectedTest + SaDirectedSeq
├── sa_driver.py      — SaDriver: gets items from sequencer, drives DUT via SaIf
├── sa_monitor.py     — SaMonitor: samples psum per column at each column's peak cycle
├── sa_scoreboard.py  — SaScoreboard: compares per column, reports pass/fail
├── sa_seq_item.py    — SaSeqItem: weights[8][8], act[8], exp_psum[8], reference model
└── sa_if.py          — SaIf: drive_weights(), drive_activation(), sample_psum()
```

The monitor accounts for per-column skew: `col[k]` is sampled at `act_cycle + BASE_OFFSET + k`, where `BASE_OFFSET = 11` (2 input regs + 8 PE rows + 2 output regs, minus 1 for zero-indexing). Monitor and scoreboard refs are passed to sequences via `UVMConfigDb` rather than direct attribute assignment, which is the standard UVM pattern and avoids attribute loss during `seq.start()`.

## Timing Model

```
Reset:          5 cycles
Weight load:    8 cycles (one row per cycle, rst_n must be high)
Idle gap:       5 cycles (Timer 50ns)
Activation:     8 cycles (ROWS cycles for full temporal accumulation)
col[0] peak:    act_start + 11 cycles
col[k] peak:    act_start + 11 + k cycles
```

## Results

```
Directed test (all-ones weights, all-ones activation):
  col[0]: exp=0x00000008  got=0x00000008  PASS
  col[1]: exp=0x00000008  got=0x00000008  PASS
  col[2]: exp=0x00000008  got=0x00000008  PASS
  col[3]: exp=0x00000008  got=0x00000008  PASS
  col[4]: exp=0x00000008  got=0x00000008  PASS
  col[5]: exp=0x00000008  got=0x00000008  PASS
  col[6]: exp=0x00000008  got=0x00000008  PASS
  col[7]: exp=0x00000008  got=0x00000008  PASS
  RESULT: PASS 8/8
```

## Running

```bash
cd sim
make
```

Requires uvm-python 0.4.0 and cocotb 1.9.1:

```bash
pip install cocotb==1.9.1 uvm-python==0.4.0
```

## Key Implementation Notes

**run_test() at time 0.** uvm-python requires `run_test()` to be called at simulation time 0. Reset is handled by a concurrent coroutine launched with `cocotb.start_soon()` so the UVM startup sequence is not delayed.

**Driver waits for reset.** The driver polls `rst_n` before pulling items from the sequencer. Weight loading during reset silently discards into flip-flops that get cleared, so this guard is necessary.

**Per-column sampling.** The monitor does not sample all columns at once. Each column has its own peak cycle due to the 1-cycle-per-column horizontal skew, so the monitor schedules 8 separate sample points per transaction and sends one analysis transaction per column.

**False-pass prevention.** UVM error count is checked in `report_phase` via `UVMReportServer.get_server().get_severity_count(UVM_ERROR)` and raises a cocotb `TestFailure` if nonzero, so a UVM scoreboard failure correctly propagates to a cocotb FAIL.

## Related Projects

- [uvm_systolic](https://github.com/RakshithSuresh2001/uvm_systolic): SystemVerilog UVM-style testbench for the same DUT, 1337/1337 checks, 15/15 coverage bins, 5 SVA properties
- [PicoRISCV-SoC](https://github.com/RakshithSuresh2001/PicoRISCV-SoC): PicoRV32 core integrated with this systolic array over AXI-Lite, implemented RTL-to-GDS on ASAP7 at 500 MHz
- [Systolic-Array](https://github.com/RakshithSuresh2001/Systolic-Array): Standalone systolic array submitted to the ChipFoundry CI2609 Sky130 shuttle

## Author

Rakshith Suresh, MS Electrical Engineering, USC Viterbi School of Engineering
[GitHub](https://github.com/RakshithSuresh2001) | [LinkedIn](https://linkedin.com/in/rakshith-suresh-890329258/)
