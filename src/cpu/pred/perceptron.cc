/* @file
 * Implementation of a perceptron branch predictor
 */

#include "cpu/pred/perceptron.hh"
#include "base/bitfield.hh"
#include "base/intmath.hh"
#include "perceptron.hh"
#include "params/PerceptronBP.hh"

namespace gem5
{

namespace branch_prediction
{

PerceptronBP::PerceptronBP(const PerceptronBPParams &params)
    : BPredUnit(params),
      globalHistoryReg(params.numThreads, 0),
      globalHistoryBits(params.GHR_len), //此时GHR_len是一个可调参数
      globalPredictorSize(params.globalPredictorSize),
      globalCtrBits(params.GHR_len),
      threshold(params.threshold),
      ToP(globalPredictorSize, Perceptron(globalCtrBits+1)) //改成perceptron的表
      
{
    if (!isPowerOf2(globalPredictorSize))
        fatal("Invalid global history predictor size.\n");

    historyRegisterMask = mask(globalHistoryBits);
    globalHistoryMask = globalPredictorSize - 1;

}

/*
 * For an unconditional branch we set its history such that
 * everything is set to taken. I.e., its choice predictor
 * chooses the taken array and the taken array predicts taken.
 */
void
PerceptronBP::uncondBranch(ThreadID tid, Addr pc, void * &bpHistory)
{
    BPHistory *history = new BPHistory;
    history->globalHistoryReg = globalHistoryReg[tid];
    history->finalPred = true;
    history->y = 0;
    bpHistory = static_cast<void*>(history);
    updateGlobalHistReg(tid, true);
}

void
PerceptronBP::squash(ThreadID tid, void *bpHistory)
{
    BPHistory *history = static_cast<BPHistory*>(bpHistory);
    globalHistoryReg[tid] = history->globalHistoryReg;

    delete history;
}

/*
 * Here we lookup the actual branch prediction. We use the PC to
 * identify the bias of a particular branch, which is based on the
 * prediction in the choice array. A hash of the global history
 * register and a branch's PC is used to index into both the taken
 * and not-taken predictors, which both present a prediction. The
 * choice array's prediction is used to select between the two
 * direction predictors for the final branch prediction.
 */
bool
PerceptronBP::lookup(ThreadID tid, Addr branchAddr, void * &bpHistory)
{
    // index -> perceptron -> cal y -> branch

    unsigned globalHistoryIdx = (((branchAddr >> instShiftAmt)
                                ^ globalHistoryReg[tid])
                                & globalHistoryMask);

    assert(globalHistoryIdx < globalPredictorSize);

    //perceptron的预测过程
    //1.计算y(dot product)
    int y = ToP[globalHistoryIdx].weight[globalCtrBits]; //初始化就加上bias
    for(int i = 0; i < globalCtrBits; i++)
    {
        if(((globalHistoryReg[tid]>>i)&1) == 1) 
        {
            y += ToP[globalHistoryIdx].weight[i];
        }
        else{ // 0 regarded as -1
            y -= ToP[globalHistoryIdx].weight[i];
        }
    }
    //2.计算预测结果
    bool finalPrediction = (y >= 0);

    BPHistory *history = new BPHistory;
    history->globalHistoryReg = globalHistoryReg[tid];
    history-> y = y; //计算结果
    history->finalPred = finalPrediction;
    bpHistory = static_cast<void*>(history);
    updateGlobalHistReg(tid, finalPrediction);

    return finalPrediction;
}

void
PerceptronBP::btbUpdate(ThreadID tid, Addr branchAddr, void * &bpHistory)
{
    globalHistoryReg[tid] &= (historyRegisterMask & ~1ULL);
}

/* Only the selected direction predictor will be updated with the final
 * outcome; the status of the unselected one will not be altered. The choice
 * predictor is always updated with the branch outcome, except when the
 * choice is opposite to the branch outcome but the selected counter of
 * the direction predictors makes a correct final prediction.
 */
void
PerceptronBP::update(ThreadID tid, Addr branchAddr, bool taken, void *bpHistory,
                 bool squashed, const StaticInstPtr & inst, Addr corrTarget)
{
    assert(bpHistory);

    BPHistory *history = static_cast<BPHistory*>(bpHistory);

    // We do not update the counters speculatively on a squash.
    // We just restore the global history register.
    if (squashed) {
        globalHistoryReg[tid] = (history->globalHistoryReg << 1) | taken;
        return;
    }

    unsigned globalHistoryIdx = (((branchAddr >> instShiftAmt)
                                ^ history->globalHistoryReg)
                                & globalHistoryMask);

    assert(globalHistoryIdx < globalPredictorSize);

    //更新权重
    if(history->finalPred != taken || abs(history->y) <= threshold) //预测错误或者y小于阈值
    {
        for(int i = 0; i < globalCtrBits; i++)
        {// Here we should use history->globalHistoryReg instead of globalHistoryReg[tid]
            if(((history->globalHistoryReg>>i)&1) == taken)
            {
                ToP[globalHistoryIdx].weight[i]++;
            }
            else
            {
                ToP[globalHistoryIdx].weight[i]--;
            }
        }
        if(taken) //特殊处理bias
        {
            ToP[globalHistoryIdx].weight[globalCtrBits]++;
        }
        else
        {
            ToP[globalHistoryIdx].weight[globalCtrBits]--;
        }
    }

    delete history;
}

void
PerceptronBP::updateGlobalHistReg(ThreadID tid, bool taken)
{
    globalHistoryReg[tid] = taken ? (globalHistoryReg[tid] << 1) | 1 :
                               (globalHistoryReg[tid] << 1);
    globalHistoryReg[tid] &= historyRegisterMask;
}


}// namespace branch_prediction
} // namespace gem5

