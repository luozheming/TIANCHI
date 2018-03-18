# -*- coding: utf-8 -*-
"""
Created on Fri Nov 24 15:16:43 2017

@author: 颜
"""
'''
This file defines the algorithm for path searching.
'''
import numpy as np
import os
import pickle
import pandas as pd
from tqdm import tqdm
import copy

cachepath='cache'

class Map():
    '''
    传入4维的numpy,map
    形如[x,y,t,2]
    最后一维为二元组[代价,风速]
    未知代价为-1
    墙被标记为风速>20
    '''
    def __init__(self,map):
        self.map=map
        self.derection=[[0,0,1],
                        [0,-1,1],
                        [0,1,1],
                        [-1,0,1],
                        [1,0,1]]
        self.shape=np.shape(map)

    def explore_map(self,start,end,k):                                                #标注地图
        '''
        start,[x,y,t]三元组
        end为,[x,y]二元组
        返回end为,[x,y,t]三元组
        '''
        self.map[start[0],start[1],start[2]][0]=0
        que0=[]
        que1=[start]
        que2=[]
        p=True
        while(p and (que1 or que2)):                                                          #没有找到end且que2非空
            que0=que1
            que1=que2
            que2=[]
            while(que0):
                x=que0.pop(0)
                for direction in self.derection:                                    #在所有方向
                    y=[x[0]+direction[0],x[1]+direction[1],x[2]+direction[2]]
                    if self.point_valid(y,start,end,k) and self.map[y[0],y[1],y[2]][0]==-1:        #x不是墙且没有生成代价
                        change_price=self.get_price(x,y,end)                        #得到代价变化量
                        self.map[y[0],y[1],y[2]][0]=change_price+self.map[x[0],x[1],x[2]][0]
                        if change_price==0:
                            que0.append(y)
                        elif change_price==1:
                            que1.append(y)
                        elif change_price==2:
                            que2.append(y)
                        if x[0]==end[0] and x[1]==end[1]:                                        #找到了终点
                            if p:
                                end=np.append(end,x[2])
                            p=False
        return end

    def get_path(self,start,end,k):                                                   #搜索路径
        '''
        输入end为三元组[x,y,t]
        返回path,[[x,y,t],...,[x,y,t]]
        '''
        path=[[end[0],end[1],end[2],self.map[end[0],end[1],end[2]][0],self.map[end[0],end[1],end[2]][1]]]
        x=end
        while(not (x[0]==start[0] and x[1]==start[1])):
            temp=True
            for direction in self.derection:
                y=[x[0]+direction[0],x[1]+direction[1],x[2]-direction[2]]
                if self.point_valid(y,start,end,k):
                    change_price=self.map[x[0],x[1],x[2]][0]-self.map[y[0],y[1],y[2]][0]
                    if self.get_price(y,x,end)==change_price and (not self.map[y[0],y[1],y[2]][0]==-1):
                        if temp==True:
                            temp=y
                        elif self.map[y[0],y[1],y[2]][1]<self.map[temp[0],temp[1],temp[2]][1]:
                                temp=y
            if temp==True:
                break
            else:
                x=[temp[0],temp[1],temp[2],self.map[temp[0],temp[1],temp[2]][0],self.map[temp[0],temp[1],temp[2]][1]]
                path.append(x)
        return path

    def point_valid(self,x,start,end,k):                                                           #是否越界
        p=True
        if x[0]<0 or x[0]>=self.shape[0]:                                           #x越界
            p=False
        elif x[1]<0 or x[1]>=self.shape[1]:                                           #y越界
            p=False
        elif x[2]<0 or x[2]>=self.shape[2]:                                          #t越界
            p=False
        elif abs(x[0]-end[0])+abs(x[1]-end[1])>self.shape[2]-x[2]-1:                 #end不可达
            p=False
        elif self.map[x[0],x[1],x[2]][1]>=15+k:                                         #是否为墙
            p=False
        return p

    def get_price(self,x,y,end):
        dis_x=abs(x[0]-end[0])+abs(x[1]-end[1])                        #x,y到end的曼哈顿距离
        dis_y=abs(y[0]-end[0])+abs(y[1]-end[1])
        if dis_x==dis_y:
            return 1
        elif dis_x>dis_y:
            return 0
        else:
            return 2

    def path_valid(self,x,y,end):                           #x->y是否符合反向搜索原则
        change_price=self.get_price(x,y,end)
        map_change_price=self.map[x[0],x[1],x[2]][0]-self.map[y[0],y[1],y[2]][0]
        return map_change_price==change_price

def generate_map(path,using_cache=True):
    '''
    用于5天的生成大地图
    '''
    a=pd.read_csv(path)
    x_max=a.xid.max()
    x_min=a.xid.min()
    y_max=a.yid.max()
    y_min=a.yid.min()
    d_max=a.date_id.max()
    d_min=a.date_id.min()
    h_max=a.hour.max()
    h_min=a.hour.min()
    A=a.values[:,0:5].astype(int)
    B=a.values[:,5]
    map=-np.ones([d_max-d_min+1,x_max-x_min+1,y_max-y_min+1,(h_max-h_min+1)*30,2],dtype=float)
    for i in tqdm(range(len(A))):
        temp=np.array([[-1.,B[i]]]).repeat(30,0)
        map[A[i][3]-d_min,A[i][1]-x_min,A[i][2]-y_min,(A[i][4]-h_min)*30:(A[i][4]-h_min)*30+30,:]=temp
    print("big map is ready !")
    for i in range(5):
        dump_map(map[i],i)

def dump_map(map,i):
    '''
    将大地图分割保存为50个文件
    '''
    with open(os.path.join(cachepath,'map_'+str(i)+'.pkl'),'wb') as file:
        pickle.dump(map,file)
    print("map index",i," in day",i+1,"dumped !")

def load_map(i):
    with open(os.path.join(cachepath,'map_'+str(i)+'.pkl'),'rb') as file:
        map=pickle.load(file)
    print("map index",i," in day",i+1,"loaded !")
    return map

def get_time(t,h_min):
    '''
    将时间坐标转化为标准格式
    '''
    min=int(t%30*2)
    hour=int((t-min/2)//30+h_min)
    if min<10:
        min='0'+str(min)
    else:
        min=str(min)
    if hour<10:
        hour='0'+str(hour)
    else:
        hour=str(hour)
    return hour+':'+min

def search_path(i,j,start,end,h_min):
    '''
    用于并发,每个进程根据(i,j)读取自己的地图文件,搜索路径并写入文件名包含index的缓存文件
    '''
    path_list=[]
    index=i*10+j
    with open(os.path.join(cachepath,'map_'+str(i)+'_'+str(j)+'.pkl'),'rb') as file:
        read_map=pickle.load(file)
    read_map[start[0],start[1],:,1]=0
    k=0
    while(1):
        print("search map: index=",index,'[',i+1,j+1,']',"k=",k)
        map=Map(copy.deepcopy(read_map))
        end_point=map.explore_map(start,end,k)
        if len(end_point)==2:
            k+=1
            del map
        else:
            break
    path=map.get_path(start,end_point,k)
    print("Path writting: index=",index,'[',i+1,j+1,']',"k=",k)
    l=len(path)
    for k in range(l):
        temp=[str(i+1),str(j+1),get_time(path[l-k-1][2],h_min),str(path[l-k-1][0]),str(path[l-k-1][1]),str(path[l-k-1][3]),str(path[l-k-1][4])]
        path_list.append(temp)
    with open(os.path.join(cachepath,'path'+str(index)+'.pkl'),'wb') as file:
        pickle.dump(path_list,file)

def write_csv(output_test_file):
    '''
    从0到49读取路径缓存并写入csv
    '''
    if output_test_file:
        k=7
    else:
        k=5
    with open("path.csv",'w') as csv:
        for index in range(50):
            with open(os.path.join(cachepath,'path'+str(index)+'.pkl'),'rb') as file:
                path_list=pickle.load(file)
                l=len(path_list)
                for i in range(l):
                    for j in range(k):
                        csv.write(str(path_list[i][j]))
                        if j==6:
                            csv.write('\n')
                        else:
                            csv.write(',')