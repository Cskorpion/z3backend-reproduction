 
import pytest
import z3
import vmprof
from pydrofoil.z3backend import z3backend, z3btypes, z3backend_executor, graph_util
from rpython.rlib.rarithmetic import r_uint 

@pytest.fixture(scope='session')
def riscv_first_shared_state():
    return graph_util.generate_shared_state_riscv64()

@pytest.fixture(scope='function')
def riscvsharedstate(riscv_first_shared_state):
    return riscv_first_shared_state.copy()

###

def _set_init_registers(riscvsharedstate, interp):
    #TODO: do we need xcause and xtvec here?
    interp.registers["zmisa"] = z3backend_executor.get_rv64_usermode_misa_w_value(riscvsharedstate)
    interp.registers["zmstatus"] = z3backend_executor.get_rv64_usermode_mstatus_w_value(riscvsharedstate)
    interp.registers["zsatp"] = z3btypes.ConstantSmallBitVector(0, 64)
    interp.registers["zcur_privilege"] = z3backend_executor.get_rv64_usermode_cur_privilege_w_value(riscvsharedstate)
    interp.registers["zmie"] = z3backend_executor.get_rv64_mie_0_w_value(riscvsharedstate)
    interp.registers["zmip"] = z3backend_executor.get_rv64_mip_0_w_value(riscvsharedstate)
    interp.registers["zmtime"] = z3backend_executor.get_rv64_mtime_0_value(riscvsharedstate)
    interp.registers["zmtimecmp"] =  z3backend_executor.get_rv64_mtimecmp_0_value(riscvsharedstate)
    interp.registers["zmedeleg"] = z3backend_executor.get_rv64_medeleg_0_w_value(riscvsharedstate)

###

import os
BENCHMARK_FILE_ABSTARCT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "abstract_bench.prof")
BENCHMARK_FILE_CONCRETE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "concrete_bench.prof")


def test_bench_thesis_concrete(riscvsharedstate):
    """ decode a concrete RISC-V opcode for profiling (ADD x1, x31, x17)"""
    file = open(BENCHMARK_FILE_CONCRETE, "w+b")

    graph = riscvsharedstate.funcs['zencdec_backwards']
    interp = z3backend.RiscvInterpreter(graph, [z3btypes.ConstantSmallBitVector(0x011f80b3, 32)], riscvsharedstate.copy())
    _set_init_registers(riscvsharedstate, interp)

    vmprof.enable(file.fileno(), period=0.00033, memory=False, native=False)
    instr_ast = interp.run()
    vmprof.disable()
    
    assert isinstance(instr_ast, z3btypes.UnionConstant)
    file.close()
