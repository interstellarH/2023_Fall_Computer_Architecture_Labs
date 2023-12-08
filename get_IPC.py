import os
# system.cpu.ipc

# 指定文件夹和文件名
folder_path = "./bfs+1.5+bimode+globalsize+32768" #根据不同文件夹修改
file_name = "stats.txt"

# 构造完整的文件路径
file_path = os.path.join(folder_path, file_name)

# 打开文件并读取内容
with open(file_path, 'r') as stats:
    lst = stats.readlines()
    IPC = 0.0
    for item in lst:
        if 'system.cpu.ipc' in item:
            IPC = float(item.split()[1])

    with open('res.txt', 'a') as res:
        res.write(str(IPC) + ' ')
    print(IPC)
