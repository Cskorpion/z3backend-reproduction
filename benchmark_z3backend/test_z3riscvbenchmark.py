import z3, pytest, time
from pydrofoil.z3backend import z3backend, z3btypes, z3backend_executor, graph_util
from rpython.rlib.rarithmetic import r_uint 


def _set_init_registers(riscvsharedstate, interp):
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

instr_tuples = []
with open("riscv/test/benchmark_opcodes_names.txt", "r") as infile:
    for typ_and_instr in infile:
        instr_tuples.append(typ_and_instr)

print("loaded instructions from disk")

code = {}
for line in instr_tuples:
    parts = line[1:-2].split(",", 1)
    typ, instr = parts[0], int(parts[1])
    if typ not in code:
        code[typ] = [z3btypes.ConstantSmallBitVector(int(instr), 32)]
    else:
        code[typ].append(z3btypes.ConstantSmallBitVector(int(instr), 32))


print("finished preprocessing of instructions")
print("executing with the z3backend")

riscvsharedstate = graph_util.generate_shared_state_riscv64()
graph_decode = riscvsharedstate.funcs['zencdec_backwards']
graph_decode_compressed = riscvsharedstate.funcs['zencdec_compressed_backwards']
graph_execute = riscvsharedstate.mthds["zexecute"]

times = {}

for typ in code:
    times[typ] = []
    for _ in range(10):

        start = time.time()
        for instr in code[typ]:
            decode_graph = graph_decode if instr.value & 0b11 == 0b11 else graph_decode_compressed

            interp_dec = z3backend.RiscvInterpreter(decode_graph, [instr], riscvsharedstate.copy())
            _set_init_registers(riscvsharedstate, interp_dec)
            interp_dec.set_verbosity(0)
            instruction_struct = interp_dec.run()

            interp_exc = z3backend.RiscvInterpreter(graph_decode, [instruction_struct], riscvsharedstate.copy())
            interp_exc.set_verbosity(0)
            # hack: cannot use method graphs to run, so do explicit method call
            # Interp must still be initialized though
            interp_exc._concrete_method_call(graph_execute, [instruction_struct])

            assert interp_exc.registers["zx17"] is not None
        
        duration = time.time() - start
        times[typ].append(duration)
                    
        print("z3backend execution of %d RISC-V %s instructions took %s seconds" % (len(code[typ]), typ, str(duration)))

for typ in code:
    print("%d-times-avg. angr execution of %d RISC-V %s instructions took %s seconds" % (len(times[typ]), len(code[typ]), typ, str(sum(times[typ])/len(times[typ]))))

with open("riscv/test/benchmark_z3b_times.txt", "w") as outfile:
    for typ in code:
        outfile.write("====%s====\n" % typ)
        outfile.write("instruction count: %d\n" % len(code[typ]))
        outfile.write("%d-times-avg. z3b execution %s\n" % (len(times[typ]), str(sum(times[typ])/len(times[typ]))))
        outfile.write("instructions: %s\n" % str(code[typ]))
        outfile.write("  \n")