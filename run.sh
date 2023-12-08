workload="bfs"

for bench in $workload; do
    echo "Running $bench"
    ./build/ARM/gem5.opt --outdir=$bench+"1.5+bimode+globalsize+32768" ./configs/proj2/two-level.py --bimode --globalsize=32768 --workload=$bench &
done