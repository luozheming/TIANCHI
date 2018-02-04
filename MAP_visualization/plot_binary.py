# -*- coding: utf-8 -*-
"""
Created on Tue Jan 30 23:48:42 2018

@author: 颜
"""

import numpy as np
import pickle
import pandas as pd
from tqdm import tqdm
import os
import torch
import matplotlib.pyplot as plt

cachepath='plot_cache'

def generate_map(path,k):
    a=pd.read_csv(path)
    x_max=int(a.xid.max())
    x_min=int(a.xid.min())
    y_max=int(a.yid.max())
    y_min=int(a.yid.min())
    d_max=int(a.date_id.max())
    d_min=int(a.date_id.min())
    h_max=int(a.hour.max())
    h_min=int(a.hour.min())
    coord=a.values[:,0:5].astype(int)
    wind=a.values[:,5]
    lr=a.values[:,6]
    WIND=np.zeros([(d_max-d_min+1)*(h_max-h_min+1),x_max-x_min+1,y_max-y_min+1,],dtype=int)#shape=[5*18,548,421]
    LR=np.zeros([(d_max-d_min+1)*(h_max-h_min+1),x_max-x_min+1,y_max-y_min+1,],dtype=int)#shape=[5*18,548,421]
    for i in tqdm(range(len(coord))):
        WIND[(coord[i][3]-d_min)*(h_max-h_min+1)+(coord[i][4]-h_min),coord[i][1]-x_min,coord[i][2]-y_min]=int(wind[i]>=15)
        LR[(coord[i][3]-d_min)*(h_max-h_min+1)+(coord[i][4]-h_min),coord[i][1]-x_min,coord[i][2]-y_min]=int(lr[i]>=k/48.3)
    dump_map(WIND,'WIND.pkl')
    dump_map(LR,'LR.pkl')
    return WIND,LR

def dump_map(map,file):
    with open(os.path.join(cachepath,file),'wb') as file:
        pickle.dump(map,file)
    print("File Dumped !")

def binary_map(wind,lr):
    start=[142,328,0]
    end_list=[[84,203],[199,371],[140,234],[236,241],[315,281],[358,207],[363,237],[423,266],[125,375],[189,274]]
    W=torch.from_numpy(wind).cuda()
    L=torch.from_numpy(lr).cuda()
    R=(3*(W*L)+2*W*(1-L)-2*(1-W)*L-3*(1-W)*(1-L)).transpose(1,2)
    R[:,start[1]-1:start[1]+2,start[0]]=-4
    R[:,start[1],start[0]-1:start[0]+2]=-4
    for p in end_list:
        R[:,p[1]-1:p[1]+2,p[0]]=4
        R[:,p[1],p[0]-1:p[0]+2]=4
    return np.flip(R.cpu().numpy().astype(dtype=float),1)

def plot_map(R):
    for i in tqdm(range(5)):
        fig = plt.gcf()
        fig.set_size_inches(80,80)
        for j in range(18):
            ax = fig.add_subplot(6,3,j+1)
            im=ax.imshow(R[i*18+j],interpolation='nearest')
            ax.set_title('day_'+str(i)+'hour'+str(j))
        if i==0:
            fig.colorbar(im)
        fig.savefig(os.path.join(cachepath,'day_'+str(i)+'.png'), dpi=100)
        del fig


generate_map('data/transformmap67.csv',13.5)
with open('plot_cache/LR.pkl','rb') as file:
    L=pickle.load(file)
with open('plot_cache/WIND.pkl','rb') as file:
    W=pickle.load(file)
R=binary_map(W,L)
plot_map(R)

