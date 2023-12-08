import matplotlib.pyplot as plt
# 如果两个值相差过大可以采用双坐标轴画法
id = ['bimode', 'local', 'tournament']
mm = [0.958526565864456, 0.9573513236039506, 0.9585276941169196]
bfs = [0.9651330983530055, 0.9530552871754961, 0.9700705675237961]
x = list(range(3))
width = [0.35 for _ in range(3)]
plt.figure() # create a new figure
plt.bar([x[i]-width[i]/2 for i in range(3)], mm,
width, color='navy')
plt.bar([x[i]+width[i]/2 for i in range(3)], bfs,
width, color='lime')
plt.legend(['2mm', 'bfs']) # set legends
plt.xticks(ticks=x, labels=id) # set the tick labels of x-axis
plt.xlabel('id') # set the label of x-axis
plt.ylabel('Branch_hit_rate') # set the label of y-axis
plt.savefig('bar1_1.png')
# plt.show()