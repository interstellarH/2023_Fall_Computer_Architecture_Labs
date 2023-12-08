/* @file
 * Implementation of a perceptron branch predictor
 */

#ifndef __CPU_PRED_PERCEPTRON_PRED_HH__
#define __CPU_PRED_PERCEPTRON_PRED_HH__

#include "base/sat_counter.hh"
#include "cpu/pred/bpred_unit.hh"
#include "params/PerceptronBP.hh"

namespace gem5
{

namespace branch_prediction
{

class Perceptron //table of perceptrons
{
  public:
    std::vector<int> weight; //之前把weight的类型写成了unsigned int导致错误
    Perceptron(unsigned int size):weight(size, 0)
    {};
};


class PerceptronBP : public BPredUnit
{
  public:
    PerceptronBP(const PerceptronBPParams &params);
    void uncondBranch(ThreadID tid, Addr pc, void * &bp_history);
    void squash(ThreadID tid, void *bp_history);
    bool lookup(ThreadID tid, Addr branch_addr, void * &bp_history);
    void btbUpdate(ThreadID tid, Addr branch_addr, void * &bp_history);
    void update(ThreadID tid, Addr branch_addr, bool taken, void *bp_history,
                bool squashed, const StaticInstPtr & inst, Addr corrTarget);
    

  private:
    void updateGlobalHistReg(ThreadID tid, bool taken);

    struct BPHistory
    {
        unsigned long globalHistoryReg;
        // was the taken array's prediction used?
        // true: takenPred used
        // false: notPred used
        unsigned long y; // 不是bool，而是一个整数，是计算结果！
        bool finalPred;
    };

    std::vector<unsigned long> globalHistoryReg;
    unsigned long globalHistoryBits;
    unsigned long historyRegisterMask;
    unsigned long globalPredictorSize;
    unsigned long globalCtrBits;
    unsigned long globalHistoryMask;
    unsigned long threshold;

    std::vector<Perceptron> ToP; //table of perceptrons

    unsigned long Threshold;
};

} // namespace branch_prediction
} // namespace gem5

#endif // __CPU_PRED_PERCEPTRON_PRED_HH__
