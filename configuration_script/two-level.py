import m5
from m5.objects import *
from new_cache import *

from optparse import OptionParser

parser = OptionParser()
parser.add_option("--o3", action="store_true")
parser.add_option("--inorder", action="store_true")
parser.add_option("--cpu_clock", type="string", default="2GHz")
parser.add_option("--ddr3_1600_8x8", action="store_true")
parser.add_option("--ddr3_2133_8x8", action="store_true")
parser.add_option("--ddr4_2400_16x4", action="store_true")
parser.add_option("--ddr4_2400_8x8", action="store_true")
parser.add_option("--lpddr2_s4_1066_1x32", action="store_true")
parser.add_option("--wideio_200_1x128", action="store_true")
parser.add_option("--lpddr3_1600_1x32", action="store_true")
# for parallel
parser.add_option(
    "--workload",
    type="string",
    default="tests/test-progs/hello/bin/arm/linux/hello",
)
(options, args) = parser.parse_args()

root = Root(full_system=False, system=System())
root.system.clk_domain = SrcClockDomain()
root.system.clk_domain.clock = "2GHz"
root.system.clk_domain.voltage_domain = VoltageDomain()

root.system.mem_mode = "timing"
root.system.mem_ranges = [AddrRange("2048MB")]
root.system.mem_ctrl = MemCtrl()
############### modify memory controller ###########################
# root.system.mem_ctrl.dram = DDR4_2400_16x4()
if options.ddr3_1600_8x8:
    root.system.mem_ctrl.dram = DDR3_1600_8x8()
elif options.ddr3_2133_8x8:
    root.system.mem_ctrl.dram = DDR3_2133_8x8()
elif options.ddr4_2400_16x4:
    root.system.mem_ctrl.dram = DDR4_2400_16x4()
elif options.ddr4_2400_8x8:
    root.system.mem_ctrl.dram = DDR4_2400_8x8()
elif options.lpddr2_s4_1066_1x32:
    root.system.mem_ctrl.dram = LPDDR2_S4_1066_1x32()
elif options.wideio_200_1x128:
    root.system.mem_ctrl.dram = WideIO_200_1x128()
elif options.lpddr3_1600_1x32:
    root.system.mem_ctrl.dram = LPDDR3_1600_1x32()
else:
    root.system.mem_ctrl.dram = DDR4_2400_16x4()  # default setting
############### modify memory controller ###########################
root.system.mem_ctrl.dram.range = root.system.mem_ranges[0]


############### modify cpu type ###########################
if options.o3:
    root.system.cpu = DerivO3CPU()
elif options.inorder:
    root.system.cpu = MinorCPU()
else:
    root.system.cpu = TimingSimpleCPU()
############### modify cpu type ###########################

############### add cpu clock domain ###########################
root.system.cpu_clk_domain = SrcClockDomain()
root.system.cpu_clk_domain.clock = options.cpu_clock
root.system.cpu_clk_domain.voltage_domain = VoltageDomain()
root.system.cpu.clk_domain = root.system.cpu_clk_domain
############### add cpu clock domain ##############################

root.system.cpu.icache = L1ICache()
root.system.cpu.dcache = L1DCache()
root.system.l2cache = L2Cache()
root.system.cpu.max_insts_any_thread = (
    1e9  # set maximum instructions as 1 billion
)

root.system.membus = SystemXBar()

root.system.cpu.icache.cpu_side = root.system.cpu.icache_port
root.system.cpu.dcache.cpu_side = root.system.cpu.dcache_port
root.system.l2bus = L2XBar()
root.system.cpu.icache.mem_side = root.system.l2bus.cpu_side_ports
root.system.cpu.dcache.mem_side = root.system.l2bus.cpu_side_ports
root.system.l2cache.cpu_side = root.system.l2bus.mem_side_ports
root.system.l2cache.mem_side = root.system.membus.cpu_side_ports

root.system.mem_ctrl.port = root.system.membus.mem_side_ports
root.system.cpu.createInterruptController()
root.system.system_port = root.system.membus.cpu_side_ports

cmd = {
    "hello": ["tests/test-progs/hello/bin/arm/linux/hello"],
    "2mm_base": ["test_bench/2MM/2mm_base"],
    "bfs": ["test_bench/BFS/bfs", "-f", "test_bench/BFS/USA-road-d.NY.gr"],
    "bzip2": [
        "test_bench/bzip2/bzip2_base.amd64-m64-gcc42-nn",
        "test_bench/bzip2/input.source",
        "280",
    ],
    "mcf": [
        "test_bench/mcf/mcf_base.amd64-m64-gcc42-nn",
        "test_bench/mcf/inp.in",
    ],
}

exe = {
    "hello": "tests/test-progs/hello/bin/arm/linux/hello",
    "2mm_base": "test_bench/2MM/2mm_base",
    "bfs": "test_bench/BFS/bfs",
    "bzip2": "test_bench/bzip2/bzip2_base.amd64-m64-gcc42-nn",
    "mcf": "test_bench/mcf/mcf_base.amd64-m64-gcc42-nn",
}

exe_path = exe[options.workload]
root.system.workload = SEWorkload.init_compatible(exe_path)

process = Process()
process.cmd = cmd[options.workload]
root.system.cpu.workload = process
root.system.cpu.createThreads()

m5.instantiate()
exit_event = m5.simulate()
print(
    "Exiting @ tick {} because {}".format(m5.curTick(), exit_event.getCause())
)
