# -*- coding: utf-8 -*-
"""
Created on Fri Jan 12 10:01:26 2018

@author: 颜
"""
import math
import numpy as np
import os
import pickle
import pandas as pd
from tqdm import tqdm
import torch
from Propagate import Propagator

cachepath='cache'

def generate_map(path,k,using_cache=True):
    '''
    用于5天的生成大地图
    '''
    a=pd.read_csv(path)
    x_max=int(a.xid.max())
    x_min=int(a.xid.min())
    y_max=int(a.yid.max())
    y_min=int(a.yid.min())
    d_max=int(a.date_id.max())
    d_min=int(a.date_id.min())
    h_max=int(a.hour.max())
    h_min=int(a.hour.min())
    w_max=a.wind.max()
    w_min=a.wind.min()
    A=a.values[:,0:5].astype(int)
    B=a.values[:,5]
    C=a.values[:,6]
    map=-np.ones([(d_max-d_min+1),x_max-x_min+1,y_max-y_min+1,(h_max-h_min+1)],dtype=float)#shape=[5,548,421,18]
    for i in tqdm(range(len(A))):
        if C[i]>=4:
            map[(A[i][3]-d_min),A[i][1]-x_min,A[i][2]-y_min,(A[i][4]-h_min)]=1.
        else:
            map[(A[i][3]-d_min),A[i][1]-x_min,A[i][2]-y_min,(A[i][4]-h_min)]=sigmoid(B[i],k)
    print("big map is ready !")
    dump_map(map,0)
    del map

def sigmoid(x,k):
    x=-(x-k/34.1)*(5./(1.5/34.1))
    x=1./(1+math.exp(x))
    return x

def dump_map(map,i):
    with open(os.path.join(cachepath,'map_'+str(i)+'.pkl'),'wb') as file:
        pickle.dump(map,file)
    print("map index",i," in day",i+1,"dumped !")

def search_path(start,end_list,min_prob=False):
    t=start[2]//5
    with open(os.path.join(cachepath,'map_'+str(0)+'.pkl'),'rb') as file:
        read_map=pickle.load(file)
    with open(os.path.join(cachepath,'path_valid_'+str(t)+'.txt'),'w') as file:
        file.write('index\tS_score\tE_score\tdead_prob\n')
    path_valid=np.zeros([5,10,3],dtype=float)
    for i in range(5):
        print("Search Day"+str(i)+', start at time'+str(start[2]))
        map=Map(read_map[i])
        end_time,end_score,end_prob=map.explore_map(start,end_list,min_prob)
        map.cache_path(start,end_list,end_time,i)
        with open(os.path.join(cachepath,'path_valid_'+str(t)+'.txt'),'a+') as file:
            for j in range(10):
                path_valid[i,j,0]=end_score[j]      #期望得分
                path_valid[i,j,1]=end_time[j]*2     #理论的粉
                path_valid[i,j,2]=end_prob[j]       #死亡概率
                file.write('%d\t%.2f\t%d\t%.6f'%(i*10+j,end_score[j],end_time[j]*2,end_prob[j]))
                file.write('\n')
        with open(os.path.join(cachepath,'path_valid_'+str(t)+'.pkl'),'wb') as file:
            pickle.dump(path_valid,file)

def write_csv(save_as,list=None,not_in=False):
    '''111
    从0到49读取路径缓存并写入csv
    '''
    dic={}
    path_valid_list=[]
    path_valid_final=np.zeros([5,10],dtype=int)
    for t in range(10):
        with open(os.path.join(cachepath,'path_valid_'+str(t)+'.pkl'),'rb') as file:
            path_valid=pickle.load(file)
        path_valid_list.append(path_valid)
        for i in range(5):
            for j in range(10):
                index=i*10+j+t*50
                dic[index]=path_valid[i,j,0]
    for k in range(50):
        path_best=min(dic,key=dic.get)
        t=path_best//50
        i=(path_best-50*t)//10
        j=path_best-50*t-10*i
        path_valid_final[i,j]=t
        for p in range(10):
            index=i*10+j+p*50
            if index in dic:
                del dic[index]
        for p in range(10):
            index=i*10+p+t*50
            if index in dic:
                del dic[index]
    with open(os.path.join(cachepath,'path_valid.txt'),'w') as file:
        file.write('index\tE_score\tS_score\tdead_prob\tleave_time\n')
        with open(save_as,'w') as csv:
            for i in range(5):
                for j in range(10):
                    t=path_valid_final[i,j]
                    path_valid=path_valid_list[t]
                    pkl='path'+str(i*10+j)+'_'+str(t)+'.pkl'
                    write_path_to_csv(csv,pkl)
                    file.write('%d\t%.2f\t%d\t%.6f\t%d'%(i*10+j,path_valid[i,j,0],path_valid[i,j,1],path_valid[i,j,2],t))
                    file.write('\n')
    '''
    with open(save_as,'w') as csv:
        for index in range(50):
            if os.path.exists(os.path.join(cachepath,'path'+str(index)+'.pkl')):
                if list==None or ((index in list) and not not_in) or ((index not in list) and not_in):
                    with open(os.path.join(cachepath,'path'+str(index)+'.pkl'),'rb') as file:
                        path_list=pickle.load(file)
                        l=len(path_list)
                        for i in range(l):
                            for j in range(k):
                                csv.write(str(path_list[i][j]))
                                if j==k-1:
                                    csv.write('\n')
                                else:
                                    csv.write(',')
    '''

def write_path_to_csv(csv,pkl):
    if not os.path.exists(os.path.join(cachepath,pkl)):
        return
    with open(os.path.join(cachepath,pkl),'rb') as file:
        path_list=pickle.load(file)
    l=len(path_list)
    for i in range(l):
        for j in range(5):
            csv.write(str(path_list[i][j]))
            if j==4:
                csv.write('\n')
            else:
                csv.write(',')

class Map():
    def __init__(self,map):
        self.map=map
        self.direction=[[0,0,1],
                        [0,-1,1],
                        [0,1,1],
                        [-1,0,1],
                        [1,0,1]]
        self.shape=np.shape(map)
        self.navigator=-np.ones([self.shape[0],self.shape[1],self.shape[2]*30],dtype=int)
        #self.clone=-np.ones([shape[0],shape[1],2,shape[2]*30],dtype=float)

    def visit(self,coord):
        '''
        访问map中坐标coord对应的点
        '''
        map_point=self.map[coord[0],coord[1],coord[2]].tolist()
        return map_point

    def get_layer(self,i):
        i=i//30
        return self.map[:,:,i]

    def explore_map(self,start,end_list,min_prob=False):
        end_score=(np.ones([10],dtype=float)*1440).tolist()
        end_time=(-np.ones([10],dtype=int)).tolist()
        end_prob=(np.ones([10],dtype=int)).tolist()
        propagator=Propagator([self.shape[0],self.shape[1]]).cuda()
        P_A=torch.Tensor(np.ones([self.shape[0],self.shape[1]],dtype=float)).cuda()
        P_A[start[0],start[1]]=0.
        for i in tqdm(range(start[2]+1,self.shape[2]*30)):
            p_B=torch.Tensor(self.get_layer(i)).cuda()
            A=torch.cat((P_A.view([self.shape[0],self.shape[1],1]),p_B.view([self.shape[0],self.shape[1],1])),2)
            P_B,B_direction,B_score=propagator.forward(A,i)
            self.navigator[:,:,i]=B_direction.cpu().numpy()
            P_A=P_B
            for j in range(10):
                end=end_list[j]
                if min_prob:
                    end_t=P_B[end[0],end[1]]
                    if end_t<end_prob[j]:
                        end_time[j]=i
                        end_score[j]=B_score[end[0],end[1]]
                        end_prob[j]=P_B[end[0],end[1]]
                else:
                    end_t=B_score[end[0],end[1]]
                    if end_t<end_score[j]:
                        end_time[j]=i
                        end_score[j]=B_score[end[0],end[1]]
                        end_prob[j]=P_B[end[0],end[1]]
        return end_time,end_score,end_prob

    def get_time(self,t,h_min):
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

    def search_path(self,start,end):
        path=[end]
        pin=end
        while(not(start[0]==pin[0] and start[1]==pin[1] and start[2]==pin[2])):
            direc=self.direction[self.navigator[pin[0],pin[1],pin[2]]]
            pin=[pin[0]-direc[0],pin[1]-direc[1],pin[2]-direc[2]]
            path.append(pin)
        return path

    def cache_path(self,start,end_list,end_time,i):
        print("Cache path in day "+str(i))
        for j in range(10):
            if end_time[j]>0:
                index=i*10+j
                end=[end_list[j][0],end_list[j][1],end_time[j]]
                path=self.search_path(start,end)
                path_list=[]
                l=len(path)
                for line in range(l):
                    temp=[str(j+1),str(i+6),self.get_time(path[l-line-1][2],3),str(path[l-line-1][0]),str(path[l-line-1][1])]
                    path_list.append(temp)
                with open(os.path.join(cachepath,'path'+str(index)+'_'+str(start[2]//5)+'.pkl'),'wb') as file:
                    pickle.dump(path_list,file)
'''
with open('cache//path20_1.pkl','rb') as file:
    path_valid=pickle.load(file)
path_valid[0]
'''

