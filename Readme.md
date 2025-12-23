# Installing Pydrofoil

- Install the dependecies for Pydrofoil
    - https://docs.pydrofoil.org/en/latest/building_pydrofoil.html
- clone the Sail-RISC-V repository
    - `git clone https://github.com/riscv/sail-riscv.git`
- go into sail-riscv folder
    - `cd sail-riscv`
- clone the Pydrofoil z3_backend branch 
    - `git clone -b z3_backend https://github.com/pydrofoil/pydrofoil`
- go into pydrofoil folder
    - `cd pydrofoil`
- run 
    - `make`
- optional run test to see if everything worked out
    - `./pypy_binary/bin/pypy pypy2/pytest.py -vv -s --pdb riscv/test/test_z3riscvexecutor.py -k test_z3backend_clz_x5_x6`

# Tests and Fuzzing

## Running z3backend (generic or Nand2Tetris) tests

- `./pypy_binary/bin/pypy pypy2/pytest.py -vv -s --pdb pydrofoil/z3backend/test`
- -vv -s --pdb optional

## Running z3backend RISC-V tests

- `./pypy_binary/bin/pypy pypy2/pytest.py -vv -s --pdb riscv/test/test_z3riscv.py`
- or riscv/test/test_z3riscvoperations.py
- or riscv/test/test_z3riscvknownbits.py

## Fuzzing angr or VexingZ3 with the z3backend

## Installation

- Download PyPy3 with Pydrofoil extension 
    - https://github.com/pydrofoil/pydrofoil/actions/workflows/plugin.yml
    - look for the last successfull run
    - download the artifact
    - extract PyPy from the zip
- set env var 'PYDROFOILHYPOTHESIS' to that PyPy3 executable
    - needed for calling the Python3 from Python2 via subprocess
- If you want to test angr: install angr-z3-converter
    - `git clone https://github.com/Cskorpion/angr-z3-converter`
    - install package in that PYDROFOILHYPOTHESIS PyPy3 
- If you want to test VexingZ3: https://github.com/cfbolz/vexingz3
    - install package in that PYDROFOILHYPOTHESIS PyPy3

- Types of generated instructions configurable by setting allowed and disallowed instruction types in angr-z3-converter/generate/pydrofoil_hypothesis.py

### Testing angr (VEX) is done via the test files: 

- test_z3riscvexecutor.py and test_z3riscvregression.py 
- for executing random instructions against angr run:
    - `./pypy_binary/bin/pypy pypy2/pytest.py -vv -s --pdb riscv/test/test_z3riscvexecutor.py -k test_gen_code_run_angr_vex_all_types`
- That tests generates 128 random opcodes, executes them on angr and the z3backend and compares the x1-x31 registers with the Z3-Solver
- If some comparison fails failing register comparison will be printed to console

### Testing angr (SLEIGH) is done via the test files: 

- test_z3riscvexecutor.py and test_z3riscvregression.py 
- install pypcode in PYDROFOILHYPOTHESIS
    - `PYDROFOILHYPOTHESIS -m pip install pypcode`
- for executing random instructions against angr run:
    - `./pypy_binary/bin/pypy pypy2/pytest.py -vv -s --pdb riscv/test/test_z3riscvexecutor.py -k test_gen_code_run_angr_pypcode_all_types`

### Testing VEX via vexingz3 

- for executing random instructions against vexingz3 run:
    - `./pypy_binary/bin/pypy pypy2/pytest.py -vv -s --pdb riscv/test/test_z3riscvexecutor.py -k test_gen_code_run_vexingz3_all_types`

### Testing with more than one CPU core

- As the z3backend runs on Python 2 there is no real multicore execution possible via threads
- start multiple processes running the fuzzing tests
- I recommend having at least 1 GB free RAM per process started   
    - 2 GB when using SLEIGH/pypcode

# Profiling 

##  Installation

- Install VMProf
    - `./pypy_binary/bin/pypy -m pip install vmprof`
- If profiles shall be visualized install the vmprof-firefox-converter on any Python 3 install
    - `python -m pip install vmprof-firefox-converter`
- Profiles in the thesis were created using the z3backend versions:
-  with_unned_reg_init: https://github.com/pydrofoil/pydrofoil/commit/a3664d7ecb3e79e820ac7e04c973a92e20e81ce3 
-  without_unned_reg_init: https://github.com/pydrofoil/pydrofoil/commit/14aee24f54b833fb394c8690c945eb6360566b00

##  Running Profiling
- Profiles created using the profiling_tests/test_z3riscvprofile.py test
-  configure Profile file in test_z3riscvprofile.py
-  place in pydrofoil/riscv/test and run:
-  ./pypy_binary/bin/pypy pypy2/pytest.py -vv -s --pdb riscv/test/test_z3riscvprofile.py 
- Convert profiles using the vmprof-firefox-converter
    -  `python -m vmprofconvert -convert path/to/your/profile.prof`


# Execution Times Comparison

## angr
- place benchmark_angr/run_bench_thesis.py and benchmark_opcodes_names.txt in angr-z3-converter/ folder
- run run_bench_thesis.py:
    - `PYDROFOILHYPOTHESIS run_bench_thesis.py`

## angr
- place benchmark_z3backend/test_z3riscvbenchmark.py and benchmark_opcodes_names.txt in pydrofoil/riscv/test/ folder
- run test_z3riscvbenchmark:
    - `./pypy_binary/bin/pypy pypy2/pytest.py -vv -s --pdb riscv/test/test_z3riscvbenchmark.py`

# Used Hardware
- All tests, benchmarks, and profiles executed on an AMD Ryzen 7 5700u, 24GB DDR4 3200mhz (dual channel), Kubuntu 24.04
- Execution Times Comparison done on internal NVME SSD
- Profiling done on an USB-SATA SSD.

