import os
# system.cpu.branchPred.condPredicted
# system.cpu.branchPred.condIncorrect

# 指定文件夹和文件名
folder_path = "./bfs+1.5+bimode+globalsize+32768" #根据不同文件夹修改
file_name = "stats.txt"

# 构造完整的文件路径
file_path = os.path.join(folder_path, file_name)

# 打开文件并读取内容
with open(file_path, 'r') as stats:
    lst = stats.readlines()
    condPredicted = condIncorrect = 0
    for item in lst:
        if 'system.cpu.branchPred.condPredicted' in item:
            condPredicted = int(item.split()[1])
        elif 'system.cpu.branchPred.condIncorrect' in item:
            condIncorrect = int(item.split()[1])

    BHitRate = condPredicted / (condPredicted + condIncorrect)
    with open('res.txt', 'a') as res:
        res.write(str(BHitRate) + ' ')
    print(BHitRate)
