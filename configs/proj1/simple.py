import m5
from m5.objects import *

root = Root(full_system=False, system=System())
root.full_system = False
root.system = System()

root.system.clk_domain = SrcClockDomain()
root.system.clk_domain.clock = "2GHz"
root.system.clk_domain.voltage_domain = VoltageDomain()

root.system.mem_mode = "timing"
root.system.mem_ranges = [AddrRange("2GB")]
root.system.mem_ctrl = MemCtrl()
root.system.mem_ctrl.dram = DDR4_2400_16x4()
root.system.mem_ctrl.dram.range = root.system.mem_ranges[0]

root.system.cpu = TimingSimpleCPU()
root.system.membus = SystemXBar()

root.system.cpu.icache_port = root.system.membus.cpu_side_ports
root.system.cpu.dcache_port = root.system.membus.cpu_side_ports
root.system.mem_ctrl.port = root.system.membus.mem_side_ports
root.system.cpu.createInterruptController()
root.system.system_port = root.system.membus.cpu_side_ports
# root.system.cpu.interrupts[0].pio = system.membus.mem_side_ports
# root.system.cpu.interrupts[0].int_requestor = system.membus.cpu_side_ports
# root.system.cpu.interrupts[0].int_responder = system.membus.mem_side_ports

exe_path = "tests/test-progs/hello/bin/arm/linux/hello"
root.system.workload = SEWorkload.init_compatible(exe_path)
process = Process()
process.cmd = [exe_path]
root.system.cpu.workload = process
root.system.cpu.createThreads()

m5.instantiate()
exit_event = m5.simulate()
print(
    "Exiting @ tick {} because {}".format(m5.curTick(), exit_event.getCause())
)
