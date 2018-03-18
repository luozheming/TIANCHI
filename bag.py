# -*- coding: utf-8 -*-
"""
Created on Fri Jan  5 18:15:29 2018

@author: 颜
"""

'''
queue为二维list,[[path序号,path贡献减分],....],path序号从0到49,path减分=1440-path理论得分
in_bag为与queue同型的list, 记录装入背包的path
empty_space 表示背包剩余空间, 初始值为72000-返回得分
queue_weight表示queue中所有项的贡献减分之和
'''
import pickle
import copy

def one_zero_bag(queue,empty_space,in_bag,queue_weight):
    if queue_weight==empty_space:
        with open("0-1.txt",'a+') as file:
            for i in in_bag:
                file.write(str(i[0])+',')
            for i in queue:
                file.write(str(i[0])+',')
            file.write('\n')
            print('find path!!!')
    elif queue_weight>empty_space and queue_weight>0:
        path=queue[0]
        del queue[0]
        queue_weight-=path[1]
        #path不装入bag
        one_zero_bag(copy.deepcopy(queue),copy.deepcopy(empty_space),copy.deepcopy(in_bag),copy.deepcopy(queue_weight))
        #path装入bag
        empty_space-=path[1]
        in_bag.append(path)
        one_zero_bag(copy.deepcopy(queue),copy.deepcopy(empty_space),copy.deepcopy(in_bag),copy.deepcopy(queue_weight))
    elif queue_weight<empty_space or queue_weight==0:
        return

if __name__ == "__main__":
    __spec__=None
    with open('path_valid.pkl','rb') as file:
        path_valid=pickle.load(file)
    queue=[]
    in_bag=[]
    queue_weight=0
    weight=0
    empty_space=72000-69448
    k=0
    for i in range(5):
        for j in range(10):
            if path_valid[i,j,2]<=0.000 and path_valid[i,j,1]>0:
                queue.append([i*10+j,1440-path_valid[i,j,1]])
                queue_weight+=1440-path_valid[i,j,1]
                k+=1
    print('search in %d path'%(k))
    one_zero_bag(queue,empty_space,in_bag,queue_weight)