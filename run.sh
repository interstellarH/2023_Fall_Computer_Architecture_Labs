workload="2mm_base bfs bzip2 mcf"

for bench in $workload; do
    echo "Running $bench"
    ./build/ARM/gem5.opt --outdir=$bench+"2rd+ddr4_2400_16x4" ./configuration_script/two-level.py --cpu_clock=1.8GHz --ddr4_2400_16x4 --workload=$bench &
done