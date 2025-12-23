import archinfo, angr, time, logging
#from generate import gen_rv64_code_names

logging.getLogger('angr').setLevel('FATAL')

#  generating code requires a special PyPy installation  #
#code = gen_rv64_code_names(512, False)
#flatcode  = []
#for typ in code:
#    for instr in code[typ]:
#        flatcode.append((typ, instr))

#with open("benchmark_opcodes_names.txt", "w") as outfile:
#     for typ_and_instr in flatcode:
#        outfile.write("%s\n" % str(typ_and_instr))

instr_tuples = []
with open("benchmark_opcodes_names.txt", "r") as infile:
    for typ_and_instr in infile:
        instr_tuples.append(typ_and_instr)

print("loaded instructions from disk")

code = {}
for line in instr_tuples:
    parts = line[1:-2].split(",", 1)
    typ, instr = parts[0], int(parts[1])
    if typ not in code:
        code[typ] = [instr]
    else:
        code[typ].append(instr)
    #code.append(int(parts[0]))

print("finished preprocessing of instructions")
print("executing with angr")

arch = archinfo.ArchRISCV64()

times = {}

for typ in code:
    times[typ] = []
    for _ in range(10):

        start = time.time()
        for instr in code[typ]:

            codesize = 4 if instr & 0b11 == 0b11 else 2
            byte_mc_code = instr.to_bytes(codesize, byteorder="little")

            project = angr.load_shellcode(byte_mc_code, arch=arch, start_offset=0,
                                        load_address=0, selfmodifying_code=True)
            entry_state = project.factory.entry_state()
            simulation = project.factory.simulation_manager(entry_state)

            simulation = simulation.step()

            activestate = simulation.active[0]
            assert getattr(activestate.regs, "x17") != None

        duration = time.time() - start
        times[typ].append(duration)

        print("angr execution of %d RISC-V %s instructions took %s seconds" % (len(code[typ]), typ, str(duration)))

for typ in code:
    print("%d-times-avg. angr execution of %d RISC-V %s instructions took %s seconds" % (len(times[typ]), len(code[typ]), typ, str(sum(times[typ])/len(times[typ]))))

with open("benchmark_angr_times.txt", "w") as outfile:
    for typ in code:
        outfile.write("====%s====\n" % typ)
        outfile.write("instruction count: %d\n" % len(code[typ]))
        outfile.write("%d-times-avg. angr execution %s\n" % (len(times[typ]), str(sum(times[typ])/len(times[typ]))))
        outfile.write("instructions: %s\n" % str(code[typ]))
        outfile.write("  \n")